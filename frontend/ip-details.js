document.getElementById('ip-form').addEventListener('submit', async (event) => {
    event.preventDefault();
    
    // Check backend connection before proceeding
    if (!backendConnected) {
        const connected = await checkBackendConnection();
        if (!connected) {
            showToast('Cannot connect to backend server. Please check your connection.', 'error');
            return;
        }
    }
    
    const darkWebUrl = document.getElementById('dark-web-url').value;
    
    // Show loading state
    const resultsDiv = document.getElementById('ip-results');
    resultsDiv.innerHTML = '<p>Revealing IP details... <i class="fas fa-spinner fa-spin"></i></p>';
    
    const data = {
        url: darkWebUrl
    };
    
    const results = await fetchData('/ip-details', data);
    
    if (results) {
        if (results.error) {
            resultsDiv.innerHTML = `<p class="error">Error: ${results.error}</p>`;
            return;
        }
        
        // Render IP details
        resultsDiv.innerHTML = `
            <div class="result-item">
                <h3>IP Details for ${darkWebUrl}</h3>
                <p><strong>IP Address:</strong> ${results.ip_address}</p>
                <p><strong>Country:</strong> ${getCountryFlag(results.country)} ${results.country}</p>
                <p><strong>City:</strong> ${results.city}</p>
                <p><strong>Coordinates:</strong> ${results.latitude.toFixed(4)}, ${results.longitude.toFixed(4)}</p>
                <p><strong>ISP:</strong> ${results.isp}</p>
                
                <div class="result-meta">
                    <div>
                        <strong>TOR Exit Node:</strong> ${results.is_tor ? 'Yes' : 'No'}
                    </div>
                    <div>
                        <strong>Proxy:</strong> ${results.is_proxy ? 'Yes' : 'No'}
                    </div>
                    <div>
                        <strong>Datacenter:</strong> ${results.is_datacenter ? 'Yes' : 'No'}
                    </div>
                </div>
                
                <div class="map-container">
                    <img src="https://maps.googleapis.com/maps/api/staticmap?center=${results.latitude},${results.longitude}&zoom=10&size=400x200&markers=color:red%7C${results.latitude},${results.longitude}&key=YOUR_API_KEY" alt="Location Map" class="location-map">
                    <p class="map-note">Note: Map is a visual representation only</p>
                </div>
            </div>
        `;
    }
});
