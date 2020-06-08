{% block qrp %}
  {
    "handover_token": "{{ spec['handover_token']  if 'handover_token' in spec else '' }}",
    "src_uri": "{{ spec['src_uri'] if 'src_uri' in spec else ''}}",
    "status": true,
    "completed_jobs": [],
    "current_job" : {},
    "error" : "",
    "ENS_VERSION": "{{ spec['ENS_VERSION'] if 'ENS_VERSION' in spec else '' }}",
    "EG_VERSION": "{{ spec['EG_VERSION'] if spec['EG_VERSION'] else ''}}",
    "contact": "{{ spec['contact'] if 'contact' in spec else '' }}",
    "comment": "{{ spec['comment'] if 'comment' in spec else ''}}",
    "user":  "{{spec['user'] if 'user' in spec else ''}}",  {# remember the , #}
    {% block pipeline %}
    {% endblock pipeline %}
 }
{% endblock qrp %}