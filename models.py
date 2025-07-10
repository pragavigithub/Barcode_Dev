from datetime import datetime
from app import db
from werkzeug.security import generate_password_hash, check_password_hash
from sqlalchemy import Enum, Numeric
import enum

class UserRole(enum.Enum):
    ADMIN = "admin"
    MANAGER = "manager"
    WAREHOUSE_STAFF = "warehouse_staff"
    QC_STAFF = "qc_staff"
    VIEW_ONLY = "view_only"

class GRPOStatus(enum.Enum):
    DRAFT = "draft"
    PENDING_QC = "pending_qc"
    QC_APPROVED = "qc_approved"
    QC_REJECTED = "qc_rejected"
    POSTED_TO_SAP = "posted_to_sap"

class User(db.Model):
    __tablename__ = 'users'
    
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(80), unique=True, nullable=False)
    email = db.Column(db.String(120), unique=True, nullable=False)
    password_hash = db.Column(db.String(256), nullable=False)
    full_name = db.Column(db.String(200), nullable=False)
    role = db.Column(Enum(UserRole), nullable=False, default=UserRole.WAREHOUSE_STAFF)
    branch_id = db.Column(db.String(20), nullable=True)  # SAP B1 Branch ID
    is_active = db.Column(db.Boolean, default=True)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    # Relationships
    grpos = db.relationship('GRPO', backref='created_by_user', lazy=True)
    qc_approvals = db.relationship('QCApproval', backref='qc_user', lazy=True)
    
    def set_password(self, password):
        self.password_hash = generate_password_hash(password)
    
    def check_password(self, password):
        return check_password_hash(self.password_hash, password)
    
    def has_permission(self, permission):
        permissions = {
            UserRole.ADMIN: ['all'],
            UserRole.MANAGER: ['grpo_create', 'grpo_edit', 'grpo_view', 'qc_approve', 'user_view', 'reports'],
            UserRole.WAREHOUSE_STAFF: ['grpo_create', 'grpo_edit', 'grpo_view'],
            UserRole.QC_STAFF: ['grpo_view', 'qc_approve'],
            UserRole.VIEW_ONLY: ['grpo_view', 'reports']
        }
        user_permissions = permissions.get(self.role, [])
        return 'all' in user_permissions or permission in user_permissions

class PurchaseOrder(db.Model):
    __tablename__ = 'purchase_orders'
    
    id = db.Column(db.Integer, primary_key=True)
    po_number = db.Column(db.String(50), unique=True, nullable=False)
    supplier_code = db.Column(db.String(50), nullable=False)
    supplier_name = db.Column(db.String(200), nullable=False)
    branch_id = db.Column(db.String(20), nullable=False)
    po_date = db.Column(db.Date, nullable=False)
    delivery_date = db.Column(db.Date, nullable=True)
    total_amount = db.Column(Numeric(15, 2), nullable=False)
    currency = db.Column(db.String(3), default='USD')
    status = db.Column(db.String(20), default='Open')
    sap_doc_entry = db.Column(db.Integer, nullable=True)  # SAP B1 Document Entry
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    
    # Relationships
    po_lines = db.relationship('PurchaseOrderLine', backref='purchase_order', lazy=True)
    grpos = db.relationship('GRPO', backref='purchase_order', lazy=True)

class PurchaseOrderLine(db.Model):
    __tablename__ = 'purchase_order_lines'
    
    id = db.Column(db.Integer, primary_key=True)
    po_id = db.Column(db.Integer, db.ForeignKey('purchase_orders.id'), nullable=False)
    line_number = db.Column(db.Integer, nullable=False)
    item_code = db.Column(db.String(50), nullable=False)
    item_description = db.Column(db.String(500), nullable=False)
    ordered_quantity = db.Column(Numeric(15, 3), nullable=False)
    received_quantity = db.Column(Numeric(15, 3), default=0)
    unit_price = db.Column(Numeric(15, 2), nullable=False)
    unit_of_measure = db.Column(db.String(20), nullable=False)
    warehouse_code = db.Column(db.String(20), nullable=False)
    
    @property
    def open_quantity(self):
        return self.ordered_quantity - self.received_quantity

class GRPO(db.Model):
    __tablename__ = 'grpos'
    
    id = db.Column(db.Integer, primary_key=True)
    grn_number = db.Column(db.String(50), unique=True, nullable=False)
    po_id = db.Column(db.Integer, db.ForeignKey('purchase_orders.id'), nullable=False)
    created_by = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)
    status = db.Column(Enum(GRPOStatus), nullable=False, default=GRPOStatus.DRAFT)
    receipt_date = db.Column(db.Date, nullable=False)
    supplier_delivery_note = db.Column(db.String(100), nullable=True)
    remarks = db.Column(db.Text, nullable=True)
    total_amount = db.Column(Numeric(15, 2), nullable=False, default=0)
    sap_doc_entry = db.Column(db.Integer, nullable=True)  # SAP B1 Document Entry
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    # Relationships
    grpo_lines = db.relationship('GRPOLine', backref='grpo', lazy=True)
    qc_approval = db.relationship('QCApproval', backref='grpo', uselist=False)
    qr_codes = db.relationship('QRCode', backref='grpo', lazy=True)

class GRPOLine(db.Model):
    __tablename__ = 'grpo_lines'
    
    id = db.Column(db.Integer, primary_key=True)
    grpo_id = db.Column(db.Integer, db.ForeignKey('grpos.id'), nullable=False)
    po_line_id = db.Column(db.Integer, db.ForeignKey('purchase_order_lines.id'), nullable=False)
    received_quantity = db.Column(Numeric(15, 3), nullable=False)
    bin_location = db.Column(db.String(50), nullable=True)
    batch_number = db.Column(db.String(50), nullable=True)
    expiry_date = db.Column(db.Date, nullable=True)
    supplier_barcode = db.Column(db.String(100), nullable=True)
    unit_price = db.Column(Numeric(15, 2), nullable=False)
    line_total = db.Column(Numeric(15, 2), nullable=False)
    
    # Relationships
    po_line = db.relationship('PurchaseOrderLine', backref='grpo_lines')

class QCApproval(db.Model):
    __tablename__ = 'qc_approvals'
    
    id = db.Column(db.Integer, primary_key=True)
    grpo_id = db.Column(db.Integer, db.ForeignKey('grpos.id'), nullable=False)
    qc_user_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)
    approval_status = db.Column(db.String(20), nullable=False)  # 'approved', 'rejected'
    qc_notes = db.Column(db.Text, nullable=True)
    approval_date = db.Column(db.DateTime, default=datetime.utcnow)

class QRCode(db.Model):
    __tablename__ = 'qr_codes'
    
    id = db.Column(db.Integer, primary_key=True)
    grpo_id = db.Column(db.Integer, db.ForeignKey('grpos.id'), nullable=False)
    qr_code_data = db.Column(db.Text, nullable=False)  # JSON data encoded in QR
    qr_code_image_path = db.Column(db.String(500), nullable=True)
    item_code = db.Column(db.String(50), nullable=False)
    quantity = db.Column(Numeric(15, 3), nullable=False)
    batch_number = db.Column(db.String(50), nullable=True)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)

class AuditLog(db.Model):
    __tablename__ = 'audit_logs'
    
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)
    action = db.Column(db.String(100), nullable=False)
    table_name = db.Column(db.String(50), nullable=False)
    record_id = db.Column(db.Integer, nullable=False)
    old_values = db.Column(db.Text, nullable=True)  # JSON
    new_values = db.Column(db.Text, nullable=True)  # JSON
    timestamp = db.Column(db.DateTime, default=datetime.utcnow)
    
    # Relationships
    user = db.relationship('User', backref='audit_logs')
