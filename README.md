# Backend API


A backend API using Python and FastAPI, that uses RESTful routes to connect the front-end with a Postgres server. Built as a project with Northcoders.


## How to Run
Note: all commands should be run in the project root directory.

### Step 1: Install dependencies
- Create and activate your virtual environment: `python -m venv .venv`.
- Then `source .venv/bin/activate`.
- Run `pip install -r requirements.txt` to install all dependencies into the environment.
- Fill in the `.env.example` file with your local credentials (except for the DB_NAME) and rename it to `.env`.

### Step 2: Creating the database
Run `psql -f db/setup.sql`. This needs to only be done once, it creates the database locally on the system using Postgres.

### Step 3: Seeding the database
Run `python db/seed.py` or the seed() function from the same file. 

This (re)creates the tables in the database, and seeds them with sample data. Should be run initially, and any subsequent time the database needs to be completely reset and reseeded.
