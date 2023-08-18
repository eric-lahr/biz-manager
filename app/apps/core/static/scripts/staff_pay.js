// staff payroll total

const pay_cell = document.querySelector(".staffpay");
const day_tots = document.querySelectorAll(".day-tot")
const week_tot = document.querySelector("#id_weekly_hours")

pay_cell.addEventListener('focusout', (e) => {
    var tot = 0;
    for (var i=0; i < day_tots.length; i++) {
        tot = tot + Number(day_tots[i].value);
    }
    week_tot.value = tot;
});