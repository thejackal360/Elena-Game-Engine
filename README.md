Elena is a framework for building chatbot-based education trivia games. Elena provides a Flask-based Python library as well as a set of JavaScript/CSS/HTML files.
Users define modules, which are essentially lessons. For each lesson, the user provides an HTML-based lab manual, which provides the background content.
This may be treated as a description of a step-by-step activity, or it may be treated as standard instructional material for a course. The user also
provides a *.json file listing all of the trivia questions for the module. The user may also write *.js files to describe games that may be played
within the chatbot. The Elena Python library can be used to organize and extend the trivia game.

## Dependencies
The following are the HTML/JS dependencies, included in the provided source code in the `src/elena/` directory:
  - jQuery 3.5.1
  - Buefy
  - Bootstrap 5.1.3
  
The following are the Python dependencies, included in `pyproject.toml` and in
`requirements.txt` (used only for running the example):
  - torch==2.1.0
  - torchvision==0.16.0
  - torchaudio==2.1.0 
  - setuptools_scm >= 2.0.0
  - setuptools >= 40.0.4
  - wheel >= 0.29.0
  - matplotlib==3.5.1'
  - flask==2.0.0
  - gunicorn==21.2.0
  - playwright==1.40.0
  - werkzeug==2.2.2

## Usage

Please see `src/example/app.py` for an example of the Python app file.
Within that file, the most important section of code is the object definitions.
This is where the user organizes the trivia game's structure.

To make sure that the example runs smoothly please install the requirements 
```bash
$ cd src/example
$ pip3 install -r requirements.txt
```

and then run the example
```bash
$ ./app.py --local
```

An automated test of basic user interface functionality is provided. Please
run test.py in the src/example/ directory after installation.


```Python
# Object Definitions

# Create necessary objects for trivia game
mymod0 = Module("Temperature Controller Part I", [])
mymod1 = Module("Temperature Controller Part II", \
                [Game("Experiment0", {}, {'bonus' : bonus}),
                 Game("ArtGen0",
                      {'art' : art},
                      {'nn_art_bio_keyword' : nn_Art_bio_keyword,
                       'nn_art_art_keyword' : nn_Art_art_keyword})])
mymod2 = Module("Bacterial Culture", [])
app = eFlask([mymod0, mymod1, mymod2], DOMAIN_NAME, 
             import_name=__name__)
```

Most requests will be routed through a root route:
```Python
@app.eroute('/', methods=['POST', 'GET'])
def root(mod):
    """
    The root route. The basic route for all incoming HTTP requests.
    @param mod: your eFlask object, app
    @return: the HTTP response, depending on the request
    """
    print("Serving index.html!")
    return mod.handle_requests()
```

The bare minimum for an app.py file is the following:
- At least one Module object
- An eFlask object
- A root route

Below is a barebones app.py file for a very basic app. DOMAIN_NAME is left blank
since it isn't necessary for purely local runs:
```
#!/usr/bin/env python3

from elena import eFlask, Module

DOMAIN_NAME = ""

mymod = Module("Sample", [])
app = eFlask([mymod], DOMAIN_NAME, import_name="Import")

@app.eroute('/', methods=['POST', 'GET'])
def root(mod):
    """
    The root route. The basic route for all incoming HTTP requests.
    @param mod: your eFlask object, app
    @return: the HTTP response, depending on the request
    """
    print("Serving index.html!")
    return mod.handle_requests()

if __name__ == "__main__":
    app.run(debug=True)
```

A "local run" is when the user is hosting and accessing the server on
localhost. In other words, the server is hosted on the same machine that
is accessing it.

## Install/Project Configuration

You can install Elena through pip
```bash
$ pip install elena-game-engine==0.0.1
```
or you can clone this repository and then manually install it by
executing the following commands
```bash
$ git clone https://github.com/thejackal360/Elena-Game-Engine.git
$ cd Elena-Game-Gngine
$ pip install .
```

To create a new Elena-based project, install the Elena library as described
above and then run the `elena_create_project.py`.

You can do the same manually instead of using the automated tool. 
Create a new directory elsewhere for your new Elena-based project. Copy over
the following files/directories:
- elena/static/ and elena/templates/ to static/ and templates/ in the new directory

If you plan on deploying on Heroku, these additional files should also be copied:
- Procfile: used for starting the server on Heroku
- runtime.txt: used to set Python version for Heroku
- wsgi.py: top-level server file for Heroku

Be sure to write an app.py file as well using the one in `src/example/app.py
as an example. And do not forget to install all the requirements your application
might need. 

All lab manuals should be HTML files (excluding <body> and <html> tags). Those will go in static/html/. The naming convention is (module name)_lab_manual.html.
Replace the spaces in (module name) with underscores. Please see static/html/ for examples.
  
All trivia questions are json files mapping questions to answers. Please see static/questions/ in this repo for examples. The naming convention is (module_name)_trivia.json. Replace the spaces in (module name) with underscores.

## Mini-Games

Mini-games are interactive game modules within the trivia loop. Users pay points to play mini-games at random points throughout the trivia session. This enables elena-based trivia games to support more complex behavior to keep users engaged. Mini-games are implemented as JavaScript functions that take a single argument, the user's response. Here is an example from the example application provided:

```JavaScript
/**
* Play the Experiment0 game. This function will be called by the
* respective module's convo function.
* @param {string} val - the user's answer to the question
*/
function Experiment0(val) {
    ...
}
```
  
Any mini-game files go in static/js/games. See static/js/games in this repo for examples. The generated subjs and jsglobals files will also go here. However, since those are generated by the Elena Python library, you don't need to think about them. The naming convention for the mini-game files is (game name).js. Please do not give games names with spaces. The game file should contain a function with a val argument. The function should have the same name as the game file. val is a string, whose value is simply the last value the user entered in their textbox.

On the Python side, mini-games are instantiated using the Game class. Game objects are provided to the corresponding Module object. Please see the "Object Definitions" code sample above.

The game class has the following skeleton:

```Python
class Game:
    """
    Class for a game.
    """

    def __init__(self, gname, http_post_ptype_to_fn={}, http_get_ptype_to_fn={}):
        """
        Initializer.
        @param gname: Game name
        @param http_post_ptype_to_fn: packet type name to
        function dictionary (POST requests)
        @param http_get_ptype_to_fn: packet type name to
        function dictionary (GET requests)
        """
```

The gname argument should simply be the name of the corresponding game JavaScript file without the *.js extension nor the parent path.

Mini-games can interact with the server via HTTP requests. On the JavaScript client side, users can use the send_http_get_request and send_http_post_request functions to send requests. On the Python server side, instantiate the Game object with the http_post_ptype_to_fn and http_get_ptype_to_fn dictionaries. These dictionaries map the packet type name for a particular request to the function that handles them. The corresponding handler functions should return Flask Response objects that will ultimately be sent back to the client. Please see the example application (src/example/app.py) and the corresponding mini-game JavaScript files (src/example/static/js/games/ArtGen0.js and src/example/static/js/games/Experiment0.js).

## Platforms Tested

The following are the browser/OS combinations on which the deployed Heroku site has been tested:

- Windows 10
  - Firefox 99.0.1

It should be noted that we have only hosted the app on Heroku 20. We are not actively providing Heroku support at this time.

Local runs have been tested on the following platforms:
- Ubuntu 20.04.4 LTS
  - Firefox 99.0

- macOS 12.5
  - Firefox 104.01
  - Opera 90.0.4480.84

In order to locally run the server for the example in this repo, run the following command in the root directory:
```
$ ./app.py --local
```

Note that the software thus far is only expected to work on a desktop/laptop web browser. Mobile platforms are not officially supported.

## Style Transfer ML Software

For generating images with various styles we use an implementation of a 
[fast-neural-style](https://github.com/rrmina/fast-neural-style-pytorch) algorithm
in Pytorch. The copyrights for the fast-neural-style-pytorch implementation
are retained by Rusty Mina. A full license note can be found in the `/static/ml/`
directory.

This image generation algorithm is not a core part of the Elena engine. It is
included as part of an example game. See app.py for more details.

## Bubble Design and Style Crediting

We modified a publicly available floating bubble [design](https://codepen.io/kirstenallen/pen/MWwPYYm)
that is used extensively throughout the game. We also borrowed a code [snippet](https://www.arungudelli.com/tutorial/css/disable-text-selection-in-html-using-user-select-css-property/#:~:text=To%20disable%20text%20selection%20highlighting%20in%20Google%20Chrome%20browser%20using,select%20CSS%20property%20to%20none.) for getting rid of text
selecting in the back button. The original authors retain all rights for these snippets. If you suspect that you
have a copyright claim to any portion of the design, feel free to contact us to cite or remove your code.
