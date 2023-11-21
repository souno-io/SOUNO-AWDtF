from datetime import datetime
from concurrent.futures import ThreadPoolExecutor
import paramiko
from rich import print as rich_print
from typing import Tuple, Optional


class SSHConnectionTester:
    def __init__(self, ips_file: str = 'ips.txt', output_file: str = 'flags.txt', max_threads: int = 5):
        self.ips_file = ips_file
        self.output_file = output_file
        self.max_threads = max_threads

    def read_ips(self) -> list:
        with open(self.ips_file, 'r') as file:
            return [ip.strip() for ip in file.readlines()]

    def write_result(self, ip: str, port: int, result: Optional[str]):
        with open(self.output_file, 'a') as file:
            if result:
                file.write(f"[ssh][{datetime.now()}] {ip}:{port} {result}")

    def execute_command(self, ip: str, port: int, command: str, username: str, password: Optional[str]) -> Tuple[
        str, Optional[str]]:
        client = paramiko.SSHClient()
        try:
            client.set_missing_host_key_policy(paramiko.AutoAddPolicy())
            client.connect(ip, port=port, username=username, password=password, timeout=1)
            stdin, stdout, stderr = client.exec_command(command)
            result = stdout.read().decode('utf-8')
            error = stderr.read().decode('utf-8')
            if error:
                rich_print(f"[bold red][-][ssh][{datetime.now()}]{ip}:{port} Error: {error}")
            else:
                rich_print(f"[bold green][+][ssh][{datetime.now()}]{ip}:{port} Response: {result}")
            return ip, result
        except Exception as e:
            rich_print(f"[!][ssh][{datetime.now()}]{ip}:{port} Connection failed: {e}")
            return ip, None
        finally:
            client.close()

    def test_all_ips(
            self, port: int = 22, command: str = 'cat /flag', username: str = "root", password: Optional[str] = None
    ):
        ips = self.read_ips()
        with ThreadPoolExecutor(max_workers=self.max_threads) as executor:
            futures = {executor.submit(self.execute_command, ip, port, command, username, password): ip for ip in ips}
            for future in futures:
                ip, result = future.result()
                self.write_result(ip, port, result)
