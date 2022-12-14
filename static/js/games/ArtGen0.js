var wantsart = false;
var asked = false;
var bioword = "";
var artword = "";
var hitKeyword = false;
var hitKeyword_art = false;
var bioword_arr = [];
var artword_arr = [];
var wantsart = false;

/**
* Play the ArtGen0 game. This function will be called by the
* respective module's convo function.
* @param {string} val - the user's answer to the question
*/
function ArtGen0(val) {
    if (!wantsart) {
        if (!asked) {
            chelsea_msgs.push("Pay 5 kiwis to see a trick? " +
		              "Please answer \"yes\" if you do.");
            asked = true;
        } else {
            let affirmative_score = check_affirmative(val);
            if (affirmative_score == 1) {
                wantsart = true;
                pay_to_play();
            } else {
                wantsart = false;
                topic =
                    Temperature_Controller_Part_II_randint_topics();
            }
            asked = false;
            Temperature_Controller_Part_II_convo(val);
        }
    } else if ((bioword == "") && (artword == "") && hitKeyword) {
        if (!val.match(/(\w+)/g)) {
            chelsea_msgs.push(
                "Please select one of the following: " +
                bioword_arr.join(',')
            );
        } else if (val.match(/(\w+)/g).length != 1) {
            chelsea_msgs.push("Please. Just one word. :)");
        } else {
            if (bioword_arr.includes(val)) {
                chelsea_msgs.push(
                    "Alright. We're going with " + val + "."
                );
                bioword = val;
                hitKeyword = false;
                Temperature_Controller_Part_II_convo(val);
            } else {
                chelsea_msgs.push(
                    "Please select one of the following: " +
                    bioword_arr.join(',')
                );
            }
        }
    } else if ((bioword != "") && (artword == "") && hitKeyword_art) {
        if (!val.match(/(\w+)/g)) {
            chelsea_msgs.push(
                "Please select one of the following: " +
                artword_arr.join(',')
            );
       } else if (val.match(/(\w+)/g).length != 1) {
            chelsea_msgs.push("Please. Just one word. :)");
       } else {
	    if (artword_arr.includes(val)) {
                chelsea_msgs.push(
                    "Alright. We're going with " + val + "."
                );
                chelsea_msgs.push("Give me one moment...");
                artword = val;
                hitKeyword_art = false;
                Temperature_Controller_Part_II_convo(val);
            } else {
                chelsea_msgs.push(
                    "Please select one of the following: " +
                    artword_arr.join(',')
                );
            }
        }
    } else if ((bioword != "") && (artword == "") && !hitKeyword_art) {
        art_word_pick = function (h) {
            chelsea_msgs.push(
                "Alright, now pick one of these words - " +
                h.responseText
            );
            artword_arr = h.responseText.split(",");
            chelsea_msgs.push(
                "Again, please just one word."
            );
            hitKeyword_art = true;
        }
        send_http_get_request(art_word_pick, "text/html",
                              internal_type = "nn_art_art_keyword");
    } else if ((bioword == "") && (artword == "") && !hitKeyword) {
        bio_word_pick = function(h) {
            chelsea_msgs.push(
                "Okay, " + name + "."
            );
            chelsea_msgs.push(
                "Pick one of these words - " + h.responseText
            );
            bioword_arr = h.responseText.split(",");
            chelsea_msgs.push(
                "Just one word. I'm not very good at this right now."
            );
            hitKeyword = true;
        }
        send_http_get_request(bio_word_pick, "application/json",
                                             "nn_art_bio_keyword");
    } else if ((name != "") && (bioword != "") && (artword != "")) {
        get_stylized = function(h) {
            style_url = h.responseText;
            chelsea_msgs.push(
                '<img src="' + style_url + 
                '" onload="scrollToBottom()"/></br>'
            );
            chelsea_msgs.push("Kind of cool, right?");
            bioword = "";
            artword = "";
            wantsart = false;
            topic = Temperature_Controller_Part_II_randint_topics();
            Temperature_Controller_Part_II_convo(val);
            youHold = false;
        }
        youHold = true;
        let request_int = window.setInterval(function() {
            if (chelsea_msgs.length == 0) {
                send_http_post_request(get_stylized,
                                       JSON.stringify({
                                            "style_img" : artword,
                                            "content_img" : bioword
                                       }), "art");
                clearInterval(request_int);
            }
        }, 1000);
    }
}
