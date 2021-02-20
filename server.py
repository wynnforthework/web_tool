# -*- coding: utf-8 -*-
import tornado
import tornado.websocket
import paramiko
import threading
import time
import os
import socket

# 配置服务器信息
HOSTS = "192.168.1.101"
PORT = 22
USERNAME = "titan"
PASSWORD = "titan4"
WsHost = ""

class MyThread(threading.Thread):
    def __init__(self, id, chan):
        threading.Thread.__init__(self)
        self.chan = chan

    def run(self):
        while not self.chan.chan.exit_status_ready():
            time.sleep(0.1)
            try:
                data = self.chan.chan.recv(1024)
                self.chan.write_message(data)
            except Exception as ex:
                print(str(ex))
        self.chan.sshclient.close()
        return False



class webSSHServer(tornado.websocket.WebSocketHandler):

    def open(self):
        self.sshclient = paramiko.SSHClient()
        self.sshclient.load_system_host_keys()
        self.sshclient.set_missing_host_key_policy(paramiko.AutoAddPolicy())
        self.sshclient.connect(HOSTS, PORT, USERNAME, PASSWORD)
        self.chan = self.sshclient.invoke_shell(term='xterm')
        self.chan.settimeout(0)
        t1 = MyThread(999, self)
        t1.setDaemon(True)
        t1.start()

    def on_message(self, message):
        try:
            self.chan.send(message)
        except Exception as ex:
            print(str(ex))

    def on_close(self):
        self.sshclient.close()

    def check_origin(self, origin):
        # 允许跨域访问
        return True

class IndexHandler(tornado.web.RequestHandler):
    def get(self):
        if(WsHost == ''):
            s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
            s.connect(('8.8.8.8', 80))
            print(s.getsockname()[0])
            s.close()
        self.render("index.html",ws_host=WsHost)

if __name__ == '__main__':
    # 设置静态文件
    settings = {
        # 'template_path': 'templates',
        "static_path": os.path.join(os.path.dirname(__file__), "static"),
        "cookie_secret": "__TODO:_GENERATE_YOUR_OWN_RANDOM_VALUE_HERE__",
        "login_url": "/login",
        "xsrf_cookies": True,
    }
    # 定义路由
    app = tornado.web.Application([
        (r"/terminals/", webSSHServer),
        (r'/', IndexHandler),
    ],
        debug=True
    ,**settings)

    # 启动服务器
    http_server = tornado.httpserver.HTTPServer(app)
    http_server.listen(3000)
    tornado.ioloop.IOLoop.current().start()
