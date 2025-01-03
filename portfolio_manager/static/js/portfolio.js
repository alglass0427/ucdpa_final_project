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
        .then(response => response.json())  // Assuming the response is HTML content
        .then(data => {

            if (data.message) {
                console.log(data.message);
                let alert = document.getElementById('alert')
                // removeAlertClasses(alert)
                document.getElementById('alertMessage').innerText = data.message;
                console.log(`Catagory : ${data.category}`);
                alert.classList.add('alert-' + data.category);
                alert.classList.remove("d-none")

                setTimeout(function() {
                    alert.classList.add("d-none");
                }, 4000);
            } else if (data.html) {


            // Update the HTML content
            const portfolioDisplay = document.getElementById('portfolioDisplay');
            portfolioDisplay.innerHTML = data.html;

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
                    const Chart1 = createChart(chartId1, labels1, values1,'Industry','doughnut');
                    window.addEventListener('resize', () => {
                        resizeLegend(Chart1);
                    });
                    

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
                    const Chart2 = createChart(chartId2, labels2, values2,'Asset Allocation','polarArea');
                    window.addEventListener('resize', () => {
                        resizeLegend(Chart2);
                    });
                })
                .catch(error => console.error(`Error fetching data for chart 2 of portfolio ${portfolioId}:`, error));

            

            });
        }
        })
    
        .catch(error => {
            console.error('Error:', error);
        });
    





    });
});

// Chart.register(ChartDataLabels);

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
                    'rgba(255, 99, 132, 0.2)',
                    'rgba(255, 159, 64, 0.2)',
                    'rgba(255, 205, 86, 0.2)',
                    'rgba(75, 192, 192, 0.2)',
                    'rgba(54, 162, 235, 0.2)',
                    'rgba(153, 102, 255, 0.2)',
                    'rgba(201, 203, 207, 0.2)'
                  ],
                  borderColor: [
                    'rgb(255, 99, 132)',
                    'rgb(255, 159, 64)',
                    'rgb(255, 205, 86)',
                    'rgb(75, 192, 192)',
                    'rgb(54, 162, 235)',
                    'rgb(153, 102, 255)',
                    'rgb(201, 203, 207)'
                  ],
                  borderWidth: 1,
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
                    display: window.innerWidth > 400,  // Show legend only for larger screens
                    
                },
                tooltip: {
                    // Tooltip will only receive click events
                    enabled: true,
                    events: ['mousemove', 'mouseout', 'click', 'touchstart', 'touchmove']
                  },
                
                datalabels: {
                    display: function (context) {
                        // Show labels only on smaller screens
                        return window.innerWidth <= 400;
                    },
                    color: '#000',
                    align: 'end',
                    anchor: 'end',
                    formatter: (value, context) => {
                        return `${context.chart.data.labels[context.dataIndex]}: ${value}`;
                    }
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



// Function to remove all alert-* classes from an element
function removeAlertClasses(element) {
    // Loop through all classes of the element
    Array.from(element.classList).forEach((className) => {
        // Check if the class starts with "alert-"
        if (className.startsWith('alert-')) {
            element.classList.remove(className); // Remove the class
        }
    });
}


function resizeLegend(chart) {
    const isSmallScreen = window.innerWidth < 600; // Adjust the threshold as needed
    chart.options.plugins.legend.display = !isSmallScreen; // Hide legend on small screens
    chart.update(); // Update the chart to apply changes
}