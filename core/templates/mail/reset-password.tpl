{* tempaltes/email/send-mail-confirm.tpl *}
{% extends "mail_templated/base.tpl" %}

{% block subject %}
forgot password
{% endblock %}


{% block html %}
<h1>Hello {{ name }} If you have forgotten your password, click the link below to reset it, otherwise ignore this message </h1>

<a href="{{ url }}" 
   style="background-color: #4CAF50; border: none; color: white; padding: 15px 32px; text-align: center; text-decoration: none; display: inline-block; font-size: 16px; margin: 4px 2px; cursor: pointer; border-radius: 12px; transition: background-color 0.3s;">
   reset password
</a>

{% endblock %}