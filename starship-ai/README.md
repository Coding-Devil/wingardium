# Readme

This project simply serves as a reference for how to construct a TUBS3 structure for CI/CD.  As such, 
it contains no actual source code.  In fact, it does nothing successfully ;)

SET THE PROJECT PYTHON DEV ENVIRONMENT

1. visit to set your Python Dev environment: https://confluence.ext.net.nokia.com/display/PATHFINDER/Python+Dev+Environment+Setup
On your linux, run the following comands:

Install pyenv -follow the page, READEME has installation steps.
https://github.com/pyenv/pyenv
 
2. sudo apt install -y   libbz2-dev   libsqlite3-dev   libreadline-dev   tk-dev   libffi-dev   libssl-dev   zlib1g-dev   liblzma-dev
 
3. pyenv install 3.10.16
 
4. pyenv global 3.10.16
 
5. Checkout the starship_ai and cd into the top-level directory of your codebase.
 python -m venv venv
 
7. source venv/bin/activate
 
8. pip install tox
 
9. pip install -r requirements.txt





RUNNING LOCALY

1. cd into starship_ai.
 
2. source venv/bin/activate
 
3. tox -e test_package

BUILDING A CONTAINER
1. cd into starship_ai
 
2. source venv/bin/activate
 
3. tox -e build_container

CHECK LINT
 
from starship_ai run "tox -e lint", fix all problems.


START starship_ai

if you did not activeate python environment already
source venv/bin/activate

from directory src run:
python -m ai.main --config_file ../starship.yaml

TO ACCESS DOCS with all APIS

go to your browers: http://localhost:5050/starship_ai/v1/docs
port info can be founded in starship.yaml

All APIs are defined in the starship.yaml
 

