import requests
import unittest
import random
import csv
import psutil
import os
import time

model_old_version = 'model_08'
model_new_version = 'model_10'

class TestInferenceServer(unittest.TestCase):

    def setUp(self):
        self.metrics_file = 'test_metrics.csv'
        self.file_exists = os.path.isfile(self.metrics_file)

    def store_metrics(self, model_name, test_type, execution_time, memory_usage):
        with open(self.metrics_file, 'a', newline='') as csvfile:
            writer = csv.writer(csvfile)
            if not self.file_exists:
                writer.writerow(['Model Name', 'Test Type', 'Execution Time', 'Memory Usage (MB)'])
                self.file_exists = True
            writer.writerow([model_name, test_type, execution_time, memory_usage])

    def get_memory_usage(self):
        process = psutil.Process(os.getpid())
        memory_info = process.memory_info()
        return memory_info.rss / (1024 * 1024)  # Convert bytes to MB

    def test_model_versioning(self):
        response = requests.get("http://localhost:3000/api/v1/list")
        self.assertEqual(response.status_code, 200)
        versions_info = response.json()
        if isinstance(versions_info, list):
            self.assertIn(model_new_version, versions_info)
        else:
            self.assertIn('versions', versions_info)
            self.assertIn(model_new_version, versions_info['versions'])

    def load_model(self, model_name):
        response = requests.post(f'http://localhost:3000/api/v1/load?name={model_name}')
        self.assertEqual(response.status_code, 200, f"Failed to load model {model_name}: {response.text}")
        return response

    def run_inference_for_model(self, model_name, payload):
        response = requests.post(
            f'http://localhost:3000/api/v1/run/{model_name}',
            json=payload
        )
        self.assertEqual(response.status_code, 200, f"Failed to run model {model_name}: {response.text}")
        return response

    def test_ab_testing(self):
        self.load_model(model_old_version)
        self.load_model(model_new_version)

        with open('./image_64.json', 'r') as file:
            image_data = file.read()
        sample_payload = {"image": image_data}

        for model_version in (model_old_version, model_new_version):
            execution_times = []
            memory_usages = []
            for _ in range(10):  # Run 10 tests for each version
                memory_before = self.get_memory_usage()
                start_time = time.time()
                response = self.run_inference_for_model(model_version, sample_payload)
                memory_after = self.get_memory_usage()
                end_time = time.time()
                execution_time = end_time - start_time
                memory_usage = memory_after - memory_before
                self.assertEqual(response.status_code, 200)
                execution_times.append(execution_time)
                memory_usages.append(memory_usage)
            avg_execution_time = sum(execution_times) / len(execution_times)
            avg_memory_usage = sum(memory_usages) / len(memory_usages)
            self.store_metrics(model_version, 'AB Testing', avg_execution_time, avg_memory_usage)

    def test_canary_release(self):
        self.load_model(model_old_version)
        self.load_model(model_new_version)

        canary_percentage = 0.10
        
        with open('./image_64.json', 'r') as file:
            image_data = file.read()
        sample_payload = {"image": image_data}
        execution_times = []
        memory_usages = []
        number_of_tests = 10
        for _ in range(number_of_tests):
            memory_before = self.get_memory_usage()
            start_time = time.time()
            model_to_call = model_new_version if random.random() < canary_percentage else model_old_version
            response = self.run_inference_for_model(model_to_call, sample_payload)
            memory_after = self.get_memory_usage()
            end_time = time.time()
            execution_time = end_time - start_time
            memory_usage = memory_after - memory_before
            self.assertEqual(response.status_code, 200)
            execution_times.append(execution_time)
            memory_usages.append(memory_usage)
            test_type = 'Canary Release - New Version' if model_to_call == model_new_version else 'Canary Release - Old Version'
            self.store_metrics(model_to_call, test_type, execution_time, memory_usage)

    def test_unload_model(self):
        response = requests.post('http://localhost:3000/api/v1/unload?name='+model_new_version)
        self.assertEqual(response.status_code, 200)
        response = requests.post('http://localhost:3000/api/v1/unload?name='+model_old_version)
        self.assertEqual(response.status_code, 200)

if __name__ == "__main__":
    unittest.main()
