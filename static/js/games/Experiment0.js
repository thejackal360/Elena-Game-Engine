var bonus_txt = [];
var bonus_idx = -1;
var given_temp = false;
var ready_for_substance_guess = false;
var substance_name = "";
var celsius = -1;

/**
* Play the Experiment0 game. This function will be called by the
* respective module's convo function.
* @param {string} val - the user's answer to the question
*/
function Experiment0(val) {
    if (!given_temp) {
        youHold = true;
        handle_bonus = function(h) {
            bonus_txt = h.responseText.split(',');
            chelsea_msgs.push("Bonus round!");
            chelsea_msgs.push("Here are the " + bonus_txt[0] + " points of different substances...");
            chelsea_msgs.push(bonus_txt[1] + "(" + bonus_txt[2] + "&#176C), " +
                              bonus_txt[3] + "(" + bonus_txt[4] + "&#176C), " +
                              bonus_txt[5] + "(" + bonus_txt[6] + "&#176C)");
            chelsea_msgs.push("Guess one temperature, and I'll tell you whether the substance starts " +
                               bonus_txt[0] + "...");
            bonus_idx = randint(3);
            youHold = false;
            given_temp = true;
        }
        send_http_get_request(handle_bonus,
            "application/json", "bonus");
    } else if (ready_for_substance_guess) {
        let kiwi_inc = false;
        if (scrub_str(val) == scrub_str(substance_name)) {
            chelsea_msgs.push("Correct!");
            inc_kiwi_count(5);
            kiwi_inc = true;
        } else {
            chelsea_msgs.push("Wrong! It's " + substance_name + ".");
        }
        ready_for_substance_guess = false;
        given_temp = false;
        topic = Temperature_Controller_Part_II_randint_topics();
        if (!kiwi_inc) {
            Temperature_Controller_Part_II_convo(val);
        }
    } else {
        if (!isNaN(val)) {
            substance_name = bonus_txt[(bonus_idx * 2) + 1];
            celsius = Number(bonus_txt[(bonus_idx * 2) + 2])
            if (celsius <= val) {
                chelsea_msgs.push("Substance " +
                    ((bonus_txt[0] == "melting") ? "melts" : "boils") +
                    "!"
                );
            } else {
                chelsea_msgs.push("Substance doesn't " +
                    ((bonus_txt[0] == "melting") ? "melt" : "boil") +
                    ".");
            }
            chelsea_msgs.push("What's your best guess? " +
                    bonus_txt[1] + " (" + bonus_txt[2] + "&#176C)," +
                    bonus_txt[3] + " (" + bonus_txt[4] + "&#176C), or " +
                    bonus_txt[5] + " (" + bonus_txt[6] + "&#176C)" + "?");
            ready_for_substance_guess = true;
        } else {
            chelsea_msgs.push("Invalid number. Please enter again.");
        }
    }
}
