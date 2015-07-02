#!/usr/bin/python
# -*- coding: utf-8 -*-

DOCUMENTATION = '''
---
module: typetalk
version_added: "1.6"
short_description: Send a message to typetalk
description:
  - Send a message to typetalk using typetalk API ( http://developers.typetalk.in/ )
options:
  client_id:
    description:
      - OAuth2 client ID
    required: true
  client_secret:
    description:
      - OAuth2 client secret
    required: true
  topic:
    description:
      - topic id to post message
    required: true
  msg:
    description:
      - message body
    required: true
requirements: [ json ]
author: "Takashi Someda (@tksmd)"
'''

EXAMPLES = '''
- typetalk: client_id=12345 client_secret=12345 topic=1 msg="install completed"
'''

import urllib

import urllib2

try:
    import json
except ImportError:
    json = None


def do_request(url, params, headers={}):
    data = urllib.urlencode(params)
    headers = dict(headers, **{
        'User-Agent': 'Ansible/typetalk module',
    })
    return urllib2.urlopen(urllib2.Request(url, data, headers))


def get_access_token(client_id, client_secret):
    params = {
        'client_id': client_id,
        'client_secret': client_secret,
        'grant_type': 'client_credentials',
        'scope': 'topic.post'
    }
    res = do_request('https://typetalk.in/oauth2/access_token', params)
    return json.load(res)['access_token']


def send_message(client_id, client_secret, topic, msg):
    """
    send message to typetalk
    """
    try:
        access_token = get_access_token(client_id, client_secret)
        url = 'https://typetalk.in/api/v1/topics/%d' % topic
        headers = {
            'Authorization': 'Bearer %s' % access_token,
        }
        do_request(url, {'message': msg}, headers)
        return True, {'access_token': access_token}
    except urllib2.HTTPError, e:
        return False, e


def main():

    module = AnsibleModule(
        argument_spec=dict(
            client_id=dict(required=True),
            client_secret=dict(required=True),
            topic=dict(required=True, type='int'),
            msg=dict(required=True),
        ),
        supports_check_mode=False
    )

    if not json:
        module.fail_json(msg="json module is required")

    client_id = module.params["client_id"]
    client_secret = module.params["client_secret"]
    topic = module.params["topic"]
    msg = module.params["msg"]

    res, error = send_message(client_id, client_secret, topic, msg)
    if not res:
        module.fail_json(msg='fail to send message with response code %s' % error.code)

    module.exit_json(changed=True, topic=topic, msg=msg)


# import module snippets
from ansible.module_utils.basic import *
main()