// ========================================
// Configuration
// ========================================
const API_BASE_URL = 'http://localhost:5001/api';

// ========================================
// State Management
// ========================================
let currentSection = 1;
const totalSections = 10;
let formData = {};
let contactCount = 1;

// ========================================
// DOM Elements
// ========================================
const form = document.getElementById('bepForm');
const sections = document.querySelectorAll('.form-section');
const prevBtn = document.getElementById('prevBtn');
const nextBtn = document.getElementById('nextBtn');
const submitBtn = document.getElementById('submitBtn');
const progressFill = document.getElementById('progressFill');
const progressText = document.getElementById('progressText');
const addContactBtn = document.getElementById('addContact');
const contactsContainer = document.getElementById('contactsContainer');
const successMessage = document.getElementById('successMessage');

// ========================================
// Initialization
// ========================================
document.addEventListener('DOMContentLoaded', () => {
    initializeForm();
    attachEventListeners();
    updateProgress();
});

function initializeForm() {
    // Show first section
    showSection(1);

    // Set min date for project dates to today
    const today = new Date().toISOString().split('T')[0];
    document.getElementById('projectStartDate').setAttribute('min', today);
}

function attachEventListeners() {
    // Navigation buttons
    prevBtn.addEventListener('click', previousSection);
    nextBtn.addEventListener('click', nextSection);
    submitBtn.addEventListener('click', handleSubmit);

    // Add contact button
    addContactBtn.addEventListener('click', addContact);

    // Success message buttons
    document.getElementById('downloadPdfBtn').addEventListener('click', downloadPDF);
    document.getElementById('downloadDocxBtn').addEventListener('click', downloadDOCX);
    document.getElementById('downloadBtn').addEventListener('click', downloadJSON);
    document.getElementById('printBtn').addEventListener('click', printSummary);
    document.getElementById('resetBtn').addEventListener('click', resetForm);

    // Form validation on input
    const inputs = form.querySelectorAll('input, select, textarea');
    inputs.forEach(input => {
        input.addEventListener('blur', () => validateField(input));
        input.addEventListener('input', () => {
            if (input.classList.contains('error')) {
                validateField(input);
            }
        });
    });

    // Date validation
    document.getElementById('projectStartDate').addEventListener('change', validateDates);
    document.getElementById('projectEndDate').addEventListener('change', validateDates);
}

// ========================================
// Section Navigation
// ========================================
function showSection(sectionNumber) {
    sections.forEach(section => {
        section.classList.remove('active');
    });

    const targetSection = document.querySelector(`[data-section="${sectionNumber}"]`);
    if (targetSection) {
        targetSection.classList.add('active');
        targetSection.scrollIntoView({ behavior: 'smooth', block: 'start' });
    }

    // Update button states
    prevBtn.disabled = sectionNumber === 1;

    if (sectionNumber === totalSections) {
        nextBtn.style.display = 'none';
        submitBtn.style.display = 'inline-flex';
    } else {
        nextBtn.style.display = 'inline-flex';
        submitBtn.style.display = 'none';
    }

    updateProgress();
}

function nextSection() {
    if (validateCurrentSection()) {
        saveCurrentSectionData();
        currentSection++;
        showSection(currentSection);
    }
}

function previousSection() {
    if (currentSection > 1) {
        saveCurrentSectionData();
        currentSection--;
        showSection(currentSection);
    }
}

function updateProgress() {
    const progress = (currentSection / totalSections) * 100;
    progressFill.style.width = `${progress}%`;
    progressText.textContent = `Section ${currentSection} of ${totalSections}`;
}

// ========================================
// Form Validation
// ========================================
function validateCurrentSection() {
    const currentSectionElement = document.querySelector(`[data-section="${currentSection}"]`);
    const requiredFields = currentSectionElement.querySelectorAll('[required]');
    let isValid = true;

    requiredFields.forEach(field => {
        if (!validateField(field)) {
            isValid = false;
        }
    });

    // Special validation for checkbox groups
    const checkboxGroups = currentSectionElement.querySelectorAll('input[type="checkbox"][required]');
    if (checkboxGroups.length > 0) {
        const groupName = checkboxGroups[0].name;
        const checkedBoxes = currentSectionElement.querySelectorAll(`input[name="${groupName}"]:checked`);

        if (checkedBoxes.length === 0) {
            const errorSpan = currentSectionElement.querySelector('.checkbox-grid + .error-message');
            if (errorSpan) {
                errorSpan.textContent = 'Please select at least one option';
                errorSpan.style.display = 'block';
                isValid = false;
            }
        } else {
            const errorSpan = currentSectionElement.querySelector('.checkbox-grid + .error-message');
            if (errorSpan) {
                errorSpan.style.display = 'none';
            }
        }
    }

    if (!isValid) {
        // Scroll to first error
        const firstError = currentSectionElement.querySelector('.form-group.error');
        if (firstError) {
            firstError.scrollIntoView({ behavior: 'smooth', block: 'center' });
        }
    }

    return isValid;
}

function validateField(field) {
    const formGroup = field.closest('.form-group');
    const errorSpan = formGroup ? formGroup.querySelector('.error-message') : null;

    // Remove previous error state
    if (formGroup) {
        formGroup.classList.remove('error');
    }
    if (errorSpan) {
        errorSpan.textContent = '';
        errorSpan.style.display = 'none';
    }

    // Check if field is required and empty
    if (field.hasAttribute('required') && !field.value.trim()) {
        setFieldError(formGroup, errorSpan, 'This field is required');
        return false;
    }

    // Email validation
    if (field.type === 'email' && field.value) {
        const emailRegex = /^[^\s@]+@[^\s@]+\.[^\s@]+$/;
        if (!emailRegex.test(field.value)) {
            setFieldError(formGroup, errorSpan, 'Please enter a valid email address');
            return false;
        }
    }

    // Number validation
    if (field.type === 'number' && field.value) {
        const min = field.getAttribute('min');
        const max = field.getAttribute('max');

        if (min !== null && parseFloat(field.value) < parseFloat(min)) {
            setFieldError(formGroup, errorSpan, `Value must be at least ${min}`);
            return false;
        }

        if (max !== null && parseFloat(field.value) > parseFloat(max)) {
            setFieldError(formGroup, errorSpan, `Value must be at most ${max}`);
            return false;
        }
    }

    return true;
}

function setFieldError(formGroup, errorSpan, message) {
    if (formGroup) {
        formGroup.classList.add('error');
    }
    if (errorSpan) {
        errorSpan.textContent = message;
        errorSpan.style.display = 'block';
    }
}

function validateDates() {
    const startDate = document.getElementById('projectStartDate');
    const endDate = document.getElementById('projectEndDate');

    if (startDate.value && endDate.value) {
        if (new Date(endDate.value) < new Date(startDate.value)) {
            const formGroup = endDate.closest('.form-group');
            const errorSpan = formGroup.querySelector('.error-message');
            setFieldError(formGroup, errorSpan, 'End date must be after start date');
            return false;
        }
    }

    return true;
}

// ========================================
// Data Management
// ========================================
function saveCurrentSectionData() {
    const currentSectionElement = document.querySelector(`[data-section="${currentSection}"]`);
    const inputs = currentSectionElement.querySelectorAll('input, select, textarea');

    inputs.forEach(input => {
        if (input.type === 'checkbox') {
            if (!formData[input.name]) {
                formData[input.name] = [];
            }
            if (input.checked && !formData[input.name].includes(input.value)) {
                formData[input.name].push(input.value);
            } else if (!input.checked) {
                formData[input.name] = formData[input.name].filter(v => v !== input.value);
            }
        } else if (input.type === 'radio') {
            if (input.checked) {
                formData[input.name] = input.value;
            }
        } else {
            formData[input.name] = input.value;
        }
    });
}

function getAllFormData() {
    saveCurrentSectionData();

    // Add metadata
    formData.metadata = {
        createdDate: new Date().toISOString(),
        version: '1.0',
        standard: formData.standardUsed || 'Not specified'
    };

    return formData;
}

// ========================================
// Contact Management
// ========================================
function addContact() {
    contactCount++;
    const contactHTML = `
        <div class="contact-item" data-contact="${contactCount}">
            <button type="button" class="remove-contact" onclick="removeContact(${contactCount})" aria-label="Remove contact">×</button>
            <h3>Contact ${contactCount}</h3>
            <div class="form-grid">
                <div class="form-group">
                    <label for="contactOrg${contactCount}">Organization <span class="required">*</span></label>
                    <input type="text" id="contactOrg${contactCount}" name="contactOrg${contactCount}" required>
                    <span class="error-message"></span>
                </div>
                <div class="form-group">
                    <label for="contactRole${contactCount}">Role <span class="required">*</span></label>
                    <select id="contactRole${contactCount}" name="contactRole${contactCount}" required>
                        <option value="">Select...</option>
                        <option value="owner">Owner</option>
                        <option value="architect">Architect</option>
                        <option value="engineer">Engineer</option>
                        <option value="contractor">General Contractor</option>
                        <option value="bim-manager">BIM Manager</option>
                        <option value="consultant">Consultant</option>
                        <option value="other">Other</option>
                    </select>
                    <span class="error-message"></span>
                </div>
                <div class="form-group">
                    <label for="contactName${contactCount}">Contact Name <span class="required">*</span></label>
                    <input type="text" id="contactName${contactCount}" name="contactName${contactCount}" required>
                    <span class="error-message"></span>
                </div>
                <div class="form-group">
                    <label for="contactEmail${contactCount}">Email <span class="required">*</span></label>
                    <input type="email" id="contactEmail${contactCount}" name="contactEmail${contactCount}" required>
                    <span class="error-message"></span>
                </div>
                <div class="form-group">
                    <label for="contactPhone${contactCount}">Phone</label>
                    <input type="tel" id="contactPhone${contactCount}" name="contactPhone${contactCount}">
                    <span class="error-message"></span>
                </div>
            </div>
        </div>
    `;

    contactsContainer.insertAdjacentHTML('beforeend', contactHTML);

    // Attach event listeners to new inputs
    const newContact = contactsContainer.querySelector(`[data-contact="${contactCount}"]`);
    const newInputs = newContact.querySelectorAll('input, select');
    newInputs.forEach(input => {
        input.addEventListener('blur', () => validateField(input));
    });

    // Scroll to new contact
    newContact.scrollIntoView({ behavior: 'smooth', block: 'center' });
}

function removeContact(contactId) {
    const contactElement = document.querySelector(`[data-contact="${contactId}"]`);
    if (contactElement && contactCount > 1) {
        contactElement.remove();

        // Remove from formData
        delete formData[`contactOrg${contactId}`];
        delete formData[`contactRole${contactId}`];
        delete formData[`contactName${contactId}`];
        delete formData[`contactEmail${contactId}`];
        delete formData[`contactPhone${contactId}`];
    }
}

// ========================================
// Form Submission
// ========================================
async function handleSubmit(e) {
    e.preventDefault();

    if (validateCurrentSection()) {
        const data = getAllFormData();
        console.log('Form submitted with data:', data);

        // Show loading state
        submitBtn.disabled = true;
        submitBtn.innerHTML = '<span>Saving...</span>';

        try {
            // Send data to backend API
            const response = await fetch(`${API_BASE_URL}/projects`, {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json',
                },
                body: JSON.stringify(data)
            });

            const result = await response.json();

            if (result.success) {
                console.log('Project saved successfully:', result);

                // Store project ID and data
                window.bepData = data;
                window.bepProjectId = result.project_id;

                // Hide form and show success message
                form.style.display = 'none';
                successMessage.style.display = 'block';
                successMessage.scrollIntoView({ behavior: 'smooth', block: 'start' });

                // Clear auto-save
                localStorage.removeItem('bep-draft');
            } else {
                throw new Error(result.error || 'Failed to save project');
            }
        } catch (error) {
            console.error('Error saving project:', error);
            alert(`Failed to save BIM Execution Plan: ${error.message}\n\nPlease check if the server is running and try again.`);

            // Reset button state
            submitBtn.disabled = false;
            submitBtn.textContent = 'Generate BEP';
        }
    }
}

// ========================================
// Export Functions
// ========================================
async function downloadPDF() {
    const projectId = window.bepProjectId;

    if (!projectId) {
        alert('Project ID not found. Please submit the form first.');
        return;
    }

    try {
        const response = await fetch(`${API_BASE_URL}/projects/${projectId}/export/pdf`);

        if (!response.ok) {
            throw new Error('Failed to generate PDF');
        }

        const blob = await response.blob();
        const url = URL.createObjectURL(blob);
        const link = document.createElement('a');
        link.href = url;

        // Get filename from response headers or use default
        const contentDisposition = response.headers.get('Content-Disposition');
        let filename = 'BIM_Execution_Plan.pdf';
        if (contentDisposition) {
            const matches = /filename[^;=\n]*=((['"]).*?\2|[^;\n]*)/.exec(contentDisposition);
            if (matches != null && matches[1]) {
                filename = matches[1].replace(/['"]/g, '');
            }
        }

        link.download = filename;
        document.body.appendChild(link);
        link.click();
        document.body.removeChild(link);
        URL.revokeObjectURL(url);
    } catch (error) {
        console.error('Error downloading PDF:', error);
        alert('Failed to download PDF. Please check if the server is running.');
    }
}

async function downloadDOCX() {
    const projectId = window.bepProjectId;

    if (!projectId) {
        alert('Project ID not found. Please submit the form first.');
        return;
    }

    try {
        const response = await fetch(`${API_BASE_URL}/projects/${projectId}/export/docx`);

        if (!response.ok) {
            throw new Error('Failed to generate DOCX');
        }

        const blob = await response.blob();
        const url = URL.createObjectURL(blob);
        const link = document.createElement('a');
        link.href = url;

        // Get filename from response headers or use default
        const contentDisposition = response.headers.get('Content-Disposition');
        let filename = 'BIM_Execution_Plan.docx';
        if (contentDisposition) {
            const matches = /filename[^;=\n]*=((['"]).*?\2|[^;\n]*)/.exec(contentDisposition);
            if (matches != null && matches[1]) {
                filename = matches[1].replace(/['"]/g, '');
            }
        }

        link.download = filename;
        document.body.appendChild(link);
        link.click();
        document.body.removeChild(link);
        URL.revokeObjectURL(url);
    } catch (error) {
        console.error('Error downloading DOCX:', error);
        alert('Failed to download DOCX. Please check if the server is running.');
    }
}

function downloadJSON() {
    const data = window.bepData || getAllFormData();
    const dataStr = JSON.stringify(data, null, 2);
    const dataBlob = new Blob([dataStr], { type: 'application/json' });

    const url = URL.createObjectURL(dataBlob);
    const link = document.createElement('a');
    link.href = url;
    link.download = `BIM-Execution-Plan-${data.projectName || 'document'}-${new Date().toISOString().split('T')[0]}.json`;
    document.body.appendChild(link);
    link.click();
    document.body.removeChild(link);
    URL.revokeObjectURL(url);
}

function printSummary() {
    // Show all sections for printing
    sections.forEach(section => {
        section.classList.add('active');
    });

    window.print();

    // Restore current section view
    setTimeout(() => {
        showSection(currentSection);
    }, 100);
}

function resetForm() {
    if (confirm('Are you sure you want to start over? All entered data will be lost.')) {
        formData = {};
        contactCount = 1;
        currentSection = 1;

        form.reset();

        // Remove extra contacts
        const contacts = contactsContainer.querySelectorAll('.contact-item');
        contacts.forEach((contact, index) => {
            if (index > 0) {
                contact.remove();
            }
        });

        // Clear error states
        document.querySelectorAll('.form-group.error').forEach(group => {
            group.classList.remove('error');
        });

        // Show form and hide success message
        form.style.display = 'block';
        successMessage.style.display = 'none';

        showSection(1);
        window.scrollTo({ top: 0, behavior: 'smooth' });
    }
}

// ========================================
// Keyboard Navigation
// ========================================
document.addEventListener('keydown', (e) => {
    // Alt + Right Arrow: Next section
    if (e.altKey && e.key === 'ArrowRight' && !nextBtn.disabled && nextBtn.style.display !== 'none') {
        nextSection();
    }

    // Alt + Left Arrow: Previous section
    if (e.altKey && e.key === 'ArrowLeft' && !prevBtn.disabled) {
        previousSection();
    }
});

// ========================================
// Auto-save to localStorage (Optional)
// ========================================
function autoSave() {
    const data = getAllFormData();
    localStorage.setItem('bep-draft', JSON.stringify(data));
    console.log('Auto-saved to localStorage');
}

// Auto-save every 30 seconds
setInterval(autoSave, 30000);

// Load draft on page load
window.addEventListener('load', () => {
    const draft = localStorage.getItem('bep-draft');
    if (draft) {
        const shouldLoad = confirm('A draft was found. Would you like to continue where you left off?');
        if (shouldLoad) {
            formData = JSON.parse(draft);
            loadFormData();
        } else {
            localStorage.removeItem('bep-draft');
        }
    }
});

function loadFormData() {
    Object.keys(formData).forEach(key => {
        const field = document.querySelector(`[name="${key}"]`);
        if (field) {
            if (field.type === 'checkbox') {
                if (Array.isArray(formData[key]) && formData[key].includes(field.value)) {
                    field.checked = true;
                }
            } else if (field.type === 'radio') {
                if (field.value === formData[key]) {
                    field.checked = true;
                }
            } else {
                field.value = formData[key];
            }
        }
    });
}

// Clear auto-save on successful submit
form.addEventListener('submit', () => {
    localStorage.removeItem('bep-draft');
});
