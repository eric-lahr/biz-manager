function setFooter () {
    var footerTXT = document.getElementById('footer-needed-view').innerText;
    if(footerTXT=="yes"){
        document.getElementById('show-if-yes').style.display = "block";
    } else {
        document.getElementById('show-if-yes').style.display = "none";
    }

    var depositTXT = document.getElementById('payment-status-view').innerText;

    if(depositTXT=="Paid Deposit"){
        document.getElementById('show-if-deposit').style.display = "block";
    } else {
        document.getElementById('show-if-deposit').style.display = "none";
    }
}

document.addEventListener('load', setFooter());