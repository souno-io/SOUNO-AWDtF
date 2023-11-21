import argparse
from ip_manager import IPManager
from banner import print_banner
from php_connection import PHPConnectionTester

if __name__ == '__main__':
    print_banner()

    parser = argparse.ArgumentParser(description='管理 IP 地址并生成 URL 列表。')
    parser.add_argument('-a', '--add', type=str, help='将 IP 范围添加到列表')
    parser.add_argument('-r', '--remove', type=str, help='从列表中删除 IP 范围')
    parser.add_argument('-q', '--query', type=str, help='查询特定 IP')
    parser.add_argument('-p', '--port', type=str, help='用于生成 URL 的端口')
    parser.add_argument('-u', '--path', type=str, help='URL 生成的路径')
    parser.add_argument('-g', '--generate', action='store_true', help='从 IP 列表生成 URL')
    parser.add_argument('-m', '--method', type=str, choices=['GET', 'POST'], default='POST',
                        help='要使用的 HTTP 方法（GET 或 POST）。')
    parser.add_argument('-s', '--use-system', action='store_true', help='使用 system 函数而不是 eval。')
    parser.add_argument('-c', '--command', type=str, help='需要执行的命令。')
    args = parser.parse_args()

    # 检查是否有参数被输入
    if not any(vars(args).values()):
        parser.print_help()
        exit(1)

    manager = IPManager()
    php_con = PHPConnectionTester()

    if args.add:
        manager.add(args.add)
    if args.remove:
        manager.remove(args.remove)
    if args.query:
        print('列表中存在 IP' if manager.query(args.query) else '列表中不存在 IP')
    if args.generate:
        if not args.port or not args.path:
            print("端口和路径是 URL 生成所必需的。")
            exit(1)
        manager.generate_urls(args.port, args.path)
        manager.save_urls_to_file()
    if args.method or args.use_system or args.command:
        php_con.test_all_urls(command=args.command, method=args.method, use_system=args.use_system)
