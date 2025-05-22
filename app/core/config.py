from dotenv import load_dotenv
import os

load_dotenv()

OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")
INSTANCE_FAISS_PATH = "data/faiss_db/vultr/instance"
INSTANCE_CSV_PATH = "data/faiss_db/vultr/vultr_filtered_plans.csv"
DB_FAISS_PATH = "data/faiss_db/vultr/db"
DB_CSV_PATH = "data/faiss_db/vultr/Filtered_DBaaS_Plans.csv"
OBJECT_STORAGE_FAISS_PATH = "data/faiss_db/vultr/object_storage"
OBJECT_STORAGE_CSV_PATH = "data/faiss_db/vultr/cluster_tier_mappings_with_city.csv"