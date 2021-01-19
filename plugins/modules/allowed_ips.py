from __future__ import absolute_import, division, print_function

__metaclass__ = type

try:
    from typing import TYPE_CHECKING

    if TYPE_CHECKING:
        from typing import Any, Dict

except ImportError:
    TYPE_CHECKING = False


try:
    import ovh
except ImportError:
    ovh = None


from ansible_collections.holyhope.ovh.plugins.module_utils.authenticated import \
    AuthenticatedOVHModuleBase

ANSIBLE_METADATA = {'metadata_version': '1.1',
                    'status': ['preview'],
                    'supported_by': 'holyhope'}

DOCUMENTATION = '''
---
module: consumer_key
version_added: "0.0.1"
short_description: Manage a consumer key
description:
    - Create/Check/Delete a consumer key.
options:
    ips:
        description:
            - The ips to authorize.
        required: true
    subject_credential_id:
        description:
            - Credential ID to manage.
              If id is None, use consumer_key.
        required: false
extends_documentation_fragment:
    - holyhope.ovh.ovh_api
author:
    - Pierre PÉRONNET <pierre.peronnet@ovhcloud.com>
'''

EXAMPLES = '''
    - name: Create a consumer key
      holyhope.ovh.allowed_ips:
        ips:
        - 127.0.0.1
        consumer_key: "{{ ovh.consumer_key }}"
'''

RETURN = '''
'''


class IPsModule(AuthenticatedOVHModuleBase):
    """Configuration class to manage ips"""

    def __init__(self):
        self.module_arg_spec = dict(
            ips=dict(
                type='list',
                required=True,
            ),
            subject_credential_id=dict(
                type='int',
                required=False,
            ),
        )

        self.subject_credential_id = 0
        self.ips = []

        super().__init__(self.module_arg_spec, supports_check_mode=True)

    def exec_module(self, **kwargs):
        """Main module execution method"""
        creds = self.subject_credential()

        if not self.check(creds):
            self.update(creds)
            self.set_changed(True)

    def subject_credential(self):
        self.debug("Getting consumer key information")

        if self.subject_credential_id is not None:
            return self.client.get('/me/api/credential/%d', self.subject_credential_id)

        return self.client.get('/auth/currentCredential')

    def check(self, credentials: 'Dict[str,Any]') -> bool:
        for ip in credentials['allowedIPs']:
            if ip not in self.ips:
                return False

        for ip in self.ips:
            if ip not in credentials['allowedIPs']:
                return False

        return True

    def update(self):
        '''
        Gets the properties of the specified cluster.
        :return: cluster state dictionary
        '''
        self.debug("Updating consumer key allowed ips")

        self.client.put('/me/api/credential/%d' % self.subject_credentials_id, body=dict(
            allowedIPs=self.ips,
        ))


def main():
    """Main execution"""
    IPsModule()


if __name__ == '__main__':
    main()
