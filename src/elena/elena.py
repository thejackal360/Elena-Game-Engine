#!/usr/bin/env python3

# Imports

from flask import Flask, Markup, Response, request, render_template
from functools import partial
from jinja2 import Template
import json
import random
import sys

# https://github.com/pallets/flask/blob/main/src/flask/scaffold.py#L36
import typing as t

# Constants/Globals

LOCALHOST = "127.0.0.1"
PORT = 5000
F = t.TypeVar("F", bound=t.Callable[..., t.Any])

# Auxiliary functions


def get_http():
    """
    Warning: Function may need to be changed for non-Heroku PaaS.
    Check request header for whether user is using http or https.
    Return which it is.
    @return: string of either "http" or "https"
    """
    if request.headers.get('X-Forwarded-Proto', 'http') == 'https':
        return "https"
    else:
        return "http"


def dict_stitching(list_of_dicts):
    """
    Create a dictionary from a list of dictionaries such that the
    keys array is the union of each dict's keys array and the
    values array is the union of each dict's values array.
    @param list_of_dicts: list of dictionaries
    @return: the concatenated dictionary
    """
    ks = []
    vs = []
    for d in list_of_dicts:
        ks += list(d.keys())
        vs += list(d.values())
    assert sorted(list(set(ks))) == sorted(ks)
    assert len(ks) == len(vs)
    return dict(zip(ks, vs))

# Core classes


class eFlask(Flask):
    """
    Class used to instantiate app objects.
    """

    def __init__(self, module_list, domain, **kwargs):
        """
        Initializer.
        @param module_list: list of module objects for trivia game
        @param domain: website's domain
        """
        super().__init__(**kwargs)
        self.module_list = module_list
        self.domain = domain
        self.http_post_ptype_to_fn = dict_stitching([
            m.http_post_ptype_to_fn for m in self.module_list])
        self.http_get_ptype_to_fn = dict_stitching([
            m.http_get_ptype_to_fn for m in self.module_list])
        self.trivia_ptype = ["{}_trivia".format(m.fn_module_name)
                             for m in self.module_list]
        self.manual_ptype = ["{}_lab_manual".format(m.fn_module_name)
                             for m in self.module_list]
        self.trivia_qs = {}
        for m in self.module_list:
            with open("./static/questions/{}_trivia.json".format(
                      m.fn_module_name), "r") as t:
                self.trivia_qs["{}_trivia".format(
                               m.fn_module_name)] = json.load(t)
        self.gen_elenajs()

    def eroute(self, rule: str, **options: t.Any) -> t.Callable[[F], F]:
        # https://github.com/pallets/flask/blob/main/src/flask/scaffold.py#L36
        """Decorate a view function to register it with the given URL
        rule and options. Calls :meth:`add_url_rule`, which has more
        details about the implementation.

        .. code-block:: python

            @app.route("/")
            def index():
                return "Hello, World!"

        See :ref:`url-route-registrations`.

        The endpoint name for the route defaults to the name of the view
        function if the ``endpoint`` parameter isn't passed.

        The ``methods`` parameter defaults to ``["GET"]``. ``HEAD`` and
        ``OPTIONS`` are added automatically.

        :param rule: The URL rule string.
        :param options: Extra options passed to the
            :class:`~werkzeug.routing.Rule` object.
        """

        def decorator(f: F) -> F:
            def _f(): return partial(f, mod=self)()
            endpoint = options.pop("endpoint", None)
            self.add_url_rule(rule, endpoint, _f, **options)
            return _f

        return decorator

    def gen_elenajs(self):
        """
        For each module, generate an elena.js file from template.
        """
        for m in self.module_list:
            elena_template_txt = ""
            with open("templates/elena.js", "r") as f:
                elena_template_txt = f.read()
            elena_template = Template(elena_template_txt)
            with open(m.elenajs, "w") as f:
                f.write(elena_template.render(module_name=m.fn_module_name,
                                              module_name_in_quotes="\""+m.fn_module_name +
                                              "\""))

    def gen_pick_mod(self):
        """
        Generate HTML markup for bubbles on the module select page,
        one for each module.
        @return: return markup
        """
        return "\n".join(["\t\t<p class=\"modsel\" " +
                          " onclick=\"{}_start_lab()\">{}".format(
                              m.fn_module_name, m.module_name) +
                          "</p></br></br>"
                          for m in self.module_list])

    def handle_requests(self):
        """
        Handle incoming HTTP request
        @return: outgoing HTTP response
        """
        if request.method == 'POST':
            return self.handle_POST()
        elif request.method == 'GET':
            return self.handle_GET()

    def handle_POST(self):
        """
        Handle incoming POST request
        @return: the HTTP response
        """
        if request.headers.get("Internal-Type") in \
                self.http_post_ptype_to_fn.keys():
            return self.http_post_ptype_to_fn[
                request.headers.get('Internal-Type')]()
        else:
            assert False

    def handle_GET(self):
        """
        Handle incoming GET request
        @return: the HTTP response
        """
        if request.headers.get('Internal-Type') in self.trivia_ptype:
            qdict = self.trivia_qs[
                request.headers.get('Internal-Type')]
            q = random.choice(list(qdict.keys()))
            return Response("[\"{}\",\"{}\"]".format(q, qdict[q]),
                            mimetype='text/html')
        elif request.headers.get('Internal-Type') in self.manual_ptype:
            with open("static/html/{}.html".format(
                      request.headers.get('Internal-Type')), "r") as f:
                return Response(f.read(), mimetype="text/html")
        elif request.headers.get('Internal-Type') \
                in self.http_get_ptype_to_fn.keys():
            return self.http_get_ptype_to_fn[
                request.headers.get('Internal-Type')]()
        else:
            http = get_http()
            gamejs = Markup("\n".join([
                m.gamejs() for m in self.module_list]))
            elenajs = Markup("\n".join([
                m.elenajs_script() for m in self.module_list]))
            module_js_globals = Markup("\n".join([
                "\t\t<script src=\"static/js/games/" +
                "{}_js_globals.js\" ".format(m.fn_module_name) +
                "type=\"application/javascript\"></script>"
                for m in self.module_list]))
            module_subjs = Markup("\n".join([
                "\t\t<script src=\"static/js/games/" +
                "{}_subjs.js\" ".format(m.fn_module_name) +
                "type=\"application/javascript\"></script>"
                for m in self.module_list]))
            return render_template('index.html',
                                   domain=http + "://" + LOCALHOST +
                                   ":" + str(PORT) + "/"
                                   if "--local" in sys.argv
                                   else http + "://" + self.domain,
                                   gamejs=gamejs,
                                   elenajs=elenajs,
                                   module_js_globals=module_js_globals,
                                   module_subjs=module_subjs,
                                   pick_mod=Markup(
                                       self.gen_pick_mod()))


class Module:
    """
    Class for a trivia module.
    """

    def __init__(self, module_name, game_list):
        """
        Initializer.
        @param module_name: name of the trivia module
        @param game_list: list of game objects associated with
        trivia module
        """
        self.module_name = module_name
        self.fn_module_name = module_name.replace(" ", "_")
        self.game_list = game_list
        self.elenajs = "static/js/games/{}_elena.js".format(
                       self.module_name)
        self.gen_subjs()
        self.gen_jsglobals()
        self.http_post_ptype_to_fn = dict_stitching([
            g.http_post_ptype_to_fn for g in self.game_list])
        self.http_get_ptype_to_fn = dict_stitching([
            g.http_get_ptype_to_fn for g in self.game_list])

    def gen_subjs(self):
        """
        Generate a subjs file for the module. subjs file contains
        a function for selecting a game.
        """
        with open("static/js/games/{}_subjs.js".format(
                self.fn_module_name), "w") as f:
            f.write("function {}_subjs(topic, val) ".format(
                self.fn_module_name) + "{\n")
            f.write("\tswitch (topic) {\n")
            [f.write("\t\tcase {}{}Topic: {}(val); ".format(
                     self.fn_module_name, g.gname, g.gname) +
                     "break;\n") for g in self.game_list]
            f.write("\t\tdefault: /* do nothing */;\n")
            f.write("\t}\n")
            f.write("}")

    def gen_jsglobals(self):
        """
        Generate a jsglobals file for the module. jsglobals file
        defines constants for use in selecting games.
        """
        with open("static/js/games/{}_js_globals.js".format(
                self.fn_module_name), "w") as f:
            f.write("const {}{}Topic = 0;\n".format(
                self.fn_module_name, "Trivia"))
            [f.write("const {}{}Topic = {};\n".format(
                     self.fn_module_name, v.gname, i+1))
             for i, v in enumerate(self.game_list)]
            f.write("const {}NumTopics = {};".format(
                self.fn_module_name, len(self.game_list)+1))

    def elenajs_script(self):
        """
        Generate HTML markup for importing this module's elena.js
        file.
        """
        return '\t<script src="{}" '.format(self.elenajs) + \
               'type="application/javascript"></script>'

    def gamejs(self):
        """
        Generate HTML markup for importing each game's elena.js
        file. Note that each game must be uniquely named. Thus,
        two different modules cannot have a game of the same name.
        """
        return "\n".join([g.get_gamesrc() for g in self.game_list])


class Game:
    """
    Class for a game.
    """

    def __init__(self, gname, http_post_ptype_to_fn={},
                 http_get_ptype_to_fn={}):
        """
        Initializer.
        @param gname: Game name
        @param http_post_ptype_to_fn: packet type name to
        function dictionary (POST requests)
        @param http_post_ptype_to_fn: packet type name to
        function dictionary (GET requests)
        """
        self.gname = gname
        self.jsfile = "static/js/games/{}.js".format(self.gname)
        self.http_post_ptype_to_fn = http_post_ptype_to_fn
        self.http_get_ptype_to_fn = http_get_ptype_to_fn

    def get_gamesrc(self):
        """
        Generate HTML markup for importing the game's js file.
        The user must draft the game's js file.
        """
        return '\t<script src="{}" '.format(self.jsfile) + \
               'type="application/javascript"></script>'
