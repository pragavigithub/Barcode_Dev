import qrcode
import json
import os
from datetime import datetime
from io import BytesIO
import base64

def generate_grn_number():
    """Generate unique GRN number"""
    timestamp = datetime.now().strftime('%Y%m%d%H%M%S')
    return f"GRN{timestamp}"

def generate_qr_code(grpo, grpo_line, quantity):
    """Generate QR code data for GRPO line"""
    qr_data = {
        'grn_number': grpo.grn_number,
        'po_number': grpo.purchase_order.po_number,
        'item_code': grpo_line.po_line.item_code,
        'item_description': grpo_line.po_line.item_description,
        'quantity': float(quantity),
        'unit_of_measure': grpo_line.po_line.unit_of_measure,
        'batch_number': grpo_line.batch_number,
        'expiry_date': grpo_line.expiry_date.isoformat() if grpo_line.expiry_date else None,
        'bin_location': grpo_line.bin_location,
        'receipt_date': grpo.receipt_date.isoformat(),
        'supplier_code': grpo.purchase_order.supplier_code,
        'generated_at': datetime.now().isoformat()
    }
    
    return json.dumps(qr_data)

def create_qr_code_image(qr_data, filename=None):
    """Create QR code image from data"""
    qr = qrcode.QRCode(
        version=1,
        error_correction=qrcode.constants.ERROR_CORRECT_L,
        box_size=10,
        border=4,
    )
    
    qr.add_data(qr_data)
    qr.make(fit=True)
    
    img = qr.make_image(fill_color="black", back_color="white")
    
    if filename:
        # Save to file
        img.save(filename)
        return filename
    else:
        # Return as base64 string
        buffer = BytesIO()
        img.save(buffer, format='PNG')
        img_str = base64.b64encode(buffer.getvalue()).decode()
        return f"data:image/png;base64,{img_str}"

def decode_qr_code(qr_data):
    """Decode QR code data"""
    try:
        return json.loads(qr_data)
    except json.JSONDecodeError:
        return None

def print_qr_label(qr_codes, printer_name=None):
    """Print QR code labels (mock implementation)"""
    # In a real implementation, this would send the QR codes to a label printer
    # For now, we'll just log the print request
    import logging
    
    logging.info(f"Printing {len(qr_codes)} QR code labels to printer: {printer_name or 'default'}")
    
    for qr_code in qr_codes:
        qr_info = decode_qr_code(qr_code.qr_code_data)
        if qr_info:
            logging.info(f"Label: {qr_info['grn_number']} - {qr_info['item_code']} - Qty: {qr_info['quantity']}")
    
    return True

def split_quantity(total_quantity, split_method='equal', split_count=2):
    """Split quantity into multiple parts"""
    if split_method == 'equal':
        base_qty = total_quantity // split_count
        remainder = total_quantity % split_count
        
        quantities = [base_qty] * split_count
        
        # Distribute remainder
        for i in range(remainder):
            quantities[i] += 1
        
        return quantities
    
    elif split_method == 'custom':
        # Custom split logic would go here
        # For now, return equal split
        return split_quantity(total_quantity, 'equal', split_count)
    
    else:
        return [total_quantity]
