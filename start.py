import sys
from getopt import getopt

from server import server_starter, server_map


class CommandStarter:
    def __init__(self):
        # 帮助信息映射
        self.usage_map = {
            "-h, --help": "show help",
            "-s, --server-type <choice>": """choice BaseServer or AutoServer
                              choices: (base, auto)
                              [-p, --processes] and [-c, --coroutines] follow with BaseServer
                              [-m, --multi] follow with AutoServer""",
            "-p, --processes <num>": "default is equal to the server computer's CPU cores",
            "-c, --coroutines <num>": "default is 10",
            "-m, --multi <num>": "Multiply processes and coroutines, default is 100"
        }
        # 命令行参数对应的函数传入形参
        self.options = {
            "-p": "processes",
            "--processes": "processes",
            "-c": "coroutines",
            "--coroutines": "coroutines",
            "-m": "concurrents",
            "--multi": "concurrents",
        }
        # 对应输入值须为自然数的命令行参数列表
        self.num_options = ["-p", "--processes", "-c", "--coroutines", "-m", "--multi"]

    # 打印每项帮助信息时，对齐打印
    @staticmethod
    def usage_format_print(options: str, info: str, table_length: int = 30, single: bool = True):
        if single:
            print("Usage:", end='')
        s = '{:<%s}{}' % table_length
        # print('{:<30}{:<20}'.format(s1, s2))
        print(s.format(options, info))

    # 打印帮助信息
    def usage(self):
        print("Usage:")
        print("python xxxxxx.py [port] [options] ")
        for options, info in self.usage_map.items():
            self.usage_format_print(options, info, single=False)

    # 启动
    def run(self):
        # 初始化参数字典
        kwargs = {}
        # 获取命令行参数
        options, args = getopt(sys.argv[1:], 'hs:p:c:m:',
                               ['help', 'server-type=', 'processes=', 'coroutines=', 'multi='])
        for name, value in options:
            # 帮助信息
            if name in ('-h', '--help'):
                self.usage()
                return
            # 服务器模式
            if name in ('-s', '--server-type'):
                if value not in server_map:
                    key = "-s, --server-type <choice>"
                    self.usage_format_print(key, self.usage_map[key])
                    return
                else:
                    kwargs['server_type'] = value
            # 校验并发参数，添加
            if name in self.num_options:
                if not value.isdecimal():
                    print(f'{name} option followed with a positive num')
                    return
                else:
                    kwargs[self.options[name]] = int(value)
        # 校验端口参数，添加
        if len(args) and args[0].isdecimal():
            kwargs['port'] = args[0]
        # 启动服务器
        server_starter(**kwargs)


if __name__ == '__main__':
    starter = CommandStarter()
    starter.run()
