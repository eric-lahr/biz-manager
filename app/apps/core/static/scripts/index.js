class Dropdown {
    constructor(container){
        this.container = container;
        this.trigger = container.querySelector('.trigger');
        this.content = container.querySelector('.content');
    }
    init(){
        this.trigger.addEventListener('click', () => {
            this.trigger.classList.toggle('active');
            this.content.classList.toggle('active');
            if (this.trigger.innerText === "Show Activity Log") {
                this.trigger.innerText = "Hide Activity Log";
            } else {
                this.trigger.innerText = "Show Activity Log";
            }
        })
    }
}

// create dropdown

const dropdowns = document.querySelectorAll('.dropdown');

dropdowns.forEach(dropdown => {
    const instance = new Dropdown(dropdown);
    instance.init()
});
