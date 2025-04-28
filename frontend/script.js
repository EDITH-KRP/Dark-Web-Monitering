async function fetchData(endpoint, data) {
    const response = await fetch(endpoint, {
        method: 'POST',
        headers: {
            'Content-Type': 'application/json',
        },
        body: JSON.stringify(data),
    });
    return await response.json();
}


document.getElementById('crawl-form').addEventListener('submit', async (event) => {
    event.preventDefault();

    const keywords = document.getElementById('keywords').value;
    const geoLocation = document.getElementById('geo-location').value;

    const data = {
        keywords: keywords,
        geo_location: geoLocation
    };

    const results = await fetchData('/crawl', data);

    const resultsDiv = document.getElementById('crawl-results');
    resultsDiv.innerHTML = results.map(result => `
        <div>
            <strong>Title:</strong> ${result.title} <br>
            <strong>Description:</strong> ${result.description} <br>
            <strong>URL:</strong> ${result.url}
        </div>
    `).join('');
});
