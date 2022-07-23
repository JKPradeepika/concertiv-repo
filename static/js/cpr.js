var content = document.getElementById("container");
content.style.display="none";
setTimeout(function(){
    content.style.display="block";
}, 500);

var spinner = document.getElementById("spinner");
spinner.style.display="block";
setTimeout(function(){
    spinner.style.display="none";
}, 500);