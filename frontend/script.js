// API URL - automatically detect the backend URL
const API_URL = (() => {
    // Default to localhost:5000 if running locally
    const defaultUrl = 'http://localhost:5000';
    
    // Check if we're in a production environment
    if (window.location.hostname !== 'localhost' && window.location.hostname !== '127.0.0.1') {
        // In production, assume API is on same host but different port or path
        // You can customize this based on your deployment setup
        return `${window.location.protocol}//${window.location.hostname}:5000`;
    }
    
    console.log('Using backend API URL:', defaultUrl);
    return defaultUrl;
})();

// Global variables to store crawl results
let crawlResults = [];
let highRiskDetected = false;
let backendConnected = false;

// Define a function to replace getAdvancedFilterValues since we removed advanced-filters.js
function getAdvancedFilterValues() {
    return {}; // Return empty object since we removed advanced filters
}

// Helper function to show toast notifications
function showToast(message, type = 'success') {
    const toastContainer = document.getElementById('toast-container');
    const toast = document.createElement('div');
    toast.className = `toast toast-${type}`;
    
    let icon = '';
    if (type === 'success') icon = '<i class="fas fa-check-circle"></i>';
    else if (type === 'error') icon = '<i class="fas fa-exclamation-circle"></i>';
    else if (type === 'warning') icon = '<i class="fas fa-exclamation-triangle"></i>';
    
    toast.innerHTML = `${icon}<span>${message}</span>`;
    toastContainer.appendChild(toast);
    
    // Remove toast after 3 seconds
    setTimeout(() => {
        toast.remove();
    }, 3000);
}

// Helper function to format risk score with color coding
function formatRiskScore(score) {
    // Handle invalid scores
    if (score === undefined || score === null || isNaN(score)) {
        console.warn('Invalid risk score:', score);
        score = 0;
    }
    
    // Ensure score is a number
    score = Number(score);
    
    let riskClass = 'risk-low';
    if (score >= 90) {
        riskClass = 'risk-high';
    } else if (score >= 60) {
        riskClass = 'risk-medium';
    }
    
    return `<span class="risk-score ${riskClass}">${Math.round(score)}</span>`;
}

// Helper function to get country flag
function getCountryFlag(country) {
    // Handle invalid country
    if (!country || typeof country !== 'string') {
        console.warn('Invalid country:', country);
        country = 'Unknown';
    }
    
    // Map country names to ISO country codes for flag icons
    const countryCodeMap = {
        'USA': 'us',
        'United States': 'us',
        'Russia': 'ru',
        'Mexico': 'mx',
        'Colombia': 'co',
        'Canada': 'ca',
        'Australia': 'au',
        'United Kingdom': 'gb',
        'Germany': 'de',
        'Netherlands': 'nl',
        'China': 'cn',
        'Japan': 'jp',
        'Brazil': 'br',
        'Sweden': 'se',
        'Switzerland': 'ch',
        'Panama': 'pa',
        'Romania': 'ro',
        'Unknown': 'un'
    };
    
    const code = countryCodeMap[country] || 'un'; // Default to UN flag if country not found
    return `<span class="fi fi-${code} country-flag"></span>`;
}

// Check backend connection
async function checkBackendConnection() {
    try {
        console.log('Checking backend connection at:', `${API_URL}/`);
        
        const controller = new AbortController();
        const timeoutId = setTimeout(() => controller.abort(), 5000); // 5 second timeout
        
        const response = await fetch(`${API_URL}/`, {
            signal: controller.signal,
            mode: 'cors', // Ensure CORS is enabled
            headers: {
                'Accept': 'application/json'
            }
        });
        
        clearTimeout(timeoutId);
        
        console.log('Backend response status:', response.status);
        backendConnected = response.ok;
        
        // Update UI to show connection status
        const vpnStatus = document.getElementById('vpn-status');
        if (backendConnected) {
            showToast('Connected to backend server', 'success');
            console.log('Backend connection successful');
            
            // Now that we're connected, check VPN status
            checkVpnStatus();
        } else {
            showToast(`Failed to connect to backend server. Status: ${response.status}`, 'error');
            console.error('Backend connection failed with status:', response.status);
            
            // Update VPN status to show backend connection issue
            if (vpnStatus) {
                vpnStatus.innerHTML = `
                    <span class="vpn-indicator error"></span>
                    <span class="vpn-text">Backend: Disconnected (${response.status})</span>
                `;
            }
        }
        
        return backendConnected;
    } catch (error) {
        console.error('Backend connection error:', error);
        backendConnected = false;
        
        // Update UI to show connection error
        const vpnStatus = document.getElementById('vpn-status');
        if (vpnStatus) {
            vpnStatus.innerHTML = `
                <span class="vpn-indicator error"></span>
                <span class="vpn-text">Backend: Error (${error.name === 'AbortError' ? 'Timeout' : error.message})</span>
            `;
        }
        
        showToast(`Backend connection error: ${error.name === 'AbortError' ? 'Connection timeout' : error.message}`, 'error');
        return false;
    }
}

// Fetch data from API
async function fetchData(endpoint, data = {}, method = 'POST') {
    try {
        // Check backend connection first if not already connected
        if (!backendConnected) {
            console.log('Backend not connected, attempting to connect...');
            const connected = await checkBackendConnection();
            if (!connected) {
                throw new Error('Backend server is not available');
            }
        }
        
        const fullUrl = `${API_URL}${endpoint}`;
        console.log(`Fetching data from ${fullUrl} with method ${method}`);
        
        const options = {
            method: method,
            headers: {
                'Content-Type': 'application/json',
                'Accept': 'application/json'
            },
            mode: 'cors' // Ensure CORS is enabled
        };
        
        // Add body for POST requests
        if (method === 'POST') {
            options.body = JSON.stringify(data);
            console.log('Request payload:', data);
        }
        
        // Set up timeout - increase to 30 seconds for crawling operations
        const controller = new AbortController();
        const timeoutDuration = endpoint.includes('crawl') ? 30000 : 10000; // 30 seconds for crawl, 10 for others
        console.log(`Setting timeout of ${timeoutDuration/1000} seconds for ${endpoint}`);
        const timeoutId = setTimeout(() => {
            console.warn(`Request to ${fullUrl} timed out after ${timeoutDuration/1000} seconds`);
            controller.abort();
        }, timeoutDuration);
        options.signal = controller.signal;
        
        const response = await fetch(fullUrl, options);
        clearTimeout(timeoutId);
        
        console.log(`Response status: ${response.status}`);
        
        if (!response.ok) {
            throw new Error(`API error: ${response.status}`);
        }
        
        const responseData = await response.json();
        console.log('Response data:', responseData);
        return responseData;
    } catch (error) {
        console.error('Error fetching data:', error);
        showToast(`Error: ${error.name === 'AbortError' ? 'Request timeout' : error.message}`, 'error');
        return null;
    }
}

// Check for high risk items and trigger alert
function checkForHighRisk(results) {
    const highRiskItems = results.filter(item => item.risk_score >= 80);
    
    if (highRiskItems.length > 0) {
        // Show alert badge
        const alertBadge = document.getElementById('alert-badge');
        alertBadge.classList.remove('hidden');
        alertBadge.classList.add('blinking');
        
        // Set global flag
        highRiskDetected = true;
        
        // Show toast notification
        showToast('High risk activity detected!', 'warning');
    }
}

// Render crawl results with animations
function renderCrawlResults(results) {
    const resultsDiv = document.getElementById('crawl-results');
    
    if (!results || results.length === 0) {
        resultsDiv.innerHTML = '<p>No results found.</p>';
        return;
    }
    
    console.log('Rendering results:', results);
    
    resultsDiv.innerHTML = results.map((result, index) => {
        // Handle missing fields with default values
        const title = result.title || 'Untitled';
        const description = result.description || result.content_sample || 'No description available';
        const url = result.url || '#';
        const riskScore = typeof result.risk_score === 'number' ? result.risk_score : 0;
        const country = result.country || 'Unknown';
        const isSeller = result.is_seller || false;
        const dateDetected = result.date_detected || new Date().toISOString().split('T')[0];
        const archiveLink = result.archive_link || '#';
        
        return `
            <div class="result-item" style="--animation-order: ${index}">
                <h3>${title}</h3>
                <p>${description}</p>
                <p><strong>URL:</strong> <a href="#" class="onion-link">${url}</a></p>
                
                <div class="result-meta">
                    <div>
                        <strong>Risk Score:</strong> ${formatRiskScore(riskScore)}
                    </div>
                    <div>
                        <strong>Country:</strong> ${getCountryFlag(country)} ${country}
                    </div>
                    <div>
                        ${isSeller ? '<span class="seller-badge"><i class="fas fa-store"></i> Seller</span>' : ''}
                    </div>
                    <div>
                        <strong>Detected:</strong> ${dateDetected}
                    </div>
                </div>
                
                <div class="result-actions">
                    <a href="${archiveLink}" target="_blank" class="archive-link">
                        <i class="fas fa-history"></i> View Archive
                    </a>
                </div>
            </div>
        `;
    }).join('');
    
    // Add staggered animation to results
    const resultItems = document.querySelectorAll('.result-item');
    resultItems.forEach((item, index) => {
        // Set a delay based on the index
        setTimeout(() => {
            item.style.animation = 'fade-in 0.5s ease-out forwards';
        }, index * 100);
    });
    
    // Check for high risk items
    checkForHighRisk(results);
}

// Function to manually test backend connection
async function testBackendConnection() {
    showToast('Testing backend connection...', 'info');
    console.log('Manually testing backend connection...');
    
    try {
        // Try a direct fetch with no timeout
        const response = await fetch(`${API_URL}/`);
        const text = await response.text();
        
        console.log('Backend response:', response.status, text);
        
        if (response.ok) {
            showToast('Backend connection successful!', 'success');
            backendConnected = true;
            
            // Update VPN status
            const vpnStatus = document.getElementById('vpn-status');
            if (vpnStatus) {
                vpnStatus.innerHTML = `
                    <span class="vpn-indicator success"></span>
                    <span class="vpn-text">Backend: Connected</span>
                `;
            }
            
            // Check VPN status
            checkVpnStatus();
        } else {
            showToast(`Backend connection failed: ${response.status}`, 'error');
        }
    } catch (error) {
        console.error('Manual backend connection test failed:', error);
        showToast(`Backend connection error: ${error.message}`, 'error');
    }
}

// Initialize the application
document.addEventListener('DOMContentLoaded', async () => {
    console.log('Dark Web Monitoring Tool initializing...');
    console.log(`Backend API URL: ${API_URL}`);
    
    // Add a test connection button
    const headerControls = document.querySelector('.header-controls');
    if (headerControls) {
        const testButton = document.createElement('button');
        testButton.className = 'test-backend-button';
        testButton.innerHTML = '<i class="fas fa-sync-alt"></i> Test Backend';
        testButton.addEventListener('click', testBackendConnection);
        headerControls.appendChild(testButton);
    }
    
    // Check backend connection
    await checkBackendConnection();
    
    // Add event listener for the mock data button
    const mockDataButton = document.getElementById('load-mock-data');
    if (mockDataButton) {
        mockDataButton.addEventListener('click', async () => {
            console.log('Mock data button clicked');
            
            // Disable the button while loading
            mockDataButton.disabled = true;
            mockDataButton.innerHTML = '<i class="fas fa-spinner fa-spin"></i> Loading...';
            
            try {
            
            // Get keywords from the form
            const keywords = document.getElementById('keywords').value || 'drugs,bitcoin,weapons';
            
            // Show loading state
            const resultsDiv = document.getElementById('crawl-results');
            resultsDiv.innerHTML = '<p>Loading test data... <i class="fas fa-spinner fa-spin"></i></p>';
            
            try {
                // Try to fetch mock data from the backend
                const mockDataUrl = `${API_URL}/mock-data?keywords=${encodeURIComponent(keywords)}&num_items=15`;
                console.log('Fetching mock data from:', mockDataUrl);
                
                const response = await fetch(mockDataUrl);
                let mockResults;
                
                if (response.ok) {
                    mockResults = await response.json();
                    console.log('Fetched mock results from backend:', mockResults);
                    showToast('Using mock data from backend', 'info');
                } else {
                    // Fall back to client-side mock data generation
                    mockResults = generateMockResults(keywords, 10);
                    console.log('Generated mock results client-side:', mockResults);
                    showToast('Using client-side mock data (backend not available)', 'warning');
                }
                
                // Store results globally
                crawlResults = mockResults;
                
                // Render results
                renderCrawlResults(mockResults);
                
                // Update timeline view
                updateTimelineView(mockResults);
            } catch (error) {
                console.error('Error loading mock data:', error);
                showToast(`Error: ${error.message}`, 'error');
                resultsDiv.innerHTML = `<p class="error">Error loading mock data: ${error.message}</p>`;
            } finally {
                // Re-enable the button
                mockDataButton.disabled = false;
                mockDataButton.innerHTML = '<i class="fas fa-vial"></i> Load Test Data';
            }
        });
    }
    
    // Add a direct crawl with mock data button
    const submitButton = document.querySelector('#crawl-form button[type="submit"]');
    if (submitButton && submitButton.parentNode) {
        const mockCrawlButton = document.createElement('button');
        mockCrawlButton.type = 'button';
        mockCrawlButton.className = 'secondary-button mock-crawl-button';
        mockCrawlButton.innerHTML = '<i class="fas fa-bolt"></i> Quick Crawl';
        mockCrawlButton.title = 'Perform a quick crawl using mock data';
        
        // Add it after the submit button
        submitButton.parentNode.appendChild(mockCrawlButton);
        
        // Add event listener
        mockCrawlButton.addEventListener('click', async () => {
            console.log('Quick crawl button clicked');
            
            // Get form values
            const keywords = document.getElementById('keywords').value || 'drugs,bitcoin,weapons';
            const geoLocation = document.getElementById('geo-location').value || 'USA';
            
            // Show loading state
            const resultsDiv = document.getElementById('crawl-results');
            resultsDiv.innerHTML = '<p>Performing quick crawl... <i class="fas fa-spinner fa-spin"></i></p>';
            
            // Disable the button while loading
            mockCrawlButton.disabled = true;
            mockCrawlButton.innerHTML = '<i class="fas fa-spinner fa-spin"></i> Crawling...';
            
            try {
                // Prepare data for API request with mock data flag
                const data = {
                    keywords: keywords,
                    geo_location: geoLocation,
                    browser_type: 'tor',
                    max_pages: 5,
                    use_mock_data: true // Use mock data for quick response
                };
                
                // Send request to the crawl endpoint
                const results = await fetchData('/crawl', data);
                
                if (results) {
                    // Store results globally
                    crawlResults = results;
                    
                    // Render results
                    renderCrawlResults(results);
                    
                    // Update timeline view
                    updateTimelineView(results);
                    
                    showToast('Quick crawl completed successfully', 'success');
                }
            } catch (error) {
                console.error('Error performing quick crawl:', error);
                showToast(`Error: ${error.message}`, 'error');
                resultsDiv.innerHTML = `<p class="error">Error performing quick crawl: ${error.message}</p>`;
            } finally {
                // Re-enable the button
                mockCrawlButton.disabled = false;
                mockCrawlButton.innerHTML = '<i class="fas fa-bolt"></i> Quick Crawl';
            }
        });
    }
});

// Handle crawl form submission - moved inside DOMContentLoaded to ensure form exists
document.addEventListener('DOMContentLoaded', () => {
    console.log('Setting up crawl form event listener');
    const crawlForm = document.getElementById('crawl-form');
    
    if (!crawlForm) {
        console.error('Crawl form not found in the DOM!');
        return;
    }
    
    // Add a click event listener to the Start Crawling button
    const startCrawlButton = document.getElementById('start-crawl-button');
    if (startCrawlButton) {
        console.log('Setting up start crawl button event listener');
        startCrawlButton.addEventListener('click', function(event) {
            // Trigger the form submission when the button is clicked
            crawlForm.dispatchEvent(new Event('submit'));
        });
    } else {
        console.error('Start crawl button not found in the DOM!');
    }
    
    // Add a submit handler to the form
    crawlForm.onsubmit = async function(event) {
        // This is critical - prevent the default form submission which would reload the page
        event.preventDefault();
        event.stopPropagation();
        
        console.log('Crawl form submitted!');
        
        // Disable the submit button to prevent multiple submissions
        const submitButton = crawlForm.querySelector('button[type="submit"]');
        if (submitButton) {
            submitButton.disabled = true;
            submitButton.innerHTML = '<i class="fas fa-spinner fa-spin"></i> Crawling...';
        }
        
        // Check backend connection before proceeding
        if (!backendConnected) {
            console.log('Backend not connected, attempting to connect...');
            const connected = await checkBackendConnection();
            if (!connected) {
                showToast('Cannot connect to backend server. Please check your connection.', 'error');
                if (submitButton) {
                    submitButton.disabled = false;
                    submitButton.innerHTML = '<i class="fas fa-search"></i> Start Crawling';
                }
                return;
            }
        }
    
    const keywords = document.getElementById('keywords').value;
    const geoLocation = document.getElementById('geo-location').value;
    
    // Reset alert badge
    const alertBadge = document.getElementById('alert-badge');
    alertBadge.classList.add('hidden');
    alertBadge.classList.remove('blinking');
    highRiskDetected = false;
    
    // Show loading state
    const resultsDiv = document.getElementById('crawl-results');
    resultsDiv.innerHTML = '<p>Crawling the dark web... <i class="fas fa-spinner fa-spin"></i></p>';
    
    // Get selected browser
    const selectedBrowser = getSelectedBrowser();
    
    // Prepare data for API request
    const data = {
        keywords: keywords,
        geo_location: geoLocation,
        browser_type: selectedBrowser,
        max_pages: 10, // Limit pages for faster response
        use_mock_data: false // Set to true to use mock data instead of real crawling
    };
    
    // Determine which endpoint to use based on whether a specific browser is selected
    let endpoint = '/crawl';
    if (selectedBrowser && selectedBrowser !== 'tor') {
        endpoint = '/crawl-with-browser';
        showToast(`Using ${selectedBrowser.toUpperCase()} browser for crawling`, 'info');
    }
    
    try {
        console.log('Sending crawl request to endpoint:', endpoint);
        console.log('Request data:', data);
        
        const results = await fetchData(endpoint, data);
        
        console.log('Received crawl results:', results);
        
        if (results) {
            if (results.error) {
                showToast(`Error: ${results.error}`, 'error');
                resultsDiv.innerHTML = `<p class="error">Error: ${results.error}</p>`;
            } else if (!Array.isArray(results)) {
                // Check if results is an array
                showToast('Invalid response format from server', 'error');
                console.error('Expected array but got:', typeof results, results);
                resultsDiv.innerHTML = '<p class="error">Invalid response format from server</p>';
            } else if (results.length === 0) {
                // Check if results array is empty
                showToast('No results found', 'info');
                resultsDiv.innerHTML = '<p>No results found. Try different keywords or check your connection.</p>';
            } else {
                // Store results globally
                crawlResults = results;
                
                // Add missing fields if needed
                crawlResults = crawlResults.map(result => {
                    // Ensure all required fields exist
                    return {
                        title: result.title || 'Untitled',
                        description: result.description || result.content_sample || 'No description available',
                        url: result.url || '#',
                        risk_score: result.risk_score || 0,
                        country: result.country || 'Unknown',
                        is_seller: result.is_seller || false,
                        date_detected: result.date_detected || new Date().toISOString().split('T')[0],
                        archive_link: result.archive_link || '#',
                        ...result
                    };
                });
                
                // Render results
                renderCrawlResults(crawlResults);
                
                // Update timeline view
                updateTimelineView(crawlResults);
                
                showToast('Crawl completed successfully!', 'success');
            }
        } else {
            showToast('No response from server', 'error');
            resultsDiv.innerHTML = '<p class="error">No response from server. Please try again.</p>';
        }
    } catch (error) {
        console.error('Error during crawl:', error);
        showToast(`Error: ${error.message}`, 'error');
        resultsDiv.innerHTML = `<p class="error">Error during crawl: ${error.message}</p>`;
    } finally {
        // Re-enable the submit button
        if (submitButton) {
            submitButton.disabled = false;
            submitButton.innerHTML = '<i class="fas fa-search"></i> Start Crawling';
        }
    }
    });
    
    // We don't need a separate click handler for the submit button anymore
    // The form's submit handler will take care of everything
    // This prevents duplicate submissions and potential race conditions
    
    // Function to generate mock results for testing
    function generateMockResults(keywords, count = 10) {
        const mockResults = [];
        const domains = [
            'darkfailllnkf4vf.onion',
            'jaz45aabn5vkemy4jkg4mi4syheisqn2wn2n4fsuitpccdackjwxplad.onion',
            'zqktlwiuavvvqqt4ybvgvi7tyo4hjl5xgfuvpdf6otjiycgwqbym2qad.onion'
        ];
        
        const titles = [
            'Illegal Marketplace - Buy Drugs, Weapons, and More',
            'Hacking Services - Professional Hackers for Hire',
            'Counterfeit Documents - Passports, IDs, Credit Cards',
            'Bitcoin Mixer - Anonymize Your Cryptocurrency',
            'Stolen Data - Credit Cards, Bank Accounts, Personal Info'
        ];
        
        const descriptions = [
            'The largest marketplace for illegal goods on the dark web. Buy drugs, weapons, and more with Bitcoin.',
            'Professional hackers for hire. We can hack any website, social media account, or email.',
            'High quality counterfeit documents including passports, IDs, and credit cards.',
            'Anonymize your Bitcoin transactions with our secure mixing service.',
            'Fresh stolen data including credit cards, bank accounts, and personal information.'
        ];
        
        const countries = ['USA', 'Russia', 'Mexico', 'Colombia', 'Canada', 'Australia', 'United Kingdom', 'Germany'];
        
        for (let i = 0; i < count; i++) {
            const domain = domains[Math.floor(Math.random() * domains.length)];
            const title = titles[Math.floor(Math.random() * titles.length)];
            const description = descriptions[Math.floor(Math.random() * descriptions.length)];
            const country = countries[Math.floor(Math.random() * countries.length)];
            const riskScore = Math.floor(Math.random() * 70) + 30; // 30-100
            const isSeller = Math.random() > 0.5;
            
            // Generate a date within the last 30 days
            const date = new Date();
            date.setDate(date.getDate() - Math.floor(Math.random() * 30));
            const dateStr = date.toISOString().split('T')[0];
            
            mockResults.push({
                url: `http://${domain}/market/${i}`,
                title: title,
                description: description,
                content_sample: description.substring(0, 100) + '...',
                risk_score: riskScore,
                country: country,
                is_seller: isSeller,
                date_detected: dateStr,
                archive_link: `https://web.archive.org/web/http://${domain}/market/${i}`,
                found_keywords: keywords.split(',').filter(k => 
                    (title + description).toLowerCase().includes(k.trim().toLowerCase())
                )
            });
        }
        
        return mockResults;
    }
});
