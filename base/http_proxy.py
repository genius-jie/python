from __future__ import print_function
import socket
from ftplib import print_line

import select
import time
import ssl
import re
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

    def __init__(self, host='0.0.0.0', port=8888, listen=10, bufsize=80, delay=1):
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
        self.question_ids = [
            "255d1095-7915-4115-a5ab-1cb8b025c108",
            "00c28ba3-023f-4569-abc0-bc0ecca67242",
            "01d6b10c-e15b-415e-8517-4dc49250e449",
            "5d552434-aaa0-4a31-a056-379487e005f0",
            "001021dc-15b8-4215-b25a-d4c7c0b25cd1",
            "10c6181f-bb15-4157-954e-da7de2125646",
            "00f8cddd-66b6-4ac2-bca4-79148d44cad2",
            "430610e4-915d-4157-959a-e3b125ab8151",
            "104fc66a-815a-4153-a535-f984e7025004",
            "002a10fa-715f-4152-5861-e25b0579cbf5",
            "010443cb-e159-415a-b5e7-88cef854d425",
            "10b64392-153d-415a-8c5c-9b25d8b07a2d",
            "010e49f0-da15-4f15-5fb9-25a45826ce7d"
        ]
        self.counter = 0

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
        # print(tmp_socket)
        return tmp_socket


    def __modify_request(self, req_data):
        # modified_req_data=req_data.replace("a","b")
        return req_data

    def __modify_response(self, resp_data):
        # if self.counter < len(self.question_ids):
        #     new_question_id = self.question_ids[self.counter]
        #     modified_resp_data = re.sub(r'"questionId":".*?"', f'"questionId":"{new_question_id}"', resp_data)
        #     self.counter += 1
        # else:
        #     modified_resp_data = resp_data
        #     self.counter = 0  # 重置计数器
        return resp_data

    def __proxy(self, socket_client):
        '''
        代理核心程序

        参数：socket_client 代理端与客户端之间建立的套接字
        '''
        # 接收客户端请求数据
        req_data = socket_client.recv(self.socket_recv_bufsize)
        if req_data == b'':
            return
        # print("before", req_data)
        # 解析http请求数据
        http_packet = HttpRequestPacket(req_data)
        # print(http_packet.host)
        # print("http_packet")

        # 获取服务端host、port
        if b':' in http_packet.host:
            server_host, server_port = http_packet.host.split(b':')
        else:
            server_host, server_port = http_packet.host, 80

        print("请求体", req_data)
        # # 修改请求数据/jzx-server/hera/rest/question/getDefaultQuestionData
        # if b"http://test.91jzx.cn/jzx-server/hera/rest/question/getDefaultQuestionData" in req_data:
        #     print("before", req_data)
        #     req_data = self.__modify_request(req_data.decode('utf-8')).encode('utf-8')
        #     print("after", req_data)
        # else:
        #     print("xiayige")


        # HTTP
        if http_packet.method in [b'GET', b'POST', b'PUT', b'DELETE', b'HEAD']:
            socket_server = self.__connect(server_host, server_port)  # 建立连接
            # print(req_data.decode('utf-8'),'ccccc')
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
                        print_line("响应:", data)
                        data = self.__modify_response(data.decode('utf-8')).encode('utf-8')
                        # print("响应-after:", data)
                        socket_client.send(data)  # 将服务端响应数据发往客户端
                        # 打印服务端响应数据
                        # print("Server Response:", data.decode('utf-8', errors='ignore'))
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
        # print("服务端：", self.handle_client_request, "客户端：", self.client_socket_accept())
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

    # 启动代理python http_proxy.py --host 192.168.1.1 --port 9090 --listen 20 --bufsize 16 --delay 2.5
    # 1、启动代理 2、adb开启机器连接代理
    SimpleHttpProxy(host, port, listen, bufsize, delay).start()