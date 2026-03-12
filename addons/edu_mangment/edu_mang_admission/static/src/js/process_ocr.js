document.addEventListener('DOMContentLoaded', function () {
    const processBtn = document.getElementById('process_ocr');
    if (processBtn) {
        processBtn.addEventListener('click', function (e) {
            e.preventDefault();
            const fileInput = document.getElementById('transcript_document');

            if (!fileInput.files || !fileInput.files.length) {
                alert('Please upload a document first');
                return;
            }

            const formData = new FormData();
            formData.append('file', fileInput.files[0]);

            // Show loading state
            const originalText = processBtn.innerHTML;
            processBtn.disabled = true;
            processBtn.innerHTML = '<i class="fa fa-spinner fa-spin me-2"></i>Processing...';

            fetch('http://localhost:5000/ocr', {
                method: 'POST',
                body: formData
            })
                .then(response => {
                    if (!response.ok) {
                        throw new Error('Network response was not ok');
                    }
                    return response.json();
                })
                .then(data => {
                    console.log('OCR Response:', data);
                    
                    if (data.error) {
                        alert('OCR Error: ' + data.error);
                        return;
                    }
                    
                    // Extract data from OCR result
                    const result = data.result || {};
                    
                    // Auto-fill National ID
                    if (result.nid || result.back_nid) {
                        const nationalIdField = document.getElementById('national_id');
                        if (nationalIdField) {
                            nationalIdField.value = result.nid || result.back_nid || '';
                            nationalIdField.classList.add('bg-success', 'bg-opacity-10');
                        }
                    }
                    
                    // Auto-fill Name
                    if (result.name) {
                        const nameField = document.getElementById('name');
                        if (nameField) {
                            nameField.value = result.name;
                            nameField.classList.add('bg-success', 'bg-opacity-10');
                        }
                    }
                    
                    // Auto-fill Address if field exists
                    if (result.address) {
                        const addressField = document.getElementById('address');
                        if (addressField) {
                            addressField.value = result.address;
                            addressField.classList.add('bg-success', 'bg-opacity-10');
                        }
                    }
                    
                    // Show success message with extracted fields
                    let extractedFields = [];
                    if (result.nid || result.back_nid) extractedFields.push('National ID');
                    if (result.name) extractedFields.push('Name');
                    if (result.address) extractedFields.push('Address');
                    
                    if (extractedFields.length > 0) {
                        alert('Document processed successfully!\n\nAuto-filled fields: ' + extractedFields.join(', '));
                    } else {
                        alert('Document processed but no data could be extracted. Please fill the fields manually.');
                    }
                    
                    console.log('Extracted data:', result);
                })
                .catch(error => {
                    console.error('Error:', error);
                    alert('Error processing document: ' + error.message);
                })
                .finally(() => {
                    processBtn.disabled = false;
                    processBtn.innerHTML = originalText;
                });
        });
    }
});