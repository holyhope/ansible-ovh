from __future__ import absolute_import, division, print_function

__metaclass__ = type

from http import HTTPStatus
from http.server import BaseHTTPRequestHandler, HTTPServer
from socket import timeout
from uuid import uuid4

from ansible.module_utils.basic import AnsibleModule
from ansible.module_utils.common.validation import check_type_str

try:
    from typing import TYPE_CHECKING

    if TYPE_CHECKING:
        from typing import Callable, Optional, Type

    class Handler(BaseHTTPRequestHandler):
        raw_requestline: bytes
        handle: 'Callable[[BaseHTTPRequestHandler], None]'

    class Server(HTTPServer):
        pass

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
    default_content_type = "text/html;charset=utf-8"

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
            response_body=dict(
                type=lambda v: check_type_str(v).encode('utf-8'),
                required=False,
                default='Success',
                no_log=True,
            ),
            response_headers=dict(
                type=dict,
                required=False,
                no_log=True,
                default={
                    "Content-Type": self.default_content_type,
                    "Server": "Ansible - holyhole.ovh.wait_for_request",
                },
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

        with self.server((address, port), self.handler) as httpd:
            self.module.log("Waiting request", log_args=dict(server_address=httpd.server_address))
            httpd.handle_request()

        if self.request is None:
            self.module.fail_json(msg='no valid request',)

        self.module.exit_json(
            changed=True,
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

        for k, v in self.module.params.get('response_headers', {}).items():
            request.send_header(k, v)

        self.request_id = request.headers.get(self.request_id_header, str(uuid4()))
        request.send_header(self.request_id_header, self.request_id)

        request.end_headers()

        request.wfile.write(self.module.params.get('response_body'))

    def handle_one_request(self, request: 'Handler'):
        """Copied form BaseHTTPRequestHandler"""
        try:
            request.raw_requestline = request.rfile.readline(65537)
            if len(request.raw_requestline) > 65536:
                request.requestline = ''
                request.request_version = ''
                request.command = ''
                request.send_error(HTTPStatus.REQUEST_URI_TOO_LONG)
                return
            if not request.raw_requestline:
                request.close_connection = True
                return
            if not request.parse_request():
                # An error code has been sent, just exit
                return
            self.handle(request)
            request.wfile.flush()  # actually send the response if not already done.
        except timeout as e:
            # a read or a write timed out.  Discard this connection
            request.log_error("Request timed out: %r", e)
            request.close_connection = True
            return

    @property
    def server(self) -> 'Type[Server]':
        return type('Server', (HTTPServer,), {
            # 'handle_error': self.handle_error,
        })

    @property
    def handler(self) -> 'Type[Handler]':
        return type('Handler', (BaseHTTPRequestHandler,), {
            'handle_one_request': (lambda request: self.handle_one_request(request)),
        })


def main():
    """Main execution"""
    WaitForRequestModule()


if __name__ == '__main__':
    main()
