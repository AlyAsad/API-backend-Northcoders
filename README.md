# Backend API


A backend API using Python and FastAPI, that uses RESTful routes to connect the front-end with a Postgres server. Built as a project with Northcoders.


## How to Run
### Step 1: Install dependencies
Create and activate your virtual environment: `python -m venv .venv`, and then `source .venv/bin/activate`. Run `pip install -r requirements.txt` to install all dependencies into the environment.

### Step 2: Creating the database
Run `psql -f db/setup.sql`