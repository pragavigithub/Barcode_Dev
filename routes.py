from flask import render_template, request, redirect, url_for, flash, session, jsonify
from datetime import datetime, date
from app import app, db
from models import User, PurchaseOrder, PurchaseOrderLine, GRPO, GRPOLine, QCApproval, QRCode, UserRole, GRPOStatus
from auth import login_required, admin_required, get_current_user
from sap_integration import SAPIntegration
from qr_generator import generate_qr_code, generate_grn_number
import json
import logging

@app.route('/')
def index():
    if 'user_id' not in session:
        return redirect(url_for('login'))
    return redirect(url_for('dashboard'))

@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        username = request.form.get('username')
        password = request.form.get('password')
        branch_id = request.form.get('branch_id')
        
        user = User.query.filter_by(username=username).first()
        
        if user and user.check_password(password) and user.is_active:
            session['user_id'] = user.id
            session['username'] = user.username
            session['role'] = user.role.value
            session['branch_id'] = branch_id or user.branch_id
            
            flash(f'Welcome, {user.full_name}!', 'success')
            return redirect(url_for('dashboard'))
        else:
            flash('Invalid username or password', 'error')
    
    return render_template('login.html')

@app.route('/logout')
def logout():
    session.clear()
    flash('You have been logged out successfully', 'info')
    return redirect(url_for('login'))

@app.route('/dashboard')
@login_required
def dashboard():
    user = get_current_user()
    
    # Get dashboard statistics
    total_grpos = GRPO.query.count()
    pending_qc = GRPO.query.filter_by(status=GRPOStatus.PENDING_QC).count()
    draft_grpos = GRPO.query.filter_by(status=GRPOStatus.DRAFT).count()
    
    # Recent GRPOs
    recent_grpos = GRPO.query.order_by(GRPO.created_at.desc()).limit(5).all()
    
    return render_template('dashboard.html', 
                         user=user,
                         total_grpos=total_grpos,
                         pending_qc=pending_qc,
                         draft_grpos=draft_grpos,
                         recent_grpos=recent_grpos)

@app.route('/grpos')
@login_required
def grpo_list():
    user = get_current_user()
    page = request.args.get('page', 1, type=int)
    status_filter = request.args.get('status', '')
    
    query = GRPO.query
    
    if status_filter:
        query = query.filter_by(status=GRPOStatus(status_filter))
    
    grpos = query.order_by(GRPO.created_at.desc()).paginate(
        page=page, per_page=20, error_out=False
    )
    
    return render_template('grpo_list.html', grpos=grpos, user=user, status_filter=status_filter)

@app.route('/grpos/new', methods=['GET', 'POST'])
@login_required
def create_grpo():
    user = get_current_user()
    
    if not user.has_permission('grpo_create'):
        flash('You do not have permission to create GRPOs', 'error')
        return redirect(url_for('grpo_list'))
    
    if request.method == 'POST':
        po_number = request.form.get('po_number')
        supplier_delivery_note = request.form.get('supplier_delivery_note')
        remarks = request.form.get('remarks')
        
        # Find the PO
        po = PurchaseOrder.query.filter_by(po_number=po_number).first()
        if not po:
            flash('Purchase Order not found', 'error')
            return redirect(url_for('create_grpo'))
        
        # Create GRPO
        grn_number = generate_grn_number()
        grpo = GRPO(
            grn_number=grn_number,
            po_id=po.id,
            created_by=user.id,
            receipt_date=date.today(),
            supplier_delivery_note=supplier_delivery_note,
            remarks=remarks,
            status=GRPOStatus.DRAFT
        )
        
        db.session.add(grpo)
        db.session.commit()
        
        flash(f'GRPO {grn_number} created successfully', 'success')
        return redirect(url_for('grpo_details', grpo_id=grpo.id))
    
    return render_template('grpo_form.html', user=user)

@app.route('/grpos/<int:grpo_id>')
@login_required
def grpo_details(grpo_id):
    user = get_current_user()
    grpo = GRPO.query.get_or_404(grpo_id)
    
    return render_template('grpo_details.html', grpo=grpo, user=user)

@app.route('/grpos/<int:grpo_id>/add_line', methods=['POST'])
@login_required
def add_grpo_line(grpo_id):
    user = get_current_user()
    grpo = GRPO.query.get_or_404(grpo_id)
    
    if not user.has_permission('grpo_edit'):
        flash('You do not have permission to edit GRPOs', 'error')
        return redirect(url_for('grpo_details', grpo_id=grpo_id))
    
    po_line_id = request.form.get('po_line_id')
    received_quantity = float(request.form.get('received_quantity', 0))
    bin_location = request.form.get('bin_location')
    batch_number = request.form.get('batch_number')
    expiry_date = request.form.get('expiry_date')
    supplier_barcode = request.form.get('supplier_barcode')
    
    po_line = PurchaseOrderLine.query.get_or_404(po_line_id)
    
    # Check if quantity is valid
    if received_quantity <= 0 or received_quantity > po_line.open_quantity:
        flash('Invalid quantity received', 'error')
        return redirect(url_for('grpo_details', grpo_id=grpo_id))
    
    # Create GRPO line
    grpo_line = GRPOLine(
        grpo_id=grpo.id,
        po_line_id=po_line.id,
        received_quantity=received_quantity,
        bin_location=bin_location,
        batch_number=batch_number,
        expiry_date=datetime.strptime(expiry_date, '%Y-%m-%d').date() if expiry_date else None,
        supplier_barcode=supplier_barcode,
        unit_price=po_line.unit_price,
        line_total=received_quantity * po_line.unit_price
    )
    
    db.session.add(grpo_line)
    
    # Update PO line received quantity
    po_line.received_quantity += received_quantity
    
    # Update GRPO total
    grpo.total_amount += grpo_line.line_total
    
    db.session.commit()
    
    flash('Line added successfully', 'success')
    return redirect(url_for('grpo_details', grpo_id=grpo_id))

@app.route('/grpos/<int:grpo_id>/submit_for_qc', methods=['POST'])
@login_required
def submit_grpo_for_qc(grpo_id):
    user = get_current_user()
    grpo = GRPO.query.get_or_404(grpo_id)
    
    if not user.has_permission('grpo_edit'):
        flash('You do not have permission to submit GRPOs for QC', 'error')
        return redirect(url_for('grpo_details', grpo_id=grpo_id))
    
    if grpo.status != GRPOStatus.DRAFT:
        flash('GRPO is not in draft status', 'error')
        return redirect(url_for('grpo_details', grpo_id=grpo_id))
    
    if not grpo.grpo_lines:
        flash('Cannot submit GRPO without any lines', 'error')
        return redirect(url_for('grpo_details', grpo_id=grpo_id))
    
    # Generate QR codes for received items
    for line in grpo.grpo_lines:
        # Check if quantity should be split
        split_quantities = request.form.getlist(f'split_qty_{line.id}')
        if split_quantities:
            for qty in split_quantities:
                if float(qty) > 0:
                    qr_data = generate_qr_code(grpo, line, float(qty))
                    qr_code = QRCode(
                        grpo_id=grpo.id,
                        qr_code_data=qr_data,
                        item_code=line.po_line.item_code,
                        quantity=float(qty),
                        batch_number=line.batch_number
                    )
                    db.session.add(qr_code)
        else:
            # Single QR code for the entire quantity
            qr_data = generate_qr_code(grpo, line, line.received_quantity)
            qr_code = QRCode(
                grpo_id=grpo.id,
                qr_code_data=qr_data,
                item_code=line.po_line.item_code,
                quantity=line.received_quantity,
                batch_number=line.batch_number
            )
            db.session.add(qr_code)
    
    grpo.status = GRPOStatus.PENDING_QC
    db.session.commit()
    
    flash('GRPO submitted for Quality Control approval', 'success')
    return redirect(url_for('grpo_details', grpo_id=grpo_id))

@app.route('/qc/pending')
@login_required
def qc_pending():
    user = get_current_user()
    
    if not user.has_permission('qc_approve'):
        flash('You do not have permission to access QC approvals', 'error')
        return redirect(url_for('dashboard'))
    
    pending_grpos = GRPO.query.filter_by(status=GRPOStatus.PENDING_QC).all()
    
    return render_template('qc_approval.html', grpos=pending_grpos, user=user)

@app.route('/qc/approve/<int:grpo_id>', methods=['POST'])
@login_required
def approve_grpo(grpo_id):
    user = get_current_user()
    grpo = GRPO.query.get_or_404(grpo_id)
    
    if not user.has_permission('qc_approve'):
        flash('You do not have permission to approve GRPOs', 'error')
        return redirect(url_for('qc_pending'))
    
    approval_status = request.form.get('approval_status')
    qc_notes = request.form.get('qc_notes')
    
    # Create QC approval record
    qc_approval = QCApproval(
        grpo_id=grpo.id,
        qc_user_id=user.id,
        approval_status=approval_status,
        qc_notes=qc_notes
    )
    
    db.session.add(qc_approval)
    
    if approval_status == 'approved':
        grpo.status = GRPOStatus.QC_APPROVED
        
        # Post to SAP B1
        try:
            sap = SAPIntegration()
            sap_doc_entry = sap.post_grpo_to_sap(grpo)
            
            if sap_doc_entry:
                grpo.sap_doc_entry = sap_doc_entry
                grpo.status = GRPOStatus.POSTED_TO_SAP
                flash('GRPO approved and posted to SAP B1 successfully', 'success')
            else:
                flash('GRPO approved but failed to post to SAP B1', 'warning')
        except Exception as e:
            logging.error(f"SAP posting error: {e}")
            flash('GRPO approved but SAP posting failed', 'warning')
    else:
        grpo.status = GRPOStatus.QC_REJECTED
        flash('GRPO rejected', 'info')
    
    db.session.commit()
    
    return redirect(url_for('qc_pending'))

@app.route('/users')
@admin_required
def user_management():
    users = User.query.all()
    return render_template('user_management.html', users=users)

@app.route('/users/new', methods=['GET', 'POST'])
@admin_required
def create_user():
    if request.method == 'POST':
        username = request.form.get('username')
        email = request.form.get('email')
        password = request.form.get('password')
        full_name = request.form.get('full_name')
        role = request.form.get('role')
        branch_id = request.form.get('branch_id')
        
        # Check if user already exists
        if User.query.filter_by(username=username).first():
            flash('Username already exists', 'error')
            return redirect(url_for('create_user'))
        
        if User.query.filter_by(email=email).first():
            flash('Email already exists', 'error')
            return redirect(url_for('create_user'))
        
        user = User(
            username=username,
            email=email,
            full_name=full_name,
            role=UserRole(role),
            branch_id=branch_id
        )
        user.set_password(password)
        
        db.session.add(user)
        db.session.commit()
        
        flash('User created successfully', 'success')
        return redirect(url_for('user_management'))
    
    return render_template('user_form.html')

@app.route('/reports')
@login_required
def reports():
    user = get_current_user()
    
    if not user.has_permission('reports'):
        flash('You do not have permission to view reports', 'error')
        return redirect(url_for('dashboard'))
    
    # Generate report data
    grpo_by_status = db.session.query(
        GRPO.status, db.func.count(GRPO.id)
    ).group_by(GRPO.status).all()
    
    monthly_grpos = db.session.query(
        db.func.date_format(GRPO.created_at, '%Y-%m').label('month'),
        db.func.count(GRPO.id).label('count')
    ).group_by(db.func.date_format(GRPO.created_at, '%Y-%m')).all()
    
    return render_template('reports.html', 
                         user=user,
                         grpo_by_status=grpo_by_status,
                         monthly_grpos=monthly_grpos)

# API endpoints for barcode scanning
@app.route('/api/scan_po', methods=['POST'])
@login_required
def scan_po():
    po_number = request.json.get('po_number')
    po = PurchaseOrder.query.filter_by(po_number=po_number).first()
    
    if not po:
        return jsonify({'error': 'Purchase Order not found'}), 404
    
    po_data = {
        'po_number': po.po_number,
        'supplier_name': po.supplier_name,
        'po_date': po.po_date.isoformat(),
        'lines': []
    }
    
    for line in po.po_lines:
        po_data['lines'].append({
            'id': line.id,
            'item_code': line.item_code,
            'item_description': line.item_description,
            'ordered_quantity': float(line.ordered_quantity),
            'received_quantity': float(line.received_quantity),
            'open_quantity': float(line.open_quantity),
            'unit_of_measure': line.unit_of_measure,
            'unit_price': float(line.unit_price)
        })
    
    return jsonify(po_data)

@app.route('/api/scan_barcode', methods=['POST'])
@login_required
def scan_barcode():
    barcode = request.json.get('barcode')
    
    # Mock barcode scanning - in real implementation, this would decode the barcode
    # and return item details, batch number, expiry date, etc.
    mock_data = {
        'item_code': 'ITEM001',
        'batch_number': 'B001-2024',
        'expiry_date': '2025-12-31',
        'supplier_barcode': barcode
    }
    
    return jsonify(mock_data)

@app.errorhandler(404)
def not_found(error):
    return render_template('404.html'), 404

@app.errorhandler(500)
def internal_error(error):
    db.session.rollback()
    return render_template('500.html'), 500
