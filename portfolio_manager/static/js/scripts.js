document.addEventListener('DOMContentLoaded', function() {
    console.log('JavaScript loaded.');
});


// setTimeout(function() {
//     let flashMessages = document.getElementsByClassName('flash-message');
//     for (var i = 0; i < flashMessages.length; i++) {
//         flashMessages[i].style.display = 'none';
//     }
// }, 3000); // 3000 milliseconds = 3 seconds

let isModal = document.querySelectorAll(".modal_link")

isModal.forEach(stockItem => {
    // Add a click event listener to each item
    stockItem.addEventListener('click', () => {
     // Get the ID of the clicked element (e.g., AAPL, MSFT)
    console.log(stockItem.innerHTML)
     let stockCode = stockItem.textContent;
    console.log(stockCode);
    stock_modal = stockCode.concat("_modal");
    console.log(stock_modal);
    // Display the modal
    let modal = document.getElementById(stock_modal);
    console.log(modal)
    setTimeout(() => {
        modal.open()
    }, 200);
    

})})
