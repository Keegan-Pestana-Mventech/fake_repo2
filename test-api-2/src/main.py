from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
import uvicorn
import sys

app = FastAPI(title="My API", version="1.0.0")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

@app.get("/")
async def root():
    return {"status": "ok", "message": "API is running"}

@app.get("/health")
async def health():
    return {"status": "healthy"}

@app.get("/shutdown")
async def shutdown():
    import os
    os._exit(0)

if __name__ == "__main__":
    port = 8000
    if len(sys.argv) > 1:
        port = int(sys.argv[1])
    
    print(f"Starting API on port {port}...")
    uvicorn.run(app, host="127.0.0.1", port=port, log_level="info")