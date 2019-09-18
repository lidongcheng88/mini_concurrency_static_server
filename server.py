import os
import socket
from multiprocessing import cpu_count, Process
from typing import List, Tuple

from gevent import monkey
from gevent.pool import Pool

monkey.patch_all()

# 计算本机的 CPU 核数
cores = cpu_count()


# 获取本机地址
def get_localhost() -> str:
    with socket.socket(socket.AF_INET, socket.SOCK_DGRAM) as s:
        s.connect(('8.8.8.8', 80))
        ip = s.getsockname()[0]
    return ip


# 定义web服务器类
class BaseServer:
    def __init__(self, processes: int, coroutines: int, port: int):
        # 保存创建成功的服务器套接字
        self.tcp_server_socket = self.begin(port)
        self.processes = processes
        self.coroutines = [coroutines for i in range(processes)]

    # 服务器初始化
    def begin(self, port: int) -> socket.socket:
        # 创建tcp服务端套接字
        tcp_server_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        # 设置端口号复用, 程序退出端口立即释放
        tcp_server_socket.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, True)
        # 绑定端口号
        tcp_server_socket.bind(("", port))
        # 设置监听
        tcp_server_socket.listen(128)
        # info about web server site
        # print(f'静态服务器地址为 {tcp_server_socket.getsockname()[0]}:{port}')
        ip = get_localhost()
        print(f"静态服务器地址为 {ip}:{port}")
        # 返回服务器主 server 对象
        return tcp_server_socket

    # 处理客户端的请求
    @staticmethod
    def handle_client_request(new_socket: socket.socket):
        # 代码执行到此，说明连接建立成功
        recv_client_data = new_socket.recv(4096)
        if len(recv_client_data) == 0:
            print("关闭浏览器了")
            new_socket.close()
            return

        # 对二进制数据进行解码
        recv_client_content = recv_client_data.decode("utf-8")
        print(recv_client_content)
        # 根据指定字符串进行分割， 最大分割次数指定2
        request_list = recv_client_content.split(" ", maxsplit=2)

        # 获取请求资源路径
        request_path = request_list[1]
        print(request_path)

        # 判断请求的是否是根目录，如果条件成立，指定首页数据返回
        if request_path == "/":
            request_path = "/index.html"

        try:
            # 动态打开指定文件
            with open("static" + request_path, "rb") as file:
                # 读取文件数据
                file_data = file.read()
        except Exception as e:
            # 请求资源不存在，返回404数据
            # 响应行
            response_line = "HTTP/1.1 404 Not Found\r\n"
            # 响应头
            response_header = "Server: PWS1.0\r\n"
            with open("static/error.html", "rb") as file:
                file_data = file.read()
            # 响应体
            response_body = file_data

            # 拼接响应报文
            response_data = (response_line + response_header + "\r\n").encode("utf-8") + response_body
            # 发送数据
            new_socket.send(response_data)
        else:
            # 响应行
            response_line = "HTTP/1.1 200 OK\r\n"
            # 响应头
            response_header = "Server: PWS1.0\r\n"

            # 响应体
            response_body = file_data

            # 拼接响应报文
            response_data = (response_line + response_header + "\r\n").encode("utf-8") + response_body
            # 发送数据
            new_socket.send(response_data)
        finally:
            # 关闭服务与客户端的套接字
            new_socket.close()

    # 启动web服务器进行工作
    def start(self):
        # TODO 获取子进程编号
        print(f'子进程：{os.getpid()}')
        if self.coroutines:
            while True:
                # 等待接受客户端的连接请求
                new_socket, ip_port = self.tcp_server_socket.accept()
                # TODO 换用协程
                # 限制协程的并发处理数
                pool = Pool(self.coroutines.pop())
                p = pool.spawn(self.handle_client_request, new_socket)
                p.join()
        else:
            while True:
                # 等待接受客户端的连接请求
                new_socket, ip_port = self.tcp_server_socket.accept()
                self.handle_client_request(new_socket)

    # TODO 搭配多进程美滋滋
    def multi_start(self):
        for x in range(self.processes):
            p = Process(target=self.start)
            p.start()


# 可指定并发数，系统自动调整进程数和协程并发数
class AutoServer(BaseServer):
    def __init__(self, concurrents: int, port: int):
        self.tcp_server_socket = self.begin(port)
        self.processes, self.coroutines = self.distribution(concurrents)

    # 并发分配
    @staticmethod
    def distribution(concurrents) -> Tuple[int, List[int]]:
        if concurrents <= cores:
            processes = concurrents
            coroutines = None
        else:
            processes = cores
            coroutines_average = concurrents // cores
            coroutines_remainder = int(concurrents % cores)
            coroutines = [coroutines_average for i in range(cores)]
            if coroutines_remainder:
                for i in range(coroutines_remainder):
                    coroutines[i] += 1
        return processes, coroutines


# 服务器映射
server_map = {
    'base': BaseServer,
    'auto': AutoServer
}


def check_int(*args: tuple) -> bool:
    for item in args:
        if not isinstance(item, int):
            print(f'The {item} parameter needs int type')
            return False
    return True


# 程序入口函数
def server_starter(server_type: str = 'auto', processes: int = cores,
                   coroutines: int = 10, concurrents: int = 100, port: int = 9000):
    # Server 类
    Server = server_map[server_type]
    # 判断 Server 类型，构造所需参数，否则打印提示信息，返回
    if server_type == 'base':
        args = (processes, coroutines, port)
    elif server_type == 'auto':
        args = (concurrents, port)
    else:
        print(f'请输入正确的服务器模式：{server_map.keys}')
        return
    # 如果参数不是自然数，打印提示信息，返回
    if not check_int(*args):
        return
    # 构造 Server 对象
    web_server = Server(*args)
    # 创建web服务器对象
    # TODO 多进程 + 协程作业
    web_server.multi_start()
    # 协程作业
    # web_server.start()


if __name__ == '__main__':
    server_starter()
    # server_starter('base')
