*注：因 gevent 的兼容性问题，与多进程配合在 win 平台上会报错，故此程序仅支持 linux 、unix 系统*

1. 使用多进程 + 协程的方案魔改 web 静态服务器，进程数默认对应服务器 CPU 核数

2. 命令行和函数式两种启动方式

    start.py     命令行启动

    server.py   函数式启动

3. 服务器有两种模式，一种自动模式和一种自定义模式，具体见代码文件

4. 获取输出本机 IP

5. 代码含注释和类型注解，方便调试和阅读
