holyhope.ovh.new_credentials
========================

Create an OVHcloud API credential.

Requirements
------------

- ovh >= 0.5

Role Variables
--------------

- ips: list of ip addresses allowed to use the new credential.
- accesses: map of {endpoint: methods} allowed for the new credential.

- ansible_application_key: application key used by ansible to update allowed ips.
- ansible_application_secret: application secret used by ansible to update allowed ips.
- ansible_consumer_key: consumer key used by ansible to update allowed ips.

- application_key: application key used to create new credential.
- application_secret: application secret used to create new credential.

Dependencies
------------

- ansible.builtin

Example Playbook
----------------

```yaml
---
- hosts: localhost
  connection: local
  roles:
  - role: holyhope.ovh.new_credentials
    vars:
      ansible_application_key: '***'
      ansible_application_secret: '***'
      ansible_consumer_key: '***'
      application_key: '***' # can be the same than ansible_application_key
      application_secret: '***' # can be the same than ansible_application_secret
      endpoint: ovh-eu
      accesses:
        /me:
        - GET
...
```

License
-------

BSD

Author Information
------------------

- Pierre PÉRONNET <pierre.peronnet@ovhcloud.com>
