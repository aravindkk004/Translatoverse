const selectTag = document.querySelectorAll("select");
let fromText = document.querySelector('.input-text-area');
let transText = document.querySelector('.output-text-area');


selectTag.forEach((get, con) =>{
    for(let country_code in countries){
        
        let selected;
        if(con == 0 && country_code == "en"){
            selected = "selected";
        }
        else if(con == 1 && country_code == "hi"){
            selected = "selected";
        }

        let option = `<option value="${country_code}" ${selected}>${countries[country_code]}</option>`
        get.insertAdjacentHTML('beforeend', option)
    }
});

//sidenav toggle
$("#menu").click(function(){
    $(".sidenav").toggleClass("active");
})