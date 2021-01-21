from __future__ import absolute_import, division, print_function

__metaclass__ = type

try:
    from typing import TYPE_CHECKING
except ImportError:
    TYPE_CHECKING = False


if TYPE_CHECKING:
    from typing import Optional, Dict, Any

import traceback

from ansible.module_utils.basic import AnsibleModule, missing_required_lib

try:
    import importlib
except ImportError:
    # This passes the sanity import test, but does not provide a user friendly error message.
    # Doing so would require catching Exception for all imports of dependencies in modules and module_utils.
    importlib = None  # type: ignore # noqa


OVH_MIN_RELEASE = '1.32'
HAS_OVH = True
HAS_OVH_EXC = None

try:
    from ovh import client as ovh
except ImportError:
    ovh = object
    ovh.ENDPOINTS = {}
    ovh.Client = object
    HAS_OVH_EXC = traceback.format_exc()
    HAS_OVH = False


COMMON_ARGS = dict(
    endpoint=dict(
        type='str',
        required=True,
        choices=ovh.ENDPOINTS.keys(),
    ),
    application_key=dict(
        type='str',
        required=True,
    ),
    application_secret=dict(
        type='str',
        required=True,
        no_log=True,
    ),
)


class OVHModuleBase(object):
    def __init__(self, derived_arg_spec, bypass_checks=False, no_log=False,
                 check_invalid_arguments=None, mutually_exclusive=None, required_together=None,
                 required_one_of=None, add_file_common_args=False, supports_check_mode=False,
                 required_if=None, facts_module=False, skip_exec=False):

        merged_arg_spec = dict()

        merged_arg_spec.update(COMMON_ARGS)

        if derived_arg_spec:
            merged_arg_spec.update(derived_arg_spec)

        self.module = AnsibleModule(argument_spec=merged_arg_spec,
                                    bypass_checks=bypass_checks,
                                    no_log=no_log,
                                    mutually_exclusive=mutually_exclusive,
                                    required_together=required_together,
                                    required_if=required_if,
                                    required_one_of=required_one_of,
                                    add_file_common_args=add_file_common_args,
                                    supports_check_mode=supports_check_mode)

        self.check_mode = self.module.check_mode

        if not HAS_OVH:
            self.fail(
                msg=missing_required_lib('ovh (ovh >= {0})'.format(OVH_MIN_RELEASE)),
                exception=HAS_OVH_EXC)

        self.facts_module = facts_module

        self.init_results()

        if not skip_exec:
            self.exec_module(**self.module.params)

        self.module.exit_json(**self.results)

    def __getattribute__(self, attribute: str) -> 'Any':
        try:
            return super().__getattribute__(attribute)
        except AttributeError:
            return self.module.params.get(attribute)

    def init_results(self):
        self.results = dict(changed=False)

    def exec_module(self, **kwargs):
        self.fail("Error: {0} failed to implement exec_module method.".format(self.__class__.__name__))

    def set_changed(self, changed: bool):
        self.results['changed'] = changed

    def fail(self, msg, **kwargs):
        '''
        Shortcut for calling module.fail()
        :param msg: Error message text.
        :param kwargs: Any key=value pairs
        :return: None
        '''
        self.module.fail_json(msg=msg, **kwargs)

    def log(self, msg, log_args: 'Optional[Dict[str,Any]]'):
        self.module.log(msg, log_args)

    def debug(self, msg):
        self.module.debug(msg)

    @property
    def client(self) -> ovh.Client:
        return self.delegated_client(self.consumer_key)

    def delegated_client(self, consumer_key: 'Optional[str]' = None) -> ovh.Client:
        return ovh.Client(
            endpoint=self.endpoint,
            application_key=self.application_key,
            application_secret=self.application_secret,
            consumer_key=consumer_key
        )
