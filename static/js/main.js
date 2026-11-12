// NeuroCardioAI Main JavaScript - Complete Version

// Global notification function
window.showNotification = function(message, type = 'info') {
    // Create notification container if it doesn't exist
    let container = $('#notification-area');
    if (container.length === 0) {
        container = $('<div id="notification-area" style="position: fixed; top: 20px; right: 20px; z-index: 9999;"></div>');
        $('body').append(container);
    }
    
    const notificationId = 'notification-' + Date.now();
    const notification = `
        <div id="${notificationId}" class="alert alert-${type} alert-dismissible fade show notification" role="alert" style="min-width: 300px; box-shadow: 0 4px 12px rgba(0,0,0,0.15);">
            ${message}
            <button type="button" class="btn-close" data-bs-dismiss="alert" aria-label="Close"></button>
        </div>
    `;
    
    container.append(notification);
    
    // Auto remove after 5 seconds
    setTimeout(function() {
        $('#' + notificationId).fadeOut('slow', function() {
            $(this).remove();
        });
    }, 5000);
};

// Global utility functions
window.formatDate = function(date) {
    const d = new Date(date);
    return d.toLocaleDateString() + ' ' + d.toLocaleTimeString();
};

window.formatNumber = function(num, decimals = 1) {
    return Number(num).toFixed(decimals);
};

window.getRiskLevel = function(score) {
    if (score < 30) return 'Low';
    if (score < 60) return 'Moderate';
    return 'High';
};

window.getRiskColor = function(score) {
    if (score < 30) return '#06d6a0';
    if (score < 60) return '#ffd166';
    return '#ef476f';
};

window.getRiskBadge = function(score, level) {
    const riskLevel = level || window.getRiskLevel(score);
    const color = window.getRiskColor(score);
    return `<span class="badge bg-${color}">${riskLevel}</span>`;
};

$(document).ready(function() {
    console.log("NeuroCardioAI Main JS initialized");
    
    // ======================================
    // BOOTSTRAP COMPONENTS
    // ======================================
    
    // Initialize tooltips
    var tooltipTriggerList = [].slice.call(document.querySelectorAll('[data-bs-toggle="tooltip"]'));
    var tooltipList = tooltipTriggerList.map(function(tooltipTriggerEl) {
        return new bootstrap.Tooltip(tooltipTriggerEl);
    });
    
    // Initialize popovers
    var popoverTriggerList = [].slice.call(document.querySelectorAll('[data-bs-toggle="popover"]'));
    var popoverList = popoverTriggerList.map(function(popoverTriggerEl) {
        return new bootstrap.Popover(popoverTriggerEl);
    });
    
    // ======================================
    // UI UTILITIES
    // ======================================
    
    // Auto-hide alerts after 5 seconds
    setTimeout(function() {
        $('.alert:not(.notification)').fadeOut('slow');
    }, 5000);
    
    // Smooth scroll for anchor links
    $('a[href*="#"]:not([href="#"])').on('click', function(e) {
        if (this.hash !== '') {
            e.preventDefault();
            const hash = this.hash;
            const target = $(hash);
            if (target.length) {
                $('html, body').animate({
                    scrollTop: target.offset().top - 100
                }, 800);
            }
        }
    });
    
    // ======================================
    // FORM VALIDATION
    // ======================================
    
    // Form validation with Bootstrap
    $('form').on('submit', function(e) {
        let isValid = true;
        $(this).find('[required]').each(function() {
            if (!$(this).val()) {
                isValid = false;
                $(this).addClass('is-invalid');
            } else {
                $(this).removeClass('is-invalid');
            }
        });
        
        if (!isValid) {
            e.preventDefault();
            window.showNotification('Please fill in all required fields', 'warning');
        }
        
        return isValid;
    });
    
    // Password strength meter
    $('#password, #new_password').on('keyup', function() {
        const password = $(this).val();
        const strength = checkPasswordStrength(password);
        updatePasswordStrength(strength, $(this));
    });
    
    $('#confirm_password').on('keyup', function() {
        const password = $('#password').val();
        const confirm = $(this).val();
        
        if (password === confirm) {
            $(this).removeClass('is-invalid').addClass('is-valid');
            $('#password-match-error').hide();
        } else {
            $(this).removeClass('is-valid').addClass('is-invalid');
            $('#password-match-error').show();
        }
    });
    
    function checkPasswordStrength(password) {
        let strength = 0;
        if (password.length >= 8) strength += 25;
        if (password.match(/[a-z]+/)) strength += 25;
        if (password.match(/[A-Z]+/)) strength += 25;
        if (password.match(/[0-9]+/)) strength += 25;
        if (password.match(/[$@#&!]+/)) strength += 25;
        return Math.min(strength, 100);
    }
    
    function updatePasswordStrength(strength, field) {
        const meter = field.closest('.mb-3').find('.password-strength');
        if (meter.length) {
            meter.css('width', strength + '%');
            meter.removeClass('bg-danger bg-warning bg-success');
            if (strength < 50) {
                meter.addClass('bg-danger');
            } else if (strength < 75) {
                meter.addClass('bg-warning');
            } else {
                meter.addClass('bg-success');
            }
        }
    }
    
    // Confirm actions
    $('.confirm-action').on('click', function(e) {
        const message = $(this).data('confirm-message') || 'Are you sure you want to proceed?';
        if (!confirm(message)) {
            e.preventDefault();
        }
    });
    
    // ======================================
    // FILE UPLOAD PREVIEW
    // ======================================
    
    // File input preview with dynamic preview ID
    $('input[type="file"]').on('change', function() {
        const file = this.files[0];
        const previewId = $(this).data('preview') || 'file-preview';
        const previewContainer = $(this).data('preview-container');
        const maxSize = $(this).data('max-size') || 5 * 1024 * 1024; // Default 5MB
        
        if (file) {
            // Validate file size
            if (file.size > maxSize) {
                window.showNotification(`File size exceeds ${Math.round(maxSize/1024/1024)}MB limit`, 'warning');
                $(this).val('');
                return;
            }
            
            // Validate file type for images
            if ($(this).attr('accept') && $(this).attr('accept').includes('image')) {
                const validTypes = ['image/jpeg', 'image/png', 'image/gif'];
                if (!validTypes.includes(file.type)) {
                    window.showNotification('Please select a valid image file (JPG, PNG, GIF)', 'warning');
                    $(this).val('');
                    return;
                }
            }
            
            const reader = new FileReader();
            reader.onload = function(e) {
                $('#' + previewId).attr('src', e.target.result).show();
                if (previewContainer) {
                    $('#' + previewContainer).show();
                }
            };
            reader.readAsDataURL(file);
            
            // Show file name
            const fileNameId = $(this).data('filename') || 'file-name';
            $('#' + fileNameId).text(file.name).show();
        }
    });
    
    // ======================================
    // DYNAMIC FORM FIELDS
    // ======================================
    
    // Dynamic form fields
    $('#add-field').on('click', function() {
        const template = $('#field-template').html();
        const container = $('#dynamic-fields');
        const newField = $(template);
        
        // Add remove button functionality
        newField.find('.remove-field').on('click', function() {
            $(this).closest('.dynamic-field').remove();
        });
        
        container.append(newField);
    });
    
    $(document).on('click', '.remove-field', function() {
        $(this).closest('.dynamic-field').remove();
    });
    
    // ======================================
    // SEARCH FUNCTIONALITY
    // ======================================
    
    // Search functionality with debounce
    let searchTimeout;
    $('#search-input').on('keyup', function() {
        clearTimeout(searchTimeout);
        const searchTerm = $(this).val().toLowerCase();
        
        searchTimeout = setTimeout(function() {
            $('.searchable-item').each(function() {
                const text = $(this).text().toLowerCase();
                if (text.indexOf(searchTerm) > -1) {
                    $(this).show();
                } else {
                    $(this).hide();
                }
            });
        }, 300);
    });
    
    // ======================================
    // SORTABLE TABLES
    // ======================================
    
    // Sortable tables with direction toggle
    $('.sortable').on('click', function() {
        const table = $(this).closest('table');
        const index = $(this).data('index');
        const rows = table.find('tbody tr').get();
        const isAsc = $(this).hasClass('asc');
        
        rows.sort(function(a, b) {
            const aValue = $(a).children('td').eq(index).text();
            const bValue = $(b).children('td').eq(index).text();
            
            // Try numeric comparison first
            const aNum = parseFloat(aValue);
            const bNum = parseFloat(bValue);
            
            if (!isNaN(aNum) && !isNaN(bNum)) {
                return isAsc ? aNum - bNum : bNum - aNum;
            }
            
            // Fall back to string comparison
            return isAsc ? 
                aValue.localeCompare(bValue) : 
                bValue.localeCompare(aValue);
        });
        
        // Update sort indicators
        table.find('.sortable').removeClass('asc desc');
        $(this).toggleClass('asc', !isAsc).toggleClass('desc', isAsc);
        
        $.each(rows, function(index, row) {
            table.children('tbody').append(row);
        });
    });
    
    // ======================================
    // DATE RANGE PICKER
    // ======================================
    
    // Date range picker (if daterangepicker is available)
    if ($('.daterange').length && typeof $.fn.daterangepicker !== 'undefined') {
        $('.daterange').daterangepicker({
            opens: 'left',
            autoUpdateInput: false,
            locale: {
                format: 'YYYY-MM-DD',
                cancelLabel: 'Clear'
            }
        });
        
        $('.daterange').on('apply.daterangepicker', function(ev, picker) {
            $(this).val(picker.startDate.format('YYYY-MM-DD') + ' - ' + picker.endDate.format('YYYY-MM-DD'));
        });
        
        $('.daterange').on('cancel.daterangepicker', function(ev, picker) {
            $(this).val('');
        });
    }
    
    // ======================================
    // REAL-TIME CLOCK
    // ======================================
    
    // Real-time clock
    function updateClock() {
        const now = new Date();
        const timeString = now.toLocaleTimeString();
        const dateString = now.toLocaleDateString();
        $('#live-clock').text(timeString);
        $('#live-date').text(dateString);
    }
    updateClock();
    setInterval(updateClock, 1000);
    
    // ======================================
    // AJAX REQUEST HELPER
    // ======================================
    
    // AJAX request helper with improved error handling
    window.api = {
        get: function(url, callback, errorCallback) {
            $.ajax({
                url: url,
                type: 'GET',
                headers: {
                    'X-Requested-With': 'XMLHttpRequest'
                },
                success: function(response) {
                    if (callback) callback(response);
                },
                error: function(xhr, status, error) {
                    console.error('API Error:', status, error);
                    let errorMsg = 'An error occurred';
                    
                    try {
                        const response = JSON.parse(xhr.responseText);
                        errorMsg = response.error || errorMsg;
                    } catch(e) {
                        errorMsg = xhr.responseText || errorMsg;
                    }
                    
                    if (errorCallback) {
                        errorCallback(errorMsg);
                    } else {
                        window.showNotification('Error: ' + errorMsg, 'danger');
                    }
                }
            });
        },
        
        post: function(url, data, callback, errorCallback) {
            $.ajax({
                url: url,
                type: 'POST',
                data: JSON.stringify(data),
                contentType: 'application/json',
                headers: {
                    'X-Requested-With': 'XMLHttpRequest'
                },
                success: function(response) {
                    if (callback) callback(response);
                },
                error: function(xhr, status, error) {
                    console.error('API Error:', status, error);
                    let errorMsg = 'An error occurred';
                    
                    try {
                        const response = JSON.parse(xhr.responseText);
                        errorMsg = response.error || errorMsg;
                    } catch(e) {
                        errorMsg = xhr.responseText || errorMsg;
                    }
                    
                    if (errorCallback) {
                        errorCallback(errorMsg);
                    } else {
                        window.showNotification('Error: ' + errorMsg, 'danger');
                    }
                }
            });
        },
        
        upload: function(url, formData, callback, errorCallback, progressCallback) {
            $.ajax({
                url: url,
                type: 'POST',
                data: formData,
                processData: false,
                contentType: false,
                headers: {
                    'X-Requested-With': 'XMLHttpRequest'
                },
                xhr: function() {
                    const xhr = new window.XMLHttpRequest();
                    if (progressCallback) {
                        xhr.upload.addEventListener('progress', function(e) {
                            if (e.lengthComputable) {
                                const percentComplete = Math.round((e.loaded / e.total) * 100);
                                progressCallback(percentComplete);
                            }
                        });
                    }
                    return xhr;
                },
                success: function(response) {
                    if (callback) callback(response);
                },
                error: function(xhr, status, error) {
                    console.error('Upload Error:', status, error);
                    let errorMsg = 'Upload failed';
                    
                    try {
                        const response = JSON.parse(xhr.responseText);
                        errorMsg = response.error || errorMsg;
                    } catch(e) {
                        errorMsg = xhr.responseText || errorMsg;
                    }
                    
                    if (errorCallback) {
                        errorCallback(errorMsg);
                    } else {
                        window.showNotification('Error: ' + errorMsg, 'danger');
                    }
                }
            });
        }
    };
    
    // ======================================
    // BACK TO TOP BUTTON
    // ======================================
    
    // Back to top button
    if ($('#back-to-top').length === 0) {
        $('body').append('<button id="back-to-top" class="btn btn-primary rounded-circle position-fixed bottom-0 end-0 m-4" style="display: none; width: 50px; height: 50px; z-index: 1000; box-shadow: 0 4px 12px rgba(0,0,0,0.2);"><i class="fas fa-arrow-up"></i></button>');
    }
    
    $(window).scroll(function() {
        if ($(this).scrollTop() > 300) {
            $('#back-to-top').fadeIn();
        } else {
            $('#back-to-top').fadeOut();
        }
    });
    
    $('#back-to-top').on('click', function() {
        $('html, body').animate({ scrollTop: 0 }, 800);
        return false;
    });
    
    // ======================================
    // CHART INITIALIZATION
    // ======================================
    
    // Initialize any charts on the page
    initializeCharts();
    
    // ======================================
    // CSRF TOKEN SETUP
    // ======================================
    
    // Add CSRF token to all AJAX requests if needed
    const csrfToken = $('meta[name="csrf-token"]').attr('content');
    if (csrfToken) {
        $.ajaxSetup({
            headers: {
                'X-CSRFToken': csrfToken
            }
        });
    }
});

// ======================================
// CHART INITIALIZATION FUNCTION
// ======================================

function initializeCharts() {
    // Check if Chart.js is available
    if (typeof Chart === 'undefined') return;
    
    // Set default options
    Chart.defaults.font.family = "'Poppins', sans-serif";
    Chart.defaults.font.size = 12;
    Chart.defaults.color = '#6c757d';
    Chart.defaults.responsive = true;
    Chart.defaults.maintainAspectRatio = false;
    
    // Initialize risk gauge if element exists
    const gaugeCanvas = document.getElementById('riskGauge');
    if (gaugeCanvas) {
        const ctx = gaugeCanvas.getContext('2d');
        const riskValue = gaugeCanvas.dataset.risk || 35;
        
        new Chart(ctx, {
            type: 'doughnut',
            data: {
                datasets: [{
                    data: [riskValue, 100 - riskValue],
                    backgroundColor: ['#ef476f', '#e9ecef'],
                    borderWidth: 0,
                    circumference: 180,
                    rotation: 270
                }]
            },
            options: {
                responsive: true,
                maintainAspectRatio: true,
                cutout: '70%',
                plugins: {
                    tooltip: { enabled: false },
                    legend: { display: false }
                }
            }
        });
    }
    
    // Initialize any charts with data attributes
    document.querySelectorAll('canvas[data-chart]').forEach(canvas => {
        const chartType = canvas.dataset.chart;
        const canvasId = canvas.id;
        
        if (!canvasId) return;
        
        try {
            const data = JSON.parse(canvas.dataset.data || '[]');
            const labels = JSON.parse(canvas.dataset.labels || '[]');
            
            switch(chartType) {
                case 'bar':
                    loadBarChart(canvasId, labels, data);
                    break;
                case 'pie':
                    if (data.length >= 2) {
                        loadPieChart(canvasId, data[0], data[1]);
                    }
                    break;
                case 'line':
                    loadLineChart(canvasId, labels, data);
                    break;
                case 'gauge':
                    if (data.length > 0) {
                        loadGaugeChart(canvasId, data[0]);
                    }
                    break;
            }
        } catch (e) {
            console.error('Error initializing chart:', e);
        }
    });
}

// ======================================
// CHART LOADER FUNCTIONS
// ======================================

// Bar Chart
function loadBarChart(canvasId, labels, data, options = {}) {
    const canvas = document.getElementById(canvasId);
    if (!canvas) return;

    // Destroy existing chart
    const existingChart = Chart.getChart(canvas);
    if (existingChart) existingChart.destroy();

    new Chart(canvas, {
        type: "bar",
        data: {
            labels: labels,
            datasets: [{
                label: options.label || "Risk %",
                data: data,
                backgroundColor: options.backgroundColor || "#4361ee",
                borderRadius: options.borderRadius || 8,
                maxBarThickness: options.maxBarThickness || 50
            }]
        },
        options: {
            responsive: true,
            maintainAspectRatio: false,
            plugins: {
                legend: { display: false },
                tooltip: {
                    callbacks: {
                        label: function(context) {
                            return `${context.dataset.label}: ${context.raw}%`;
                        }
                    }
                }
            },
            scales: {
                y: {
                    beginAtZero: true,
                    max: 100,
                    grid: { color: 'rgba(0,0,0,0.05)' }
                },
                x: { grid: { display: false } }
            }
        }
    });
}

// Pie Chart
function loadPieChart(canvasId, high, low, options = {}) {
    const canvas = document.getElementById(canvasId);
    if (!canvas) return;

    // Destroy existing chart
    const existingChart = Chart.getChart(canvas);
    if (existingChart) existingChart.destroy();

    const data = options.data || [high, low];
    const labels = options.labels || ["High Risk", "Low Risk"];
    const colors = options.colors || ["#e74c3c", "#2ecc71"];

    new Chart(canvas, {
        type: "pie",
        data: {
            labels: labels,
            datasets: [{
                data: data,
                backgroundColor: colors,
                borderWidth: options.borderWidth || 2
            }]
        },
        options: {
            responsive: true,
            maintainAspectRatio: false,
            plugins: {
                legend: { position: options.legendPosition || 'bottom' },
                tooltip: {
                    callbacks: {
                        label: function(context) {
                            const total = context.dataset.data.reduce((a, b) => a + b, 0);
                            const percentage = ((context.raw / total) * 100).toFixed(1);
                            return `${context.label}: ${context.raw} (${percentage}%)`;
                        }
                    }
                }
            }
        }
    });
}

// Line Chart
function loadLineChart(canvasId, labels, data, options = {}) {
    const canvas = document.getElementById(canvasId);
    if (!canvas) return;

    // Destroy existing chart
    const existingChart = Chart.getChart(canvas);
    if (existingChart) existingChart.destroy();

    new Chart(canvas, {
        type: "line",
        data: {
            labels: labels,
            datasets: [{
                label: options.label || 'Risk Trend',
                data: data,
                borderColor: options.borderColor || '#4361ee',
                backgroundColor: 'transparent',
                tension: options.tension || 0.3,
                fill: false,
                pointBackgroundColor: options.pointColor || '#4361ee',
                pointBorderColor: '#ffffff',
                pointBorderWidth: 2,
                pointRadius: options.pointRadius || 4
            }]
        },
        options: {
            responsive: true,
            maintainAspectRatio: false,
            plugins: {
                legend: { display: false },
                tooltip: { mode: 'index', intersect: false }
            },
            scales: {
                y: {
                    beginAtZero: true,
                    max: 100,
                    grid: { color: 'rgba(0,0,0,0.05)' }
                }
            }
        }
    });
}

// Gauge Chart
function loadGaugeChart(canvasId, value, options = {}) {
    const canvas = document.getElementById(canvasId);
    if (!canvas) return;

    // Destroy existing chart
    const existingChart = Chart.getChart(canvas);
    if (existingChart) existingChart.destroy();

    // Determine color based on value
    let color = '#06d6a0';
    if (value > 60) color = '#ef476f';
    else if (value > 30) color = '#ffd166';

    new Chart(canvas, {
        type: "doughnut",
        data: {
            datasets: [{
                data: [value, 100 - value],
                backgroundColor: [color, '#e9ecef'],
                borderWidth: 0,
                circumference: 180,
                rotation: 270
            }]
        },
        options: {
            responsive: true,
            maintainAspectRatio: true,
            cutout: '70%',
            plugins: {
                tooltip: { enabled: false },
                legend: { display: false }
            }
        }
    });
}

// ======================================
// PLOTLY CONFIGURATION
// ======================================

// Plotly default config (if Plotly is available)
if (typeof Plotly !== 'undefined') {
    Plotly.setPlotConfig({
        responsive: true,
        displaylogo: false,
        modeBarButtonsToRemove: [
            'sendDataToCloud', 'zoom2d', 'pan2d', 'select2d', 
            'lasso2d', 'zoomIn2d', 'zoomOut2d', 'autoScale2d', 
            'resetScale2d', 'hoverClosestCartesian', 'hoverCompareCartesian'
        ]
    });
}

// ======================================
// EXPORT FUNCTIONS
// ======================================

// Make chart functions globally available
window.loadBarChart = loadBarChart;
window.loadPieChart = loadPieChart;
window.loadLineChart = loadLineChart;
window.loadGaugeChart = loadGaugeChart;