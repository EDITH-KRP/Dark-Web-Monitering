function filterResults(results, keywords, geoLocation) {
    return results.filter(result => {
        const matchesKeyword = result.description.includes(keywords);
        const matchesGeoLocation = result.location.includes(geoLocation);
        return matchesKeyword && matchesGeoLocation;
    });
}


document.getElementById('filter-form').addEventListener('submit', async (event) => {
    event.preventDefault();

    const keywords = document.getElementById('keywords').value;
    const geoLocation = document.getElementById('geo-location').value;

    const filteredResults = filterResults(results, keywords, geoLocation);

   
    const resultsDiv = document.getElementById('filtered-results');
    resultsDiv.innerHTML = filteredResults.map(result => `
        <div>
            <strong>Title:</strong> ${result.title} <br>
            <strong>Description:</strong> ${result.description} <br>
            <strong>Location:</strong> ${result.location}
        </div>
    `).join('');
});
