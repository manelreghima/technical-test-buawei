import requests
import unittest
import random

# Load models for canary release testing
model_old_version = 'model_08'
model_new_version = 'model_10'
class TestInferenceServer(unittest.TestCase):


    def test_model_versioning(self):
        """
        Test to ensure that the model versioning is handled correctly.
        This test would ideally check for the existence of different model versions
        and their metadata.
        """
        response = requests.get("http://localhost:3000/api/v1/list")
        self.assertEqual(response.status_code, 200)

        # Extract the version info from the response
        versions_info = response.json()
        
        # Check if the response is a list, then the list itself is the versions info
        if isinstance(versions_info, list):
            # Check if the expected version exists
            
            self.assertIn(model_new_version, versions_info)
        else:
            # If it's not a list, check that the response contains version information as a key
            self.assertIn('versions', versions_info)

            # Check if the expected version exists within the 'versions' key
            self.assertIn(model_new_version, versions_info['versions'])

    
    def load_model(self, model_name):
        response = requests.post(f'http://localhost:3000/api/v1/load?name={model_name}')
        self.assertEqual(response.status_code, 200, f"Failed to load model {model_name}: {response.text}")
        return response
    
    def run_inference_for_model(self, model_name, payload):
        # Send this in the POST request with the payload
        response = requests.post(
            f'http://localhost:3000/api/v1/run/{model_name}',
            json=payload  # Ensure that the payload is passed as a JSON-formatted string
        )
        self.assertEqual(response.status_code, 200, f"Failed to run model {model_name}: {response.text}")
        return response


    def test_ab_testing(self):
        """
        Test A/B testing of model versions.
        This assumes that the server can handle two versions and return their performance.
        """
        # Load models for A/B testing
        load_v8=self.load_model(model_old_version)
        load_v10=self.load_model(model_new_version)
        # Inside test_ab_testing method, replace calls to run_inference_for_model with:
        with open('./image_64.json', 'r') as file:
            image_data = file.read()
        sample_payload = {"image": image_data}
        
        response_v8 = self.run_inference_for_model(model_old_version, sample_payload)
        response_v10 = self.run_inference_for_model(model_new_version, sample_payload)


        self.assertEqual(response_v8.status_code, 200)
        self.assertEqual(response_v10.status_code, 200)

        # Run inferences for A/B testing
        for _ in range(10):
            response_v8_inference = self.run_inference_for_model(model_old_version,sample_payload)
            response_v10_inference = self.run_inference_for_model(model_new_version,sample_payload)
            self.assertEqual(response_v8_inference.status_code, 200)
            self.assertEqual(response_v10_inference.status_code, 200)
    
    def test_canary_release(self):
        """
        Test canary release of a new model version.
        This will send a certain percentage of inference requests to the new model version
        and the rest to the old one.
        """
        
        self.load_model(model_old_version)
        self.load_model(model_new_version)

        # Simulate canary release where 10% of the traffic is sent to the new version
        canary_percentage = 0.10  # 10% of the traffic goes to the new model

        with open('./image_64.json', 'r') as file:
            image_data = file.read()
        sample_payload = {"image": image_data}

        # Perform canary testing
        number_of_tests = 100  # Total number of tests to simulate
        for _ in range(number_of_tests):
            # Determine which model version to call based on the canary percentage
            model_to_call = model_new_version if random.random() < canary_percentage else model_old_version
            response = self.run_inference_for_model(model_to_call, sample_payload)
            self.assertEqual(response.status_code, 200)
        
    def test_unload_model(self):
    
        response = requests.post('http://localhost:3000/api/v1/unload?name='+model_new_version)
        response = requests.post('http://localhost:3000/api/v1/unload?name='+model_old_version)

        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.content, b'200')

if __name__ == "__main__":
    unittest.main()
