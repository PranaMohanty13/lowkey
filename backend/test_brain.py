import os
from dotenv import load_dotenv
from langchain_google_genai import ChatGoogleGenerativeAI

# 1. Load the vault (access secrets in .env)
load_dotenv()

# Debug: Check if the key is actually loaded
api_key = os.getenv("GOOGLE_API_KEY")
if not api_key:
    print("❌ ERROR: GOOGLE_API_KEY not found in .env file!")
    exit()
else:
    print("✅ Key found (starts with):", api_key[:5] + "...")

# 2. Wake up the Brain
# We use LangChain's wrapper so it plugs into our future RAG system
llm = ChatGoogleGenerativeAI(model="gemini-2.5-flash")

# 3. Send a test message
print("\n--- Sending signal to Google Gemini... ---")
try:
    response = llm.invoke("Hello! Are you online and ready to be an AI Engineer?")
    
    # 4. Print the result
    print("\n--- Response Received: ---")
    print(response.content)
except Exception as e:
    print("\n❌ Connection Failed:")
    print(e)