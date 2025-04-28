document.getElementById('ip-form').addEventListener('submit', async (event) => {
    event.preventDefault();

    const darkWebUrl = document.getElementById('dark-web-url').value;

    const results = await fetchData(`/ip-details?url=${darkWebUrl}`);

    const resultsDiv = document.getElementById('ip-details-results');
    resultsDiv.innerHTML = `
        <div>
            <strong>IP Address:</strong> ${results.ip_address} <br>
            <strong>Country:</strong> ${results.country} <br>
            <strong>City:</strong> ${results.city} <br>
        </div>
    `;
});
