from __future__ import absolute_import, division, print_function

__metaclass__ = type

from http import HTTPStatus
from http.server import BaseHTTPRequestHandler, HTTPServer
from uuid import uuid4

from ansible.module_utils.basic import AnsibleModule

try:
    from typing import TYPE_CHECKING

    if TYPE_CHECKING:
        from typing import Optional, Type
except ImportError:
    TYPE_CHECKING = False

ANSIBLE_METADATA = {'metadata_version': '1.1',
                    'status': ['preview'],
                    'supported_by': 'holyhope'}

DOCUMENTATION = '''
---
module: wait_for_request
version_added: "0.0.1"
short_description: Wait for a http request
description:
    - Wait for an http request to a specific port.
options:
    port:
        description:
            - The port to listen.
        required: true
    address:
        description:
            - The address to bind.
        required: false
        default: 0.0.0.0
    response_status:
        description:
            - The status code to respond to the request.
        default: 200
        required: false
    response_headers:
        description:
            - Headers to send to the client.
        default:
            Content-Type: "text/html;charset=utf-8",
            Server: "Ansible - holyhole.ovh.wait_for_request"
    response_body:
        description:
            - The html content to send to the client when requesting the address:port.
        default: Success
        required: false
author:
    - Pierre PÉRONNET <pierre.peronnet@ovhcloud.com>
'''

EXAMPLES = '''
    - name: Wait for a HTTP request on a specific port.
      holyhope.ovh.wait_for_request:
        port: 8080
'''

RETURN = '''
request_id:
    description:
        - The request ID header.
        - The value come from header request and is returned in the header response.
        - The ID is generated if no request_id is found in the request headers.
    type: str
    returned: always
    sample: ddaa609c-028b-4a12-b1db-6cb598af5dc3
method:
    description:
        - The request HTTP method.
    type: str
    returned: always
    sample: GET
path:
    description:
        - The request path.
    type: str
    returned: always
    sample: /the/request/path
client_addr
    description:
        - The ip address which sent the request.
    type: str
    returned: always
    sample: 127.0.0.1
user_agent:
    description:
        - The user agent of the requester.
    type: str
    returned: if specified in the request
    sample: Mozilla/5.0 ...
headers:
    description:
        - The headers from the request.
    type: dict
    returned: always
    sample:
        Host: "localhost:8080"
'''


class WaitForRequestModule(object):
    request_id_header = 'X-Request-ID'
    user_agent_header = 'User-Agent'

    def __init__(self):
        arg_spec = dict(
            port=dict(
                type='int',
                required=True,
            ),
            address=dict(
                type=str,
                required=False,
                default='0.0.0.0'
            ),
            method=dict(
                type=str,
                required=False,
                default='GET'
            ),
            path=dict(
                type=str,
                required=False,
                default=''
            ),
            response_body=dict(
                type=bytes,
                required=False,
                default=b'Success',
            ),
            response_headers=dict(
                type=dict,
                required=False,
            ),
            response_status=dict(
                type=int,
                required=False,
                default=HTTPStatus.OK,
            ),
        )

        self.request: 'Optional[BaseHTTPRequestHandler]' = None

        self.module = AnsibleModule(argument_spec=arg_spec, supports_check_mode=True)
        self.exec()

    def exec(self):
        address = self.module.params.get('address')
        port = self.module.params.get('port')

        with HTTPServer((address, port), self.get_Handler()) as httpd:
            self.module.log("Waiting request", log_args=dict(server_address=httpd.server_address))
            httpd.handle_request()

        self.module.exit_json(
            request_id=self.request_id,
            method=self.request.command,
            path=self.request.path,
            client_addr='%s:%d' % self.request.client_address,
            user_agent=self.request.headers.get(self.user_agent_header),
            headers=dict(self.request.headers)
        )

    def handle(self, request: 'BaseHTTPRequestHandler') -> None:
        self.module.debug('request_received')

        self.request = request

        request.send_response(self.module.params.get('response_status'))

        headers = self.module.params.get('response_headers')

        if headers is not None:
            for k, v in headers.items():
                request.send_header(k, v)

        self.request_id = request.headers.get(self.request_id_header, str(uuid4()))
        request.send_header(self.request_id_header, self.request_id)

        request.end_headers()

        request.wfile.write(self.module.params.get('response_body'))

    def get_Handler(self) -> 'Type[BaseHTTPRequestHandler]':
        method = self.module.params.get('method')
        return type('Handler', (BaseHTTPRequestHandler,), {'do_' + method: lambda request: self.handle(request)})


def main():
    """Main execution"""
    WaitForRequestModule()


if __name__ == '__main__':
    main()
