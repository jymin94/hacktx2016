from flask import Flask, render_template, request
import requests

# [START config]
MAILGUN_DOMAIN_NAME = 'mg.pushnote.com'
MAILGUN_API_KEY = 'key-fb23139ac9cbb10c7f42a9f72a62529c'
# [END config]

# [START simple_message]
def send_simple_message(to):
    print("wtf")
    url = 'https://api.mailgun.net/v3/{}/messages'.format(MAILGUN_DOMAIN_NAME)
    auth = ('api', MAILGUN_API_KEY)
    data = {
        'from': 'Mailgun User <postmaster@{}>'.format(MAILGUN_DOMAIN_NAME),
        'to': to,
        'subject': 'Simple Mailgun Example',
        'text': 'Plaintext content',
    }

    response = requests.post(url, auth=auth, data=data)
    print(response)
    response.raise_for_status()
# [END simple_message]

send_simple_message('Jiyoung Min <jymin94@gmail.com>')
