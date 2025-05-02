// Timeline view functionality
const dateFilter = document.getElementById('date-filter');
const dateFilterValue = document.getElementById('date-filter-value');

// Update the date filter value display
dateFilter.addEventListener('input', () => {
    const days = dateFilter.value;
    dateFilterValue.textContent = days === '1' ? 'Last 1 day' : `Last ${days} days`;
    
    // Filter results based on date
    if (crawlResults.length > 0) {
        updateTimelineView(crawlResults);
    }
});

// Function to update timeline view based on date filter
function updateTimelineView(results) {
    console.log('Updating timeline view with results:', results);
    
    if (!results || !Array.isArray(results) || results.length === 0) {
        console.warn('No results to display in timeline');
        const timelineResults = document.getElementById('timeline-results');
        timelineResults.innerHTML = '<p>No results available for timeline view.</p>';
        return;
    }
    
    const daysFilter = parseInt(dateFilter.value) || 30; // Default to 30 days if invalid
    const timelineResults = document.getElementById('timeline-results');
    
    // Calculate the cutoff date
    const cutoffDate = new Date();
    cutoffDate.setDate(cutoffDate.getDate() - daysFilter);
    
    // Filter results by date
    const filteredResults = results.filter(result => {
        try {
            if (!result.date_detected) {
                console.warn('Result missing date_detected:', result);
                return false;
            }
            const detectionDate = new Date(result.date_detected);
            if (isNaN(detectionDate.getTime())) {
                console.warn('Invalid date format:', result.date_detected);
                return false;
            }
            return detectionDate >= cutoffDate;
        } catch (error) {
            console.error('Error filtering result by date:', error, result);
            return false;
        }
    });
    
    console.log(`Filtered timeline results: ${filteredResults.length} of ${results.length} items`);
    
    // Sort by date (newest first)
    try {
        filteredResults.sort((a, b) => {
            return new Date(b.date_detected) - new Date(a.date_detected);
        });
    } catch (error) {
        console.error('Error sorting results by date:', error);
    }
    
    // Render timeline
    if (filteredResults.length === 0) {
        timelineResults.innerHTML = '<p>No results found in the selected time period.</p>';
        return;
    }
    
    try {
        timelineResults.innerHTML = filteredResults.map(result => {
            // Handle missing or invalid fields
            const title = result.title || 'Untitled';
            const description = result.description || result.content_sample || 'No description available';
            const dateDetected = result.date_detected || new Date().toISOString().split('T')[0];
            const riskScore = typeof result.risk_score === 'number' ? result.risk_score : 0;
            const country = result.country || 'Unknown';
            
            return `
                <div class="result-item">
                    <div class="timeline-date">${dateDetected}</div>
                    <h3>${title}</h3>
                    <p>${description.substring(0, 100)}${description.length > 100 ? '...' : ''}</p>
                    <div class="result-meta">
                        <div>
                            <strong>Risk Score:</strong> ${formatRiskScore(riskScore)}
                        </div>
                        <div>
                            <strong>Country:</strong> ${getCountryFlag(country)} ${country}
                        </div>
                    </div>
                </div>
            `;
        }).join('');
    } catch (error) {
        console.error('Error rendering timeline:', error);
        timelineResults.innerHTML = `<p>Error rendering timeline: ${error.message}</p>`;
    }
}