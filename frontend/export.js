// Export functionality
document.getElementById('export-csv').addEventListener('click', async () => {
    // Check backend connection before proceeding
    if (!backendConnected) {
        const connected = await checkBackendConnection();
        if (!connected) {
            showToast('Cannot connect to backend server. Please check your connection.', 'error');
            return;
        }
    }
    
    if (crawlResults.length === 0) {
        showToast('No data to export. Run a crawl first.', 'warning');
        return;
    }
    
    try {
        // Create a download link
        const link = document.createElement('a');
        link.href = `${API_URL}/export-csv`;
        link.download = 'dark_web_data.csv';
        document.body.appendChild(link);
        link.click();
        document.body.removeChild(link);
        
        showToast('CSV export started. Your download should begin shortly.', 'success');
    } catch (error) {
        console.error('Error exporting CSV:', error);
        showToast(`Error exporting CSV: ${error.message}`, 'error');
    }
});

document.getElementById('export-excel').addEventListener('click', async () => {
    // Check backend connection before proceeding
    if (!backendConnected) {
        const connected = await checkBackendConnection();
        if (!connected) {
            showToast('Cannot connect to backend server. Please check your connection.', 'error');
            return;
        }
    }
    
    if (crawlResults.length === 0) {
        showToast('No data to export. Run a crawl first.', 'warning');
        return;
    }
    
    try {
        // Create a download link
        const link = document.createElement('a');
        link.href = `${API_URL}/export-excel`;
        link.download = 'dark_web_data.xlsx';
        document.body.appendChild(link);
        link.click();
        document.body.removeChild(link);
        
        showToast('Excel export started. Your download should begin shortly.', 'success');
    } catch (error) {
        console.error('Error exporting Excel:', error);
        showToast(`Error exporting Excel: ${error.message}`, 'error');
    }
});