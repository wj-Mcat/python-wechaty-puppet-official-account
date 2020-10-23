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

from dataclasses import dataclass
from typing import Literal, List
from wechaty_puppet import ContactGender

OAMessageType = Literal[
    'text',
    'image',
    'voice',
    'video',
    'shortvideo',
    'location',
    'link'
]

OAMediaType = Literal['image', 'voice', 'video', 'thumb']

Language = Literal['zh_CN', 'zh_TW', 'en']


@dataclass
class ErrorPayload:
    errcode: int
    errmsg: str


@dataclass
class OAMessagePayload:
    ToUserName: str
    FromUserName: str
    CreateTime: str
    MsgType: OAMessageType
    Content: str
    MsgId: str


@dataclass
class OAContactPayload:
    subscribe: int
    openid: str
    nickname: str
    sex: ContactGender
    language: Language
    city: str
    province: str
    country: str
    headimgurl: str
    subscribe_time: int
    unionid: str
    remark: str
    groupid: int
    tagid_list: List[int]
    subscribe_scene: str
    qr_scene: int
    qr_scene_str: str

@dataclass
class VerifyArgs:
    timestamp: int
    nonce: str
    signature: str
    echostr: str
