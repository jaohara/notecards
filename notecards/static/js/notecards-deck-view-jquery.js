$(document).ready(function(){
    var animationSpeed = 150;

    $('.tag-input-toggle').click(function(event){
        event.preventDefault();
        $('#id_word').animate({
            width: "+=120",
        }, animationSpeed, function(){});
        $('#id_word').focus()
    });

    $('#id_word').blur(function(event){
        $('#id_word').animate({
            width: "-=120",
        }, animationSpeed, function(){});
    });
});