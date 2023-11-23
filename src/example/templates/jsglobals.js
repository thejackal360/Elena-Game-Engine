const {{fn_module_name}}TriviaTopic = 0;
{% for i in range(game_list | length) %}
const {{fn_module_name}}{{game_list[i]}}Topic = {{i+1}};
{% endfor %}
const {{fn_module_name}}NumTopics = {{(game_list | length) + 1}};