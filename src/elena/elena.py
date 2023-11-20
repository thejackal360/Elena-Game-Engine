#!/usr/bin/env python3

# Imports

from flask import Flask, Response, request, render_template
from functools import partial
from itertools import chain
from jinja2 import Environment, FileSystemLoader, Template
from pathlib import Path
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
    if request.headers.get("X-Forwarded-Proto", "http") == "https":
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

    def __init__(
        self,
        module_list,
        domain,
        kiwi_cost_to_play_game=5,
        ask_for_game_every_N_rounds=3,
        bouncing_text=True,
        **kwargs,
    ):
        """
        Initializer.
        @param module_list: list of module objects for trivia game
        @param domain: website's domain
        @param kiwi_cost_to_play_game: how many kiwis does it cost to play a game? default value is 5
        @param ask_for_game_every_N_rounds: minimum number of rounds between games; default value is 3
        @param bouncing_text: controls whether textboxes are animated to bounce up and down; default value is True
        """
        super().__init__(**kwargs)
        self.module_list = module_list
        self.domain = domain
        self.kiwi_cost_to_play_game = kiwi_cost_to_play_game
        self.ask_for_game_every_N_rounds = ask_for_game_every_N_rounds
        self.bouncing_text = bouncing_text
        self.http_post_ptype_to_fn = dict_stitching(
            [m.http_post_ptype_to_fn for m in self.module_list]
        )
        self.http_get_ptype_to_fn = dict_stitching(
            [m.http_get_ptype_to_fn for m in self.module_list]
        )
        self.trivia_ptype = [
            "{}_trivia".format(m.fn_module_name) for m in self.module_list
        ]
        self.manual_ptype = [
            "{}_lab_manual".format(m.fn_module_name) for m in self.module_list
        ]
        self.trivia_qs = {}
        for m in self.module_list:
            with open(
                Path("static/questions/") / "{}_trivia.json".format(m.fn_module_name),
                "r",
            ) as t:
                self.trivia_qs["{}_trivia".format(m.fn_module_name)] = json.load(t)
        self.gen_elenajs()
        self.gen_elena_top_js()
        self.gen_css()

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
            def _f():
                return partial(f, mod=self)()

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
            with open(Path("templates/elena.js"), "r") as f:
                elena_template_txt = f.read()
            elena_template = Template(elena_template_txt)
            with open(m.elenajs, "w") as f:
                f.write(
                    elena_template.render(
                        module_name=m.fn_module_name,
                        module_name_in_quotes='"' + m.fn_module_name + '"',
                    )
                )

    def gen_elena_top_js(self):
        """
        Generate a subjs file for the module. subjs file contains
        a function for selecting a game.
        """
        env = Environment(loader=FileSystemLoader("."))
        template = env.get_template("templates/elena_top.js")
        rendered_content = template.render(
            kiwi_cost_to_play_game=self.kiwi_cost_to_play_game,
            ask_for_game_every_N_rounds=self.ask_for_game_every_N_rounds,
        )
        with open("static/js/elena_top.js", "w") as f:
            f.write(rendered_content)

    def gen_css(self):
        """
        Generate a subjs file for the module. subjs file contains
        a function for selecting a game.
        """
        env = Environment(loader=FileSystemLoader("."))
        template = env.get_template("templates/elena.css")
        rendered_content = template.render(bouncing_text=self.bouncing_text)
        with open("static/css/elena.css", "w") as f:
            f.write(rendered_content)

    def handle_requests(self):
        """
        Handle incoming HTTP request
        @return: outgoing HTTP response
        """
        if request.method == "POST":
            return self.handle_POST()
        elif request.method == "GET":
            return self.handle_GET()

    def handle_POST(self):
        """
        Handle incoming POST request
        @return: the HTTP response
        """
        if request.headers.get("Internal-Type") in self.http_post_ptype_to_fn.keys():
            return self.http_post_ptype_to_fn[request.headers.get("Internal-Type")]()
        else:
            assert False

    def handle_GET(self):
        """
        Handle incoming GET request
        @return: the HTTP response
        """
        if request.headers.get("Internal-Type") in self.trivia_ptype:
            qdict = self.trivia_qs[request.headers.get("Internal-Type")]
            q = random.choice(list(qdict.keys()))
            return Response('["{}","{}"]'.format(q, qdict[q]), mimetype="text/html")
        elif request.headers.get("Internal-Type") in self.manual_ptype:
            with open(
                Path("static/html/")
                / "{}.html".format(request.headers.get("Internal-Type")),
                "r",
            ) as f:
                return Response(f.read(), mimetype="text/html")
        elif request.headers.get("Internal-Type") in self.http_get_ptype_to_fn.keys():
            return self.http_get_ptype_to_fn[request.headers.get("Internal-Type")]()
        else:
            http = get_http()
            js_files = list(
                chain(*[[g.jsfile for g in m.game_list] for m in self.module_list])
            )
            elenajs = list([m.elenajs for m in self.module_list])
            module_js_globals = [
                "static/js/games/{}_js_globals.js".format(m.fn_module_name)
                for m in self.module_list
            ]
            module_subjs = [
                "static/js/games/{}_subjs.js".format(m.fn_module_name)
                for m in self.module_list
            ]
            pick_mod = {m.fn_module_name: m.module_name for m in self.module_list}
            return render_template(
                "index.html",
                domain=http + "://" + LOCALHOST + ":" + str(PORT) + "/"
                if "--local" in sys.argv
                else http + "://" + self.domain,
                js_files=js_files,
                elenajs=elenajs,
                module_js_globals=module_js_globals,
                module_subjs=module_subjs,
                pick_mod=pick_mod,
            )


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
        self.elenajs = Path("static/js/games/") / "{}_elena.js".format(self.module_name)
        self.gen_subjs()
        self.gen_jsglobals()
        self.http_post_ptype_to_fn = dict_stitching(
            [g.http_post_ptype_to_fn for g in self.game_list]
        )
        self.http_get_ptype_to_fn = dict_stitching(
            [g.http_get_ptype_to_fn for g in self.game_list]
        )

    def gen_subjs(self):
        """
        Generate a subjs file for the module. subjs file contains
        a function for selecting a game.
        """
        env = Environment(loader=FileSystemLoader("."))
        template = env.get_template("templates/subjs.js")
        rendered_content = template.render(
            fn_module_name=self.fn_module_name,
            game_list=[g.gname for g in self.game_list],
        )
        with open(f"static/js/games/{self.fn_module_name}_subjs.js", "w") as f:
            f.write(rendered_content)

    def gen_jsglobals(self):
        """
        Generate a jsglobals file for the module. jsglobals file
        defines constants for use in selecting games.
        """
        env = Environment(loader=FileSystemLoader("."))
        template = env.get_template("templates/jsglobals.js")
        rendered_content = template.render(
            fn_module_name=self.fn_module_name,
            game_list=[g.gname for g in self.game_list],
        )
        with open(f"static/js/games/{self.fn_module_name}_js_globals.js", "w") as f:
            f.write(rendered_content)


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
        @param http_post_ptype_to_fn: packet type name to
        function dictionary (GET requests)
        """
        self.gname = gname
        self.jsfile = Path("static/js/games/") / "{}.js".format(self.gname)
        self.http_post_ptype_to_fn = http_post_ptype_to_fn
        self.http_get_ptype_to_fn = http_get_ptype_to_fn
