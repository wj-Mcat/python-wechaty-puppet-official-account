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

import os
from typing import Any, Optional
from dataclasses import dataclass

from diskcache import Cache
from wechaty_puppet import (
    get_logger,
    WechatyPuppetOperationError
)
from .schema import (
    OAMessagePayload,
    OAContactPayload,
    AccessTokenPayload
)


@dataclass
class DataStoreOption:
    cache_dir: str = os.path.join(
        os.getcwd(),
        '.wechaty',
        'wechaty-puppet-official-account',
        'data_cache'
    )


logger = get_logger('DataStore')


class DataStore:
    """
    store the payload with domain
    """

    def __init__(self, option: Optional[DataStoreOption] = None):
        """init the payload directory"""
        if not option:
            option = DataStoreOption()

        logger.info(f'init DataStore instance <{option}>')
        self.option: DataStoreOption = option

        if not os.path.exists(self.option.cache_dir):
            os.makedirs(self.option.cache_dir)

    def get(self, key: str) -> Optional[Any]:
        """get the key-value from the diskcache"""
        with Cache(self.option.cache_dir) as warehouse:
            data = warehouse.get(key, None)
        return data

    def set(self, key: str, value: Any):
        """set the object by key to the disk cache"""
        with Cache(self.option.cache_dir) as warehouse:
            warehouse.set(key, value)

    def get_message_payload(self, message_id: str) -> OAMessagePayload:
        """
        get the message payload
        """
        payload = self.get(f'message-{message_id}')
        if not payload:
            raise WechatyPuppetOperationError(f'message payload<{message_id}> not found')
        if not isinstance(payload, OAMessagePayload):
            raise WechatyPuppetOperationError(f'payload<{payload}> type is not OAMessagePayload')
        return payload

    def set_message_payload(self, message_id: str, payload: OAMessagePayload):
        """
        set the message payload
        """
        self.set(f'message-{message_id}', payload)

    def get_contact_payload(self, contact_id: str) -> OAContactPayload:
        """
        get the contact payload
        """
        payload = self.get(f'contact-{contact_id}')
        if not payload:
            raise WechatyPuppetOperationError(f'contact payload <{contact_id}> not found')

        if not isinstance(payload, OAContactPayload):
            raise WechatyPuppetOperationError(f'payload<{payload}> type is not OAContactPayload')
        return payload

    def set_contact_payload(self, contact_id: str, payload: OAContactPayload):
        """
        set the contact payload
        """
        self.set(f'contact-{contact_id}', payload)

    def set_access_token_payload(self, payload: AccessTokenPayload):
        """
        set the access_token payload
        """
        self.set('access_token', payload)

    def get_access_token_payload(self) -> Optional[AccessTokenPayload]:
        """
        get the access token payload
        """
        payload = self.get('access_token')
        if payload and not isinstance(payload, AccessTokenPayload):
            raise WechatyPuppetOperationError(f'payload<{payload}> type is not AccessTokenPayload')
        return payload
