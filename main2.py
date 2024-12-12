import requests
import json
import time
from datetime import datetime

class DataCollector:
    def __init__(self, api_url, headers=None, params=None, storage_file="data.json"):
        self.api_url = api_url
        self.headers = headers or {}
        self.params = params or {}
        self.storage_file = storage_file
        self.data = []

    def fetch_data(self):
        try:
            response = requests.get(self.api_url, headers=self.headers, params=self.params)
            response.raise_for_status()
            return response.json()
        except requests.exceptions.RequestException as e:
            print(f"An error occurred: {e}")
            return None

    def save_data(self, data):
        with open(self.storage_file, 'a') as file:
            entry = {
                "timestamp": datetime.now().isoformat(),
                "data": data
            }
            file.write(json.dumps(entry) + "\n")
            self.data.append(entry)
    
    def run(self, interval=60):
        while True:
            data = self.fetch_data()
            if data:
                self.save_data(data)
                print("Data saved successfully.")
            time.sleep(interval)

# Usage
collector = DataCollector(
    api_url="https://galaxy.ansible.com/api/v1/roles/",
)
collector.run()
