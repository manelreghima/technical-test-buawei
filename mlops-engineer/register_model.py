import requests
import unittest

class TestInferenceServer(unittest.TestCase):
    
    def test_register_model(self):
        new_model_name='model_05'
        model_path = './'+new_model_name+'.onnx'

        # send POST request to register the new model
        with open(model_path, 'rb') as model_file:
            files = {'file': (new_model_name, model_file, 'application/octet-stream')}
            url = f'http://localhost:3000/api/v1/register?model_name='+new_model_name
            response = requests.post(url, files=files)
        
        self.assertEqual(response.status_code, 200)
        self.assertIn('Model registered successfully', response.text)


if __name__ == "__main__":
    unittest.main()
