from __future__ import absolute_import, division, print_function

__metaclass__ = type

try:
    from typing import TYPE_CHECKING

    if TYPE_CHECKING:
        from typing import Dict, List, Optional
except ImportError:
    TYPE_CHECKING = False

try:
    import ovh
except ImportError:
    ovh = None

try:
    from warnings import warn
except ImportError:
    def warn(*args, **kwargs):  # type: ignore
        None

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
    - name: Get a consumer key
      holyhope.ovh.consumer_key:
        application_key: abcde
        application_secret: abcde
        consumer_key: abcde
      register: ovh

    - name: Get a consumer key from credential id
      holyhope.ovh.consumer_key:
        application_key: abcde
        application_secret: abcde
        consumer_key: abcde
        subject_credential_id: 1234
      register: ovh
'''

RETURN = '''
state:
    description:
        - The credential state.
    returned: if credential is valid
    type: str
    sample: validated
credential_id:
    description:
        - The id of the credential.
    returned: if credential is valid and subject_credential_id is not None
    type: int
    sample: 1234
accesses:
    description:
        - The accesses to request.
    returned: if credential is valid
    type: dict
    sample: {"/me/*": ["GET"]}
'''


class ConsumerKeyModule(AuthenticatedOVHModuleBase):
    """Configuration class for a consumer key"""

    def __init__(self):
        self.module_arg_spec = dict(
            subject_credential_id=dict(
                type='int',
                required=False,
            ),
        )

        super().__init__(self.module_arg_spec, supports_check_mode=True)

    def exec_module(self, **kwargs):
        """Main module execution method"""
        creds = self.subject_credential()

        self.update_results(
            creds['status'],
            creds['credentialId'],
            self._transform_accesses(creds['rules'])
        )

    def subject_credential(self):
        default_value = dict(
            status=None,
            credentialId=None,
            rules=None,
        )

        if self.subject_credential_id is not None:
            default_value.update(self.client.get('/me/api/credential/%d', self.subject_credential_id))
            return default_value

        try:
            default_value.update(self.client.get('/auth/currentCredential'))
            return default_value
        except ovh.InvalidCredential as e:
            warn("invalid credentials", RuntimeWarning, source=e)
            return default_value

    def update_results(self, state: 'Optional[str]', credential_id: 'Optional[int]',
                       accesses: 'Optional[Dict[str,List[str]]]'):
        self.results = dict(
            state=state,
            credential_id=credential_id,
            accesses=accesses,
        )

    def _transform_accesses(self, rules: 'List[Dict[str,str]]') -> 'Dict[str,List[str]]':
        accesses: 'Dict[str,List[str]]' = {}

        if not rules:
            return accesses

        for rule in rules:
            path, method = rule['path'], rule['method']

            if path not in accesses:
                accesses[path] = [method]
            else:
                accesses[path].append(method)

        return accesses


def main():
    """Main execution"""
    ConsumerKeyModule()


if __name__ == '__main__':
    main()
