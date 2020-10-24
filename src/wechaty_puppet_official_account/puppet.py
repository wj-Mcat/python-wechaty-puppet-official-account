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
from typing import List, Optional
from dataclasses import dataclass
from pyee import AsyncIOEventEmitter

from wechaty_puppet.schemas.types import PayloadType    # type: ignore

from wechaty_puppet import (  # type: ignore
    EventScanPayload,
    ScanStatus,

    EventReadyPayload,

    EventDongPayload,
    EventRoomTopicPayload,
    EventRoomLeavePayload,
    EventRoomJoinPayload,
    EventRoomInvitePayload,

    EventMessagePayload,
    EventLogoutPayload,
    EventLoginPayload,
    EventFriendshipPayload,
    EventHeartbeatPayload,
    EventErrorPayload,
    FileBox, RoomMemberPayload, RoomPayload, RoomInvitationPayload,
    RoomQueryFilter, FriendshipPayload, ContactPayload, MessagePayload,
    MessageQueryFilter,

    ImageType,
    EventType,
    MessageType,
    Puppet,
    PuppetOptions,
    MiniProgramPayload,
    UrlLinkPayload,

    get_logger
)

from wechaty_puppet.exceptions import (  # type: ignore
    WechatyPuppetConfigurationError,
    WechatyPuppetError,
    WechatyPuppetGrpcError,
    WechatyPuppetOperationError,
    WechatyPuppetPayloadError
)

from wechaty_puppet_official_account import config
from .official_account import OfficialAccount, OfficialAccountOption
from .schema import OAMessagePayload

logger = get_logger('OfficialAccountPuppet')


@dataclass
class OfficialAccountPuppetOptions(PuppetOptions):
    app_id: Optional[str] = None
    app_secret: Optional[str] = None
    port: Optional[int] = 80


class OfficialAccountPuppet(Puppet):

    def __init__(self, options: Optional[OfficialAccountPuppetOptions]):
        if not options:
            options = OfficialAccountPuppetOptions(
                app_id=config.app_id,
                app_secret=config.app_secret,
                token=config.token,
                port=config.port
            )
        if not options.app_id:
            raise WechatyPuppetConfigurationError('WECHATY_PUPPET_OA_APP_ID environment variable not found')
        if not options.app_secret:
            raise WechatyPuppetConfigurationError('WECHATY_PUPPET_OA_APP_SECRET environment variable not found')
        if not options.token:
            raise WechatyPuppetConfigurationError('WECHATY_PUPPET_OA_TOKEN environment variable not found')

        super().__init__(options, 'puppet-official-account')

        self.oa: OfficialAccount = OfficialAccount(
            options=OfficialAccountOption(
                app_id=options.app_id,
                app_secret=options.app_secret,
                port=options.port,
                token=options.token
            )
        )
        self._event_emitter: AsyncIOEventEmitter = AsyncIOEventEmitter()

    async def init_event_bridge(self):
        """
        init the event bus
        """
        async def on_message(oaPayload: OAMessagePayload):
            payload = MessagePayload(
                id=oaPayload.MsgId
            )
            self._event_emitter.emit('message', payload)

        self._event_emitter.on('message', on_message)

    async def message_image(self, message_id: str, image_type: ImageType) -> FileBox:
        pass

    async def ding(self, data: Optional[str] = None):
        pass

    def on(self, event_name: str, caller):
        """listen the event"""
        self._event_emitter.on(event_name, caller)

    def listener_count(self, event_name: str) -> int:
        return self._event_emitter.listeners(event_name).count()

    async def start(self) -> None:
        """start the puppet"""
        await self.oa.start()
        while True:
            await asyncio.sleep(2)

    async def stop(self):
        await self.oa.stop()

    async def contact_list(self) -> List[str]:
        pass

    async def tag_contact_delete(self, tag_id: str) -> None:
        pass

    async def tag_favorite_delete(self, tag_id: str) -> None:
        pass

    async def tag_contact_add(self, tag_id: str, contact_id: str):
        pass

    async def tag_favorite_add(self, tag_id: str, contact_id: str):
        pass

    async def tag_contact_remove(self, tag_id: str, contact_id: str):
        pass

    async def tag_contact_list(self, contact_id: Optional[str] = None) -> List[str]:
        pass

    async def message_send_text(self, conversation_id: str, message: str, mention_ids: List[str] = None) -> str:
        pass

    async def message_send_contact(self, contact_id: str, conversation_id: str) -> str:
        pass

    async def message_send_file(self, conversation_id: str, file: FileBox) -> str:
        pass

    async def message_send_url(self, conversation_id: str, url: str) -> str:
        pass

    async def message_send_mini_program(self, conversation_id: str, mini_program: MiniProgramPayload) -> str:
        pass

    async def message_search(self, query: Optional[MessageQueryFilter] = None) -> List[str]:
        pass

    async def message_recall(self, message_id: str) -> bool:
        pass

    async def message_payload(self, message_id: str) -> MessagePayload:
        pass

    async def message_forward(self, to_id: str, message_id: str):
        pass

    async def message_file(self, message_id: str) -> FileBox:
        pass

    async def message_contact(self, message_id: str) -> str:
        pass

    async def message_url(self, message_id: str) -> UrlLinkPayload:
        pass

    async def message_mini_program(self, message_id: str) -> MiniProgramPayload:
        pass

    async def contact_alias(self, contact_id: str, alias: Optional[str] = None) -> str:
        pass

    async def contact_payload_dirty(self, contact_id: str):
        pass

    async def contact_payload(self, contact_id: str) -> ContactPayload:
        pass

    async def contact_avatar(self, contact_id: str, file_box: Optional[FileBox] = None) -> FileBox:
        pass

    async def contact_tag_ids(self, contact_id: str) -> List[str]:
        pass

    def self_id(self) -> str:
        pass

    async def friendship_search(self, weixin: Optional[str] = None, phone: Optional[str] = None) -> Optional[str]:
        pass

    async def friendship_add(self, contact_id: str, hello: str):
        pass

    async def friendship_payload(self, friendship_id: str,
                                 payload: Optional[FriendshipPayload] = None) -> FriendshipPayload:
        pass

    async def friendship_accept(self, friendship_id: str):
        pass

    async def room_list(self) -> List[str]:
        pass

    async def room_create(self, contact_ids: List[str], topic: str = None) -> str:
        pass

    async def room_search(self, query: RoomQueryFilter = None) -> List[str]:
        pass

    async def room_invitation_payload(self, room_invitation_id: str,
                                      payload: Optional[RoomInvitationPayload] = None) -> RoomInvitationPayload:
        pass

    async def room_invitation_accept(self, room_invitation_id: str):
        pass

    async def contact_self_qr_code(self) -> str:
        pass

    async def contact_self_name(self, name: str):
        pass

    async def contact_signature(self, signature: str):
        pass

    async def room_payload(self, room_id: str) -> RoomPayload:
        pass

    async def room_members(self, room_id: str) -> List[str]:
        pass

    async def room_add(self, room_id: str, contact_id: str):
        pass

    async def room_delete(self, room_id: str, contact_id: str):
        pass

    async def room_quit(self, room_id: str):
        pass

    async def room_topic(self, room_id: str, new_topic: str):
        pass

    async def room_announce(self, room_id: str, announcement: str = None) -> str:
        pass

    async def room_qr_code(self, room_id: str) -> str:
        pass

    async def room_member_payload(self, room_id: str, contact_id: str) -> RoomMemberPayload:
        pass

    async def room_avatar(self, room_id: str) -> FileBox:
        pass

    async def logout(self):
        pass

    async def login(self, user_id: str):
        pass

    async def dirty_payload(self, payload_type: PayloadType, payload_id: str):
        pass