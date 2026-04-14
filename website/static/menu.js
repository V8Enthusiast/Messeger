// var coll = document.getElementsByClassName("collapsible");
// var i;

// for (i = 0; i < coll.length; i++) {
//   coll[i].addEventListener("click", function() {
//     this.classList.toggle("active");
//     var content = this.nextElementSibling;
//     if (content.style.maxHeight){
//       content.style.maxHeight = null;
//     } else {
//       content.style.maxHeight = content.scrollHeight + "px";
//     } 
//   });
// }

window.onload = function() {
  var main = document.getElementById("main");
  var content = main.querySelector("page-content");
  var messageBox = content.querySelector("message-box");
  //messageBox.scroll({ top: messageBox.scrollHeight, behavior: 'smooth', block: 'end'});
  messageBox.scrollTop = messageBox.scrollHeight;
};
document.addEventListener("DOMContentLoaded", function () {
  // Your JavaScript code here
  scrollToBottom();
});

var sidebarState = 0;

function scrollToBottom() {
  var messageBox = document.getElementById("messages");
  //messageBox.scroll({ top: messageBox.scrollHeight, behavior: 'smooth', block: 'end'});
  messageBox.scrollTop = messageBox.scrollHeight;
}

document.onkeydown = function (e) {
  e = e || window.event;
  switch (e.which || e.keyCode) {
    case 13:
      e.preventDefault(); // Prevent the default behavior of the Enter key
      document.getElementById("send-btn").click();
  }
};


function toggleNav() {
  if (sidebarState == 0) {
    sidebarState = 1;
    openNav()
  }
  else {
    sidebarState = 0;
    closeNav()
  }
}

/* Set the width of the side navigation to 250px and the left margin of the page content to 250px */
function openNav() {
  let element = document.getElementById('page-content')

  document.getElementById("mySidenav").style.width = "250px";
  if (element !== null) {
    document.getElementById("page-content").style.width = "89%";
  }
  document.getElementById("main").style.marginLeft = "250px";
}

/* Set the width of the side navigation to 0 and the left margin of the page content to 0 */
function closeNav() {
  let element = document.getElementById('page-content')
  document.getElementById("mySidenav").style.width = "0";
  if (element !== null) {
    document.getElementById("page-content").style.width = "95%";
  }
  document.getElementById("main").style.marginLeft = "0";
}

function changeCSS(cssFile) {
  var dark = '../static/dark.css';
  var light = '../static/light.css';


  //document.getElementById('stylesheet').href=cssFile;
  if (cssFile === dark) {
    document.getElementById('theme').onclick = function () { changeCSS(light); };
    document.getElementById('theme').href = "/set/light";
  }
  else {
    document.getElementById('theme').onclick = function () { changeCSS(dark); };
    document.getElementById('theme').href = "/set/dark";
  }
}