// Attendance Management System - Main JavaScript

document.addEventListener('DOMContentLoaded', function() {
    // Initialize all components
    initFlashMessages();
    initFormValidation();
    initConfirmDialogs();
    initDatePicker();
    initAnimations();
});

// Flash Messages Auto-dismiss
function initFlashMessages() {
    const alerts = document.querySelectorAll('.alert');
    alerts.forEach(alert => {
        setTimeout(() => {
            alert.style.opacity = '0';
            alert.style.transform = 'translateY(-10px)';
            setTimeout(() => alert.remove(), 300);
        }, 5000);
    });
}

// Form Validation
function initFormValidation() {
    const forms = document.querySelectorAll('form[data-validate]');
    forms.forEach(form => {
        form.addEventListener('submit', function(e) {
            const inputs = form.querySelectorAll('[required]');
            let isValid = true;
            
            inputs.forEach(input => {
                if (!input.value.trim()) {
                    isValid = false;
                    input.classList.add('error');
                    showInputError(input, 'This field is required');
                } else {
                    input.classList.remove('error');
                    hideInputError(input);
                }
            });
            
            // Email validation
            const emailInputs = form.querySelectorAll('input[type="email"]');
            emailInputs.forEach(input => {
                if (input.value && !isValidEmail(input.value)) {
                    isValid = false;
                    input.classList.add('error');
                    showInputError(input, 'Please enter a valid email');
                }
            });
            
            // Password confirmation
            const password = form.querySelector('input[name="password"]');
            const confirmPassword = form.querySelector('input[name="confirm_password"]');
            if (password && confirmPassword && password.value !== confirmPassword.value) {
                isValid = false;
                confirmPassword.classList.add('error');
                showInputError(confirmPassword, 'Passwords do not match');
            }
            
            if (!isValid) {
                e.preventDefault();
            }
        });
    });
}

function isValidEmail(email) {
    return /^[^\s@]+@[^\s@]+\.[^\s@]+$/.test(email);
}

function showInputError(input, message) {
    let errorEl = input.parentElement.querySelector('.input-error');
    if (!errorEl) {
        errorEl = document.createElement('span');
        errorEl.className = 'input-error';
        errorEl.style.cssText = 'color: var(--danger); font-size: 0.8rem; margin-top: 0.25rem; display: block;';
        input.parentElement.appendChild(errorEl);
    }
    errorEl.textContent = message;
}

function hideInputError(input) {
    const errorEl = input.parentElement.querySelector('.input-error');
    if (errorEl) errorEl.remove();
}

// Confirm Dialogs
function initConfirmDialogs() {
    const confirmButtons = document.querySelectorAll('[data-confirm]');
    confirmButtons.forEach(button => {
        button.addEventListener('click', function(e) {
            const message = this.getAttribute('data-confirm') || 'Are you sure?';
            if (!confirm(message)) {
                e.preventDefault();
            }
        });
    });
}

// Date Picker Enhancement
function initDatePicker() {
    const datePicker = document.getElementById('attendance-date');
    if (datePicker) {
        datePicker.addEventListener('change', function() {
            const url = new URL(window.location.href);
            url.searchParams.set('date', this.value);
            window.location.href = url.toString();
        });
    }
}

// Scroll Animations
function initAnimations() {
    const observerOptions = {
        threshold: 0.1,
        rootMargin: '0px 0px -50px 0px'
    };
    
    const observer = new IntersectionObserver((entries) => {
        entries.forEach(entry => {
            if (entry.isIntersecting) {
                entry.target.classList.add('animate-slide-up');
                observer.unobserve(entry.target);
            }
        });
    }, observerOptions);
    
    document.querySelectorAll('.stat-card, .class-card, .card').forEach(el => {
        el.style.opacity = '0';
        observer.observe(el);
    });
}

// Select All Students for Attendance
function selectAllAttendance(status) {
    const radios = document.querySelectorAll(`input[type="radio"][value="${status}"]`);
    radios.forEach(radio => {
        radio.checked = true;
    });
}

// Toggle Mobile Navigation
function toggleMobileNav() {
    const nav = document.querySelector('.navbar-nav');
    nav.classList.toggle('show');
}

// Search/Filter Students
function filterStudents(searchTerm) {
    const rows = document.querySelectorAll('.student-row');
    const term = searchTerm.toLowerCase();
    
    rows.forEach(row => {
        const name = row.querySelector('.student-name').textContent.toLowerCase();
        const details = row.querySelector('.student-details').textContent.toLowerCase();
        
        if (name.includes(term) || details.includes(term)) {
            row.style.display = '';
        } else {
            row.style.display = 'none';
        }
    });
}

// Filter students in dropdown (for adding students to class)
function filterAvailableStudents(searchTerm) {
    const select = document.getElementById('student-select');
    const options = select.querySelectorAll('option');
    const term = searchTerm.toLowerCase();
    
    options.forEach(option => {
        if (option.value === '') {
            option.style.display = 'none'; // Hide the placeholder
            return;
        }
        
        const name = option.getAttribute('data-name') || '';
        const roll = option.getAttribute('data-roll') || '';
        const email = option.getAttribute('data-email') || '';
        
        if (name.includes(term) || roll.includes(term) || email.includes(term)) {
            option.style.display = '';
        } else {
            option.style.display = 'none';
        }
    });
}

// Format Date
function formatDate(dateString) {
    const options = { weekday: 'long', year: 'numeric', month: 'long', day: 'numeric' };
    return new Date(dateString).toLocaleDateString('en-US', options);
}

// Calculate Attendance Percentage
function calculateAttendancePercentage(present, total) {
    if (total === 0) return 0;
    return Math.round((present / total) * 100);
}

// Export functions for global access
window.selectAllAttendance = selectAllAttendance;
window.filterStudents = filterStudents;
window.filterAvailableStudents = filterAvailableStudents;