{% macro silver(name) -%}
    delta_scan('../../lake/silver/{{ name }}')
{%- endmacro %}
