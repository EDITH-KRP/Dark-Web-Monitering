// Advanced filtering functionality
document.addEventListener('DOMContentLoaded', function() {
    // Set up advanced filter toggle
    setupAdvancedFilterToggle();
    
    // Initialize date range picker
    initializeDateRangePicker();
    
    // Set up risk threshold slider
    setupRiskThresholdSlider();
});

// Set up advanced filter toggle
function setupAdvancedFilterToggle() {
    const toggleButton = document.getElementById('advanced-filter-toggle');
    const advancedFilters = document.getElementById('advanced-filters');
    
    if (toggleButton && advancedFilters) {
        toggleButton.addEventListener('click', function() {
            advancedFilters.classList.toggle('expanded');
            
            // Update button text
            if (advancedFilters.classList.contains('expanded')) {
                toggleButton.innerHTML = '<i class="fas fa-chevron-up"></i> Hide Advanced Filters';
            } else {
                toggleButton.innerHTML = '<i class="fas fa-chevron-down"></i> Show Advanced Filters';
            }
        });
    }
}

// Initialize date range picker
function initializeDateRangePicker() {
    const startDateInput = document.getElementById('start-date');
    const endDateInput = document.getElementById('end-date');
    
    if (startDateInput && endDateInput) {
        // Set default values (last 30 days)
        const today = new Date();
        const thirtyDaysAgo = new Date();
        thirtyDaysAgo.setDate(today.getDate() - 30);
        
        startDateInput.valueAsDate = thirtyDaysAgo;
        endDateInput.valueAsDate = today;
        
        // Add event listeners to validate date range
        startDateInput.addEventListener('change', validateDateRange);
        endDateInput.addEventListener('change', validateDateRange);
    }
}

// Validate date range
function validateDateRange() {
    const startDateInput = document.getElementById('start-date');
    const endDateInput = document.getElementById('end-date');
    
    if (startDateInput && endDateInput) {
        const startDate = new Date(startDateInput.value);
        const endDate = new Date(endDateInput.value);
        
        if (startDate > endDate) {
            showToast('Start date cannot be after end date', 'error');
            startDateInput.valueAsDate = endDate;
        }
    }
}

// Set up risk threshold slider
function setupRiskThresholdSlider() {
    const riskSlider = document.getElementById('risk-threshold');
    const riskValue = document.getElementById('risk-threshold-value');
    
    if (riskSlider && riskValue) {
        // Update the value display when the slider changes
        riskSlider.addEventListener('input', function() {
            riskValue.textContent = riskSlider.value;
            
            // Update the color based on the risk level
            updateRiskSliderColor(riskSlider.value);
        });
        
        // Set initial color
        updateRiskSliderColor(riskSlider.value);
    }
}

// Update risk slider color based on value
function updateRiskSliderColor(value) {
    const riskSlider = document.getElementById('risk-threshold');
    
    if (riskSlider) {
        // Remove existing classes
        riskSlider.classList.remove('risk-low', 'risk-medium', 'risk-high');
        
        // Add appropriate class
        if (value < 40) {
            riskSlider.classList.add('risk-low');
        } else if (value < 70) {
            riskSlider.classList.add('risk-medium');
        } else {
            riskSlider.classList.add('risk-high');
        }
    }
}

// Get all advanced filter values
function getAdvancedFilterValues() {
    const filters = {};
    
    // Date range
    const startDateInput = document.getElementById('start-date');
    const endDateInput = document.getElementById('end-date');
    if (startDateInput && endDateInput && startDateInput.value && endDateInput.value) {
        filters.date_range = [startDateInput.value, endDateInput.value];
    }
    
    // Risk threshold
    const riskSlider = document.getElementById('risk-threshold');
    if (riskSlider) {
        filters.risk_threshold = parseInt(riskSlider.value);
    }
    
    // Seller only
    const sellerOnly = document.getElementById('seller-only');
    if (sellerOnly) {
        filters.seller_only = sellerOnly.checked;
    }
    
    // Country
    const country = document.getElementById('country-filter');
    if (country && country.value) {
        filters.country = country.value;
    }
    
    // State/Region
    const state = document.getElementById('state-filter');
    if (state && state.value) {
        filters.state = state.value;
    }
    
    // District/City
    const district = document.getElementById('district-filter');
    if (district && district.value) {
        filters.district = district.value;
    }
    
    // Category
    const category = document.getElementById('category-filter');
    if (category && category.value) {
        filters.category = category.value;
    }
    
    return filters;
}