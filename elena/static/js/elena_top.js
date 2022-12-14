var modname = "";
var _enter = function() {};
var youHold = false;

var hercounter = 0;
var youcounter = 0;
    
var topic = -1;
var name = "";
var question_asked = false;
var question_sel = -1;
var rounds_since_last_game = 0;

var ans_txt = "";
var kiwi_inc_waits = 0;
var kiwicount_var = 0;
var herready = false;
var already_hit = false;
var chelsea_msgs = ["Hi! I'm Chelsea. What's your name?"];
var convo_counter = 0;

/**
* Sometimes a user's response won't be in the form you expect.
* You need to have standard rules by which answers are to be
* formatted for fair comparisons.
* There are three particular corrections that scrub_str makes:
* - convert numbers to words
* - remove articles 'the' and 'a'
* - make all letters lowercase
* @param {string} s - the answer string to be modified
*/
function scrub_str(s) {
    var _s = "";
    s.split(" ").forEach(function (itm, idx) {
       if ((itm.toLowerCase() != "the") &&
           (itm.toLowerCase() != "a")) {
           _s += itm;
        }
    });
    return _s.toLowerCase();
}

/**
* Focus the user on the input text box to provide an answer.
*/
function statement_focus() {
    document.getElementById("statement").focus({preventScroll:true});
}

/**
* Same as statement_focus, except scroll to the bottom of the page
* as well.
*/
function refocus() {
    if (document.getElementById("statement")) {
        statement_focus();
    }
    scrollToBottom();
}

/**
* Any attempt to click outside of the textbox forces the user back.
*/
addEventListener("click", e => {
    refocus();
}, true);
window.oncontextmenu = refocus;

var jdomain = $('#jdomain').data("name");

/**
* Pretty self-explanatory. Force the user to the top of the page.
*/
function scrollToTop() {
    window.scrollTo(0, 0);
}

/**
* Pretty self-explanatory. Force the user to the bottom of the page.
*/
function scrollToBottom() {
    window.scrollTo(0, document.body.scrollHeight);
}

/**
* Create a new bubble for Chelsea.
*/
function newChelseaBubble() {
    document.getElementById("chat").innerHTML +=
        "<p id=\"her" + hercounter.toString() +
        "\" class=\"chelseabubble\">Chelsea: " +
        "<span id=\"bub\"></span>" +
        "</p></br></br>";
    scrollToBottom();
}

/**
* Create a new bubble for the user.
*/
function newYouBubble() {
    document.getElementById("chat").innerHTML +=
        '<p id="you' + youcounter.toString() +
        '" class="yourbubble">You: ' +
        '<input type="text" id="statement" ' +
        'class="textbox" onkeypress="_enter()"/></p></br></br>';
    statement_focus();
    scrollToBottom();
}

/**
* Format and send an XMLHttpRequest to a particular domain.
* @param {function} done_fn -> function to call when response
* is received.
* @param {function} error_fn -> function to call when an error
* occurs
* @param {boolean} is_post -> is this a POST request? False implies
* a GET request.
* @param {string} json -> stringified JSON array to send with
* POST requests
* @param {string} content_type -> content type field for GET request
* headers
* @param {string} internal_type -> internal_type field,
* blank by default
*/
function send_http_request_to_domain(done_fn, error_fn, domain,
    is_post, json, content_type, internal_type = "") {
    let http_request = new XMLHttpRequest();
    http_request.open(is_post ? "POST" : "GET", domain, false);
    http_request.onreadystatechange = function() {
        if (http_request.readyState === 4) {
            if (http_request.status === 200) {
                done_fn(http_request);
            } else {
                error_fn();
            }
        }
    }
    http_request.setRequestHeader("Content-Type",
        is_post ? "application/json" : content_type);
    http_request.setRequestHeader("Access-Control-Allow-Origin", "*");
    http_request.setRequestHeader("Internal-Type", internal_type);
    if (is_post) {
        http_request.send(json);
    } else {
        http_request.send();
    }
}

/**
* Format and send an XMLHttpRequest to this site.
* @param {function} done_fn -> function to call when response
* is received.
* @param {boolean} is_post -> is this a POST request? False implies
* a GET request.
* @param {string} json -> stringified JSON array to send with
* POST requests
* @param {string} content_type -> content type field for GET request
* headers
* @param {string} internal_type -> internal_type field,
* blank by default
*/
function send_http_request(done_fn, is_post, json,
                           content_type, internal_type = "") {
    e_fn = function() {
        console.log("Error!");
    }
    send_http_request_to_domain(done_fn,
                                e_fn, jdomain,
                                is_post, json, content_type,
                                internal_type);
}

/**
* Generate a random number less than m.
* @param {BigInt} m - maximum random number value (exclusive)
*/
function randint(m) {
    return Math.floor(Math.random() * m);
}

/**
* Display the module selection page.
*/
function start() {
    $("body").animate({opacity: 0}, {duration: 3000});
    $("body").promise().done(function () {
        $("#pick_mod").show();
        $("body").animate({opacity: 1}, {duration: 250});
        $("body").promise().done(function () {
            scrollToTop();
            $("#pick_mod").animate({opacity: 1}, {duration: 500});
        });
    });
}

/** Game Functions
*
* Functions that you will call in your game modules
*/

/**
* Pay 5 kiwis to play a game.
*/
function pay_to_play() {
    kiwicount_var -= 5;
    document.getElementById("kiwicount").innerHTML = kiwicount_var;
}

/**
* Increment someone's score by i kiwis, either through answering a
* trivia question or through a bonus round.
* @param {BigInt} i - number of kiwis by which to increment the user's
* score.
*/
function inc_kiwi_count(i = 1) {
    // Wait for chelsea msg to be posted.
    youHold = true;
    if (i == 1) {
        var kiwi_convo_idx = randint(3);
        if (kiwi_convo_idx == 0) {
            chelsea_msgs.push("Here's a kiwi. One less for me.");
        } else if (kiwi_convo_idx == 1) {
            chelsea_msgs.push("Have a kiwi.");
        } else {
            chelsea_msgs.push("I shall award you with one kiwi.");
        }
    } else if (i > 0) {
        chelsea_msgs.push("Congrats! Here's a " +
            i.toString() + " kiwi bonus!");
    }
    kiwi_inc_waits += i;
}

/**
* Format and send a POST request to this site.
* @param {function} done_fn -> function to call when response
* is received.
* @param {string} json -> stringified JSON array to send with
* POST requests
* @param {string} internal_type -> internal_type field,
* blank by default
*/
function send_http_post_request(done_fn, json, internal_type = "") {
    send_http_request(done_fn, true, json, "", internal_type);
}

/**
* Format and send a GET request to this site.
* @param {function} done_fn -> function to call when response
* is received.
* @param {string} content_type -> content type field for GET request
* headers
* @param {string} internal_type -> internal_type field,
* blank by default
*/
function send_http_get_request(done_fn,
                               content_type,
                               internal_type = "") {
    send_http_request(done_fn, false, [], content_type, internal_type);
}

/**
* Return 1 if yes, -1 if no, 0 if neither.
* @param {string} s -> string of user's response
*/
function check_affirmative(s) {
    return (s.toLowerCase() == "yes") ?  1 :
           (s.toLowerCase() == "no" ) ? -1 : 0;
}

/**
* Go back to the lab selection page after clicking back button.
*/
function back_button_click() {
    $("#kbar").animate({opacity: 0}, {duration: 3000});
    $("#chat").animate({opacity: 0}, {duration: 3000}).promise().done(function() {
        $("#chat").hide();
        document.getElementById("final_score").innerHTML =
            "<br/>Final score: " + kiwicount_var.toString() + "&#129373;";
        $("#final_score").animate({opacity: 1}, {duration: 3000}).promise().done(function() {
            $("#final_score").animate({opacity: 0}, {duration: 3000}).promise().done(function() {
                document.location.reload();
            });
        });
    });
}

start();
