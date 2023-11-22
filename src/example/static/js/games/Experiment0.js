var bonus_content = {};
var bonus_txt = "";
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
            bonus_content = h;
            chelsea_msgs.push("Bonus round!");
            chelsea_msgs.push("Here are the " + h["property"] + " points of different substances...");
            bonus_txt = "";
            for (var key in h["materials"]) {
                bonus_txt += key + "(" + h["materials"][key] + "&#176C), ";
            }
            bonus_txt = bonus_txt.slice(0, -2);
            chelsea_msgs.push(bonus_txt);
            chelsea_msgs.push("Guess one temperature, and I'll tell you whether the substance starts " +
                               h["property"] + "...");
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
            let tmp_idx = 0;
            for (var key in bonus_content["materials"]) {
                if (tmp_idx == bonus_idx) {
                    substance_name = key;
                    celsius = Number(bonus_content[key]);
                    break;
                }
                tmp_idx += 1;
            }
            if (celsius <= val) {
                chelsea_msgs.push("Substance " +
                    ((bonus_content["property"] == "melting") ? "melts" : "boils") +
                    "!"
                );
            } else {
                chelsea_msgs.push("Substance doesn't " +
                    ((bonus_content["property"] == "melting") ? "melt" : "boil") +
                    ".");
            }
            chelsea_msgs.push("What's your best guess? " + bonus_txt + "?");
            ready_for_substance_guess = true;
        } else {
            chelsea_msgs.push("Invalid number. Please enter again.");
        }
    }
}
