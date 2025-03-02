from fastapi import FastAPI, WebSocket, WebSocketDisconnect, UploadFile, Form, File, Depends
from pydantic import BaseModel
from typing import List, Dict
from openai import AzureOpenAI 
import asyncpg
import logging
import os
import json
import PyPDF2
from fastapi.middleware.cors import CORSMiddleware
from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.chrome.options import Options
from webdriver_manager.chrome import ChromeDriverManager
import time
import re

app = FastAPI()

# Configure logging
logging.basicConfig(level=logging.INFO)
app = FastAPI()

# Enable CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:3000"],  # React frontend URL
    allow_credentials=True,
    allow_methods=["*"],  # Allow all HTTP methods
    allow_headers=["*"],  # Allow all headers
)

AZURE_OPENAI_ENDPOINT = os.getenv("AZURE_OPENAI_ENDPOINT")
AZURE_OPENAI_KEY = os.getenv("AZURE_OPENAI_KEY")
AZURE_DEPLOYMENT_NAME = "gpt-4o-mini"

openai_client = AzureOpenAI(  
    azure_endpoint=AZURE_OPENAI_ENDPOINT,  
    api_key=AZURE_OPENAI_KEY,  
    api_version="2024-05-01-preview",
)

DATABASE_URL = 'postgresql://ritesh-pg-user:admin@127.0.0.1:5432/hr_bot'

# Database connection
async def get_db():
    return await asyncpg.connect(DATABASE_URL)

class CandidateInput(BaseModel):
    email: str
    resume_path: str
    job_url: str

def fetch_job_description(job_url: str) -> str:
    options = Options()
    options.add_argument("--headless")  # Run in headless mode (no GUI)
    options.add_argument("--disable-gpu")
    options.add_argument("--no-sandbox")

    # Initialize the Chrome driver with WebDriver Manager
    driver = webdriver.Chrome(service=Service(ChromeDriverManager().install()), options=options)
    
    driver.get(job_url)
    time.sleep(5)  # Wait for JavaScript to load

    # Extract text content from the page
    page_content = driver.find_element("tag name", "body").text
    driver.quit()

    # Clean text
    text_content = re.sub(r'\s+', ' ', page_content).strip()
    
    if any(keyword in text_content for keyword in ["Job Description", "Responsibilities", "Requirements"]):
        prompt = f"Extract job description from the following content:\n{text_content}"
        job_description = generate_openai_response(prompt)  # Assuming generate_openai_response is defined
        logging.info(f"Job Description \n {job_description}")
        return job_description

    raise ValueError("Failed to find 'Job Description' in the job content.")

async def generate_screening_questions(job_desc: str, resume_text: str) -> str:
    prompt = (
        f"Job Description:\n{job_desc}\n\n"
        f"Candidate Resume:\n{resume_text}\n\n"
        "Generate 2 screening questions based on the required job skills. "
        "Return the questions in a JSON array format like [{\"question\": \"What is the question here?\"}, ...]. "
        "Only return the JSON response."
    )
    questions_response = await generate_openai_response(prompt)
    
    # Extract JSON array from the response
    json_match = re.search(r'\[\s*{.*}\s*\]', questions_response[0], re.DOTALL)
    if json_match:
        questions_json = json_match.group(0)
        return questions_json
    else:
        raise ValueError("Failed to extract JSON from OpenAI response")

async def generate_openai_response(prompt: str) -> str:
    response = openai_client.chat.completions.create(
        model="gpt-4o-mini",
        messages=[
            {"role": "system", "content": "You are a AI HR assistant who is responsible for screening the candidate skills based on the job description and resume."},
            {"role": "user", "content": prompt}
        ],
        max_tokens=800,
        temperature=0.7,
    )
    return [choice.message.content.strip() for choice in response.choices]

@app.post("/submit-candidate")
async def submit_candidate(email: str = Form(...), job_url: str = Form(...), file: UploadFile = File(...)):
    file_location = f"resumes/{file.filename}"
    
    # Save the uploaded file to the resumes folder
    with open(file_location, "wb") as buffer:
        buffer.write(await file.read())
    
    # Read the PDF file
    try:
        with open(file_location, "rb") as pdf_file:
            reader = PyPDF2.PdfReader(pdf_file)
            resume_text = ""
            for page_num in range(len(reader.pages)):
                page = reader.pages[page_num]
                resume_text += page.extract_text()
    except Exception as e:
        return {"error": f"Failed to read PDF file: {str(e)}"}
    
    db = await get_db()
    await db.execute("INSERT INTO candidates (email, resume_path, job_url, summary) VALUES ($1, $2, $3, $4)", email, file_location, job_url, resume_text)
    await db.close()
    return {"message": "Candidate submitted", "email": email, "resume_path": file_location, "job_url": job_url}

@app.websocket("/ws/screen/{email}")
async def screen_candidate(websocket: WebSocket, email: str):
    await websocket.accept()
    await websocket.send_text(f"Hi {email}, please wait while we screen your resume...")
    db = await get_db()
    candidate = await db.fetchrow("SELECT * FROM candidates WHERE email = $1", email)
    if not candidate:
        await websocket.send_text("Candidate not found.")
        await websocket.close()
        return
    
    job_desc = await fetch_job_description(candidate["job_url"])
    resume_text = candidate["summary"]
    questions_json = await generate_screening_questions(job_desc, resume_text)
    
    try:
        questions = json.loads(questions_json)
    except json.JSONDecodeError:
        await websocket.send_text("Failed to parse questions.")
        await websocket.close()
        return

    answers = []
    for question in questions:
        await websocket.send_text(question["question"])
        answer = await websocket.receive_text()
        answers.append({"question": question["question"], "answer": answer})
        await db.execute("INSERT INTO candidate_answers (candidate_id, question, answer) VALUES ($1, $2, $3)", candidate["id"], question["question"], answer)

    # Generate score and summary
    assessment_prompt = (
        f"Job Description:\n{job_desc}\n\n"
        f"Candidate Resume:\n{resume_text}\n\n"
        f"Questions and Answers:\n{json.dumps(answers, indent=2)}\n\n"
        "Evaluate the candidate's answers and provide a score out of 100 and a summary of their performance. "
        "Return the response in a JSON format like {\"score\": 85, \"summary\": \"The candidate performed well...\"}. "
        "Only return the JSON response."
    )
    assessment_response = await generate_openai_response(assessment_prompt)

    # Extract JSON from the response
    json_match = re.search(r'{\s*"score":\s*\d+,\s*"summary":\s*".*"\s*}', assessment_response[0], re.DOTALL)
    if json_match:
        assessment_data = json.loads(json_match.group(0))
        score = assessment_data.get("score")
        summary = assessment_data.get("summary")
    else:
        await websocket.send_text("Failed to extract JSON from assessment response.")
        await websocket.close()
        return

    logging.info(assessment_data)
    try:
        assessment_data = json.loads(assessment_response[0])
        score = assessment_data.get("score")
        summary = assessment_data.get("summary")
    except json.JSONDecodeError:
        await websocket.send_text("Failed to parse assessment response.")
        await websocket.close()
        return

    # Insert assessment data into the database
    await db.execute(
        "INSERT INTO assessments (candidate_id, score, summary, created_at) VALUES ($1, $2, $3, NOW())",
        candidate["id"], score, summary
    )

    await websocket.send_text(f"Assessment complete! Score: {score}, Summary: {summary}")
    await websocket.close()
    await db.close()

@app.get("/test-db")
async def test_db_connection():
    try:
        db = await asyncpg.connect(DATABASE_URL)
        version = await db.fetchval("SELECT version();")
        await db.close()
        return {"message": "Database Connected!", "version": version}
    except Exception as e:
        return {"error": str(e)}