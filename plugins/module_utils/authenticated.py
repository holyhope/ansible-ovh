from __future__ import absolute_import, division, print_function

__metaclass__ = type

try:
    import importlib
except ImportError:
    # This passes the sanity import test, but does not provide a user friendly error message.
    # Doing so would require catching Exception for all imports of dependencies in modules and module_utils.
    importlib = None  # type: ignore # noqa


from ansible_collections.holyhope.ovh.plugins.module_utils.common import \
    OVHModuleBase

try:
    from ovh import client as ovh
except ImportError:
    ovh = object
    ovh.Client = object


COMMON_ARGS = dict(
    consumer_key=dict(
        type='str',
        required=True,
        no_log=True,
    ),
)


class AuthenticatedOVHModuleBase(OVHModuleBase):
    def __init__(self, derived_arg_spec, *args, **kwargs):

        merged_arg_spec = dict()

        merged_arg_spec.update(COMMON_ARGS)

        if derived_arg_spec:
            merged_arg_spec.update(derived_arg_spec)

        return super().__init__(derived_arg_spec=merged_arg_spec, *args, **kwargs)

    @property
    def client(self) -> ovh.Client:
        return self.delegated_client(self.consumer_key)
