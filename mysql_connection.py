import pymysql
from datetime import datetime
from concurrent.futures import ThreadPoolExecutor, as_completed  # 确保导入as_completed
from rich import print as rich_print


class MySQLConnectionTester:
    def __init__(self, port: int, username: str, password: str, database: str = None, max_workers: int = 5):
        self.port = port
        self.username = username
        self.password = password
        self.database = database
        self.max_workers = max_workers

    def read_ips(self):
        with open('ips.txt', 'r') as file:
            ips = [line.strip() for line in file.readlines()]  # 使用readlines()确保读取所有行
        return ips

    def test_connection(self, host: str) -> str:
        try:
            connection = pymysql.connect(host=host, port=self.port, user=self.username, password=self.password,
                                         database=self.database)
            cursor = connection.cursor()
            cursor.execute("SELECT VERSION()")
            version = cursor.fetchone()
            result = f"MySQL version: {version[0]}"
            rich_print(f"[bold green][+][mysql][{datetime.now()}]{host}:{self.port} Response: {result}")
            return result
        except Exception as e:
            rich_print(f"[bold red][-][mysql][{datetime.now()}]{host}:{self.port} Connection failed: {e}")
            return f"Connection failed: {e}"
        finally:
            if 'connection' in locals() and connection.open:
                connection.close()

    def test_all_connections(self):
        ips = self.read_ips()
        results = []
        with ThreadPoolExecutor(max_workers=self.max_workers) as executor:
            futures = {executor.submit(self.test_connection, host): host for host in ips}
            for future in as_completed(futures):
                results.append(future.result())
        return results
