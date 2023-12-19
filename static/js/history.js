let bookmark = document.getElementById('bookmark');
let bookmarked = document.getElementById('bookmarked');
let remove = document.getElementById('remove');

bookmark.addEventListener('click',()=>{
	bookmarked.style.display = 'inline-flex';
	remove.style.display = 'inline-flex';
	bookmark.style.display = 'none';
})

remove.addEventListener('click',()=>{
	bookmark.style.display = 'inline-flex';
	bookmarked.style.display = 'none';
	remove.style.display = 'none';
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