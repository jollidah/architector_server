from dotenv import load_dotenv
import os

load_dotenv()

OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")
FAISS_PATH = os.getenv("FAISS_PATH")
CSV_PATH = os.getenv("CSV_PATH")