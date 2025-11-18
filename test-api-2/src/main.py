from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
import uvicorn
import sys
import os

# Test Api 2 - Pandas endpoint example
try:
    import pandas as pd
except ImportError:
    pd = None


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
    """Test endpoint with sample data, customized by API_NAME"""
    
    sample_list = [1, 2, 3, 4, 5]
    data_payload = {}
    data_type = "default"
    
    if pd:
        try:
            df = pd.DataFrame({
                'column_a': sample_list,
                'column_b': [x * 2 for x in sample_list]
            })
            data_payload = df.to_dict('records') # 'records' format: [{"col_a": 1, "col_b": 2}, ...]
            data_type = "pandas_dataframe_as_dict"
        except Exception as e:
            data_payload = {"error": f"Pandas processing failed: {e}"}
            data_type = "error"
    else:
        data_payload = {"error": "Pandas is not installed"}
        data_type = "error"
        
    return {
        "status": "success",
        "api_name": API_NAME,
        "data_type": data_type,
        "data": data_payload,
        "message": f"This is test data from {API_NAME}"
    }


@app.get("/shutdown")
async def shutdown():
    """Graceful shutdown endpoint - called by Tauri on app close"""
    print(f"[{API_NAME}] Received shutdown request")
    print(f"[{API_NAME}] Performing cleanup...")
    
    # Perform any necessary cleanup here
    # (close database connections, save state, etc.)
    
    print(f"[{API_NAME}] Shutdown complete")
    # NOTE: os._exit(0) is what causes the network error on the client,
    # as it terminates the process immediately without sending a response.
    # This is expected.
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
    print(f"[{API_NAME}] API_NAME: {API_NAME}")
    print(f"[{API_NAME}] Health check available at: http://127.0.0.1:{port}/health")
    print(f"[{API_NAME}] Test data available at: http://127.0.0.1:{port}/test")
    
    # Run the FastAPI app
    uvicorn.run(
        app,
        host="127.0.0.1",  # Localhost only - security
        port=port,
        log_level="info"
    )