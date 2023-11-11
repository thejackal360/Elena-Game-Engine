Elena is a framework for building chatbot-based education trivia games. Elena provides a Flask-based Python library as well as a set of JavaScript/CSS/HTML files.
Users define modules, which are essentially lessons. For each lesson, the user provides an HTML-based lab manual, which provides the background content.
This may be treated as a description of a step-by-step activity, or it may be treated as standard instructional material for a course. The user also
provides a *.json file listing all of the trivia questions for the module. The user may also write *.js files to describe games that may be played
within the chatbot. The Elena Python library can be used to organize and extend the trivia game.

## Dependencies
The following are the HTML/JS dependencies, included in the provided source code in the elena/ directory:
  - jQuery 3.5.1
  - Buefy
  - Bootstrap 5.1.3

The following are the Python dependencies, included in requirements.txt:
  - torch==1.10.0+cpu
  - torchvision==0.11.1+cpu
  - torchaudio==0.10.0+cpu 
  - matplotlib == 3.3.4
  - flask == 2.0.0
  - gunicorn

## Usage

Please see app.py for an example of the Python app file. Within that file, the most important section of code is the object definitions.
This is where the user organizes the trivia game's structure.

```
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
```
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

## Install/Project Configuration

To create a new Elena-based project, first install the Elena library and its dependencies from the cloned git repo's root:
```
$ python3 -m pip install -r requirements.txt --user
$ python3 -m pip install . --user
```

Then create a new directory elsewhere for your new Elena-based project. Copy over the following files/directories:
- elena/static/ and elena/templates/ to static/ and templates/ in the new directory

If you plan on deploying on Heroku, these additional files should also be copied:
- Procfile: used for starting the server on Heroku
- runtime.txt: used to set Python version for Heroku
- wsgi.py: top-level server file for Heroku

Be sure to write an app.py file as well using the one in this README as an example.

All lab manuals should be HTML files (excluding <body> and <html> tags). Those will go in static/html/. The naming convention is (module name)_lab_manual.html.
Replace the spaces in (module name) with underscores. Please see static/html/ for examples.
  
All trivia questions are json files mapping questions to answers. Please see static/questions/ in this repo for examples. The naming convention is (module_name)_trivia.json. Replace the spaces in (module name) with underscores.
  
Any game files go in static/js/games. See static/js/games in this repo for examples. The generated subjs and jsglobals files will go here. However, since those are generated by the Elena Python library, you don't need to think about them. The naming convention for the game files is (game name).js. Please do not give games names with spaces. The game file should contain a function with a val argument. The function should have the same name as the game file. val is a string, whose value is simply the last value the user entered in their textbox.

The default domain is "elena-heroku.herokuapp.com". Please change the DOMAIN_NAME constant in app.py to fit your Heroku project's domain.

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

## Bubble Design and Style Crediting

We modified a publicly available floating bubble [design](https://codepen.io/kirstenallen/pen/MWwPYYm)
that is used extensively throughout the game. We also borrowed a code [snippet](https://www.arungudelli.com/tutorial/css/disable-text-selection-in-html-using-user-select-css-property/#:~:text=To%20disable%20text%20selection%20highlighting%20in%20Google%20Chrome%20browser%20using,select%20CSS%20property%20to%20none.) for getting rid of text
selecting in the back button. The original authors retain all rights for these snippets. If you suspect that you
have a copyright claim to any portion of the design, feel free to contact us to cite or remove your code.
