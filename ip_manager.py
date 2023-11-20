import ipaddress
import re
import rich

class IPManager:
    def __init__(self):
        self.ip_list = set()
        self.file_path = 'ip.txt'
        self.load_from_file()
        
    def load_from_file(self):
        try:
            with open(self.file_path, 'r') as f:
                for line in f:
                    self.ip_list.add(line.strip())
        except FileNotFoundError:
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
        self._save_to_file()
        self.show()

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
        self._save_to_file()
        self.show()
    
    def show(self):
        rich.print("IP地址列表为：",self.ip_list)

    def query(self, ip):
        return ip in self.ip_list

    def _save_to_file(self):
        with open(self.file_path, 'w') as f:
            for ip in sorted(self.ip_list):
                f.write(str(ip) + '\n')

if __name__ == '__main__':
    import argparse

    parser = argparse.ArgumentParser(description='管理IP地址或者生成url')
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
