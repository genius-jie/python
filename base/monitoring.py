#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
    simple-http-proxy ( https://github.com/WengChaoxi/simple-http-proxy )
    ~ ~ ~ ~ ~ ~
    一个简单的http代理

    :copyright: (c) 2021 by WengChaoxi.
    :license: MIT, see LICENSE for more details.
"""
from __future__ import print_function

import json
import socket
import select
import time
import ssl
from common.http_requests import HTTPRequest2


def debug(tag, msg):
    print('[%s] %s' % (tag, msg))


class HttpRequestPacket(object):
    '''
    HTTP请求包
    '''

    def __init__(self, data):
        self.__parse(data)

    def __parse(self, data):
        '''
        解析一个HTTP请求数据包
        GET http://test.wengcx.top/index.html HTTP/1.1\r\nHost: test.wengcx.top\r\nProxy-Connection: keep-alive\r\nCache-Control: max-age=0\r\n\r\n

        参数：data 原始数据
        '''
        i0 = data.find(b'\r\n')  # 请求行与请求头的分隔位置
        i1 = data.find(b'\r\n\r\n')  # 请求头与请求数据的分隔位置

        # 请求行 Request-Line
        self.req_line = data[:i0]
        self.method, self.req_uri, self.version = self.req_line.split()  # 请求行由method、request uri、version组成

        # 请求头域 Request Header Fields
        self.req_header = data[i0 + 2:i1]
        self.headers = {}
        for header in self.req_header.split(b'\r\n'):
            k, v = header.split(b': ')
            self.headers[k] = v
        self.host = self.headers.get(b'Host')

        # 请求数据
        self.req_data = data[i1 + 4:]


class SimpleHttpProxy(object):
    '''
    简单的HTTP代理

    客户端(client) <=> 代理端(proxy) <=> 服务端(server)
    '''

    def __init__(self, host='0.0.0.0', port=8888, listen=10, bufsize=8, delay=1):
        '''
        初始化代理套接字，用于与客户端、服务端通信

        参数：host 监听地址，默认0.0.0.0，代表本机任意ipv4地址
        参数：port 监听端口，默认8080
        参数：listen 监听客户端数量，默认10
        参数：bufsize 数据传输缓冲区大小，单位kb，默认8kb
        参数：delay 数据转发延迟，单位ms，默认1ms
        '''
        self.socket_proxy = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.socket_proxy.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)  # 将SO_REUSEADDR标记为True, 当socket关闭后，立刻回收该socket的端口
        self.socket_proxy.bind((host, port))
        self.socket_proxy.listen(listen)

        self.socket_recv_bufsize = bufsize * 1024
        self.delay = delay / 1000.0

        debug('info', 'bind=%s:%s' % (host, port))
        debug('info', 'listen=%s' % listen)
        debug('info', 'bufsize=%skb, delay=%sms' % (bufsize, delay))

    def __del__(self):
        self.socket_proxy.close()

    def __connect(self, host, port):
        '''
        解析DNS得到套接字地址并与之建立连接

        参数：host 主机
        参数：port 端口
        返回：与目标主机建立连接的套接字
        '''
        # 解析DNS获取对应协议簇、socket类型、目标地址
        # getaddrinfo -> [(family, sockettype, proto, canonname, target_addr),]
        (family, sockettype, _, _, target_addr) = socket.getaddrinfo(host, port)[0]

        tmp_socket = socket.socket(family, sockettype)
        tmp_socket.setblocking(0)
        tmp_socket.settimeout(5)
        tmp_socket.connect(target_addr)
        print(tmp_socket)
        return tmp_socket


    def __modify_request(self, req_data):
        '''
        修改请求数据，确保答案正确

        参数：req_data 原始请求数据
        返回：修改后的请求数据
        '''
        # 示例：假设请求体中包含 "answer=wrong"，我们将其修改为 "answer=correct"
        # modified_req_data = req_data.replace('"userAnswer":"4"', '"userAnswer":"2"')
        # r = HTTPRequest2()
        # login_url = "http://test.91jzx.cn/poseidon/hera/rest/lesson/task/start"
        # login_data = {"chapterId": "1261289714145562624", "isPrimarySchool": "false",
        #               "patternId": ["652ed79a-7674-43ab-bf5d-23d5e3d4dc09"], "processInstanceId": "", "sceneType": "S5",
        #               "startType": 0,
        #               "taskId": ""}
        # json_payload = json.dumps(login_data)
        # h = {"JZX-AppID": "com.jzx.client.aiteacher.math",
        #      "ACCESS-TOKEN": "eyJpc3MiOiJKWlgiLCJhbGciOiJFUzI1NiJ9.eyJ1c2VySWQiOiIxODQ1NzI2ODAxMjI0NjA5NzkzIiwiY3JlYXRlVGltZSI6IjE3MzI1MDEyMDU5NzIiLCJuaWNrTmFtZSI6IiIsImlzTWFpbiI6ZmFsc2V9.ABwfDDcCZ7tiTs4l7aopNcqp29JDg5EEQJ21gGAItCFj550g8dfto7vvOMDBUwH75xkqb8PRAtgRQyOFTu_cqg",
        #      "Content-Type": "application/json; charset=UTF-8",
        #      "Cookie": "JSESSIONID=F2E6FA306174FC22FBB5B0CEE6647945; acw_tc=1a0c385017303449682111334e003aa6f175e04221a1a73c6e228e80af78fd"}
        # respone = r.request(method='post', url=login_url, data=json_payload, headers=h)
        # # print(respone.text)
        # #
        # login_url = "http://test.91jzx.cn/poseidon/hera/rest/lesson/task/nextQuestion?taskId={}&processInstanceId={}".format(
        #     respone.json()["data"]["taskId"], respone.json()["data"]["processInstanceId"])
        # h = {
        #     "ACCESS-TOKEN": "eyJpc3MiOiJKWlgiLCJhbGciOiJFUzI1NiJ9.eyJ1c2VySWQiOiIxODQ1NzI2ODAxMjI0NjA5NzkzIiwiY3JlYXRlVGltZSI6IjE3MzI1MDEyMDU5NzIiLCJuaWNrTmFtZSI6IiIsImlzTWFpbiI6ZmFsc2V9.ABwfDDcCZ7tiTs4l7aopNcqp29JDg5EEQJ21gGAItCFj550g8dfto7vvOMDBUwH75xkqb8PRAtgRQyOFTu_cqg",
        #     "Content-Type": "application/json; charset=UTF-8",
        #     "Cookie": "JSESSIONID=F2E6FA306174FC22FBB5B0CEE6647945; acw_tc=1a0c385017303449682111334e003aa6f175e04221a1a73c6e228e80af78fd"}
        # respone = r.request(method='get', url=login_url, headers=h)
        # print(respone.json())
        # answer = (respone.json()["data"]["questionResponseVO"]["formatStandardAnswers"][0]["answer"][0])
        # print(answer, type(answer))
        # if 'result' in answer:
        #     answer_1 = answer.replace('\\d', '\\\\d')
        #     # print(answer_1)
        # else:
        #     answer_1 = answer
        # import re
        # # 新值为空字符串
        # new_value = answer_1
        # # print(new_value,'AAA')
        # # print(req_data)
        # # 使用正则表达式进行替换
        # updated_string = re.sub(r'"userAnswer":"\d+"', f'"userAnswer":"{new_value}"', req_data)
        # updated_string = re.sub(r'"correctAnswer":"\d+"', f'"correctAnswer":"{new_value}"', updated_string)
        # # print(updated_string)
        modified_req_data = req_data.replace('"result":0', '"result":1')



        # 输出结果
        # return updated_string
        return modified_req_data

    def __modify_response(self, resp_data):
        '''
        修改响应数据

        参数：resp_data 原始响应数据
        返回：修改后的响应数据
        '''
        # 示例：假设响应体中包含 "legalChoice":"0"，我们将其修改为 "legalChoice":"1"
        modified_resp_data = resp_data.replace('"legalChoice":"0"', '"legalChoice":"1"')
        # modified_resp_data = resp_data.replace('"code":"00000"', '"code":"12212"')

        return modified_resp_data

    def __proxy(self, socket_client):
        '''
        代理核心程序

        参数：socket_client 代理端与客户端之间建立的套接字
        '''
        # 接收客户端请求数据
        req_data = socket_client.recv(self.socket_recv_bufsize)
        if req_data == b'':
            return
        print("before", req_data)
        # 解析http请求数据
        http_packet = HttpRequestPacket(req_data)
        print(http_packet.host)
        print("http_packet")

        # 获取服务端host、port
        if b':' in http_packet.host:
            server_host, server_port = http_packet.host.split(b':')
        else:
            server_host, server_port = http_packet.host, 80


        # # 修改请求数据
        if b"http://test.91jzx.cn/poseidon/hera/rest/lesson/task/submit" in req_data:
            print("before", req_data)
            req_data = self.__modify_request(req_data.decode('utf-8')).encode('utf-8')
            print("after", req_data)
        else:
            print("xiayige")


        # HTTP
        if http_packet.method in [b'GET', b'POST', b'PUT', b'DELETE', b'HEAD']:
            socket_server = self.__connect(server_host, server_port)  # 建立连接
            print(req_data.decode('utf-8'),'ccccc')
            socket_server.send(req_data)  # 将客户端请求数据发给服务端

        # HTTPS，会先通过CONNECT方法建立TCP连接
        elif http_packet.method == b'CONNECT':
            socket_server = self.__connect(server_host, server_port)  # 建立连接

            success_msg = b'%s %d Connection Established\r\nConnection: close\r\n\r\n' \
                          % (http_packet.version, 200)
            socket_client.send(success_msg)  # 完成连接，通知客户端

            # 客户端得知连接建立，会将真实请求数据发送给代理服务端
            req_data = socket_client.recv(self.socket_recv_bufsize)  # 接收客户端真实数据
            req_data = self.__modify_request(req_data)  # 修改请求数据
            socket_server.send(req_data)  # 将客户端真实请求数据发给服务端

            # 使用 SSL 包装 socket_server
            socket_server = ssl.wrap_socket(socket_server, server_side=False)

        # 使用select异步处理，不阻塞
        self.__nonblocking(socket_client, socket_server)

    def __nonblocking(self, socket_client, socket_server):
        '''
        使用select实现异步处理数据

        参数：socket_client 代理端与客户端之间建立的套接字
        参数：socket_server 代理端与服务端之间建立的套接字
        '''
        _rlist = [socket_client, socket_server]
        is_recv = True
        while is_recv:
            try:
                rlist, _, elist = select.select(_rlist, [], [], 2)
                if elist:
                    break
                for tmp_socket in rlist:
                    is_recv = True
                    # 接收数据
                    data = tmp_socket.recv(self.socket_recv_bufsize)
                    if data == b'':
                        is_recv = False
                        continue

                    # socket_client状态为readable, 当前接收的数据来自客户端
                    if tmp_socket is socket_client:
                        socket_server.send(data)  # 将客户端请求数据发往服务端
                        # debug('proxy', 'client -> server')

                    # socket_server状态为readable, 当前接收的数据来自服务端
                    elif tmp_socket is socket_server:
                        print("数据类型:", data)
                        data = self.__modify_response(data.decode('utf-8')).encode('utf-8')
                        print("数据类型-after:", data)
                        socket_client.send(data)  # 将服务端响应数据发往客户端
                        # 打印服务端响应数据
                        print("Server Response:", data.decode('utf-8', errors='ignore'))
                        # debug('proxy', 'client <- server')

                time.sleep(self.delay)  # 适当延迟以降低CPU占用
            except Exception as e:
                break

        socket_client.close()
        socket_server.close()

    def client_socket_accept(self):
        '''
        获取已经与代理端建立连接的客户端套接字，如无则阻塞，直到可以获取一个建立连接套接字

        返回：socket_client 代理端与客户端之间建立的套接字
        '''
        socket_client, _ = self.socket_proxy.accept()
        return socket_client

    def handle_client_request(self, socket_client):
        try:
            self.__proxy(socket_client)
        except:
            pass

    def start(self):
        try:
            import _thread as thread  # py3
        except ImportError:
            import thread  # py2
        print("服务端：", self.handle_client_request, "客户端：", self.client_socket_accept())
        while True:
            try:
                thread.start_new_thread(self.handle_client_request, (self.client_socket_accept(),))
            except KeyboardInterrupt:
                break


if __name__ == '__main__':
    # 默认参数
    host, port, listen, bufsize, delay = '0.0.0.0', 8888, 10, 8, 1

    import sys, getopt

    try:
        opts, _ = getopt.getopt(sys.argv[1:], 'h:p:l:b:d:', ['host=', 'port=', 'listen=', 'bufsize=', 'delay='])
        for opt, arg in opts:
            if opt in ('-h', '--host'):
                host = arg
            elif opt in ('-p', '--port'):
                port = int(arg)
            elif opt in ('-l', '--listen'):
                listen = int(arg)
            elif opt in ('-b', '--bufsize'):
                bufsize = int(arg)
            elif opt in ('-d', '--delay'):
                delay = float(arg)
    except:
        debug('error', 'read the readme.md first!')
        sys.exit()

    # 启动代理python monitoring.py --host 192.168.1.1 --port 9090 --listen 20 --bufsize 16 --delay 2.5
    SimpleHttpProxy(host, port, listen, bufsize, delay).start()