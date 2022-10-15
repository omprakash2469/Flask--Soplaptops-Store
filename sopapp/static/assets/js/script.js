// ---------- Navigation Bar Toggle ----------
// Navigation Bar
let navbar = document.getElementById('menu-list')
function navOpen() {
    console.log(navbar.classList.remove('hidden'))
}

function navClose() {
    console.log(navbar.classList.add('hidden'))
}

// Toggle Checkout Sidebar
let checkoutBar = document.getElementById('checkoutBar')

// ---------- Cart Sidebar Toggle ----------
function openCheckoutBar() {
    checkoutBar.classList.remove('hidden')
}
function closeCheckoutBar() {
    checkoutBar.classList.add('hidden')
}
// Open Cart and Add Item
function addAndOpenCart(){
    openCheckoutBar()
    sendCart()
}

// ---------- Add to Cart ----------
// Send Request to add product in cart
const makeRequest = (action, item) => {
    let config = {
        method : "POST",
        headers : {
            "Content-type": "application/json"
        },
        body : JSON.stringify(item)
    }

    let response = fetch(action, config)
        .then((response) => response.json())
        .then((json) => {
            alert(json)
        });
}

// Fetch all values and create a request
const sendCart = ()=>{
    let item = {
        pid: document.getElementById('pid').value,
        quantity: document.getElementById('quantity').value
    }
    makeRequest("/cart", item)
}

// Display Alert Message in checkout
const alert = (state) =>{
    let alert = document.getElementById('addtocartalert')
    alert.classList.remove('hidden') // Display alert
    alert.classList.add(state['state'])
    alert.innerText = state['message']
    
    // Display Message for 5s
    setInterval(() => {
        alert.classList.add('hidden') 
        alert.classList.remove(state['state'])
        alert.innerText = ""
    }, 4000);
}

// Remove Cart Item
let cartItems = document.getElementsByClassName('removecartitem')
for (let i = 0; i < cartItems.length; i++) {
    cartItems[i].addEventListener('click', ()=>{
        cartpid = {"value": cartItems[i].value}
        makeRequest("/removeitem", cartpid)
    })
}

// Remove Checkout Item
let checkoutItems = document.getElementsByClassName('removecheckoutitem')
for (let i = 0; i < checkoutItems.length; i++) {
    checkoutItems[i].addEventListener('click', ()=>{
        checkoutpid = {"value": checkoutItems[i].value}
        makeRequest("/removeitem", checkoutpid)
        openCheckoutBar()
    })
}