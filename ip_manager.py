import ipaddress
import rich


class IPManager:
    def __init__(self):
        self.ip_list = set()
        self.urls = set()
        self.file_path = 'ips.txt'
        self.file_urls = 'urls.txt'
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
        rich.print("IP地址列表为：", self.ip_list)

    def query(self, ip):
        return ip in self.ip_list

    def _save_to_file(self):
        with open(self.file_path, 'w') as f:
            for ip in sorted(self.ip_list):
                f.write(str(ip) + '\n')

    def generate_urls(self, port, path):
        for ip in self.ip_list:
            url = f"http://{ip}:{port}{path}"
            self.urls.add(url)

    def save_urls_to_file(self):
        with open(self.file_urls, 'w') as file:
            for url in self.urls:
                file.write(url + '\n')
        rich.print(f"URLs have been saved to {self.file_urls}")

