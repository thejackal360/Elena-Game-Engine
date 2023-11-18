const {fn_module_name}TriviaTopic = 0;
{% for i in range(len(game_list)) %}
const {fn_module_name}{game_list[i]}Topic = {i+1};
{% endfor %}
const {fn_module_name}NumTopics = {len(game_list) + 1};