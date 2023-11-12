#!/usr/bin/env python3

# elena Sample App

# Imports
import random
import json
from pathlib import Path
import numpy as np
import os
import time
from matplotlib import pyplot as plt
from flask import request, Response, send_from_directory
from PIL import Image
from static.ml.stylize import stylize
from elena import eFlask, Module, Game

# Constants

DOMAIN_NAME = "elena-heroku.herokuapp.com"
NN_ART_MUTEX = False
stylized_img_idx = 0

# Function Definitions

def bonus():
    """
    Trivia bonus round. Users need to guess the material of interest
    based on information of a physical property.
    The game is partly up to chance. Used in Experiment0 game.
    @return: HTTP response containing JSON string with the property
    name and list of materials
    """
    bonus_str_src_arr = random.choice(bonus_qs)
    bonus_str = [bonus_str_src_arr["property"]]
    mat_arr = bonus_str_src_arr["materials"]
    for i in range(0, len(mat_arr.keys())):
        key = list(mat_arr.keys())[i]
        bonus_str.append(key)
        bonus_str.append(mat_arr[key])
    bonus_str = str(bonus_str).replace(
        "'", "").replace("[", "").replace("]", "")
    return Response(bonus_str, mimetype='application/json')

def nn_Art_art_keyword():
    """
    For the ArtGen0 game, send 3 art-related keywords back to the user.
    @return: a list of 3 art-related keywords
    """
    art_pic_names = []
    # Need to keep track of number of iterations and kill runaway
    # requests to preserve cloud bandwidth.
    styles_lst = ['lazy', 'mosaic', \
                  'wave', 'bayanihan', 'ghoul']
    count = 0
    max_count = 5
    while len(art_pic_names) < 3:
        if count > max_count:
            return
        a = random.choice(styles_lst)
        if a not in art_pic_names:
            assert a != ""
            art_pic_names.append(a)
        count += 1
    art_pic_names = [Path(a).stem for a in art_pic_names]
    art_pic_names = ','.join(art_pic_names)
    return Response(art_pic_names, mimetype='text/html')

def nn_Art_bio_keyword():
    """
    For the ArtGen0 game, send 3 bio-related keywords back to the user.
    @return: a list of 3 bio-related keywords
    """
    bio_pic_names = []
    count = 0
    max_count = 5
    while len(bio_pic_names) < 3:
        if count > max_count:
            return
        b = random.choice(
            [f for f in
                os.popen("ls static/content_images/")\
                  .read().split("\n")
                if f not in bio_pic_names and f != ""])
        if b not in bio_pic_names:
            assert b != ""
            bio_pic_names.append(b)
    bio_pic_names = [Path(b).stem for b in bio_pic_names]
    bio_pic_names = ','.join(bio_pic_names)
    return Response(bio_pic_names, mimetype='text/html')

def art():
    """
    Given the user's selected art-related and bio-related keywords,
    generate a synthesized image satisfying both.
    @return: link to the generated image file
    """
    global NN_ART_MUTEX
    global stylized_img_idx
    while NN_ART_MUTEX:
        time.sleep(3)
    NN_ART_MUTEX = True
    post_body = json.loads(request.data)
    c = "static/content_images/" + post_body["content_img"] + ".png"
    s = "static/style_images/" + post_body["style_img"] + ".jpg"
    content_img = load_img_cv(c)
    stylized_img = stylize(content_img, style=post_body['style_img'])
    # Required to run on Heroku. Heroku's filesystem frequently deletes
    # directories.
    os.system("mkdir -p static/gen_imgs/")
    plt.imsave("static/gen_imgs/stylized_img" +
               str(stylized_img_idx) + ".png", \
               np.squeeze(stylized_img))
    stylized_img_idx += 1
    NN_ART_MUTEX = False
    return Response("static/gen_imgs/stylized_img"
                    + str(stylized_img_idx - 1)
                    + ".png", mimetype="text/html")


def load_img_cv(img_path):
    """
    Load an image as a numpy array
    @param img_path: string of path to image file
    @return: numpy array
    """
    im = Image.open(img_path)
    if im.mode != 'RGB':
        im = im.convert('RGB')
    return np.array(im)


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

# Load the bonus questions into a global bonus_qs variable
with open("./static/questions/bonus_round.csv", "r") as b:
    bonus_qs = eval(b.read())


# Routes

@app.eroute('/', methods=['POST', 'GET'])
def root(mod):
    """
    The root route. The basic route for all incoming HTTP requests.
    @param mod: your eFlask object, app
    @return: the HTTP response, depending on the request
    """
    print("Serving index.html!")
    return mod.handle_requests()


# Note: Heroku periodically deletes image files.
# May need to add storage ephemerality for other PaaSs.
@app.route('/static/gen_imgs/<path:filename>')
def gen_img(filename):
    """
    Send users the generated image file based on requested path.
    Used in ArtGen0 game.
    @param filename: name of the generated image file
    @return: HTTP response of generated image file content
    """
    return send_from_directory("static/gen_imgs/", filename)


#@app.before_request
#def firewall():
    """
    Only tested for Heroku PaaS. Check the IP whitelist file
    allowed_ips_list and do nothing if we detect a blacklisted IP.
    """
    #if "--local" not in sys.argv:
    #    with open("allowed_ips_list", "r") as a:
    #        allowed_ips = a.read().split('\n')
    #        if request.headers['X-Forwarded-For'] not in allowed_ips:
    #            abort(403)


if __name__ == "__main__":
    app.run(debug=True)
