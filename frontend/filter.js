// Filter functionality for search results
function filterResults(results, filters) {
    if (!results || results.length === 0) return [];
    
    let filteredResults = [...results];
    
    // Filter by risk level
    if (filters.minRisk !== undefined) {
        filteredResults = filteredResults.filter(item => item.risk_score >= filters.minRisk);
    }
    
    if (filters.maxRisk !== undefined) {
        filteredResults = filteredResults.filter(item => item.risk_score <= filters.maxRisk);
    }
    
    // Filter by country
    if (filters.country) {
        filteredResults = filteredResults.filter(item => 
            item.country && item.country.toLowerCase() === filters.country.toLowerCase()
        );
    }
    
    // Filter by seller status
    if (filters.isSeller !== undefined) {
        filteredResults = filteredResults.filter(item => item.is_seller === filters.isSeller);
    }
    
    // Filter by date range
    if (filters.fromDate) {
        const fromDate = new Date(filters.fromDate);
        filteredResults = filteredResults.filter(item => {
            const itemDate = new Date(item.date_detected);
            return itemDate >= fromDate;
        });
    }
    
    if (filters.toDate) {
        const toDate = new Date(filters.toDate);
        filteredResults = filteredResults.filter(item => {
            const itemDate = new Date(item.date_detected);
            return itemDate <= toDate;
        });
    }
    
    // Filter by search term
    if (filters.searchTerm) {
        const term = filters.searchTerm.toLowerCase();
        filteredResults = filteredResults.filter(item => 
            (item.title && item.title.toLowerCase().includes(term)) || 
            (item.description && item.description.toLowerCase().includes(term)) ||
            (item.url && item.url.toLowerCase().includes(term))
        );
    }
    
    // Legacy filter support
    if (filters.keywords) {
        const keywords = filters.keywords.toLowerCase();
        filteredResults = filteredResults.filter(item => 
            (item.description && item.description.toLowerCase().includes(keywords))
        );
    }
    
    if (filters.geoLocation) {
        const geoLocation = filters.geoLocation.toLowerCase();
        filteredResults = filteredResults.filter(item => 
            (item.country && item.country.toLowerCase().includes(geoLocation))
        );
    }
    
    return filteredResults;
}
