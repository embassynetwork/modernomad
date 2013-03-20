$('#navbar').scroll(function() 
{ 
    $('#fixed').css('top': $(this).scrollTop());
}