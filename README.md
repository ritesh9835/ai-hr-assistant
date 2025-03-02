# AI HR Assisstant

AI Bot to screen candidate based on Job description

## Required setup
- PgSql
- Python(3.10.8)
- Node.Js

## Steps
- Create database hr_bot on pgsql
- Execute hr_bot_tables.sql to create tables on hr_bot database
- Replace Azure OpenAI key and endpoint in backend-fastpi/main.py file
- Change PgSql db connection details in backend-fastpi/main.py file
- install required packages using pip install `pip install fastapi uvicorn openai psycopg2-binary selenium beautifulsoup4 aiohttp python-dotenv`
- Start the backend server by `uvicorn main:app --reload`
- naviagte to hr-bot folder and do `npm install`
- run frotnend code `npm start`

### This project is developed as assignment of IIIT, Bangalore AI/ML PG Program. Please feel free to extand this based on your requirements. 