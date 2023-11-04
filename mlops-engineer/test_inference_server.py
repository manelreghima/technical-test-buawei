import requests
import unittest
import time
import csv


class TestInferenceServer(unittest.TestCase):
    def store_metrics(self, model_name, endpoint, execution_time):
        with open('metrics.csv', 'a', newline='') as csvfile:
            writer = csv.writer(csvfile)
            writer.writerow([model_name, endpoint, execution_time])

    def test_list_models(self):
        start_time = time.time()
        response = requests.get("http://localhost:3000/api/v1/list")
        end_time = time.time()
        execution_time = end_time - start_time
        self.store_metrics('N/A', 'list', execution_time)

        self.assertEqual(response.status_code, 200)
        self.assertIn("model_10", response.json())

    def test_load_model(self):
        start_time = time.time()
        response = requests.post('http://localhost:3000/api/v1/load?name=model_10')
        end_time = time.time()
        execution_time = end_time - start_time
        self.store_metrics('model_10', 'load', execution_time)

        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.text, '200')

    def test_run_inference(self):
        # base64-encoded image
        with open('./image_64.json', 'r') as file:
            image_data = file.read()

        start_time = time.time()
        response = requests.post('http://localhost:3000/api/v1/run/model_10', json={'image': image_data})
        end_time = time.time()
        execution_time = end_time - start_time
        self.store_metrics('model_10', 'run', execution_time)

        self.assertEqual(response.status_code, 200)
        self.assertIn('category', response.json())

    def test_unload_model(self):
        start_time = time.time()
        response = requests.post('http://localhost:3000/api/v1/unload?name=model_10')
        end_time = time.time()
        execution_time = end_time - start_time
        self.store_metrics('model_10', 'unload', execution_time)

        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.content, b'200')


    def test_register_model(self):
        model_name = 'arcfaceresnet100-11-int8'
        model_path = './arcfaceresnet100-11-int8.onnx'

        # send POST request to register the new model
        with open(model_path, 'rb') as model_file:
            files = {'file': (model_name, model_file, 'application/octet-stream')}
            url = f'http://localhost:3000/api/v1/register?model_name={model_name}'
            response = requests.post(url, files=files)
        
        self.assertEqual(response.status_code, 200)
        self.assertIn('Model registered successfully', response.text)

    

if __name__ == "__main__":
    unittest.main()
