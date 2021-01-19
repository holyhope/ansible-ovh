
try:
    from typing import TYPE_CHECKING

    if TYPE_CHECKING:
        from typing import Any
except ImportError:
    TYPE_CHECKING = False


from ansible.module_utils.common.validation import (check_type_dict,
                                                    check_type_list,
                                                    check_type_str)

try:
    from ovh import consumer_key as ovh
except ImportError:
    ovh = object


def check_type_access_method(method: 'Any') -> str:
    '''
    >>> check_type_access_method('GET')
    'GET'
    >>> check_type_access_method('poSt')
    'POST'
    >>> check_type_access_method('invalid')
    Traceback (most recent call last):
        ...
    ValueError: INVALID must be one of (GET,POST,PUT,DELETE)
    >>> check_type_access_method({})
    Traceback (most recent call last):
        ...
    ValueError: {} must be one of (GET,POST,PUT,DELETE)
    >>> check_type_access_method(0.3)
    Traceback (most recent call last):
        ...
    ValueError: 0.3 must be one of (GET,POST,PUT,DELETE)
    '''
    method = check_type_str(method).upper()
    if method not in ovh.API_READ_WRITE:
        raise ValueError('%s must be one of (%s)' % (method, ','.join(ovh.API_READ_WRITE)))

    return method


def check_type_accesses(accesses: 'Any') -> dict:
    '''
    >>> check_type_accesses(dict())
    {}
    >>> check_type_accesses('{"/me": ["GET", "post"]}')
    {'/me': ['GET', 'POST']}
    >>> check_type_accesses({
    ...     '/me': [],
    ... })
    Traceback (most recent call last):
        ...
    ValueError: no permissions specfied for /me
    >>> check_type_accesses('GET')
    Traceback (most recent call last):
        ...
    TypeError: dictionary requested, could not parse JSON or key=value
    '''
    accesses = check_type_dict(accesses)
    result = accesses

    for (endpoint, perms) in accesses.items():
        result[endpoint] = []

        methods = check_type_list(perms)
        if not methods:
            raise ValueError("no permissions specfied for %s" % endpoint)

        for method in methods:
            method = check_type_access_method(method)

            result[endpoint].append(method)

    return result
