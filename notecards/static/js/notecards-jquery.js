$(document).ready(function() {
    /*
        Defines jQuery behavior that spans the entire application.
    */


    console.log("Ready has fired.");

    /*

    $("a.delete-link").on("click", function(event){
        event.stopImmediatePropagation();
        event.preventDefault();

        if(confirm("Really delete this deck?")){
            window.location.href = $(this).attr("href");
        }
    });

    */

    // important to allow for ajax stuff
    function getCookie(name){
        var cookieValue = null;

        if (document.cookie && document.cookie != ""){
            var cookies = document.cookie.split(";");

            for (var i = 0; i < cookies.length; i++){
                var cookie = jQuery.trim(cookies[i]);

                // does this cookie string begin with the name we want?
                if (cookie.substring(0, name.length + 1) == (name + "=")){
                    cookieValue = decodeURIComponent(cookie.substring(name.length + 1));
                    break;
                }
            }
        }

        return cookieValue;
    }

    $.ajaxSetup({
        beforeSend: function(xhr, settings){
            if (!(/^http:.*/.test(settings.url) || /^https:.*/.test(settings.url))){
                //only send the token to relative URLs, i.e. locally
                xhr.setRequestHeader("X-CSRFToken", getCookie('csrftoken'));
            }
        }
    });
    // end ajax cookie stuff
});

function logResult(successBool, message){
    console.log(successBool ? "Success: " + message : "Failure: " + message);
}