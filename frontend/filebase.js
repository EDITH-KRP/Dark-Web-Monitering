// Filebase upload functionality
document.getElementById('upload-filebase').addEventListener('click', async () => {
    // Check backend connection before proceeding
    if (!backendConnected) {
        const connected = await checkBackendConnection();
        if (!connected) {
            showToast('Cannot connect to backend server. Please check your connection.', 'error');
            return;
        }
    }
    
    if (crawlResults.length === 0) {
        showToast('No data to upload. Run a crawl first.', 'warning');
        return;
    }
    
    // Show loading toast
    showToast('Uploading to decentralized storage...', 'info');
    
    try {
        // Use the fetchData function we defined in script.js
        const result = await fetchData('/upload-to-filebase', {
            data_type: 'crawl_results'
        });
        
        if (result && result.success) {
            showToast(`${result.message} CID: ${result.cid}`, 'success');
        } else if (result) {
            showToast(`Upload failed: ${result.message || 'Unknown error'}`, 'error');
        }
    } catch (error) {
        console.error('Error uploading to Filebase:', error);
        showToast(`Error uploading to Filebase: ${error.message}`, 'error');
    }
});