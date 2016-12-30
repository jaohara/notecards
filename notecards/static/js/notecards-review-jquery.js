$(document).ready(function(){

    $(document).keypress(function(event){
        if($.inArray(event.key, ["a", "f"] != -1)){
            // a is back, f is forward

            // weird case - is this the first card? if so, don't go to previous card
            // I can account for this with a custom attribute

            switch(event.key){
                case "a":
                    if ($(".review-prev").attr("first") != "true"){
                        window.location.href = $(".review-prev").attr("href");
                    }
                    break;
                case "f":
                    window.location.href = $(".review-next").attr("href");
                    break;
            }
        }
    });
});