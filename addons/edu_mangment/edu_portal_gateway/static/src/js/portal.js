/**
 * Educational Portal Gateway - JavaScript
 * ========================================
 * Client-side interactions for the Zewail City Educational ERP Portal
 */

(function () {
    'use strict';

    // Wait for DOM to be ready
    document.addEventListener('DOMContentLoaded', function () {
        initSidebar();
        initAlerts();
        initFileUpload();
        initFormValidation();
        initSearchFilters();
        initTooltips();
        initConfirmDialogs();
        initCartActions();
        initDynamicForms();
    });

    /**
     * Sidebar Toggle for Mobile
     */
    function initSidebar() {
        const sidebar = document.querySelector('.edu-portal-sidebar');
        const toggle = document.querySelector('.sidebar-toggle');
        const main = document.querySelector('.edu-portal-main');

        if (!sidebar || !toggle) return;

        toggle.addEventListener('click', function (e) {
            e.preventDefault();
            sidebar.classList.toggle('open');
        });

        // Close sidebar when clicking outside on mobile
        if (main) {
            main.addEventListener('click', function () {
                if (window.innerWidth <= 768 && sidebar.classList.contains('open')) {
                    sidebar.classList.remove('open');
                }
            });
        }

        // Handle window resize
        window.addEventListener('resize', function () {
            if (window.innerWidth > 768) {
                sidebar.classList.remove('open');
            }
        });
    }

    /**
     * Auto-dismiss alerts
     */
    function initAlerts() {
        const alerts = document.querySelectorAll('.alert');

        alerts.forEach(function (alert) {
            // Add close button functionality
            const closeBtn = alert.querySelector('.alert-close');
            if (closeBtn) {
                closeBtn.addEventListener('click', function () {
                    dismissAlert(alert);
                });
            }

            // Auto-dismiss after 5 seconds for success alerts
            if (alert.classList.contains('alert-success')) {
                setTimeout(function () {
                    dismissAlert(alert);
                }, 5000);
            }
        });
    }

    function dismissAlert(alert) {
        alert.style.opacity = '0';
        alert.style.transform = 'translateY(-10px)';
        alert.style.transition = 'opacity 0.3s, transform 0.3s';
        setTimeout(function () {
            alert.remove();
        }, 300);
    }

    /**
     * File Upload with Preview
     */
    function initFileUpload() {
        const uploadZones = document.querySelectorAll('.file-upload-zone');

        uploadZones.forEach(function (zone) {
            const input = zone.querySelector('.file-input');
            const browseBtn = zone.querySelector('.btn-secondary');
            const fileList = zone.querySelector('.file-list') || createFileList(zone);

            if (!input) return;

            // Click to browse
            if (browseBtn) {
                browseBtn.addEventListener('click', function (e) {
                    e.preventDefault();
                    input.click();
                });
            }

            // Also allow clicking the zone
            zone.addEventListener('click', function (e) {
                if (e.target === zone || e.target.classList.contains('upload-text') ||
                    e.target.classList.contains('upload-hint') || e.target.classList.contains('upload-icon')) {
                    input.click();
                }
            });

            // Drag and drop
            zone.addEventListener('dragover', function (e) {
                e.preventDefault();
                zone.classList.add('dragover');
            });

            zone.addEventListener('dragleave', function () {
                zone.classList.remove('dragover');
            });

            zone.addEventListener('drop', function (e) {
                e.preventDefault();
                zone.classList.remove('dragover');
                const files = e.dataTransfer.files;
                handleFiles(files, input, fileList);
            });

            // File input change
            input.addEventListener('change', function () {
                handleFiles(this.files, input, fileList);
            });
        });
    }

    function createFileList(zone) {
        const list = document.createElement('div');
        list.className = 'file-list';
        zone.appendChild(list);
        return list;
    }

    function handleFiles(files, input, fileList) {
        fileList.innerHTML = '';

        Array.from(files).forEach(function (file) {
            // Validate file size (10MB max)
            if (file.size > 10 * 1024 * 1024) {
                showNotification('File "' + file.name + '" is too large. Maximum size is 10MB.', 'error');
                return;
            }

            // Validate file type
            const allowedTypes = ['application/pdf', 'image/jpeg', 'image/png', 'image/gif'];
            if (!allowedTypes.includes(file.type)) {
                showNotification('File "' + file.name + '" is not an allowed type. Please upload PDF or image files.', 'error');
                return;
            }

            const item = document.createElement('div');
            item.className = 'attachment-item';

            const icon = document.createElement('span');
            icon.className = 'attachment-icon';
            icon.textContent = file.type.includes('pdf') ? '📄' : '🖼️';

            const name = document.createElement('span');
            name.className = 'attachment-name';
            name.textContent = file.name;

            const size = document.createElement('span');
            size.className = 'attachment-size';
            size.textContent = formatFileSize(file.size);
            size.style.color = 'var(--text-muted)';
            size.style.fontSize = '13px';

            const remove = document.createElement('button');
            remove.type = 'button';
            remove.className = 'btn btn-sm btn-link';
            remove.textContent = '×';
            remove.style.fontSize = '20px';
            remove.addEventListener('click', function () {
                item.remove();
                // Reset input if all files removed
                if (fileList.children.length === 0) {
                    input.value = '';
                }
            });

            item.appendChild(icon);
            item.appendChild(name);
            item.appendChild(size);
            item.appendChild(remove);
            fileList.appendChild(item);
        });
    }

    function formatFileSize(bytes) {
        if (bytes < 1024) return bytes + ' B';
        if (bytes < 1024 * 1024) return (bytes / 1024).toFixed(1) + ' KB';
        return (bytes / (1024 * 1024)).toFixed(1) + ' MB';
    }

    /**
     * Form Validation
     */
    function initFormValidation() {
        const forms = document.querySelectorAll('form[data-validate]');

        forms.forEach(function (form) {
            form.addEventListener('submit', function (e) {
                let valid = true;
                const required = form.querySelectorAll('[required]');

                required.forEach(function (field) {
                    clearFieldError(field);
                    if (!field.value.trim()) {
                        showFieldError(field, 'This field is required');
                        valid = false;
                    }
                });

                // Email validation
                const emailFields = form.querySelectorAll('input[type="email"]');
                emailFields.forEach(function (field) {
                    if (field.value && !isValidEmail(field.value)) {
                        showFieldError(field, 'Please enter a valid email address');
                        valid = false;
                    }
                });

                if (!valid) {
                    e.preventDefault();
                    showNotification('Please fill in all required fields correctly.', 'error');
                }
            });
        });
    }

    function showFieldError(field, message) {
        field.classList.add('error');
        field.style.borderColor = 'var(--danger-color)';

        let error = field.parentNode.querySelector('.field-error');
        if (!error) {
            error = document.createElement('span');
            error.className = 'field-error';
            error.style.color = 'var(--danger-color)';
            error.style.fontSize = '12px';
            error.style.marginTop = '4px';
            error.style.display = 'block';
            field.parentNode.appendChild(error);
        }
        error.textContent = message;
    }

    function clearFieldError(field) {
        field.classList.remove('error');
        field.style.borderColor = '';
        const error = field.parentNode.querySelector('.field-error');
        if (error) error.remove();
    }

    function isValidEmail(email) {
        return /^[^\s@]+@[^\s@]+\.[^\s@]+$/.test(email);
    }

    /**
     * Search and Filter Interactions
     */
    function initSearchFilters() {
        // Auto-submit on filter change
        const filterSelects = document.querySelectorAll('.filter-select[data-auto-submit]');
        filterSelects.forEach(function (select) {
            select.addEventListener('change', function () {
                this.closest('form').submit();
            });
        });

        // Debounced search
        const searchInputs = document.querySelectorAll('.search-input[data-auto-submit]');
        searchInputs.forEach(function (input) {
            let timeout;
            input.addEventListener('input', function () {
                clearTimeout(timeout);
                const form = this.closest('form');
                timeout = setTimeout(function () {
                    form.submit();
                }, 500);
            });
        });
    }

    /**
     * Tooltips
     */
    function initTooltips() {
        const tooltipTriggers = document.querySelectorAll('[data-tooltip]');

        tooltipTriggers.forEach(function (trigger) {
            trigger.addEventListener('mouseenter', function () {
                const text = this.getAttribute('data-tooltip');
                const tooltip = document.createElement('div');
                tooltip.className = 'tooltip';
                tooltip.textContent = text;
                tooltip.style.cssText = `
                    position: absolute;
                    background: var(--text-primary);
                    color: white;
                    padding: 6px 12px;
                    border-radius: 4px;
                    font-size: 12px;
                    z-index: 1000;
                    white-space: nowrap;
                `;

                document.body.appendChild(tooltip);

                const rect = this.getBoundingClientRect();
                tooltip.style.top = (rect.top - tooltip.offsetHeight - 8 + window.scrollY) + 'px';
                tooltip.style.left = (rect.left + (rect.width - tooltip.offsetWidth) / 2) + 'px';

                this._tooltip = tooltip;
            });

            trigger.addEventListener('mouseleave', function () {
                if (this._tooltip) {
                    this._tooltip.remove();
                    this._tooltip = null;
                }
            });
        });
    }

    /**
     * Confirmation Dialogs
     */
    function initConfirmDialogs() {
        const confirmBtns = document.querySelectorAll('[data-confirm]');

        confirmBtns.forEach(function (btn) {
            btn.addEventListener('click', function (e) {
                const message = this.getAttribute('data-confirm');
                if (!confirm(message)) {
                    e.preventDefault();
                }
            });
        });
    }

    /**
     * Cart Actions (Registration Module)
     */
    function initCartActions() {
        // Add to cart button
        const addToCartBtns = document.querySelectorAll('.add-to-cart-btn');

        addToCartBtns.forEach(function (btn) {
            btn.addEventListener('click', function (e) {
                e.preventDefault();
                const courseId = this.getAttribute('data-course-id');

                // Show loading state
                const originalText = this.textContent;
                this.textContent = 'Adding...';
                this.disabled = true;

                // Submit form or redirect
                const form = this.closest('form');
                if (form) {
                    form.submit();
                } else {
                    window.location.href = '/edu-portal/student/cart/add/' + courseId;
                }
            });
        });

        // Remove from cart button
        const removeFromCartBtns = document.querySelectorAll('.remove-from-cart-btn');

        removeFromCartBtns.forEach(function (btn) {
            btn.addEventListener('click', function (e) {
                if (!confirm('Remove this course from your cart?')) {
                    e.preventDefault();
                }
            });
        });

        // Checkout button
        const checkoutBtn = document.querySelector('.checkout-btn');
        if (checkoutBtn) {
            checkoutBtn.addEventListener('click', function (e) {
                const courseCount = document.querySelectorAll('.cart-item').length;
                if (courseCount === 0) {
                    e.preventDefault();
                    showNotification('Your cart is empty.', 'warning');
                    return;
                }

                if (!confirm('Register for ' + courseCount + ' course(s)? This action cannot be undone.')) {
                    e.preventDefault();
                }
            });
        }
    }

    /**
     * Dynamic Forms
     */
    function initDynamicForms() {
        // Toggle password visibility
        const passwordToggles = document.querySelectorAll('.password-toggle');
        passwordToggles.forEach(function (toggle) {
            toggle.addEventListener('click', function () {
                const input = this.parentNode.querySelector('input');
                if (input.type === 'password') {
                    input.type = 'text';
                    this.textContent = '🙈';
                } else {
                    input.type = 'password';
                    this.textContent = '👁️';
                }
            });
        });

        // Conditional field visibility
        const conditionalTriggers = document.querySelectorAll('[data-show-if]');
        conditionalTriggers.forEach(function (trigger) {
            const targetId = trigger.getAttribute('data-show-if');
            const targetValue = trigger.getAttribute('data-show-value');
            const targetField = document.getElementById(targetId);

            if (targetField) {
                function updateVisibility() {
                    const show = targetField.value === targetValue ||
                        (targetField.type === 'checkbox' && targetField.checked);
                    trigger.style.display = show ? '' : 'none';
                }

                targetField.addEventListener('change', updateVisibility);
                updateVisibility();
            }
        });

        // Character counter for textareas
        const textareas = document.querySelectorAll('textarea[maxlength]');
        textareas.forEach(function (textarea) {
            const maxLength = parseInt(textarea.getAttribute('maxlength'));
            const counter = document.createElement('span');
            counter.className = 'char-counter';
            counter.style.cssText = 'display: block; text-align: right; font-size: 12px; color: var(--text-muted); margin-top: 4px;';

            textarea.parentNode.appendChild(counter);

            function updateCounter() {
                const remaining = maxLength - textarea.value.length;
                counter.textContent = remaining + ' characters remaining';
                counter.style.color = remaining < 50 ? 'var(--warning-color)' : 'var(--text-muted)';
            }

            textarea.addEventListener('input', updateCounter);
            updateCounter();
        });
    }

    /**
     * Notification Helper
     */
    function showNotification(message, type) {
        type = type || 'info';

        const notification = document.createElement('div');
        notification.className = 'alert alert-' + type;
        notification.style.cssText = `
            position: fixed;
            top: 20px;
            right: 20px;
            z-index: 9999;
            min-width: 300px;
            max-width: 400px;
            animation: slideIn 0.3s ease;
        `;

        const icons = {
            success: '✓',
            error: '✕',
            warning: '⚠',
            info: 'ℹ'
        };

        notification.innerHTML = `
            <span class="alert-icon">${icons[type] || icons.info}</span>
            <span class="alert-text">${message}</span>
            <button type="button" class="alert-close">×</button>
        `;

        document.body.appendChild(notification);

        // Add animation styles if not already present
        if (!document.getElementById('notification-styles')) {
            const style = document.createElement('style');
            style.id = 'notification-styles';
            style.textContent = `
                @keyframes slideIn {
                    from {
                        opacity: 0;
                        transform: translateX(100%);
                    }
                    to {
                        opacity: 1;
                        transform: translateX(0);
                    }
                }
            `;
            document.head.appendChild(style);
        }

        // Close button
        notification.querySelector('.alert-close').addEventListener('click', function () {
            dismissAlert(notification);
        });

        // Auto dismiss after 5 seconds
        setTimeout(function () {
            dismissAlert(notification);
        }, 5000);
    }

    /**
     * Session Timeout Warning
     */
    function initSessionTimeout() {
        // Check session every minute
        setInterval(function () {
            fetch('/edu-portal/session-check', {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json',
                },
                credentials: 'same-origin'
            })
                .then(function (response) { return response.json(); })
                .then(function (data) {
                    if (data.expired) {
                        window.location.href = '/edu/login?session_expired=1';
                    } else if (data.warning) {
                        showNotification('Your session will expire in 5 minutes. Please save your work.', 'warning');
                    }
                })
                .catch(function () {
                    // Silent fail
                });
        }, 60000);
    }

    // Export functions for use in templates
    window.EduPortal = {
        showNotification: showNotification,
        formatFileSize: formatFileSize
    };

})();
