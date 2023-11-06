import os
import subprocess

# Set the directory where the zip files are located
images_directory = "./images"
# Set the URL endpoint where files will be uploaded
upload_url = "http://127.0.0.1:8000/upload"

# Loop through all .zip files in the images directory
for filename in os.listdir(images_directory):
    if filename.endswith(".zip"):
        # Construct the full file path
        file_path = os.path.join(images_directory, filename)
        # Construct the curl command
        curl_command = [
            'curl',
            '-X', 'POST',
            '-F', f"file=@{file_path}",
            upload_url
        ]

        # Print the command that will be executed
        print('Executing:', ' '.join(curl_command))
        
        # Perform the POST request with curl
        try:
            # Execute the curl command
            result = subprocess.run(curl_command, check=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
            # Print curl output
            print(result.stdout.decode())
        except subprocess.CalledProcessError as e:
            # Print any errors
            print(e.stderr.decode())

        print(f"Uploaded {filename}")
