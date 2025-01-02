document.addEventListener('DOMContentLoaded', function () {
    const refreshButton = document.getElementById('refreshButton');

    refreshButton.addEventListener('click', function () {
        const url = this.dataset.url;  // Get the URL from the data attribute
        const portfolio = document.getElementById('portfolioList').value;
        const csrfToken = document.querySelector('[name=csrfmiddlewaretoken]').value; // Get CSRF token

        console.log(`Portfolio Value: ${portfolio}`);
        console.log(url);

        // Fetch the updated data from the server
        fetch(url, {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json',
                'X-CSRFToken': csrfToken  // Include CSRF token in headers
            },
            body: JSON.stringify({ 'portfolio': portfolio })  // Send data as JSON
        })
        .then(response => response.text())  // Assuming the response is HTML content
        .then(data => {
            // Update the HTML content
            const portfolioDisplay = document.getElementById('portfolioDisplay');
            portfolioDisplay.innerHTML = data;

            // After updating the content, fetch chart data for each portfolio
            const portfolioIds = Array.from(document.querySelectorAll('[data-portfolio-id]'))
                .map(el => el.dataset.portfolioId); // Collect all portfolio IDs from the updated content

            portfolioIds.forEach(portfolioId => {
                // Fetch industry totals for the current portfolio
                // Fetch data for the first chart
                fetch(`/charts/portfolio/${portfolioId}/industry/`)
                .then(response => response.json())
                .then(data => {
                    const chartId1 = `portfolioChart-${portfolioId}-1`;
                    const labels1 = data.industry_totals.map(item => item.asset__industry || "Unknown");
                    const values1 = data.industry_totals.map(item => item.total_holding_value);

                    // Render the first chart
                    createChart(chartId1, labels1, values1,'Industry','doughnut');
                })
                .catch(error => console.error(`Error fetching data for chart 1 of portfolio ${portfolioId}:`, error));

            // Fetch data for the asset weighting chart
                fetch(`/charts/portfolio/${portfolioId}/weighting/`) // Adjusted endpoint
                .then(response => {
                    if (!response.ok) {
                        throw new Error(`HTTP error! Status: ${response.status}`);
                    }
                    return response.json();
                })
                .then(data => {
                    const chartId2 = `portfolioChart-${portfolioId}-2`;

                    // Extract labels (tickers) and values (weighting percentages)
                    const labels2 = data.assets.map(asset => asset.ticker || "Unknown");
                    const values2 = data.assets.map(asset => asset.weighting);

                    // Render the asset weighting chart
                    createChart(chartId2, labels2, values2,'Asset Allocation','polarArea');
                })
                .catch(error => console.error(`Error fetching data for chart 2 of portfolio ${portfolioId}:`, error));



            });
        })
        .catch(error => {
            console.error('Error:', error);
        });






    });
});

// Reusable function to create a pie chart
function createChart(chartId, labels, data,chartTitle,chartType) {
    const ctx = document.getElementById(chartId).getContext('2d');
    return new Chart(ctx, {
        type: chartType,
        data: {
            labels: labels,
            datasets: [{
                data: data,
                backgroundColor: [
                    '#FF6384',
                    '#36A2EB',
                    '#FFCE56',
                    '#4BC0C0',
                    '#9966FF',
                    '#FF9F40'
                ],
                hoverOffset: 4
            }]
        },
        options: {

            layout: {
                padding: {
                    bottom: 20
                }
            },

            events: ['mousemove', 'mouseout', 'click', 'touchstart', 'touchmove'],

            responsive: true,
            plugins: {
                legend: {
                    position: 'bottom',
                    display: true
                },
                tooltip: {
                    // Tooltip will only receive click events
                    events: ['mousemove', 'mouseout', 'click', 'touchstart', 'touchmove']
                  },
                title: {
                display: true,
                text: chartTitle //'Custom Chart Title'
            }
                

                
            },
        }
    });
}


// // Reusable function to create a pie chart
// function createBarChart(chartId, labels, data) {
//     const ctx = document.getElementById(chartId).getContext('2d');
//     return new Chart(ctx, {
//         type: 'polarArea',
//         data: {
//             labels: labels,
//             datasets: [{
//                 data: data,
//                 backgroundColor: [
//                     '#FF6384',
//                     '#36A2EB',
//                     '#FFCE56',
//                     '#4BC0C0',
//                     '#9966FF',
//                     '#FF9F40'
//                 ],
//                 hoverOffset: 4
//             }]
//         },
//         options: {

//             layout: {
//                 padding: {
//                     bottom: 20
//                 }
//             },

//             events: ['mousemove', 'mouseout', 'click', 'touchstart', 'touchmove'],

//             responsive: true,
//             plugins: {
//                 legend: {
//                     position: 'bottom',
//                     display: true
//                 },
//                 tooltip: {
//                     // Tooltip will only receive click events
//                     events: ['mousemove', 'mouseout', 'click', 'touchstart', 'touchmove']
//                   }
//             },
//         }
//     });
// }
