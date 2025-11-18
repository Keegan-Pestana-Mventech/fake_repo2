from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
import uvicorn
import sys
import os

# Get API name from environment or default
API_NAME = os.environ.get("API_NAME", "Test API")

app = FastAPI(title=API_NAME, version="1.0.0")

# CORS configuration - critical for Tauri app communication
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Allows all origins (safe for local desktop app)
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

@app.get("/")
async def root():
    """Root endpoint - basic connectivity check"""
    return {
        "status": "ok",
        "message": f"{API_NAME} is running",
        "api_name": API_NAME
    }

@app.get("/health")
async def health():
    """Health check endpoint - used by frontend validation"""
    return {
        "status": "healthy",
        "api_name": API_NAME,
        "message": "All systems operational"
    }

@app.get("/info")
async def info():
    """Detailed API information"""
    return {
        "api_name": API_NAME,
        "version": "1.0.0",
        "endpoints": [
            {"path": "/", "method": "GET", "description": "Root endpoint"},
            {"path": "/health", "method": "GET", "description": "Health check"},
            {"path": "/info", "method": "GET", "description": "API information"},
            {"path": "/test", "method": "GET", "description": "Test endpoint with sample data"},
            {"path": "/shutdown", "method": "GET", "description": "Shutdown endpoint"},
        ]
    }

@app.get("/test")
async def test():
    """Test endpoint with sample data"""
    return {
        "status": "success",
        "api_name": API_NAME,
        "data": {
            "sample_string": "Hello from Python!",
            "sample_number": 50,
            "sample_array": [10, 20, 30, 40, 50],
            "sample_object": {
                "nested_key": "nested_value",
                "nested_number": 999
            }
        },
        "message": "This is sample test data API 2"
    }

@app.get("/shutdown")
async def shutdown():
    """Graceful shutdown endpoint - called by Tauri on app close"""
    print(f"[{API_NAME}] Received shutdown request")
    print(f"[{API_NAME}] Performing cleanup...")
    
    # Perform any necessary cleanup here
    # (close database connections, save state, etc.)
    
    print(f"[{API_NAME}] Shutdown complete")
    os._exit(0)

if __name__ == "__main__":
    # Port is passed as first command line argument by Tauri
    port = 8000
    if len(sys.argv) > 1:
        try:
            port = int(sys.argv[1])
        except ValueError:
            print(f"[{API_NAME}] Invalid port argument: {sys.argv[1]}, using default 8000")
    
    print(f"[{API_NAME}] Starting on port {port}...")
    print(f"[{API_NAME}] Health check available at: http://127.0.0.1:{port}/health")
    
    # Run the FastAPI app
    uvicorn.run(
        app,
        host="127.0.0.1",  # Localhost only - security
        port=port,
        log_level="info"
    )