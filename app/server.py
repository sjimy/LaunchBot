#!/usr/bin/env python
# --coding:utf-8--
import re
import _thread
from http.server import BaseHTTPRequestHandler, HTTPServer
import json
from app.config import FS_ROBOT_APP_VERIFICATION_TOKEN
from app.service.feishu_service import get_tenant_access_token, send_fs_chat_msg
from app.service.robot_service import get_chat_msg


class RequestHandler(BaseHTTPRequestHandler):
    history_event_ids = []

    def do_POST(self):
        # 解析请求 body
        req_body = self.rfile.read(int(self.headers['content-length'])).decode("utf-8")
        print(req_body)
        obj = json.loads(req_body)

        # 校验 verification token 是否匹配，token 不匹配说明该回调并非来自开发平台
        token = obj.get("token", "")
        req_type = obj.get("type", "")
        if token != FS_ROBOT_APP_VERIFICATION_TOKEN:
            print("verification token not match, token =", token)
            self.response("")
            return

        # 根据 type 处理不同类型事件
        if "url_verification" == req_type:  # 验证请求 URL 是否有效
            self.handle_request_url_verify(obj)
        elif "event_callback" == req_type:  # 事件回调 1.0
            # 获取事件内容和类型，并进行相应处理，此处只关注给机器人推送的消息事件
            event = obj.get("event")
            if event.get("type", "") == "message":
                event_id = obj.get("uuid", "")
                msg_type = event.get("msg_type", "")
                chat_id = event.get("open_chat_id", "")
                text = event.get("text", "")
                # 启动新线程处理消息
                _thread.start_new_thread(
                    self.handle_message,
                    (event_id, msg_type, chat_id, text)
                )
                # 先返回response，再处理逻辑
                self.response("")
        return

    def handle_request_url_verify(self, post_obj):
        # 原样返回 challenge 字段内容
        challenge = post_obj.get("challenge", "")
        rsp = {'challenge': challenge}
        self.response(json.dumps(rsp))
        return

    def handle_message(self, event_id, msg_type, chat_id, text):
        # 此处只处理 text 类型消息，其他类型消息忽略
        if msg_type != "text":
            print("unknown msg_type =", msg_type)
            return

        # 防止收到重复内容
        for index in range(0, len(self.history_event_ids)):
            if self.history_event_ids[index] == event_id:
                return
        self.history_event_ids.append(event_id)
        if len(self.history_event_ids) > 1000:
            self.history_event_ids.pop(0)

        # 调用发消息 API 之前，先要获取 API 调用凭证：tenant_access_token
        access_token = get_tenant_access_token()
        if access_token == "":
            return

        # 解析字符串
        pattern = re.compile(r'<[^*]+>', re.S)
        text_final = pattern.sub('', text).lstrip('@_user_1 ').lstrip().rstrip()

        # 机器人 echo 收到的消息
        result_msg = get_chat_msg(text_final)
        post_content = [
            [{"tag": "text", "text": result_msg}]
        ]
        send_fs_chat_msg(access_token, chat_id, "", post_content)
        return

    def response(self, body):
        self.send_response(200)
        self.send_header('Content-Type', 'application/json')
        self.end_headers()
        self.wfile.write(body.encode())


def server_run():
    port = 8000
    server_address = ('', port)
    httpd = HTTPServer(server_address, RequestHandler)
    print("start.....")
    httpd.serve_forever()
