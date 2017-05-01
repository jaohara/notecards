$(document).ready(function(){
    var animationSpeed = 150;
    var deckPk = $(".deck-meta").attr("id").split("-")[1];

    bindRemoveTags(deckPk);

    $('.tag-input-toggle').click(function(event){
        event.preventDefault();
        $('#id_word').animate({
            width: "10em",
        }, animationSpeed, function(){});
        $('#id_word').focus();
        $(this).fadeOut(animationSpeed);
    });

    // this is too janky with variable-width fonts
    /*
    $('#id_word').keypress(function(event){
        console.log("Keypress event detected on #id_word.");
        $('#id_word').css({
            width: "" + $('#id_word').val().length + "em",
        });
    });
    */

    $('#id_word').blur(function(event){
        $('#id_word').animate({
            //width: "-=120",
            width: "0em",
        }, animationSpeed, function(){});
        $('.tag-input-toggle').fadeIn(animationSpeed);
    });

    $(".tag-form").on("submit", function(event){
        event.preventDefault();
        console.log(".tag-form submitted.");

        var tagWord = $(this).find("#id_word").val();
        // question marks cause errors in URL formatting... maybe not the best way to deal with this
        tagWord = tagWord.replace("?", "");
        var ajaxUrl = '/deck/' + deckPk + '/tag/add/';


        $.ajax({
            url: ajaxUrl,
            context: this,
            type: 'POST',
            data: {tag_word: tagWord},
            success: function(data){
                console.log(data.success ? "Success: " + data.message : "Failure: " + data.message);

                $(this).find("#id_word").val("");
                //$(this).find("#id_word").blur();

                /*
                    Part of this is going to be hardcoded and gross, and that's
                    the part where we add the a.remove-tag part of the span.deck-tag.

                    The reason for this is that this is normally constructed dynamically
                    via Django's template engine - which is the more sane way - but I 
                    don't know any way to do this while having my javascript in a 
                    separate file from my django template. Kind of a trade off of which
                    poor practice is the lesser of two evils, but I'm going to keep
                    it this way for now as it's a bit more straightforward. This will
                    probably come back to haunt me later on.

                    Also, isn't this a security issue? Can't this be used for
                    any end user to know how to get to the code that rmeoves
                    tags? Maybe I should scrap this entirely and just call 
                    a new method that recalculates all of the tags. 

                    Shit, what's the best way to handle this?
                */

                /*
                    Okay, here's what we need to do when we resume:

                        1. make sure the new tags are links to their proper tag pages
                        2. maybe increase the char limit on tags?
                        3. find a way to add tags that isn't revealed client side/hardcoded (code to access urls for deletion, etc)
                            - is this really as bad? They kind of see where the links go anyway
                        4. run that thing to rebind the ajax-remove method once a new tag is added
                        5. I think that's all?


                */

                /*
                    Another thing of note - you kind of have to be the 
                    author of the deck to ever get to this point... so
                    an added tag will always have a remove-tag anchor
                    added as well. I guess I don't need to worry too much
                    about that.
                */

                /*
                    We're going to make this its own template like we do with deck_list and
                    deck_item. That way we can just render to string and return this from
                    the server-side.
                */
                var elementString = '<span class="deck-tag"><a href="/tag/'
                    + data.tag_word 
                    + '/">'
                    + data.tag_word
                    + '</a>&nbsp'
                    + '<a href="/deck/'
                    + deckPk
                    + "/remove-tag/"
                    + data.tag_word
                    + '/"><span class="glyphicon glyphicon-remove"></span></a></span>';

                $(elementString).insertBefore($(this).find("#id_word"));
                bindRemoveTags(deckPk);
            }
        });
    });

    // deck like stuff
    $("div.deck-likes a").click(function(event){
        event.preventDefault();

        $.ajax({
            // this should be a little less hard-coded
            url: '/deck/' + deckPk + '/like/',
            dataType: 'json',
            type: 'POST',
            success: function(data){
                // make this more specific, only a child of the div that caught the event so we can like multiple things on the same page
                $(".deck-like-control").text(data.deck_likes);

                // I suppose here is where we'd work out some sort of animation
                $(".like-icon").toggleClass("unliked");
                $(".like-icon").toggleClass("liked");
            }
        });
    });
});

function bindRemoveTags(deckPk){
    $(".remove-tag").click(function(event){
        event.preventDefault();

        var tagWord = $.trim($($(this).parent().get(0)).text());
        var ajaxUrl = '/deck/' + deckPk + '/tag/remove/' + tagWord + "/";

        $.ajax({
            url: ajaxUrl,
            context: this,
            dataType: 'json',
            type: 'POST',
            success: function(data){
                console.log(data.success ? "Success: " + data.message : "Failure: " + data.message);
                /*
                    'context: this' is important in the above line - without
                    it, 'this' doesn't refer to the jQuery object anymore but
                    rather the ajax event object. 

                    Here's an explanation of the error I was getting on StackOverflow:
                    http://stackoverflow.com/questions/3936211/jquery-cannot-read-property-defaultview-of-undefined-error
                */
                if (data.success)
                    $($(this).parent().get(0)).remove();
            }
        });
    });
}