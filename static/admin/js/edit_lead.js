// footer drop down

function loaded () {
    var cur_foot = document.getElementById('footer_form_drop').value;
    var cur_pay = document.getElementById('payment_form_drop').value;

    if(cur_foot == 'YS'){
        document.getElementById('reveal-if-footer').style.display = "block";
    } else {
        document.getElementById('reveal-if-footer').style.display = "none";
    }

    if(cur_pay=='DP'){
        document.getElementById('reveal-if-deposit').style.display = "block";
    } else {
        document.getElementById('reveal-if-deposit').style.display = "none";
    }
}

document.addEventListener('load', loaded())

document.getElementById('footer_form_drop').addEventListener('change',  function() {
    if(document.getElementById('footer_form_drop').value == 'YS'){
        document.getElementById('reveal-if-footer').style.display = "block";
    } else {
        document.getElementById('reveal-if-footer').style.display = "none";
    }
})

document.getElementById('payment_form_drop').addEventListener('change',  function() {
    if(document.getElementById('payment_form_drop').value == 'DP'){
        document.getElementById('reveal-if-deposit').style.display = "block";
    } else {
        document.getElementById('reveal-if-deposit').style.display = "none";
    }
})