$(document).ready(function(){
    /*
        This script defines the UI behavior and hotkeys for the notecard quiz
    */
    // this variable just exists for testing jquery things.
    var DEBUG = true;

    //hotkey definitions
    var firstChoice     = "a";
    var secondChoice    = "s";
    var thirdChoice     = "d";
    var fourthChoice    = "f"

    //debug/test hotkeys
    var negKey = "i";
    var posKey = "o";
    var neuKey = "p";

    //feedback animation speeds
    var feedbackAnimationDelay = 2500;
    var feedbackSlideSpeed = 800;

    // fade feedback panel out if it exists (length doesn't eval to 0)
    var posFeedback = $(".feedback-positive");
    var negFeedback = $(".feedback-negative");

    if (posFeedback.length || negFeedback.length){
        if (posFeedback.length){
            posFeedback.delay(feedbackAnimationDelay).slideUp(feedbackSlideSpeed);
        } else {
            negFeedback.delay(feedbackAnimationDelay).slideUp(feedbackSlideSpeed);
        }
    }

    $(document).keypress(function(event){

        if ($.inArray(event.key, [firstChoice,secondChoice,thirdChoice,fourthChoice]) != -1){

            switch (event.key){
                case firstChoice:
                    //$(".quiz-answer-0").trigger("click");
                    window.location.href = $('.quiz-answer-0').attr('href');
                    break;
                case secondChoice:
                    //$(".quiz-answer-1").trigger("click");
                    window.location.href = $('.quiz-answer-1').attr('href');
                    break;
                case thirdChoice:
                    //$(".quiz-answer-2").trigger("click");
                    window.location.href = $('.quiz-answer-2').attr('href');
                    break;
                case fourthChoice:
                    //$(".quiz-answer-3").trigger("click");
                    window.location.href = $('.quiz-answer-3').attr('href');
                    break;
            }
        }

        if (DEBUG){
            // this is just silly nonsense for now, show and hide the feedback panels.
            if ($.inArray(event.key, [negKey,posKey,neuKey]) != -1){
                //alert("We've read one of the keys");
                switch(event.key){
                    case negKey:
                        //alert($(".feedback-negative").html());
                        $(".feedback-negative").slideToggle("slow");
                        break;
                    case posKey:
                        $(".feedback-positive").slideToggle();
                        break;
                    case neuKey:
                        $(".feedback-neutral").slideToggle();
                        break;
                }
            }
        }
    });
});