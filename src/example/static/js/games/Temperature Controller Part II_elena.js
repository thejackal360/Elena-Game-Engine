/**
* Check whether chat topic is valid given (a) number of kiwis,
* or trivia points earned by the user for correct answers, and (b)
* the number of rounds since the last game.
* @param {BigInt} _t - topic index; limited by NumTopics constant
* in generated *_globals.js file in static/js/games/
*/
function Temperature_Controller_Part_II_acceptable_topic(_t) {
    if (((kiwicount_var >= kiwi_cost_to_play_game) &&
         (rounds_since_last_game >= ask_for_game_every_N_rounds) &&
         (_t != Temperature_Controller_Part_IITriviaTopic)) ||
         (_t == Temperature_Controller_Part_IITriviaTopic)) {
        return true;
    } else {
        return false;
    }
}

/**
* Check whether chat topic is valid given (a) number of kiwis,
* or trivia points earned by the user for correct answers, and (b)
* the number of rounds since the last game.
* @param {BigInt} _t - topic index; limited by NumTopics constant
* in generated *_globals.js file in static/js/games/
*/
function Temperature_Controller_Part_II_randint_topics() {
    do {
        t = randint(Temperature_Controller_Part_IINumTopics);
    } while (!Temperature_Controller_Part_II_acceptable_topic(t));
    return t;
}

/**
* Function called when user presses the "Enter" key when answerng
* a question.
* @param {string} val - the user's answer to the question
*/
function Temperature_Controller_Part_II_enter(val) {
    Temperature_Controller_Part_II_convo(val);
    youcounter++;
}

/**
* The callback that generates Chelsea's next messages for the
* conversation.
* @param {string} val - the user's answer to the question
*/
function Temperature_Controller_Part_II_convo(val) {
    if (topic == Temperature_Controller_Part_IITriviaTopic) {
        rounds_since_last_game++;
    } else {
        rounds_since_last_game = 0;
    }
    if (name == "") {
        name = val;
        // Race condition: No youHold and no more chelsea_msgs
        // Need to hold until you generate topic content.
        chelsea_msgs.push("Good to meet you, " + val);
        topic = Temperature_Controller_Part_II_randint_topics();
        Temperature_Controller_Part_II_convo(val);
    } else if (topic == Temperature_Controller_Part_IITriviaTopic) {
        if (question_asked) {
            let kiwi_inc = false;
            if (scrub_str(ans_txt) == scrub_str(val)) {
                chelsea_msgs.push("That is correct!");
                inc_kiwi_count();
                kiwi_inc = true;
            } else {
                chelsea_msgs.push("Incorrect! The answer is: " +
                    ans_txt
                );
            }
            question_asked = false;
            topic = Temperature_Controller_Part_II_randint_topics();
            if (!kiwi_inc) {
                Temperature_Controller_Part_II_convo(val);
            }
        } else {
            youHold = true;
            get_qa = function(h) {
                ans_txt = h["answer"];
                chelsea_msgs.push(h["question"]);
                question_asked = true;
                youHold = false;
            }
            send_http_get_request(get_qa, "application/json",
                                  modname + "_trivia");
        }
    } else {
        Temperature_Controller_Part_II_subjs(topic, val);
    }
}

/**
* Function called when you click on a modsel bubble to select
* a lab module. It loads the lab manual.
*/
function Temperature_Controller_Part_II_start_lab() {
    modname = "Temperature_Controller_Part_II";
    $("#pick_mod").animate({ opacity: 0 }, { duration: 1000 });
    scrollToTop();
    $("#pick_mod").promise().done(function () {
        $("#pick_mod").hide();
        send_http_get_request(function (data) {
            // Assuming data is the response text, modify accordingly if it's different
            $("#lab_manual").html(
                "<div class=\"labmanbubble\">" +
                data + "</div>" +
                "</br></br><p class=\"modsel\" " +
                "onclick=\"Temperature_Controller_Part_II_start_game()\">" +
                "Start Prelab</p></br></br>"
            );
            $("#lab_manual").show();
            $("#chat").show();
            $("#top_chat").show();
            $("#lab_manual").animate({ opacity: 1 }, { duration: 1000 });
            $("#chat").animate({ opacity: 1 }, { duration: 1000 });
        }, "application/json", modname + "_lab_manual");
    });
}

/**
* Function called when you click the "Start Prelab" button. It loads
* the trivia game.
*/
function Temperature_Controller_Part_II_start_game() {
    $("#lab_manual").animate({opacity: 0}, {duration: 1000});
    $("#lab_manual").promise().done(function() {
        $("#lab_manual").hide();
        newChelseaBubble();
        $("body").animate({opacity: 1}, {duration: 3000});
        $("#kbar").animate({opacity: 1}, {duration: 3000});
        var ellipsis_interval = window.setInterval(function() {
            var bub = document.getElementById("bub");
            if (bub) {
                if (bub.innerHTML.length > 2) bub.innerHTML = "";
                else bub.innerHTML += ".";
            }
        }, 1000);
        var kiwi_inc_interval = window.setInterval(function() {
            if ((chelsea_msgs.length == 0) &&
                (kiwi_inc_waits > 0)) {
                kiwicount_var += kiwi_inc_waits;
                kiwi_inc_waits = 0;
                $("#kiwicount").fadeOut(100).fadeIn(100).fadeOut(100).
                                         fadeIn(100).fadeOut(100).
                                         fadeIn(100).fadeOut(100).
                                         fadeIn(100).fadeOut(100).
                    html(kiwicount_var).fadeIn(100);
                document.getElementById("kiwicount").innerHTML =
                    kiwicount_var;
                youHold = false;
                Temperature_Controller_Part_II_convo(null);
                newChelseaBubble();
            }
        }, 1000);
        var bub_interval = window.setInterval(function() {
            if (chelsea_msgs.length != 0) {
                if (!document.getElementById("bub")) {
                    newChelseaBubble();
                } else {
                    document.getElementById("bub").remove();
                    document.getElementById(
                        "her" + hercounter.toString()
                    ).innerHTML = "Chelsea: " + chelsea_msgs.shift();
                    scrollToBottom();
                    hercounter++;
                    if (chelsea_msgs.length != 0) {
                        newChelseaBubble();
                    } else if (!youHold) {
                        newYouBubble();
                    }
                }
            }
        }, 7000);
    });

    _enter = function(e) {
        if (!e) e = window.event;
        if (e.key == 'Enter') {
            p = document.getElementById("you" + youcounter.toString());
            s = document.getElementById("statement");
            s.display = "none";
            val = s.value;
            p.innerHTML = "You: " + val;
            newChelseaBubble();
            Temperature_Controller_Part_II_enter(val);
        }
    }
}