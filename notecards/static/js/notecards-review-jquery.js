$(document).ready(function(){
    /*
        This script defines the hotkeys for the notecard reveiw
    */

    // hotkey definitions
    var prevKey = "a";
    var nextKey = "f";

    $(document).keypress(function(event){
        if($.inArray(event.key, [prevKey, nextKey] != -1)){
            // a is back, f is forward

            // weird case - is this the first card? if so, don't go to previous card
            // I can account for this with a custom attribute

            switch(event.key){
                case prevKey:
                    if ($(".review-prev").attr("first") != "true"){
                        window.location.href = $(".review-prev").attr("href");
                    }
                    break;
                case nextKey:
                    window.location.href = $(".review-next").attr("href");
                    break;
            }
        }
    });
});