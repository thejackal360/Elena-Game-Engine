function {{fn_module_name}}_subjs(topic, val) {
    switch (topic) {
        {% for gname in game_list %}
        case {{fn_module_name}}{{gname}}Topic:
            {{gname}}(val);
            break;
        {% endfor %}
        default: /* do nothing */;
    }
}