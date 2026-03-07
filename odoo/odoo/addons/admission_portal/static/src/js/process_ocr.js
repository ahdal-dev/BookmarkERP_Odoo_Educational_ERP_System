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
                    alert('Document processed successfully!');
                    // You can use the OCR response here
                    // For example: populate form fields with extracted data
                    console.log('Extracted data:', data);
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