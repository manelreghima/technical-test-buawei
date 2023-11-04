# technical-test-buawei
# Data Engineer Test
## Install Requirements
### Access the 'data-engineer' folder
```bash
cd data-engineer
```
### Set Up a Python Virtual Environment
```bash
python -m venv venv
venv\Scripts\activate
pip install -r requirements.txt
```
### Install data-provider as a Python module
```bash
pip install .
```
### Generate a fixed number of new annotations
```bash
python -m data_provider generate 20 --output-dir ./images
```





