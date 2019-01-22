# Pre-requisities

## Python

### Environment setup
1. Install python: https://www.python.org/downloads/
1. Install pip: https://pip.pypa.io/en/stable/installing/
1. Install virtualenv: https://virtualenv.pypa.io/en/latest/installation/
	1. `pip install virtualenv`
1. Windows-specific pre-reqs:
	1. Install VS C++ build tools: https://visualstudio.microsoft.com/thank-you-downloading-visual-studio/?sku=BuildTools&rel=15

### Virtual Environment
1. build a virtualenv for your project
	- `cd <project path>`
	- `virtualenv venv`
	- Linux: `source venv/bin/activate`
	- Windows: `venv/Scripts/activate`
1. Install application requirements in your virtual environment:
	- `pip install -r requirements.txt`
1. Run the application (make sure you run this from the project directory):
	- `python src/app.py`

Point your web browser to `http://localhost:5000`

## Database setup
1. Install PostgresSQL (https://www.postgresql.org/download/)
	- Use an admin username/password that you will remember later.
	- This is different based on your OS, just make sure you don't deviate from the defaults.
1. Create the "ChoreExplore" Database
	- You can do this using PGAdmin (should have been installed if you ran the Windows installer), or using the command line tool.
	- Create a user account 'cxp' with the password 'choresarereallyfun'
		- This is hard-coded for now into our config, will change this in production
	- Make 'cxp' the owner of the ChoreExplore database
	- Make 'cxp' the owner of the public schema under the ChoreExplore database
1. Run the python setup scripts
	- From the project directory, run:
		1. `python .\setup-scripts\XX-CleanDatabase.py`
			- This script deletes all of the tables (cleans up) and prepares for the next script below
		2. `python .\setup-scripts\01-CreateAndSeedTables.py`
			- This will create all of the necessary tables, seed the administrator user, and seed the roles.
	- You should run these two commands every time you check out a new branch - things may have changed.


## Building the frontend

### Pre-reqs:
1. Install Node (https://nodejs.org/en/download/)
1. Instal Gulp (`npm install gulp -g`  from the command line)
1. Install Yarn (https://yarnpkg.com/en/docs/install)

### Build it
Open your terminal, execute the following in the root folder:
1. `yarn` (Downloads all frontend/development dependencies)
1. `gulp fonts` (Copies fontawesome fonts over to static/fonts)
1. `gulp min` (runs min to minify JS/CSS files)
	- You need to re-run `gulp min` every time you make a change to JS/CSS files for it to re-minify and pick up your changes.



