$(document).ready(function(){
    $('.leftSideBarBtn').click(function(){
        $('.leftSideBarBtn').toggleClass('backGRND');
        $('.leftSideBarMenu,.menuOptions').slideToggle(2);
        /*$(this).show();*/
    });

    //index.html leftSideBar stuff
    $('.menuOptions span').click(function(){
        $(this).next('ul').slideToggle();
    });
});