$(document).ready(function(){

    // set some sort of boolean with a checkbox?
    //if ($('.hotkey-toggle').is(":checked")){

    $(document).keypress(function(event){

        if ($.inArray(event.key, ["s","a","d","f"]) != -1){

            switch (event.key){
                case "a":
                    //$(".quiz-answer-0").trigger("click");
                    window.location.href = $('.quiz-answer-0').attr('href');
                    break;
                case "s":
                    //$(".quiz-answer-1").trigger("click");
                    window.location.href = $('.quiz-answer-1').attr('href');
                    break;
                case "d":
                    //$(".quiz-answer-2").trigger("click");
                    window.location.href = $('.quiz-answer-2').attr('href');
                    break;
                case "f":
                    //$(".quiz-answer-3").trigger("click");
                    window.location.href = $('.quiz-answer-3').attr('href');
                    break;
            }
        }
    });
    //}
});