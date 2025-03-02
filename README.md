# AI HR Assisstant

The system allows candidates to submit their profiles, resumes, and job URLs, and then engages them in a chatbot-based screening process. Leveraging Azure OpenAI GPT-4.0 mini model, the system generates relevant screening questions based on the job description extracted from the provided URL. The candidate's responses are analyzed, and an assessment summary, including a score and overall evaluation, is generated.

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
- navigate to hr-bot folder and do `npm install`
- run frontend code `npm start`

### This project is developed as assignment of IIIT, Bangalore AI/ML PG Program. Please feel free to extend this based on your requirements. 