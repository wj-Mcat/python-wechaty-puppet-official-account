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

from typing import Optional

import requests
from dataclasses import dataclass
from datetime import datetime

from wechaty_puppet import get_logger, WechatyPuppetError
from wechaty_puppet_official_account.schema import VerifyArgs
from wechaty_puppet_official_account.webhook import Webhook, WebhookOptions
from .payload_store import PayloadStore
from .schema import OAMessagePayload


logger = get_logger('OfficialAccount')


@dataclass
class AccessTokenPayload:
    expires_in: int
    timestamp: float
    token: str


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
        self.payload_store = PayloadStore()
        self._access_token_payload: Optional[AccessTokenPayload] = None
        self._server_base_url: str = 'https://api.weixin.qq.com/cgi-bin/'

    @property
    def access_token(self) -> str:
        """
        get the access token
        """
        if not self._access_token_payload:
            raise ValueError(f'access_token is None')
        return self._access_token_payload.token

    async def start(self):
        """start the official account"""

        # 1. listen the event from webhook
        async def on_message(payload: OAMessagePayload):
            self.payload_store.set_message_payload(
                message_id=payload.MsgId,
                payload=payload
            )

        self.webhook.on('message', on_message)

        # 2. start to fetch access token

    @staticmethod
    def _is_error(response: dict) -> bool:
        """check if the result is error"""
        return 'errcode' in response and response['errcode'] != 0

    async def _update_access_token(self):
        """update the access token data"""
        logger.info('_update_access_token()')

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

        self._access_token_payload = AccessTokenPayload(
            expires_in=response_data['expires_in'],
            timestamp=datetime.now().timestamp(),
            token=response_data['token']
        )

        logger.debug(f'_update_access_token() synced. New token will expiredIn {response_data["expires_in"]} seconds')
