"""
Python Wechaty - https://github.com/wechaty/python-wechaty

Authors:    Jingjing WU (吴京京) <https://github.com/wj-Mcat>

2020-now @ Copyright Wechaty

Licensed under the Apache License, Version 2.0 (the 'License');
you may not use this file except in compliance with the License.
You may obtain a copy of the License at

http://www.apache.org/licenses/LICENSE-2.0

Unless required by applicable law or agreed to in writing, software
distributed under the License is distributed on an 'AS IS' BASIS,
WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
See the License for the specific language governing permissions and
limitations under the License.
"""
from __future__ import annotations

import asyncio

from aiohttp.web_runner import BaseSite
from pyee import AsyncIOEventEmitter
from aiohttp import web
from aiohttp.web_request import Request
from dataclasses import dataclass
from typing import Callable, Optional
from wechaty_puppet import get_logger, WechatyPuppetOperationError

from Crypto.Hash import SHA1
import xmltodict

from .schema import VerifyArgs, OAMessagePayload


@dataclass
class WebhookOptions:
    port: int
    token: str

logger = get_logger('Webhook')


class Webhook(AsyncIOEventEmitter):
    """
    listen the event from official account
    """

    def __init__(self, options: WebhookOptions):
        super().__init__()
        self.options: WebhookOptions = options
        self.site: Optional[BaseSite] = None

    def init_site(self):
        """init the web site configuration"""
        routes = web.RouteTableDef()

        @routes.get('/')
        async def verify_auth(request: Request):
            """check the authentication"""
            query_json = dict(request.query)
            logger.debug("receive query from tencent server <%s>", request.query_string)
            verify_args = VerifyArgs(**query_json)
            data = [verify_args.timestamp, verify_args.nonce, self.options.token]
            sha1 = SHA1.new()
            sha1.update(''.join(data).encode())
            hash_data = sha1.hexdigest()
            text = verify_args.echostr if hash_data == verify_args.signature else ''
            logger.debug(f'final auth text result : {text}')
            return web.Response(body=text)

        @routes.post('/')
        async def receive_message(request: Request):
            data = await request.text()
            logger.debug(f'receive message <{data}>')

            payload_json = xmltodict.parse(data)

            payload = OAMessagePayload(**payload_json['xml'])

            if payload.MsgType in ['text', 'image']:
                self.emit('message', payload)

        app = web.Application()
        app.add_routes(routes)

        runner = web.AppRunner(app)
        await runner.setup()

        self.site = web.TCPSite(runner, '0.0.0.0', self.options.port)

    @staticmethod
    async def receive_message(request):
        pass

    async def start(self):
        """
        start the webhook local server
        """
        logger.info('starting the webhook server ...')

        async def run_server():
            if not self.site:
                raise WechatyPuppetOperationError(f'please init the site configuration before starting the site ...')
            await self.site.start()

        loop = asyncio.get_event_loop()
        asyncio.run_coroutine_threadsafe(run_server(), loop=loop)
        logger.info(f'the server started at: http://0.0.0.0:{self.options.port}')
        logger.info('webhook server started ...')

    async def stop(self):
        """stopping web application"""
        await self.site.stop()
