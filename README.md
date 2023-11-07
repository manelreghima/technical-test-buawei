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
### Install data-provider
```bash
pip install .
```
### Generate a fixed number of new annotations
```bash
python -m data_provider generate 20 --output-dir ./images
```
# Data MLops Test
## Install Requirements
### Access the 'mlops-engineer' folder
```bash
cd mlops-engineer
```
### Set Up a Python Virtual Environment
```bash
python -m venv venv
venv\Scripts\activate
pip install -r requirements.txt
```
### Install inference-server
```bash
pip install .
```






