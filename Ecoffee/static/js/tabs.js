//select elements with attributes data-tab-target and data-tab-content
const tabs = document.querySelectorAll('[data-tab-target]')
const tabContents = document.querySelectorAll('[data-tab-content]')
//make active tabs
tabs.forEach(tab => {
    tab.addEventListener('click', () => {
        const target = document.querySelector(tab.dataset.tabTarget)
        //remove active class from all tab content sections
        tabContents.forEach(tabContent => {
            tabContent.classList.remove('active')
        })
        //add active class to currently clicked tab
        target.classList.add('active')
        tabs.forEach(tab => {
            tab.classList.remove('active')
        })
        tab.classList.add('active')
        target.classList.add('active')
    })
})