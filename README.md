# Intro to my Flask webapp process:

1. Generic pre-reqs:
	1. Install python: https://www.python.org/downloads/
	1. Install pip: https://pip.pypa.io/en/stable/installing/
	1. Install virtualenv: https://virtualenv.pypa.io/en/latest/installation/
		- `pip install virtualenv`
1. Windows-specific pre-reqs:
	1. Install VS C++ build tools: https://visualstudio.microsoft.com/thank-you-downloading-visual-studio/?sku=BuildTools&rel=15

1. build a virtualenv for your project
	- `cd <project path>`
	- `virtualenv venv`
	- Linux: `source venv/bin/activate`
	- Windows: `venv/Scripts/activate`
1. Install requirements:
	- `pip install -r requirements.txt`
1. run temp server:
	- `python src/app.py`

Point your web browser to `localhost:5000`

# Database setup
1. Install PostgresSQL (https://www.postgresql.org/download/)
	- Use an admin username/password that we can all agree on during the setup procedure.
	- This is different based on your OS, just make sure you don't deviate from the defaults.
1. Set your database URL environmental variable by running this at the command prompt/shell:
	* Linux: `export DATABASE_URL="postgresql://cxp:choresarereallyfun@localhost/ChoreExplore"`
	* Windows (cmd): `setx DATABASE_URL "postgresql://cxp:choresarereallyfun@localhost/ChoreExplore"`
	* *Note: that cxp and choresarereallyfun are just sample username/password values*
	* *Note: ChoreExplore is the database name, and this is case-sensitive*

# Building the frontend

Pre-reqs:
1. Install Node (https://nodejs.org/en/download/)
1. Instal Gulp (`npm install gulp -g`  from the command line)
1. Install Yarn (https://yarnpkg.com/en/docs/install)

Open your terminal, execute the following in the root folder:
1. `yarn` (Downloads all frontend/development dependencies)
1. `gulp fonts` (Copies fontawesome fonts over to static/fonts)
1. `gulp min` (runs min to minify JS/CSS files)
	- You need to re-run `gulp min` every time you make a change to JS/CSS files for it to re-minify and pick up your changes.



