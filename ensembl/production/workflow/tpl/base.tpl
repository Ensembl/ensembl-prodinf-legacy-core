{% block qrp %}
  {
    "handover_token": {{ handover_token  if handover_token else '""' }},
    "src_uri": {{ src_uri if src_uri else '""'}},
    "status": "true",
    "ENS_VERSION": {{ ENS_VERSION if ENS_VERSION else '""' }},
    "EG_VERSION": {{ EG_VERSION if EG_VERSION else '""'}},
    "contact": {{ contact if contact else '""' }},
    "comment": {{ comment if comment else '""'}},
    "user":  {{user if user else '""'}},

    {% block pipeline %}

    {% endblock pipeline %}
 }
{% endblock qrp %}