import json
import logging
from urllib import request

import requests
from app.config import FS_MESSAGES_URL, FS_ROBOT_CHAT_MESSAGES_URL, FS_ROBOT_ACCESS_TOKEN_URL, FS_ROBOT_APP_ID, \
    FS_ROBOT_APP_SECRET


def send_fs_msg(notify_key, title, msg):
    url = f"{FS_MESSAGES_URL}{notify_key}"
    post_content = [
        [{"tag": "text", "text": msg}]
    ]
    post_data = {"msg_type": "post", "content": {
        "post": {"zh_cn": {
            "title": title,
            "content": post_content
        }}
    }}
    data_json = json.dumps(post_data)
    logging.info(f"fs msg: {post_content}")
    logging.info(f"fs request data: {str(data_json)}")
    res = requests.post(url=url, headers={'Content-Type': 'application/json'}, data=data_json)
    logging.info(f"fs result: {res}")


def send_fs_chat_msg(token, chat_id, title, post_content):
    url = FS_ROBOT_CHAT_MESSAGES_URL
    headers = {
        "Authorization": "Bearer " + token,
        "Content-Type": "application/json; charset=utf-8"
    }
    post_data = {
        "receive_id": chat_id,
        "msg_type": "post",
        "content": json.dumps({"zh_cn": {
            "title": title,
            "content": post_content
        }})
    }
    data = bytes(json.dumps(post_data), encoding='utf8')
    req = request.Request(url=url, data=data, headers=headers, method='POST')
    try:
        response = request.urlopen(req)
    except Exception as e:
        print(e.read().decode())
        return
    rsp_body = response.read().decode('utf-8')
    rsp_dict = json.loads(rsp_body)
    code = rsp_dict.get("code", -1)
    if code != 0:
        print("send message error, code = ", code, ", msg =", rsp_dict.get("msg", ""))


def get_tenant_access_token():
    url = FS_ROBOT_ACCESS_TOKEN_URL
    headers = {
        "Content-Type": "application/json"
    }
    req_body = {
        "app_id": FS_ROBOT_APP_ID,
        "app_secret": FS_ROBOT_APP_SECRET
    }
    data = bytes(json.dumps(req_body), encoding='utf8')
    req = request.Request(url=url, data=data, headers=headers, method='POST')
    try:
        response = request.urlopen(req)
    except Exception as e:
        print(e.read().decode())
        return ""
    rsp_body = response.read().decode('utf-8')
    rsp_dict = json.loads(rsp_body)
    code = rsp_dict.get("code", -1)
    if code != 0:
        print("get tenant_access_token error, code =", code)
        return ""
    return rsp_dict.get("tenant_access_token", "")
