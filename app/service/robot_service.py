import json

import requests

from app.config import AI_CHAT_ROBOT_URL


def get_chat_msg(context):
    url = f"{AI_CHAT_ROBOT_URL}{context}"
    res = requests.get(url=url)
    try:
        rsp_dict = json.loads(res.content)
        if rsp_dict['message'] == 'success':
            text = rsp_dict['data']['info']['text']
            return text
    except Exception as e:
        print(e)
    return "额呀，我现在出了点问题"

