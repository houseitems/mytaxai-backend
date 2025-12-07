from fastapi import FastAPI
import os

app = FastAPI(title="MyTaxAI Debug")

print("🚀 DEBUG: Starting MyTaxAI Backend")
print(f"🚀 DEBUG: DEEPSEEK_API_KEY exists: {'DEEPSEEK_API_KEY' in os.environ}")
print(f"🚀 DEBUG: DEEPSEEK_API_KEY value: {os.getenv('DEEPSEEK_API_KEY', 'NOT SET')[:10]}...")

@app.get("/")
def root():
    return {"message": "DEBUG - Basic app working"}

@app.get("/health")
def health():
    return {"status": "healthy", "debug": True}

@app.get("/test")
def test():
    return {"test": "ok", "env_keys": list(os.environ.keys())}
