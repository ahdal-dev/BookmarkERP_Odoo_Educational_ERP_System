/** @odoo-module **/

odoo.define('education_management.student_ocr', function (require) {
    'use strict';

    var AbstractField = require('web.AbstractField');
    var fieldRegistry = require('web.field_registry');
    var core = require('web.core');
    var _t = core._t;

    var IDDocumentOCRField = AbstractField.extend({
        template: 'EducationManagement.IDDocumentOCR',
        events: {
            'change input[type="file"]': '_onFileChange',
        },

        _onFileChange: function (ev) {
            var self = this;
            var file = ev.target.files[0];
            
            if (!file) return;

            // Validate file type
            var validTypes = ['image/jpeg', 'image/jpg', 'image/png', 'image/bmp'];
            if (!validTypes.includes(file.type)) {
                this.displayNotification({
                    message: _t('Please upload a valid image file (JPG, PNG, or BMP)'),
                    type: 'warning'
                });
                return;
            }

            // Show loading indicator
            this.$el.find('.ocr-loading').show();
            this.displayNotification({
                message: _t('Processing ID document...'),
                type: 'info'
            });

            // Read file as base64
            var reader = new FileReader();
            reader.onload = function (e) {
                var imageData = e.target.result;

                // Call OCR service
                self._rpc({
                    route: '/education/ocr/process',
                    params: {
                        image_data: imageData
                    }
                }).then(function (result) {
                    self.$el.find('.ocr-loading').hide();
                    
                    if (result.success) {
                        // Auto-fill form fields
                        var data = result.data;
                        
                        // Update fields
                        if (data.national_id) {
                            self._setValue(data.national_id, 'national_id');
                            self.trigger_up('field_changed', {
                                dataPointID: self.dataPointID,
                                changes: { national_id: data.national_id }
                            });
                        }
                        if (data.name) {
                            self.trigger_up('field_changed', {
                                dataPointID: self.dataPointID,
                                changes: { name: data.name }
                            });
                        }
                        if (data.address) {
                            self.trigger_up('field_changed', {
                                dataPointID: self.dataPointID,
                                changes: { address: data.address }
                            });
                        }

                        self.displayNotification({
                            message: _t('ID document processed successfully! Fields have been auto-filled.'),
                            type: 'success'
                        });
                    } else {
                        self.displayNotification({
                            message: result.error || _t('Failed to process ID document'),
                            type: 'danger'
                        });
                    }
                }).catch(function (error) {
                    self.$el.find('.ocr-loading').hide();
                    console.error('OCR Error:', error);
                    self.displayNotification({
                        message: _t('Error processing ID document: ') + error.message,
                        type: 'danger'
                    });
                });
            };
            reader.readAsDataURL(file);
        },
    });

    fieldRegistry.add('id_document_ocr', IDDocumentOCRField);

    return IDDocumentOCRField;
});
