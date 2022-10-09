// Navigation Bar
let navbar = document.getElementById('menu-list')
function navOpen() {
    console.log(navbar.classList.remove('hidden'))
}

function navClose() {
    console.log(navbar.classList.add('hidden'))
}

// Slider
const slides = document.getElementById('slider').children
const leftArrow = document.getElementById('leftarrow')
const rightArrow = document.getElementById('rightarrow')

let currSlide = 0

rightArrow.addEventListener('click', () => {
    currSlide++
    if (currSlide > slides.length - 1){
        currSlide = 0
        
    }
    setActiveSlide()
    // console.log(currSlide)
})

leftArrow.addEventListener('click', () => {
    currSlide--
    if (currSlide < 0){
        currSlide = slides.length - 1
        
    }
    setActiveSlide()
    // console.log(currSlide)
})

function setActiveSlide() {
    //remove active class from all
    for(const slide of slides){
        slide.classList.add('hidden')
    }
    //only adding active class to the currently active slide
    slides[currSlide].classList.remove('hidden')
}
