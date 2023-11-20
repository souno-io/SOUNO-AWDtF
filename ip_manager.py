import ipaddress
import re

class IPManager:
    def __init__(self):
        self.ip_list = set()

    def add(self, ip_rule):
        if '-' in ip_rule:
            start_ip, end_ip = ip_rule.split('-')
            start_ip = ipaddress.ip_address(start_ip)
            end_ip = ipaddress.ip_address(end_ip)
            for ip_int in range(int(start_ip), int(end_ip) + 1):
                self.ip_list.add(str(ipaddress.ip_address(ip_int)))
        elif '/' in ip_rule:
            network = ipaddress.ip_network(ip_rule, strict=False)
            for ip in network:
                self.ip_list.add(str(ip))
        else:
            self.ip_list.add(ip_rule)

    def remove(self, ip_rule):
        if '-' in ip_rule:
            start_ip, end_ip = ip_rule.split('-')
            start_ip = ipaddress.ip_address(start_ip)
            end_ip = ipaddress.ip_address(end_ip)
            for ip_int in range(int(start_ip), int(end_ip) + 1):
                self.ip_list.discard(str(ipaddress.ip_address(ip_int)))
        elif '/' in ip_rule:
            network = ipaddress.ip_network(ip_rule, strict=False)
            for ip in network:
                self.ip_list.discard(str(ip))
        else:
            self.ip_list.discard(ip_rule)

    def query(self, ip):
        return ip in self.ip_list

    def save_to_file(self, filename):
        with open(filename, 'w') as file:
            for ip in sorted(self.ip_list):
                file.write(f'http://{ip}\n')

if __name__ == '__main__':
    import argparse

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
    if args.save:
        manager.save_to_file(args.save)
