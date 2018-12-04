Intro to my Flask webapp process:

1. install python: https://www.python.org/downloads/
2. install pip: https://pip.pypa.io/en/stable/installing/
3. install virtualenv: https://virtualenv.pypa.io/en/latest/installation/
   - `pip install virtualenv`
4. build a virtualenv for your project
    - `cd <project path>`
    - `virtualenv venv`
    - Linux: `source venv/bin/activate`
    - Windows: `source venv/Scripts/activate`
5. install requirements:
    - `pip install -r requirements.txt`
6. run temp server:
    - `python src/routes.py`

Point your webbrowser to `localhost:5000`
