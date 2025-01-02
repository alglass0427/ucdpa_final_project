document.getElementById('addAssetButton').addEventListener('click', function() {
    const assetData = {
        ticker: document.getElementById('ticker').value,
        company_name: document.getElementById('companyName').value,
        industry: document.getElementById('industry').value
    };

    fetch('/add_asset', {
        method: 'POST',
        headers: {
            'Content-Type': 'application/json'
        },
        body: JSON.stringify(assetData)
    })
    .then(response => response.json())
    .then(data => {
        if (data.message) {
            console.log(data.message);  // Log success message
        } else {
            console.error(data.error);  // Log error message
        }
    })
    .catch(error => console.error('Error:', error));
});


