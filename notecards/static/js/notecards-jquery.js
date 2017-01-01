$(document).ready(function() {
    /*
        Defines jQuery behavior that spans the entire application.
    */


    /*
        I want to have this better handled in the future. Instead of using
        the browser confirm dialog, I want to make a div appear with a 
        confirm or cancel button so we keep focus within the same window
        and maintain a similar visual scheme between the app and the dialog.
    */
    $("a.delete-link").on("click", function(event){
        event.stopImmediatePropagation();
        event.preventDefault();

        if(confirm("Really delete this deck?")){
            window.location.href = $(this).attr("href");
        }
    });
});