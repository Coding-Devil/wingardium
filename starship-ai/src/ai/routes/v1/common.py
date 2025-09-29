#  Copyright (c) 2025 Nokia - Nokia Proprietary Internal Use Only - All Rights Reserved.
import datetime
import uuid
from typing import Callable, Tuple, Union

import httpx
from fastapi import Request, Response, status
from fastapi.responses import JSONResponse
from fastapi.routing import APIRoute

from ai import LOG
from ai.config import CONFIG
from ai.endpoints.v1 import EndpointTypes
from ai.models.v1.common import GENERAL_ERROR, ForbiddenError, GeneralError, ParseErrors

SERVER_ERROR = {status.HTTP_500_INTERNAL_SERVER_ERROR: {
    'model': GeneralError,
    'description': 'Internal server error'
}}


PARSE_ERRORS = {status.HTTP_422_UNPROCESSABLE_ENTITY: {
    'model': ParseErrors,
    'description': 'could not parse request body'
}}

FORBIDDEN_ERROR = {status.HTTP_403_FORBIDDEN: {
    'model': ForbiddenError,
    'description': 'Access forbidden'
}}


COMMON_ERRORS = {**FORBIDDEN_ERROR,
                 **SERVER_ERROR,
                 **PARSE_ERRORS}


async def call_endpoint(ep_type: EndpointTypes, method: str, url: str, headers: dict,
                        error_action: str, body: Union[dict, list, None] = None, params=None,
                        verify: bool = True) -> \
        Tuple[Union[list, dict, JSONResponse, None], int]:  # pragma: nocover
    """
    Call the given endpoint asynchronously.

    :param ep_type: type of endpoint being called
    :param method: method to use (expected to be a valid REST method, all caps (not enforced)
    :param url: URL to call (should not include any query parameters)
    :param headers: any headers to supply in the call
    :param error_action: string to use if we encounter an error (e.g., could not <error_action>)
    :param body: body to send (should be json serializable - may work if not but no guarantees)
    :param params: query parameters to use when making the call
    :param verify: Set to False to disable TLS verification to the given URL
    :return: The response (either a list or dict) plus the return code or JSONResponse plus a
             return code of 500 if we encounter an error
    """
    _error = GENERAL_ERROR.format(action='communicate with server')
    LOG.debug(f"executing {method} to endpoint type {ep_type.value} using url {url}, "
              f"headers: {headers}, body: {body}")
    _connect_timeout = CONFIG.endpoints.by_type(ep_type)[0].connect_timeout
    _read_timeout = CONFIG.endpoints.by_type(ep_type)[0].read_timeout
    _timeout = httpx.Timeout(5, connect=_connect_timeout, read=_read_timeout)
    try:
        async with httpx.AsyncClient(verify=verify, timeout=_timeout) as client:
            if method == 'GET':
                _r = await client.get(url=url, headers=headers, params=params)
            if method == 'POST':
                _r = await client.post(url=url, headers=headers, json=body, params=params)
            if method == 'PUT':
                _r = await client.put(url=url, headers=headers, json=body, params=params)
            if method == 'PATCH':
                _r = await client.patch(url=url, headers=headers, json=body, params=params)
            if method == 'DELETE':
                _r = await client.delete(url=url, headers=headers, params=params)
        _status = _r.status_code
        if len(_r.content) > 0:
            _body = _r.json()
        else:
            _body = None
        LOG.info(f"successful {method} for {url}")
        LOG.debug(f"{method} {url} status code: {_status}, body: {_body}")
        return _body, _status
    except (httpx.ConnectTimeout, httpx.ReadTimeout):
        _uuid = uuid.uuid4()
        LOG.warning(f"error_id: {_uuid}, timeout on {method}: {error_action}")
        _response = GeneralError(error=_error, id=str(_uuid))
        return JSONResponse(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                            content=_response.dict()), 500
    except Exception as e:
        _uuid = uuid.uuid4()
        LOG.warning(f"error_id: {_uuid}, unexpected exception during {method}: {error_action} "
                    f"exception: {repr(e)}")
        _response = GeneralError(error=_error, id=str(_uuid))
        return JSONResponse(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                            content=_response.dict()), 500


def log_usage(user: str, subscription: str, request: Request):
    LOG.info(f'user: {user}, subscription: {subscription}, method: {request.method}, '
             f'path: {request.url.path}')


class TimedRoute(APIRoute):
    def get_route_handler(self) -> Callable:
        orig_handler = super().get_route_handler()

        async def route_time(request: Request) -> Response:
            then = datetime.datetime.now(datetime.timezone.utc)
            response: Response = await orig_handler(request)
            duration = datetime.datetime.now(datetime.timezone.utc) - then
            LOG.info(f"processing_time: {duration}")
            return response

        return route_time
