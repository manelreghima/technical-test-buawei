import requests
import unittest
import time
import csv
import psutil
import os
import json

#model_name='arcfaceresnet100-11-int8'
model_name='model_10'

class TestInferenceServer(unittest.TestCase):
    
    def store_metrics(self, model_name, endpoint, execution_time, memory_usage, payload_size):
        file_exists = os.path.isfile('./metrics.csv')
        with open('./metrics.csv', 'a', newline='') as csvfile:
            writer = csv.writer(csvfile)
            if not file_exists:
                writer.writerow(['Model Name', 'Endpoint', 'Execution Time', 'Memory Usage (MB)', 'Payload Size (Bytes)'])
            writer.writerow([model_name, endpoint, execution_time, memory_usage, payload_size])

    def get_memory_usage(self):
        process = psutil.Process(os.getpid())
        memory_info = process.memory_info()
        return memory_info.rss / (1024 * 1024)  # Convert bytes to MB

    def get_payload_size(self, payload):
        if isinstance(payload, dict):
            # If the payload is a dictionary, convert it to a string to calculate the size.
            return len(json.dumps(payload).encode('utf-8'))
        elif isinstance(payload, bytes):
            # If the payload is bytes, return its size directly.
            return len(payload)
        elif isinstance(payload, str):
            # If the payload is a string, encode it to bytes to get the size.
            return len(payload.encode('utf-8'))
        else:
            raise ValueError("Unsupported payload type for size calculation")

    def test_list_models(self):
        # No payload for GET request, so payload size is 0
        payload_size = 0

        memory_before = self.get_memory_usage()
        start_time = time.time()
        response = requests.get("http://localhost:3000/api/v1/list")
        end_time = time.time()
        memory_after = self.get_memory_usage()
        execution_time = end_time - start_time
        memory_usage = memory_after - memory_before
        self.store_metrics('N/A', 'list', execution_time, memory_usage, payload_size)

        self.assertEqual(response.status_code, 200)
        self.assertIn(model_name, response.json())

    def test_load_model(self):
        # No significant payload for loading model by name, so payload size is negligible/small
        payload_size = len(model_name)

        memory_before = self.get_memory_usage()
        start_time = time.time()
        response = requests.post('http://localhost:3000/api/v1/load?name='+model_name)
        end_time = time.time()
        memory_after = self.get_memory_usage()
        execution_time = end_time - start_time
        memory_usage = memory_after - memory_before
        self.store_metrics(model_name, 'load', execution_time, memory_usage, payload_size)

        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.text, '200')

    def test_run_inference(self):
        with open('./image_64.json', 'r') as file:
            image_data = file.read()
        
        payload = {'image': image_data}
        payload_size = self.get_payload_size(payload)

        memory_before = self.get_memory_usage()
        start_time = time.time()
        response = requests.post('http://localhost:3000/api/v1/run/'+model_name, json=payload)
        end_time = time.time()
        memory_after = self.get_memory_usage()
        execution_time = end_time - start_time
        memory_usage = memory_after - memory_before
        self.store_metrics(model_name, 'run', execution_time, memory_usage, payload_size)

        self.assertEqual(response.status_code, 200)
        self.assertIn('category', response.json())

    def test_unload_model(self):
        # No significant payload for unloading model by name, so payload size is negligible/small
        payload_size = len(model_name)

        memory_before = self.get_memory_usage()
        start_time = time.time()
        response = requests.post('http://localhost:3000/api/v1/unload?name='+model_name)
        end_time = time.time()
        memory_after = self.get_memory_usage()
        execution_time = end_time - start_time
        memory_usage = memory_after - memory_before
        self.store_metrics(model_name, 'unload', execution_time, memory_usage, payload_size)

        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.content, b'200')


if __name__ == "__main__":
    unittest.main()
