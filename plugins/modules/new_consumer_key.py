from __future__ import absolute_import, division, print_function

__metaclass__ = type

try:
    from typing import TYPE_CHECKING

    if TYPE_CHECKING:
        from typing import Dict, List
except ImportError:
    TYPE_CHECKING = False

try:
    import ovh
except ImportError:
    ovh = None

from ansible_collections.holyhope.ovh.plugins.module_utils.common import \
    OVHModuleBase
from ansible_collections.holyhope.ovh.plugins.module_utils.validation import \
    check_type_accesses

ANSIBLE_METADATA = {'metadata_version': '1.1',
                    'status': ['preview'],
                    'supported_by': 'holyhope'}

DOCUMENTATION = '''
---
module: new_consumer_key
version_added: "0.0.1"
short_description: Manage a consumer key
description:
    - Create a consumer key.
options:
    accesses:
        description:
            - The accesses to request.
        required: true
    redirect_url:
        description:
            - The url to redirect to once logged in.
        required: false
extends_documentation_fragment:
    - holyhope.ovh.ovh_api
author:
    - Pierre PÉRONNET <pierre.peronnet@ovhcloud.com>
'''

EXAMPLES = '''
    - name: Create a consumer key
      holyhope.ovh.new_consumer_key:
        accesses:
          '/me/*': ["GET"]
      register: ovh
'''

RETURN = '''
consumer_key:
    description:
        - The consumer key.
    returned: always
    type: str
    sample: abcdef
validation_url:
    description:
        - The url to validate the consumer key.
    returned: if consumer_key input was empty.
    sample: https://...
'''


class NewConsumerKeyModule(OVHModuleBase):
    """Configuration class for a consumer key"""

    def __init__(self):
        self.module_arg_spec = dict(
            accesses=dict(
                type=check_type_accesses,
                required=True,
            ),
            redirect_url=dict(
                type='str',
                required=False,
            ),
        )

        super().__init__(self.module_arg_spec, supports_check_mode=True)

    def exec_module(self, **kwargs):
        """Main module execution method"""
        self.debug("Creating the consumer key")

        ck = self.delegated_client(None) \
            .request_consumerkey(self._transform_accesses(self.accesses), self.redirect_url)

        self.update_results(True, ck['consumerKey'], ck['validationUrl'])

    def _transform_accesses(self, accesses: 'Dict[str,List[str]]') -> 'List[Dict[str,str]]':
        rules: 'List[Dict[str,str]]' = []

        if not accesses:
            return rules

        for endpoint, methods in accesses.items():
            for method in methods:
                rules.append({'path': endpoint, 'method': method})

        return rules

    def update_results(self, changed: bool, consumer_key: str, validation_url: str):
        self.set_changed(changed)

        self.results = dict(
            consumer_key=consumer_key,
            validation_url=validation_url,
        )


def main():
    """Main execution"""
    NewConsumerKeyModule()


if __name__ == '__main__':
    main()
