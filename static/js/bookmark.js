let no_cont = document.querySelector(".no_cont");
let undo = document.querySelector(".undo");
let bookmark1 = document.querySelector('.bookmark1');
let remove = document.getElementById('remove');

remove.addEventListener('click',()=>{
	bookmark1.style.display = 'none';
	undo.style.display = 'inline-flex';
	no_cont.style.display = 'inline-flex';
})

undo.addEventListener('click',()=>{
	bookmark1.style.display = 'block';
	undo.style.display = 'none';
	no_cont.style.display = 'none';
})

let profile = document.getElementById('profile_box');
let toggle_bar = document.querySelector('.toggle_bar_profile');

function toggle(){
    if(toggle_bar.style.display === 'none'){
        toggle_bar.style.display = 'inline-flex';
    }
    else{
        toggle_bar.style.display = 'none'
    }
}

//sidenav toggle
$("#menu").click(function(){
    $(".sidenav").toggleClass("active");
})