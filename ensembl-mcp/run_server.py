#!/usr/bin/env python3
import uvicorn
import os
import sys

# Add the project root to Python path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

if __name__ == "__main__":
    print("Starting Ensembl MCP server...")
    print("==============================")
    print("Server will be available at: http://localhost:8000")
    print("Press CTRL+C to stop the server")
    
    # Run the FastAPI app
    uvicorn.run("ensembl_mcp_server.server:app", host="0.0.0.0", port=8000, reload=True)