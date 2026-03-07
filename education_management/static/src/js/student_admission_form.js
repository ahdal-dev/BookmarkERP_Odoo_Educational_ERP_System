/** @odoo-module **/

import { registry } from "@web/core/registry";
import { formView } from "@web/views/form/form_view";
import { FormController } from "@web/views/form/form_controller";
import { useService } from "@web/core/utils/hooks";

export class StudentAdmissionFormController extends FormController {
    setup() {
        super.setup();
        this.rpc = useService("rpc");
        this.notification = useService("notification");
    }

    async onIDDocumentUpload(ev) {
        const file = ev.target.files[0];
        if (!file) return;

        // Validate file type
        const validTypes = ['image/jpeg', 'image/jpg', 'image/png'];
        if (!validTypes.includes(file.type)) {
            this.notification.add('Please upload a valid image file (JPG or PNG)', {
                type: 'warning'
            });
            return;
        }

        // Show loading notification
        this.notification.add('Processing ID document...', {
            type: 'info'
        });

        // Read file as base64
        const reader = new FileReader();
        reader.onload = async (e) => {
            try {
                const imageData = e.target.result;

                // Call OCR service
                const result = await this.rpc('/education/ocr/process', {
                    image_data: imageData
                });

                if (result.success) {
                    // Auto-fill form fields
                    const data = result.data;
                    
                    if (data.national_id) {
                        this.model.root.update({ national_id: data.national_id });
                    }
                    if (data.name) {
                        this.model.root.update({ name: data.name });
                    }
                    if (data.address) {
                        this.model.root.update({ address: data.address });
                    }

                    this.notification.add('ID document processed successfully! Fields have been auto-filled.', {
                        type: 'success'
                    });
                } else {
                    this.notification.add(result.error || 'Failed to process ID document', {
                        type: 'danger'
                    });
                }
            } catch (error) {
                console.error('OCR Error:', error);
                this.notification.add('Error processing ID document: ' + error.message, {
                    type: 'danger'
                });
            }
        };
        reader.readAsDataURL(file);
    }
}

registry.category("views").add("student_admission_form", {
    ...formView,
    Controller: StudentAdmissionFormController,
});
