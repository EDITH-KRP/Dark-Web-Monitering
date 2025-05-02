// Browser selector functionality
document.addEventListener('DOMContentLoaded', function() {
    // Check which browsers are available
    checkAvailableBrowsers();
    
    // Set up browser selection event listeners
    setupBrowserSelectors();
});

// Check which browsers are available from the backend
async function checkAvailableBrowsers() {
    try {
        const response = await fetch(`${API_URL}/browser-status`);
        
        if (!response.ok) {
            throw new Error(`API error: ${response.status}`);
        }
        
        const browserStatus = await response.json();
        
        // Update the UI to show available browsers
        updateBrowserUI(browserStatus);
    } catch (error) {
        console.error('Error checking browser status:', error);
        showToast(`Error checking available browsers: ${error.message}`, 'error');
    }
}

// Update the UI to show available browsers
function updateBrowserUI(browserStatus) {
    const browserSelector = document.getElementById('browser-selector');
    
    if (!browserSelector) {
        // Create the browser selector if it doesn't exist
        createBrowserSelector(browserStatus);
    } else {
        // Update the existing browser selector
        for (const [browser, available] of Object.entries(browserStatus)) {
            const option = browserSelector.querySelector(`[data-browser="${browser}"]`);
            
            if (option) {
                if (!available) {
                    option.classList.add('disabled');
                    option.setAttribute('title', `${browser.toUpperCase()} is not available`);
                } else {
                    option.classList.remove('disabled');
                    option.setAttribute('title', `Use ${browser.toUpperCase()} browser`);
                }
            }
        }
    }
}

// Create the browser selector UI
function createBrowserSelector(browserStatus) {
    // Create the browser selector container
    const selectorContainer = document.createElement('div');
    selectorContainer.className = 'browser-selector-container';
    selectorContainer.innerHTML = `
        <label for="browser-selector">Select Dark Web Browser:</label>
        <div id="browser-selector" class="browser-selector">
            <div class="browser-option ${browserStatus.tor ? '' : 'disabled'}" data-browser="tor" title="${browserStatus.tor ? 'Use TOR browser' : 'TOR is not available'}">
                <i class="fas fa-globe"></i> TOR
            </div>
            <div class="browser-option ${browserStatus.i2p ? '' : 'disabled'}" data-browser="i2p" title="${browserStatus.i2p ? 'Use I2P browser' : 'I2P is not available'}">
                <i class="fas fa-project-diagram"></i> I2P
            </div>
            <div class="browser-option ${browserStatus.freenet ? '' : 'disabled'}" data-browser="freenet" title="${browserStatus.freenet ? 'Use Freenet browser' : 'Freenet is not available'}">
                <i class="fas fa-server"></i> Freenet
            </div>
            <div class="browser-option ${browserStatus.tails ? '' : 'disabled'}" data-browser="tails" title="${browserStatus.tails ? 'Use TAILS browser' : 'TAILS is not available'}">
                <i class="fas fa-user-secret"></i> TAILS
            </div>
        </div>
    `;
    
    // Insert the selector before the crawl form
    const crawlForm = document.getElementById('crawl-form');
    crawlForm.parentNode.insertBefore(selectorContainer, crawlForm);
}

// Set up browser selection event listeners
function setupBrowserSelectors() {
    // Use event delegation since the browser selector might be created dynamically
    document.addEventListener('click', function(event) {
        const option = event.target.closest('.browser-option');
        
        if (option && !option.classList.contains('disabled')) {
            // Remove active class from all options
            document.querySelectorAll('.browser-option').forEach(opt => {
                opt.classList.remove('active');
            });
            
            // Add active class to the clicked option
            option.classList.add('active');
            
            // Store the selected browser
            window.selectedBrowser = option.dataset.browser;
            
            // Show toast notification
            showToast(`Selected ${option.dataset.browser.toUpperCase()} browser`, 'success');
        }
    });
}

// Function to get the currently selected browser
function getSelectedBrowser() {
    return window.selectedBrowser || 'tor'; // Default to TOR
}