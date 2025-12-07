# Deployment timestamp:[21:38]
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
import os
from openai import OpenAI

app = FastAPI(title="MyTaxAI Backend")

# Allow your frontend to connect
app.add_middleware(
    CORSMiddleware,
    allow_origins=[
        "http://localhost:3000",  # Local development
        "https://mytaxai-app.vercel.app",  # Your Vercel frontend
        "https://*.vercel.app",  # All Vercel deployments
        "https://mytaxai.co.uk",  # Your custom domain (future)
    ],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Initialize DeepSeek - Handle missing key
api_key = os.getenv("DEEPSEEK_API_KEY")
if api_key and api_key != "dummy-key-for-now":
    client = OpenAI(
        api_key=api_key,
        base_url="https://api.deepseek.com"
    )
    print("✅ DeepSeek client initialized")
else:
    client = None
    print("⚠️ DeepSeek API key not set. AI functionality disabled.")

class TaxQuestion(BaseModel):
    question: str
    user_id: str = "anonymous"

@app.get("/")
def root():
    return {"message": "MyTaxAI Backend API"}

@app.get("/health")
def health():
    return {"status": "healthy", "service": "MyTaxAI API"}

@app.post("/api/ask")
async def ask_tax_question(tax_q: TaxQuestion):
    """Ask AI a tax question"""
    # Check if client is initialized
    if client is None:
        return {
            "success": False,
            "error": "DeepSeek API key not configured",
            "message": "Please add DEEPSEEK_API_KEY to Railway Variables"
        }
    
    try:
        response = client.chat.completions.create(
            model="deepseek-chat",
            messages=[
                {"role": "system", "content": "You are a professional UK tax advisor. Always mention this is not professional advice. Use UK tax rates for 2024/25."},
                {"role": "user", "content": tax_q.question}
            ],
            max_tokens=500,
            temperature=0.7
        )
        
        return {
            "success": True,
            "answer": response.choices[0].message.content,
            "tokens": response.usage.total_tokens
        }
        
    except Exception as e:
        return {"success": False, "error": str(e)}

# Simple tax calculator
@app.get("/api/calculate/{income}")
def calculate_tax(income: float):
    """Calculate UK income tax for 2024/25"""
    if income <= 12570:
        tax = 0
    elif income <= 50270:
        tax = (income - 12570) * 0.20
    elif income <= 125140:
        tax = (50270 - 12570) * 0.20 + (income - 50270) * 0.40
    else:
        tax = (50270 - 12570) * 0.20 + (125140 - 50270) * 0.40 + (income - 125140) * 0.45
    
    return {
        "income": income,
        "tax": round(tax, 2),
        "net": round(income - tax, 2),
        "effective_rate": round((tax/income)*100, 2) if income > 0 else 0
    }
