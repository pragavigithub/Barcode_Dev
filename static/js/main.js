// Main JavaScript file for WMS Application
// Common functionality and utilities

// Global variables
const WMS = {
    baseUrl: window.location.origin,
    version: '1.0.0',
    debug: true,
    currentUser: null,
    settings: {
        autoRefreshInterval: 30000, // 30 seconds
        timeoutDelay: 5000, // 5 seconds
        maxRetries: 3
    }
};

// Utility functions
const Utils = {
    // Format currency
    formatCurrency: function(amount, currency = 'USD') {
        return new Intl.NumberFormat('en-US', {
            style: 'currency',
            currency: currency
        }).format(amount);
    },

    // Format date
    formatDate: function(date, format = 'short') {
        if (!date) return 'N/A';
        const dateObj = new Date(date);
        return dateObj.toLocaleDateString('en-US', {
            year: 'numeric',
            month: format === 'long' ? 'long' : 'short',
            day: 'numeric'
        });
    },

    // Format date and time
    formatDateTime: function(datetime) {
        if (!datetime) return 'N/A';
        const dateObj = new Date(datetime);
        return dateObj.toLocaleString('en-US', {
            year: 'numeric',
            month: 'short',
            day: 'numeric',
            hour: '2-digit',
            minute: '2-digit'
        });
    },

    // Debounce function
    debounce: function(func, wait) {
        let timeout;
        return function executedFunction(...args) {
            const later = () => {
                clearTimeout(timeout);
                func(...args);
            };
            clearTimeout(timeout);
            timeout = setTimeout(later, wait);
        };
    },

    // Show loading state
    showLoading: function(element, message = 'Loading...') {
        const loadingHtml = `
            <div class="d-flex justify-content-center align-items-center p-3">
                <div class="spinner-border text-primary me-2" role="status">
                    <span class="visually-hidden">Loading...</span>
                </div>
                <span>${message}</span>
            </div>
        `;
        element.innerHTML = loadingHtml;
    },

    // Hide loading state
    hideLoading: function(element) {
        element.innerHTML = '';
    },

    // Show error message
    showError: function(element, message = 'An error occurred') {
        const errorHtml = `
            <div class="alert alert-danger" role="alert">
                <i class="fas fa-exclamation-triangle me-2"></i>
                ${message}
            </div>
        `;
        element.innerHTML = errorHtml;
    },

    // Show success message
    showSuccess: function(element, message = 'Success') {
        const successHtml = `
            <div class="alert alert-success" role="alert">
                <i class="fas fa-check-circle me-2"></i>
                ${message}
            </div>
        `;
        element.innerHTML = successHtml;
    },

    // Generate random ID
    generateId: function() {
        return 'id_' + Math.random().toString(36).substr(2, 9);
    },

    // Copy to clipboard
    copyToClipboard: function(text) {
        navigator.clipboard.writeText(text).then(function() {
            WMS.showToast('Copied to clipboard', 'success');
        }, function() {
            WMS.showToast('Failed to copy', 'error');
        });
    },

    // Validate form
    validateForm: function(formElement) {
        const inputs = formElement.querySelectorAll('input[required], select[required], textarea[required]');
        let isValid = true;
        
        inputs.forEach(input => {
            if (!input.value.trim()) {
                isValid = false;
                input.classList.add('is-invalid');
            } else {
                input.classList.remove('is-invalid');
            }
        });
        
        return isValid;
    }
};

// API Helper
const API = {
    // Generic GET request
    get: async function(url, options = {}) {
        try {
            const response = await fetch(url, {
                method: 'GET',
                headers: {
                    'Content-Type': 'application/json',
                    ...options.headers
                },
                ...options
            });
            
            if (!response.ok) {
                throw new Error(`HTTP error! status: ${response.status}`);
            }
            
            return await response.json();
        } catch (error) {
            console.error('API GET error:', error);
            throw error;
        }
    },

    // Generic POST request
    post: async function(url, data, options = {}) {
        try {
            const response = await fetch(url, {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json',
                    ...options.headers
                },
                body: JSON.stringify(data),
                ...options
            });
            
            if (!response.ok) {
                throw new Error(`HTTP error! status: ${response.status}`);
            }
            
            return await response.json();
        } catch (error) {
            console.error('API POST error:', error);
            throw error;
        }
    },

    // Generic PUT request
    put: async function(url, data, options = {}) {
        try {
            const response = await fetch(url, {
                method: 'PUT',
                headers: {
                    'Content-Type': 'application/json',
                    ...options.headers
                },
                body: JSON.stringify(data),
                ...options
            });
            
            if (!response.ok) {
                throw new Error(`HTTP error! status: ${response.status}`);
            }
            
            return await response.json();
        } catch (error) {
            console.error('API PUT error:', error);
            throw error;
        }
    },

    // Generic DELETE request
    delete: async function(url, options = {}) {
        try {
            const response = await fetch(url, {
                method: 'DELETE',
                headers: {
                    'Content-Type': 'application/json',
                    ...options.headers
                },
                ...options
            });
            
            if (!response.ok) {
                throw new Error(`HTTP error! status: ${response.status}`);
            }
            
            return await response.json();
        } catch (error) {
            console.error('API DELETE error:', error);
            throw error;
        }
    }
};

// Toast notifications
WMS.showToast = function(message, type = 'info', duration = 3000) {
    const toastContainer = document.getElementById('toastContainer') || createToastContainer();
    
    const toastId = Utils.generateId();
    const toastHtml = `
        <div class="toast" id="${toastId}" role="alert" aria-live="assertive" aria-atomic="true">
            <div class="toast-header">
                <i class="fas fa-${getToastIcon(type)} text-${type} me-2"></i>
                <strong class="me-auto">WMS</strong>
                <button type="button" class="btn-close" data-bs-dismiss="toast" aria-label="Close"></button>
            </div>
            <div class="toast-body">
                ${message}
            </div>
        </div>
    `;
    
    toastContainer.insertAdjacentHTML('beforeend', toastHtml);
    
    const toastElement = document.getElementById(toastId);
    const toast = new bootstrap.Toast(toastElement, { delay: duration });
    toast.show();
    
    // Remove toast element after it's hidden
    toastElement.addEventListener('hidden.bs.toast', function() {
        toastElement.remove();
    });
    
    function createToastContainer() {
        const container = document.createElement('div');
        container.id = 'toastContainer';
        container.className = 'toast-container position-fixed top-0 end-0 p-3';
        container.style.zIndex = '1070';
        document.body.appendChild(container);
        return container;
    }
    
    function getToastIcon(type) {
        const icons = {
            'success': 'check-circle',
            'error': 'exclamation-triangle',
            'warning': 'exclamation-triangle',
            'info': 'info-circle'
        };
        return icons[type] || 'info-circle';
    }
};

// Form handling
WMS.handleForm = function(formElement, options = {}) {
    formElement.addEventListener('submit', async function(e) {
        e.preventDefault();
        
        if (!Utils.validateForm(formElement)) {
            WMS.showToast('Please fill in all required fields', 'error');
            return;
        }
        
        const formData = new FormData(formElement);
        const data = Object.fromEntries(formData);
        
        const submitButton = formElement.querySelector('button[type="submit"]');
        const originalText = submitButton.textContent;
        
        try {
            submitButton.disabled = true;
            submitButton.innerHTML = '<span class="spinner-border spinner-border-sm me-2" role="status"></span>Processing...';
            
            const response = await API.post(formElement.action || window.location.pathname, data);
            
            if (options.onSuccess) {
                options.onSuccess(response);
            } else {
                WMS.showToast('Operation completed successfully', 'success');
                if (options.redirect) {
                    window.location.href = options.redirect;
                }
            }
        } catch (error) {
            if (options.onError) {
                options.onError(error);
            } else {
                WMS.showToast('An error occurred. Please try again.', 'error');
            }
        } finally {
            submitButton.disabled = false;
            submitButton.textContent = originalText;
        }
    });
};

// Data table enhancements
WMS.enhanceTable = function(tableElement, options = {}) {
    // Add sorting functionality
    const headers = tableElement.querySelectorAll('th[data-sort]');
    headers.forEach(header => {
        header.style.cursor = 'pointer';
        header.addEventListener('click', function() {
            const column = this.dataset.sort;
            const currentOrder = this.dataset.order || 'asc';
            const newOrder = currentOrder === 'asc' ? 'desc' : 'asc';
            
            // Update header
            headers.forEach(h => h.classList.remove('sorted-asc', 'sorted-desc'));
            this.classList.add(`sorted-${newOrder}`);
            this.dataset.order = newOrder;
            
            // Sort table
            sortTable(tableElement, column, newOrder);
        });
    });
    
    // Add search functionality
    if (options.searchable) {
        const searchInput = document.getElementById(options.searchInput);
        if (searchInput) {
            searchInput.addEventListener('input', Utils.debounce(function() {
                filterTable(tableElement, this.value);
            }, 300));
        }
    }
    
    function sortTable(table, column, order) {
        const tbody = table.querySelector('tbody');
        const rows = Array.from(tbody.querySelectorAll('tr'));
        
        rows.sort((a, b) => {
            const aValue = a.querySelector(`td[data-${column}]`)?.textContent || '';
            const bValue = b.querySelector(`td[data-${column}]`)?.textContent || '';
            
            if (order === 'asc') {
                return aValue.localeCompare(bValue);
            } else {
                return bValue.localeCompare(aValue);
            }
        });
        
        rows.forEach(row => tbody.appendChild(row));
    }
    
    function filterTable(table, searchTerm) {
        const tbody = table.querySelector('tbody');
        const rows = tbody.querySelectorAll('tr');
        
        rows.forEach(row => {
            const text = row.textContent.toLowerCase();
            const matches = text.includes(searchTerm.toLowerCase());
            row.style.display = matches ? '' : 'none';
        });
    }
};

// Auto-refresh functionality
WMS.startAutoRefresh = function(callback, interval = WMS.settings.autoRefreshInterval) {
    return setInterval(callback, interval);
};

WMS.stopAutoRefresh = function(intervalId) {
    clearInterval(intervalId);
};

// Session management
WMS.checkSession = function() {
    const lastActivity = localStorage.getItem('lastActivity');
    const now = Date.now();
    const sessionTimeout = 30 * 60 * 1000; // 30 minutes
    
    if (lastActivity && (now - lastActivity) > sessionTimeout) {
        WMS.showToast('Session expired. Please log in again.', 'warning');
        window.location.href = '/login';
    }
};

WMS.updateLastActivity = function() {
    localStorage.setItem('lastActivity', Date.now());
};

// Print functionality
WMS.printElement = function(element, options = {}) {
    const printWindow = window.open('', '_blank');
    const printContent = element.innerHTML;
    
    printWindow.document.write(`
        <!DOCTYPE html>
        <html>
        <head>
            <title>${options.title || 'WMS Print'}</title>
            <link href="https://cdn.replit.com/agent/bootstrap-agent-dark-theme.min.css" rel="stylesheet">
            <link href="${WMS.baseUrl}/static/css/style.css" rel="stylesheet">
            <style>
                body { background: white; color: black; }
                .card { border: 1px solid #000; }
                .table th, .table td { border: 1px solid #000; }
                @media print {
                    .no-print { display: none !important; }
                }
            </style>
        </head>
        <body>
            ${printContent}
        </body>
        </html>
    `);
    
    printWindow.document.close();
    printWindow.focus();
    
    setTimeout(() => {
        printWindow.print();
        printWindow.close();
    }, 500);
};

// Initialize application
document.addEventListener('DOMContentLoaded', function() {
    // Initialize tooltips
    const tooltipTriggerList = [].slice.call(document.querySelectorAll('[data-bs-toggle="tooltip"]'));
    tooltipTriggerList.map(function(tooltipTriggerEl) {
        return new bootstrap.Tooltip(tooltipTriggerEl);
    });
    
    // Initialize popovers
    const popoverTriggerList = [].slice.call(document.querySelectorAll('[data-bs-toggle="popover"]'));
    popoverTriggerList.map(function(popoverTriggerEl) {
        return new bootstrap.Popover(popoverTriggerEl);
    });
    
    // Track user activity
    document.addEventListener('click', WMS.updateLastActivity);
    document.addEventListener('keypress', WMS.updateLastActivity);
    
    // Check session periodically
    setInterval(WMS.checkSession, 5000);
    
    // Auto-focus first input in modals
    document.addEventListener('shown.bs.modal', function(event) {
        const firstInput = event.target.querySelector('input:not([type="hidden"]), select, textarea');
        if (firstInput) {
            firstInput.focus();
        }
    });
    
    // Enhanced form submission
    const forms = document.querySelectorAll('form[data-enhanced]');
    forms.forEach(form => {
        WMS.handleForm(form, {
            onSuccess: function(response) {
                WMS.showToast('Form submitted successfully', 'success');
            },
            onError: function(error) {
                WMS.showToast('Form submission failed', 'error');
            }
        });
    });
    
    // Enhanced tables
    const tables = document.querySelectorAll('table[data-enhanced]');
    tables.forEach(table => {
        WMS.enhanceTable(table, {
            searchable: true,
            searchInput: 'tableSearch'
        });
    });
    
    // Add loading states to buttons
    const buttons = document.querySelectorAll('button[data-loading]');
    buttons.forEach(button => {
        button.addEventListener('click', function() {
            if (this.type !== 'submit') {
                const originalText = this.textContent;
                this.disabled = true;
                this.innerHTML = '<span class="spinner-border spinner-border-sm me-2" role="status"></span>Loading...';
                
                setTimeout(() => {
                    this.disabled = false;
                    this.textContent = originalText;
                }, 2000);
            }
        });
    });
    
    console.log('WMS Application initialized successfully');
});

// Export for global use
window.WMS = WMS;
window.Utils = Utils;
window.API = API;
