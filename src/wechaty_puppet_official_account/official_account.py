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
from dataclasses import dataclass
from datetime import datetime, timedelta
from typing import Optional

import requests
from apscheduler.schedulers.asyncio import AsyncIOScheduler
from apscheduler.triggers.interval import IntervalTrigger

from wechaty_puppet import get_logger, WechatyPuppetError

from wechaty_puppet_official_account.webhook import Webhook, WebhookOptions
from .data_store import DataStore
from .schema import OAMessagePayload, AccessTokenPayload

logger = get_logger('OfficialAccount')


@dataclass
class OfficialAccountOption:
    app_id: str
    app_secret: str
    port: int
    token: str


class OfficialAccount:

    def __init__(self, options: OfficialAccountOption):
        self.webhook: Webhook = Webhook(
            options=WebhookOptions(
                port=options.port,
                token=options.token
            )
        )
        self.options = options
        self._data_store = DataStore()
        self._server_base_url: str = 'https://api.weixin.qq.com/cgi-bin/'

        self._scheduler: AsyncIOScheduler = AsyncIOScheduler()

    @property
    def access_token(self) -> str:
        """
        get the access token
        """
        payload: AccessTokenPayload = self._data_store.get_access_token_payload()
        return payload.token

    async def start(self):
        """start the official account"""

        # 1. listen the event from webhook & start the webhook server
        async def on_message(payload: OAMessagePayload):
            self._data_store.set_message_payload(
                message_id=payload.MsgId,
                payload=payload
            )

        self.webhook.on('message', on_message)
        await self.webhook.start()

        # 2. start to fetch access token
        await self._update_access_token()

        # https://developers.weixin.qq.com/doc/offiaccount/Basic_Information/Get_access_token.html
        # refresh the access_tokens every five minutes
        self._scheduler.add_job(
            self._update_access_token,
            trigger=IntervalTrigger(seconds=300)
        )
        self._scheduler.start()

    async def stop(self):
        """stop the official account"""
        logger.info('stop() stopping the official account.')

        # 1. stop the webhook
        await self.webhook.stop()

    @staticmethod
    def _is_error(response: dict) -> bool:
        """check if the result is error"""
        return 'errcode' in response and response['errcode'] != 0

    async def _update_access_token(self):
        """update the access token data"""
        logger.info('_update_access_token()')

        # 1. check if the disk has cached access token
        access_token_payload = self._data_store.get_access_token_payload()

        if access_token_payload:
            # check the expire time of the access_token
            now = datetime.now()
            if access_token_payload.refresh_time + timedelta(seconds=access_token_payload.expires_in) > now:
                logger.debug(f'the access_token_payload<{access_token_payload}> is in expire time')
                return

        res = requests.get(
            f'{self._server_base_url}token?grant_type=client_credential&'
            f'appid=${self.options.app_id}&secret=${self.options.app_secret}'
        )

        if res.status_code != 200:
            raise WechatyPuppetError('can not get access token')
        response_data = res.json()

        logger.debug(f'_update_access_token() receive data <{response_data}>')

        if self._is_error(response_data):
            raise WechatyPuppetError(f'can not get access token with msg <{response_data["errmsg"]}>')

        access_token_payload = AccessTokenPayload(
            expires_in=response_data['expires_in'],
            refresh_time=datetime.now(),
            token=response_data['token']
        )

        self._data_store.set_access_token_payload(access_token_payload)
        logger.debug(f'update_access_token() synced. New token will expiredIn {response_data["expires_in"]} seconds')
