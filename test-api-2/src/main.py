from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
import uvicorn
import sys
import os
import traceback

# Get API name from environment or default
API_NAME = os.environ.get("API_NAME", "Test API")

# CRITICAL: Try imports BEFORE creating FastAPI app
# This ensures we catch import errors early with detailed logging
print(f"[{API_NAME}] Starting import verification...")

# Test numpy import
numpy_available = False
np = None
try:
    import numpy as np
    numpy_available = True
    print(f"[{API_NAME}] ✓ numpy {np.__version__} loaded from {np.__file__}")
except ImportError as e:
    print(f"[{API_NAME}] ✗ numpy import failed: {e}")
    traceback.print_exc()
except Exception as e:
    print(f"[{API_NAME}] ✗ numpy error: {e}")
    traceback.print_exc()

# Test pandas import
pandas_available = False
pd = None
try:
    import pandas as pd
    pandas_available = True
    print(f"[{API_NAME}] ✓ pandas {pd.__version__} loaded from {pd.__file__}")
except ImportError as e:
    print(f"[{API_NAME}] ✗ pandas import failed: {e}")
    traceback.print_exc()
except Exception as e:
    print(f"[{API_NAME}] ✗ pandas error: {e}")
    traceback.print_exc()

print(f"[{API_NAME}] Import verification complete")
print(f"[{API_NAME}] numpy_available: {numpy_available}")
print(f"[{API_NAME}] pandas_available: {pandas_available}")

# Create FastAPI app
app = FastAPI(title=API_NAME, version="1.0.0")

# CORS configuration
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
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
        "message": "All systems operational",
        "numpy_available": numpy_available,
        "pandas_available": pandas_available
    }

@app.get("/debug/imports")
async def debug_imports():
    """Debug endpoint to check import status"""
    import_status = {
        "numpy": {
            "available": numpy_available,
            "version": np.__version__ if numpy_available else None,
            "path": np.__file__ if numpy_available else None
        },
        "pandas": {
            "available": pandas_available,
            "version": pd.__version__ if pandas_available else None,
            "path": pd.__file__ if pandas_available else None
        }
    }
    return {
        "api_name": API_NAME,
        "imports": import_status,
        "python_version": sys.version,
        "executable": sys.executable
    }

@app.get("/debug/routes")
async def debug_routes():
    """Debug endpoint to list all registered routes"""
    routes = []
    for route in app.routes:
        if hasattr(route, "path"):
            routes.append({
                "path": route.path,
                "name": route.name if hasattr(route, "name") else None,
                "methods": list(route.methods) if hasattr(route, "methods") else []
            })
    return {
        "api_name": API_NAME,
        "total_routes": len(routes),
        "routes": routes
    }

@app.get("/info")
async def info():
    """Detailed API information"""
    return {
        "api_name": API_NAME,
        "version": "1.0.0",
        "numpy_available": numpy_available,
        "pandas_available": pandas_available,
        "endpoints": [
            {"path": "/", "method": "GET", "description": "Root endpoint"},
            {"path": "/health", "method": "GET", "description": "Health check"},
            {"path": "/info", "method": "GET", "description": "API information"},
            {"path": "/test", "method": "GET", "description": "Test endpoint with sample data"},
            {"path": "/debug/imports", "method": "GET", "description": "Import status"},
            {"path": "/debug/routes", "method": "GET", "description": "Registered routes"},
            {"path": "/shutdown", "method": "GET", "description": "Shutdown endpoint"},
        ]
    }

@app.get("/test")
async def test():
    """Test endpoint with sample data"""
    print(f"[{API_NAME}] /test endpoint called")
    print(f"[{API_NAME}] numpy_available: {numpy_available}")
    print(f"[{API_NAME}] pandas_available: {pandas_available}")
    
    sample_list = [1, 2, 3, 4, 5]
    data_payload = {}
    data_type = "default"
    error_details = None
    
    # Try numpy processing
    if numpy_available and np:
        try:
            print(f"[{API_NAME}] Attempting numpy processing...")
            np_array = np.array(sample_list) * 10
            data_payload = np_array.tolist()
            data_type = "numpy_array_as_list"
            print(f"[{API_NAME}] ✓ numpy processing successful")
        except Exception as e:
            print(f"[{API_NAME}] ✗ numpy processing failed: {e}")
            traceback.print_exc()
            error_details = {
                "stage": "numpy_processing",
                "error": str(e),
                "traceback": traceback.format_exc()
            }
            data_payload = {"error": f"Numpy processing failed: {e}"}
            data_type = "error"
    
    # Try pandas processing (if numpy failed or not available)
    elif pandas_available and pd:
        try:
            print(f"[{API_NAME}] Attempting pandas processing...")
            df = pd.DataFrame({
                'column_a': sample_list,
                'column_b': [x * 2 for x in sample_list]
            })
            data_payload = df.to_dict('records')
            data_type = "pandas_dataframe_as_dict"
            print(f"[{API_NAME}] ✓ pandas processing successful")
        except Exception as e:
            print(f"[{API_NAME}] ✗ pandas processing failed: {e}")
            traceback.print_exc()
            error_details = {
                "stage": "pandas_processing",
                "error": str(e),
                "traceback": traceback.format_exc()
            }
            data_payload = {"error": f"Pandas processing failed: {e}"}
            data_type = "error"
    else:
        error_details = {
            "stage": "import",
            "error": "Neither numpy nor pandas is available",
            "numpy_available": numpy_available,
            "pandas_available": pandas_available
        }
        data_payload = {"error": "Neither numpy nor pandas is available"}
        data_type = "error"
    
    response = {
        "status": "success" if data_type != "error" else "error",
        "api_name": API_NAME,
        "data_type": data_type,
        "data": data_payload,
        "message": f"This is test data from {API_NAME}"
    }
    
    if error_details:
        response["error_details"] = error_details
    
    return response

@app.get("/shutdown")
async def shutdown():
    """Graceful shutdown endpoint"""
    print(f"[{API_NAME}] Received shutdown request")
    print(f"[{API_NAME}] Performing cleanup...")
    print(f"[{API_NAME}] Shutdown complete")
    os._exit(0)

if __name__ == "__main__":
    port = 8000
    if len(sys.argv) > 1:
        try:
            port = int(sys.argv[1])
        except ValueError:
            print(f"[{API_NAME}] Invalid port argument: {sys.argv[1]}, using default 8000")
    
    print(f"[{API_NAME}] Starting on port {port}...")
    print(f"[{API_NAME}] API_NAME: {API_NAME}")
    print(f"[{API_NAME}] Python: {sys.version}")
    print(f"[{API_NAME}] Executable: {sys.executable}")
    print(f"[{API_NAME}] Health check: http://127.0.0.1:{port}/health")
    print(f"[{API_NAME}] Test data: http://127.0.0.1:{port}/test")
    print(f"[{API_NAME}] Debug imports: http://127.0.0.1:{port}/debug/imports")
    print(f"[{API_NAME}] Debug routes: http://127.0.0.1:{port}/debug/routes")
    
    uvicorn.run(
        app,
        host="127.0.0.1",
        port=port,
        log_level="info"
    )