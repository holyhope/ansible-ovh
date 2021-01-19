# -*- coding: utf-8 -*-


from __future__ import absolute_import, division, print_function

__metaclass__ = type


class ModuleDocFragment(object):

    # Rapi doc fragment
    DOCUMENTATION = r'''

options:
    endpoint:
        description:
            - The endpoint to communicate with ovh. See https://github.com/ovh/python-ovh#configuration
        required: true
    application_key:
        description:
            - The Application key created thanks to https://api.ovh.com/createApp
        required: true
    application_secret:
        description:
            - The Application secret matching the key
        required: true
    consumer_key:
        description:
            - Consumer key used by Ansible o communicate with OVHcloud API.
        required: True
requirements:
    - ovh >= 0.5
'''
