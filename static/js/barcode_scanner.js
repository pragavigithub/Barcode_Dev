// Barcode Scanner functionality for WMS Application
// Handles barcode scanning, QR code generation, and related operations

const BarcodeScanner = {
    isScanning: false,
    activeInput: null,
    scanHistory: [],
    settings: {
        scanTimeout: 10000, // 10 seconds
        minBarcodeLength: 6,
        maxBarcodeLength: 50,
        allowedChars: /^[A-Za-z0-9\-_.]+$/
    }
};

// Initialize barcode scanner
BarcodeScanner.init = function() {
    // Listen for keyboard input for barcode scanning
    document.addEventListener('keydown', this.handleKeyDown.bind(this));
    document.addEventListener('keyup', this.handleKeyUp.bind(this));
    
    // Initialize scan buttons
    const scanButtons = document.querySelectorAll('[data-scan-target]');
    scanButtons.forEach(button => {
        button.addEventListener('click', (e) => {
            const target = e.target.getAttribute('data-scan-target');
            this.startScan(target);
        });
    });
    
    console.log('Barcode Scanner initialized');
};

// Start barcode scanning
BarcodeScanner.startScan = function(targetInput) {
    if (this.isScanning) {
        this.stopScan();
    }
    
    this.isScanning = true;
    this.activeInput = targetInput;
    this.scanBuffer = '';
    this.scanStartTime = Date.now();
    
    // Visual feedback
    this.showScanningModal();
    
    // Auto-stop scanning after timeout
    this.scanTimeoutId = setTimeout(() => {
        this.stopScan();
        WMS.showToast('Scan timeout. Please try again.', 'warning');
    }, this.settings.scanTimeout);
};

// Stop barcode scanning
BarcodeScanner.stopScan = function() {
    this.isScanning = false;
    this.activeInput = null;
    this.scanBuffer = '';
    
    if (this.scanTimeoutId) {
        clearTimeout(this.scanTimeoutId);
        this.scanTimeoutId = null;
    }
    
    this.hideScanningModal();
};

// Handle keyboard input for scanning
BarcodeScanner.handleKeyDown = function(e) {
    if (!this.isScanning) return;
    
    // Handle Enter key (end of barcode)
    if (e.key === 'Enter') {
        e.preventDefault();
        this.processScan();
        return;
    }
    
    // Handle Escape key (cancel scan)
    if (e.key === 'Escape') {
        e.preventDefault();
        this.stopScan();
        return;
    }
    
    // Accumulate barcode characters
    if (e.key.length === 1) {
        this.scanBuffer += e.key;
        this.updateScanDisplay();
    }
};

// Handle key up events
BarcodeScanner.handleKeyUp = function(e) {
    if (!this.isScanning) return;
    
    // Reset buffer if too much time has passed (indicates manual typing)
    const now = Date.now();
    if (now - this.lastKeyTime > 100) {
        this.scanBuffer = '';
    }
    this.lastKeyTime = now;
};

// Process scanned barcode
BarcodeScanner.processScan = function() {
    const barcode = this.scanBuffer.trim();
    
    if (!this.validateBarcode(barcode)) {
        WMS.showToast('Invalid barcode format', 'error');
        this.stopScan();
        return;
    }
    
    // Add to scan history
    this.scanHistory.push({
        barcode: barcode,
        timestamp: new Date(),
        target: this.activeInput
    });
    
    // Process based on target type
    if (this.activeInput) {
        this.processTargetScan(barcode);
    } else {
        this.processGenericScan(barcode);
    }
    
    this.stopScan();
};

// Validate barcode format
BarcodeScanner.validateBarcode = function(barcode) {
    if (!barcode || barcode.length < this.settings.minBarcodeLength) {
        return false;
    }
    
    if (barcode.length > this.settings.maxBarcodeLength) {
        return false;
    }
    
    if (!this.settings.allowedChars.test(barcode)) {
        return false;
    }
    
    return true;
};

// Process scan for specific target
BarcodeScanner.processTargetScan = function(barcode) {
    const targetElement = document.getElementById(this.activeInput);
    
    if (targetElement) {
        targetElement.value = barcode;
        targetElement.dispatchEvent(new Event('change'));
        
        // Auto-submit form if configured
        if (targetElement.hasAttribute('data-auto-submit')) {
            const form = targetElement.closest('form');
            if (form) {
                form.dispatchEvent(new Event('submit'));
            }
        }
        
        WMS.showToast('Barcode scanned successfully', 'success');
    }
};

// Process generic scan
BarcodeScanner.processGenericScan = function(barcode) {
    // Determine barcode type and process accordingly
    if (this.isPONumber(barcode)) {
        this.processPOScan(barcode);
    } else if (this.isItemCode(barcode)) {
        this.processItemScan(barcode);
    } else if (this.isSupplierBarcode(barcode)) {
        this.processSupplierBarcodeScan(barcode);
    } else {
        WMS.showToast('Barcode type not recognized', 'warning');
    }
};

// Check if barcode is a PO number
BarcodeScanner.isPONumber = function(barcode) {
    return barcode.startsWith('PO-') || barcode.startsWith('PO');
};

// Check if barcode is an item code
BarcodeScanner.isItemCode = function(barcode) {
    return barcode.startsWith('ITEM') || barcode.startsWith('ITM');
};

// Check if barcode is a supplier barcode
BarcodeScanner.isSupplierBarcode = function(barcode) {
    return barcode.startsWith('SUP-') || barcode.startsWith('S-');
};

// Process PO scan
BarcodeScanner.processPOScan = function(barcode) {
    API.post('/api/scan_po', { po_number: barcode })
        .then(response => {
            if (response.error) {
                WMS.showToast(response.error, 'error');
            } else {
                this.displayPOInfo(response);
                WMS.showToast('PO information loaded', 'success');
            }
        })
        .catch(error => {
            WMS.showToast('Failed to load PO information', 'error');
        });
};

// Process item scan
BarcodeScanner.processItemScan = function(barcode) {
    API.post('/api/scan_item', { item_code: barcode })
        .then(response => {
            if (response.error) {
                WMS.showToast(response.error, 'error');
            } else {
                this.displayItemInfo(response);
                WMS.showToast('Item information loaded', 'success');
            }
        })
        .catch(error => {
            WMS.showToast('Failed to load item information', 'error');
        });
};

// Process supplier barcode scan
BarcodeScanner.processSupplierBarcodeScan = function(barcode) {
    API.post('/api/scan_barcode', { barcode: barcode })
        .then(response => {
            if (response.error) {
                WMS.showToast(response.error, 'error');
            } else {
                this.displaySupplierInfo(response);
                WMS.showToast('Supplier barcode processed', 'success');
            }
        })
        .catch(error => {
            WMS.showToast('Failed to process supplier barcode', 'error');
        });
};

// Display PO information
BarcodeScanner.displayPOInfo = function(poData) {
    const infoContainer = document.getElementById('poInfo') || document.getElementById('barcodeInfo');
    if (!infoContainer) return;
    
    const html = `
        <div class="alert alert-success">
            <h6>PO Information</h6>
            <p><strong>PO Number:</strong> ${poData.po_number}</p>
            <p><strong>Supplier:</strong> ${poData.supplier_name}</p>
            <p><strong>Date:</strong> ${poData.po_date}</p>
            <p><strong>Lines:</strong> ${poData.lines.length}</p>
        </div>
    `;
    
    infoContainer.innerHTML = html;
};

// Display item information
BarcodeScanner.displayItemInfo = function(itemData) {
    const infoContainer = document.getElementById('itemInfo') || document.getElementById('barcodeInfo');
    if (!infoContainer) return;
    
    const html = `
        <div class="alert alert-info">
            <h6>Item Information</h6>
            <p><strong>Item Code:</strong> ${itemData.item_code}</p>
            <p><strong>Description:</strong> ${itemData.description}</p>
            <p><strong>Unit Price:</strong> ${Utils.formatCurrency(itemData.unit_price)}</p>
            <p><strong>Stock Level:</strong> ${itemData.stock_level}</p>
        </div>
    `;
    
    infoContainer.innerHTML = html;
};

// Display supplier information
BarcodeScanner.displaySupplierInfo = function(supplierData) {
    const infoContainer = document.getElementById('supplierInfo') || document.getElementById('barcodeInfo');
    if (!infoContainer) return;
    
    const html = `
        <div class="alert alert-warning">
            <h6>Supplier Barcode Information</h6>
            <p><strong>Item Code:</strong> ${supplierData.item_code}</p>
            <p><strong>Batch Number:</strong> ${supplierData.batch_number}</p>
            <p><strong>Expiry Date:</strong> ${supplierData.expiry_date}</p>
            <p><strong>Supplier Code:</strong> ${supplierData.supplier_barcode}</p>
        </div>
    `;
    
    infoContainer.innerHTML = html;
    
    // Auto-fill form fields if available
    this.autoFillSupplierData(supplierData);
};

// Auto-fill supplier data into form fields
BarcodeScanner.autoFillSupplierData = function(data) {
    const fields = {
        'batch_number': data.batch_number,
        'expiry_date': data.expiry_date,
        'supplier_barcode': data.supplier_barcode,
        'item_code': data.item_code
    };
    
    Object.keys(fields).forEach(fieldName => {
        const field = document.getElementById(fieldName);
        if (field && fields[fieldName]) {
            field.value = fields[fieldName];
            field.dispatchEvent(new Event('change'));
        }
    });
};

// Show scanning modal
BarcodeScanner.showScanningModal = function() {
    const modalHtml = `
        <div class="modal fade" id="scanningModal" tabindex="-1" data-bs-backdrop="static" data-bs-keyboard="false">
            <div class="modal-dialog modal-dialog-centered">
                <div class="modal-content">
                    <div class="modal-header bg-primary text-white">
                        <h5 class="modal-title">
                            <i class="fas fa-barcode me-2"></i>Scanning Barcode
                        </h5>
                    </div>
                    <div class="modal-body text-center">
                        <div class="barcode-scanner active mb-3">
                            <div class="scanner-line"></div>
                            <i class="fas fa-barcode fa-3x text-primary"></i>
                        </div>
                        <h6>Point the barcode scanner at the barcode</h6>
                        <p class="text-muted">Or use the keyboard to enter the barcode manually</p>
                        <div class="scan-display">
                            <input type="text" class="form-control text-center" id="scanDisplay" 
                                   placeholder="Scanned code will appear here" readonly>
                        </div>
                    </div>
                    <div class="modal-footer">
                        <button type="button" class="btn btn-secondary" onclick="BarcodeScanner.stopScan()">
                            <i class="fas fa-times me-2"></i>Cancel
                        </button>
                        <button type="button" class="btn btn-primary" onclick="BarcodeScanner.processScan()">
                            <i class="fas fa-check me-2"></i>Process
                        </button>
                    </div>
                </div>
            </div>
        </div>
    `;
    
    // Remove existing modal if present
    const existingModal = document.getElementById('scanningModal');
    if (existingModal) {
        existingModal.remove();
    }
    
    // Add new modal
    document.body.insertAdjacentHTML('beforeend', modalHtml);
    
    // Show modal
    const modal = new bootstrap.Modal(document.getElementById('scanningModal'));
    modal.show();
    
    // Focus on scan display
    document.getElementById('scanDisplay').focus();
};

// Hide scanning modal
BarcodeScanner.hideScanningModal = function() {
    const modal = bootstrap.Modal.getInstance(document.getElementById('scanningModal'));
    if (modal) {
        modal.hide();
    }
};

// Update scan display
BarcodeScanner.updateScanDisplay = function() {
    const scanDisplay = document.getElementById('scanDisplay');
    if (scanDisplay) {
        scanDisplay.value = this.scanBuffer;
    }
};

// Manual barcode entry
BarcodeScanner.enterManualBarcode = function() {
    const barcode = prompt('Enter barcode manually:');
    if (barcode) {
        this.scanBuffer = barcode;
        this.processScan();
    }
};

// Get scan history
BarcodeScanner.getScanHistory = function() {
    return this.scanHistory;
};

// Clear scan history
BarcodeScanner.clearScanHistory = function() {
    this.scanHistory = [];
};

// Export scan history
BarcodeScanner.exportScanHistory = function() {
    const data = this.scanHistory.map(scan => ({
        barcode: scan.barcode,
        timestamp: scan.timestamp.toISOString(),
        target: scan.target
    }));
    
    const json = JSON.stringify(data, null, 2);
    const blob = new Blob([json], { type: 'application/json' });
    const url = URL.createObjectURL(blob);
    
    const a = document.createElement('a');
    a.href = url;
    a.download = `scan_history_${new Date().toISOString().split('T')[0]}.json`;
    a.click();
    
    URL.revokeObjectURL(url);
};

// QR Code generation helpers
const QRCodeGenerator = {
    generate: function(data, size = 200) {
        // In a real implementation, this would use a QR code library
        // For now, we'll return a placeholder
        return this.createPlaceholder(size);
    },
    
    createPlaceholder: function(size) {
        const canvas = document.createElement('canvas');
        canvas.width = size;
        canvas.height = size;
        const ctx = canvas.getContext('2d');
        
        // Draw QR code placeholder
        ctx.fillStyle = '#000';
        ctx.fillRect(0, 0, size, size);
        
        ctx.fillStyle = '#fff';
        for (let i = 0; i < size; i += 10) {
            for (let j = 0; j < size; j += 10) {
                if (Math.random() > 0.5) {
                    ctx.fillRect(i, j, 8, 8);
                }
            }
        }
        
        return canvas.toDataURL();
    }
};

// Global functions for easy access
window.startBarcodeScan = function(targetInput) {
    BarcodeScanner.startScan(targetInput);
};

window.processBarcodeManually = function() {
    BarcodeScanner.enterManualBarcode();
};

// Initialize on page load
document.addEventListener('DOMContentLoaded', function() {
    BarcodeScanner.init();
});

// Export for global use
window.BarcodeScanner = BarcodeScanner;
window.QRCodeGenerator = QRCodeGenerator;
