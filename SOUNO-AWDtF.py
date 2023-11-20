import argparse
from ip_manager import IPManager
from banner import print_banner

if __name__ == '__main__':
    print_banner()

    parser = argparse.ArgumentParser(description='Manage IP addresses and generate a URL list.')
    parser.add_argument('-a', '--add', type=str, help='Add IP range to list')
    parser.add_argument('-r', '--remove', type=str, help='Remove IP range from list')
    parser.add_argument('-q', '--query', type=str, help='Query a specific IP')
    parser.add_argument('-s', '--save', type=str, help='Save the list to a file')
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
    if args.query:
        print('IP exists in list' if manager.query(args.query) else 'IP does not exist in list')
