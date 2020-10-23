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
from diskcache import Cache
from wechaty_puppet import (
    get_logger,
    WechatyPuppetOperationError
)
from wechaty_puppet_official_account.schema import (
    OAMessagePayload,
    OAContactPayload
)


logger = get_logger('PayloadStore')


class PayloadStore:
    """
    store the payload with domain
    """
    def __init__(self):
        """init the payload directory"""
        self.path = os.path.join(
            os.getcwd(),
            '.wechaty',
            'wechaty-puppet-official-account',
            'payload_cache'
        )
        if not os.path.exists(self.path):
            os.makedirs(self.path)

    def get_message_payload(self, message_id: str) -> OAMessagePayload:
        """
        get the message payload
        """
        with Cache(self.path) as warehouse:
            payload = warehouse.get(f'message-{message_id}')
            if not isinstance(payload, OAMessagePayload):
                raise WechatyPuppetOperationError(f'payload<{payload}> type is not OAMessagePayload')
            return payload

    def set_message_payload(self, message_id: str, payload: OAMessagePayload):
        """
        set the message payload
        """
        with Cache(self.path) as warehouse:
            warehouse.set(f'message-{message_id}', payload)

    def get_contact_payload(self, contact_id: str) -> OAContactPayload:
        """
        get the contact payload
        """
        with Cache(self.path) as warehouse:
            payload = warehouse.get(f'contact-{contact_id}')
            if not isinstance(payload, OAContactPayload):
                raise WechatyPuppetOperationError(f'payload<{payload}> type is not OAContactPayload')
            return payload

    def set_contact_payload(self, contact_id: str, payload: OAContactPayload):
        """
        set the contact payload
        """
        with Cache(self.path) as warehouse:
            warehouse.set(f'contact-{contact_id}', payload)
