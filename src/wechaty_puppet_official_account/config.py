"""get the default configuration for puppet-official-account"""
from __future__ import annotations
import os

app_id = os.environ.get('WECHATY_PUPPET_OA_APP_ID', None)
app_secret = os.environ.get('WECHATY_PUPPET_OA_APP_SECRET', None)
token = os.environ.get('WECHATY_PUPPET_OA_TOKEN', None)
port = os.environ.get('WECHATY_PUPPET_OA_PORT', None)

official_account_url = "https://api.weixin.qq.com/cgi-bin/"
