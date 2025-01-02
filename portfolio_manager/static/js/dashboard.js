// Function to display error messages
function showError(inputElement, message) {
    const errorElement = document.createElement('div');
    errorElement.className = 'error-message';
    errorElement.style.color = 'red';
    errorElement.innerText = message;
    inputElement.parentElement.appendChild(errorElement);
}

// Function to clear previous error messages
function clearErrorMessages() {
    const errorMessages = document.querySelectorAll('.error-message');
    errorMessages.forEach(function(message) {
        message.remove();
    });
}

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

document.addEventListener('DOMContentLoaded', function() {
    var stockDropdown = document.getElementById('stockDropdown');
    var refreshButton = document.getElementById('refreshStockButton');

    // Function to toggle the button state based on the selected value
    function toggleRefreshButton() {
        if (stockDropdown.value === '') {
            refreshButton.disabled = true;  // Disable if no stock selected
        } else {
            refreshButton.disabled = false;  // Enable if stock selected
        }
    }

    // Initially disable the button if no stock is selected
    toggleRefreshButton();

    // Add event listener for changes in the dropdown selection
    stockDropdown.addEventListener('change', toggleRefreshButton);
});


function applyEventListeners () {

    isModal = document.querySelectorAll(".modal_link")
        console.log(`This is the Modals List ${isModal}`)
        // console.log(isModal)
            isModal.forEach(stockItem => {
                console.log(stockItem)
                // Add a click event listener to each item
                stockItem.addEventListener('click', () => {
                 // Get the ID of the clicked element (e.g., AAPL, MSFT)
                console.log(stockItem.innerHTML)
                 let stockCode = stockItem.textContent;
                console.log(stockCode);
                stock_modal = stockCode.concat("_modal");
                console.log(`MODAL ELEMENT ID :  ${stock_modal}`)
                console.log(stock_modal);
                // Display the modal
                let modal = document.getElementById(stock_modal);
                console.log(`MODAL ELEMENT ID :  ${modal}`)
                setTimeout(() => {
                    modal.open()
                }, 200);
            })})

    removeButton()
        }


        document.addEventListener('DOMContentLoaded', function() {
            // Get the refresh button element
            const refreshButton = document.getElementById('refreshButton');
        
            if (refreshButton) {
                refreshButton.addEventListener('click', function() {
                    // Reset the form
                    document.getElementById("addStockForm").reset();
        
                    // Get the value of the Yahoo Finance switch
                    const yahooFinanceSwitch = document.getElementById("yahooFinance");
                    const yfFlag = yahooFinanceSwitch.checked ? 'on' : 'off';
        
                    // Get the selected portfolio
                    const portfolio = document.getElementById('portfolioList').value;
        
                    // Get URL from the data attribute of the button
                    const url = this.dataset.url;
        
                    console.log(url);
        
                    // Get CSRF token from the page
                    const csrfToken = document.querySelector('[name=csrfmiddlewaretoken]').value;
        
                    // Prepare the data to send with the request
                    const data = {
                        'portfolio': portfolio,
                        'yf_flag': yfFlag
                    };
        
                    // Send a POST request using the Fetch API
                    fetch(url, {
                        method: 'POST',
                        headers: {
                            'Content-Type': 'application/json',  // Set content type to JSON
                            'X-CSRFToken': csrfToken  // Include CSRF token in the header
                        },
                        body: JSON.stringify(data)  // Convert data to JSON string
                    })
                    .then(response => response.text())  // Get the response as text (HTML)
                    .then(response => {
                        // Update the table section with the new content
                        document.getElementById('tableSection').innerHTML = response;
                        
                        // Call any function to apply event listeners if needed
                        applyEventListeners();  
                    })
                    .catch(error => {
                        console.error('Error:', error);  // Log any errors for debugging
                    });
                });
            }
        });
    



// /////////////////////////////////////////////////////////////////

document.getElementById('addStockButton').addEventListener('click', function() {
    console.log('INSIDE THE API')
    fieldCheck  =  allFieldsValid()
    if (fieldCheck === true){
        console.log(fieldCheck)
    const assetData = {
        stock_code: document.getElementById('stockDropdown').value,
        buy_price: document.getElementById('buyPrice').value,
        no_of_shares: document.getElementById('noOfShares').value,
        stop_loss: document.getElementById('stopLoss').value,
        cash_out: document.getElementById('cashOut').value,
        comment: document.getElementById('comment').value,
        portfolioName: document.getElementById('portfolioList').value
    };
    const url = this.dataset.url;  // Get URL from data attribute
    fetch(url, {
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
            document.getElementById('refreshButton').click();
            // alert(data.message)
            let alert = document.getElementById('alert')
            removeAlertClasses(alert)
            document.getElementById('alertMessage').innerText = data.message
            console.log(`Catagory : ${data.category}`)
            alert.classList.add('alert-' + data.category);
            alert.classList.remove("d-none")

            setTimeout(function() {
                alert.classList.add("d-none");
            }, 6000);

        } else {
            console.error(data.error);  // Log error message
            let alert = document.getElementById('alert')
            removeAlertClasses(alert)
            document.getElementById('alertMessage').innerText = data.message
            alert.classList.add('alert-' + data.category);
            alert.classList.remove("d-none")  
        }
    })
    .then()
    .catch(error => console.error('Error:', error));
}
});


// ################### sell stock button

document.getElementById('sellStockButton').addEventListener('click', function() {
    yahooFinanceSwitch = document.getElementById("yahooFinance");
    yahooFinanceSwitch.checked = false
    console.log('INSIDE SELL STOCK THE API')
    fieldCheck  =  allFieldsValid()
    if (fieldCheck === true){
        console.log(fieldCheck)
    const assetData = {
        stock_code: document.getElementById('stockDropdown').value,
        buy_price: document.getElementById('buyPrice').value,
        no_of_shares: document.getElementById('noOfShares').value,
        stop_loss: document.getElementById('stopLoss').value,
        cash_out: document.getElementById('cashOut').value,
        comment: document.getElementById('comment').value,
        portfolioName: document.getElementById('portfolioList').value
    };

    fetch('/sell_partial_db', {
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
            document.getElementById('refreshButton').click();
            // alert(data.message)
            let alert = document.getElementById('alert')
            removeAlertClasses(alert)
            document.getElementById('alertMessage').innerText = data.message
            console.log(`Catagory : ${data.category}`)
            alert.classList.add('alert-' + data.category);
            alert.classList.remove("d-none")

            setTimeout(function() {
                alert.classList.add("d-none");
            }, 6000);

        } else {
            console.error(data.error);  // Log error message
            let alert = document.getElementById('alert')
            removeAlertClasses(alert)
            document.getElementById('alertMessage').innerText = data.message
            alert.classList.add('alert-' + data.category);
            alert.classList.remove("d-none")  
        }
    })
    .then()
    .catch(error => console.error('Error:', error));
}
});


function allFieldsValid() {
let isValid = true; // Flag to track if the form is valid
let portfolioName = portfolioList.value
// Get form fields
const stockCode = document.getElementById('stockDropdown');
const buyPrice = document.querySelector('input[name="buy_price"]');
const noOfShares = document.querySelector('input[name="no_of_shares"]');
const stopLoss = document.querySelector('input[name="stop_loss"]');
const cashOut = document.querySelector('input[name="cash_out"]');
const comment = document.querySelector('input[name="comment"]');
// Clear previous error messages
clearErrorMessages();

// Validate each field using a switch statement
[stockCode, buyPrice, noOfShares, stopLoss, cashOut,comment].forEach((input) => {
    switch (input.name) {
        case 'stock_code':
            if (input.value === '') {
                showError(input, 'Please select a stock ticker.');
                isValid = false;
            }
            break;
        case 'buy_price':
            if (input.value === '' || isNaN(input.value) || input.value <= 0) {
                showError(input, 'Please enter a valid buy price.');
                isValid = false;
            }
            break;
        case 'no_of_shares':
            if (input.value === '' || isNaN(input.value) || input.value <= 0) {
                showError(input, 'Please enter a valid volume.');
                isValid = false;
            }
            break;
        case 'stop_loss':
            if (input.value === '' || isNaN(input.value) || input.value <= 0) {
                showError(input, 'Please enter a stop loss price.');
                isValid = false;
            }
            break;
        case 'cash_out':
            if (input.value === '' || isNaN(input.value) || input.value <= 0) {
                showError(input, 'Please enter a profit price');
                isValid = false;
            }
            break;
        case 'comment':
            if (input.value === '') {
                showError(input, 'Please enter trade note');
                isValid = false;
            }
            break;
        default:
            break;
    }
});
console.log(isValid)
return isValid
// If all validations pass, submit the form
}


////////////Get LATEST PRICE

document.addEventListener('DOMContentLoaded', function() {
    document.getElementById('stockDropdown').addEventListener('change', getLatestPrice);
    document.getElementById('refreshStockButton').addEventListener('click', getLatestPrice)
    });

function getLatestPrice() {
        tickerSelect =  document.getElementById('stockDropdown')
        let ticker = tickerSelect.value
        let url = tickerSelect.getAttribute('data-url');  // Get URL from data attribute
        const csrfToken = document.querySelector('[name=csrfmiddlewaretoken]').value; 
        console.log(ticker);
        console.log(url);

        // Using the Fetch API
        fetch(url, {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json',
                'X-CSRFToken': csrfToken
            },
            body: JSON.stringify({ 'ticker': ticker })  // Send ticker as JSON
        })
        .then(response => {
            if (!response.ok) {
                throw new Error('Network response was not ok');
            }
            return response.json();  // Parse JSON response
        })
        .then(data => {
            console.log(data)
            if (data['last_quote'] === "NA") {
                let alert = document.getElementById('alert')
                    removeAlertClasses(alert)
                    document.getElementById('alertMessage').innerText = data.message
                    console.log(data)
                    alert.classList.add('alert-' + data.catagory);
                    alert.classList.remove("d-none")
                    setTimeout(function() {
                        alert.classList.add("d-none");
                    }, 6000);
            }
            else {
                    document.getElementById('buyPrice').value = data['last_quote'].toFixed(2);  // Set the buy price value
            }
        })
        .catch(error => {
            console.error('Error:', error.message);  // Handle errors
        });
   
};





////////////////REMOVE STOCK API TO RETURN the HTML TEMPLATE


function removeButton () {
    // Select all the remove buttons
    console.log("Remove Listener")
    const removeButtons = document.querySelectorAll('.remove-stock-btn');
    // Loop through each button and attach the click event
    removeButtons.forEach(function(button) {
        button.addEventListener('click', function() {
            yahooFinanceSwitch = document.getElementById("yahooFinance");
            yahooFinanceSwitch.checked = false
            const csrfToken = document.querySelector('[name=csrfmiddlewaretoken]').value; 
            // Get the URL from the data-url attribute
            const url = button.getAttribute('data-url');
            console.log(url)
            // Use fetch API to call the remove_stock route
            fetch(url, {
                method: 'POST',  // You can use POST if the route requires it
                headers: {
                    'Content-Type': 'application/json',
                    'X-CSRFToken': csrfToken
                    
                }
            })
            .then(response => {
                if (!response.ok) {
                    throw new Error('Network response was not ok');
                }
                return response.json();  // Assuming the server returns JSON
            })
            .then(data => {
                if (data.message) {
                    console.log(data.message);  // Log success message
                    document.getElementById('refreshButton').click();
                    
                    let alert = document.getElementById('alert')
                    removeAlertClasses(alert)
                    document.getElementById('alertMessage').innerText = data.message
                    console.log(data)
                    alert.classList.add('alert-' + data.catagory);
                    alert.classList.remove("d-none")
                    setTimeout(function() {
                        alert.classList.add("d-none");
                    }, 6000);
                    
                } else {
                    console.error(data.error);  // Log error message
                    let alert = document.getElementById('alert')
                    removeAlertClasses(alert)
                    document.getElementById('alertMessage').innerText = data.message
                    alert.classList.add('alert-' + data.category);
                    alert.classList.remove("d-none")                    
                }
            })
        .then()
        .catch(error => console.error('Error:', error));
        });
    });
};


document.addEventListener('DOMContentLoaded', function() {
    const alert = document.getElementById('alert');
    const closeButton = document.getElementById('alertCloseButton');
    
    // Handle close button click
    closeButton.addEventListener('click', function() {
      alert.classList.add('d-none');  // Hide the alert instead of removing it
    });
  });