// Web Archive functionality
document.getElementById('archive-form').addEventListener('submit', async (event) => {
    event.preventDefault();
    
    // Check backend connection before proceeding
    if (!backendConnected) {
        const connected = await checkBackendConnection();
        if (!connected) {
            showToast('Cannot connect to backend server. Please check your connection.', 'error');
            return;
        }
    }
    
    const archiveUrl = document.getElementById('archive-url').value;
    
    // Show loading state
    const resultsDiv = document.getElementById('archive-results');
    resultsDiv.innerHTML = '<p>Checking archives... <i class="fas fa-spinner fa-spin"></i></p>';
    
    const data = {
        url: archiveUrl
    };
    
    const results = await fetchData('/web-archive', data);
    
    if (results) {
        if (results.error) {
            resultsDiv.innerHTML = `<p class="error">Error: ${results.error}</p>`;
            return;
        }
        
        if (results.status === 'not found') {
            resultsDiv.innerHTML = `
                <div class="result-item">
                    <h3>No Archives Found</h3>
                    <p>No archived versions of ${archiveUrl} were found.</p>
                </div>
            `;
            return;
        }
        
        // Render archive results
        resultsDiv.innerHTML = `
            <div class="result-item">
                <h3>Archive Results for ${archiveUrl}</h3>
                <p><strong>Latest Archive:</strong> <a href="${results.url}" target="_blank">${results.url}</a></p>
                <p><strong>Total Snapshots:</strong> ${results.total_snapshots}</p>
                
                ${results.snapshots && results.snapshots.length > 0 ? `
                    <h4>Available Snapshots:</h4>
                    <ul class="archive-list">
                        ${results.snapshots.map(snapshot => `
                            <li>
                                <a href="${snapshot.url}" target="_blank">
                                    ${new Date(snapshot.timestamp.slice(0, 4) + '-' + 
                                               snapshot.timestamp.slice(4, 6) + '-' + 
                                               snapshot.timestamp.slice(6, 8)).toLocaleDateString()} 
                                    (${snapshot.timestamp.slice(8, 10)}:${snapshot.timestamp.slice(10, 12)})
                                </a>
                            </li>
                        `).join('')}
                    </ul>
                ` : ''}
            </div>
        `;
    }
});