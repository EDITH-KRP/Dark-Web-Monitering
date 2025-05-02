// VPN status functionality
const vpnStatusElement = document.getElementById('vpn-status');

// Function to update VPN status display
function updateVpnStatusDisplay(status) {
    if (!status) return;
    
    const vpnText = vpnStatusElement.querySelector('.vpn-text');
    
    if (status.connected && status.is_masked) {
        vpnStatusElement.className = 'vpn-status vpn-connected';
        vpnText.innerHTML = `VPN Connected: ${status.ip_address} (${status.location})`;
    } else {
        vpnStatusElement.className = 'vpn-status vpn-disconnected';
        vpnText.innerHTML = 'VPN Disconnected';
    }
}

// Function to check VPN status
async function checkVpnStatus() {
    try {
        const response = await fetch(`${API_URL}/vpn-status`);
        if (!response.ok) {
            throw new Error(`API error: ${response.status}`);
        }
        
        const status = await response.json();
        updateVpnStatusDisplay(status);
        
        return status;
    } catch (error) {
        console.error('Error checking VPN status:', error);
        vpnStatusElement.className = 'vpn-status vpn-disconnected';
        vpnStatusElement.querySelector('.vpn-text').innerHTML = 'VPN Status: Error';
        return null;
    }
}

// Check backend connection first, then VPN status on page load
// This will be called from script.js after the backend connection check

// Check VPN status periodically
setInterval(() => {
    // Only check VPN if backend is connected
    if (backendConnected) {
        checkVpnStatus();
    } else {
        // Try to reconnect to backend
        checkBackendConnection();
    }
}, 30000); // Every 30 seconds