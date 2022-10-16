let tabs = document.getElementById('userTabs').children
let blocks = document.getElementById('userBlocks').children
// Reset Active state
const resetActive = () => {
    for (let i = 0; i < tabs.length; i++) {
        tabs[i].classList.remove('bg-gray-200')
        blocks[i].classList.add('hidden')
    }
}

// Toggle Tabs Bar
for (let i = 0; i < tabs.length; i++) {
    tabs[i].addEventListener('click', () => {
        resetActive()
        tabs[i].classList.add('bg-gray-200')
        blocks[i].classList.remove('hidden')
    })
}
