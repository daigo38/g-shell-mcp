from mcp.server.fastmcp import FastMCP
import subprocess
import json
import requests
import os
from typing import Optional, List, Dict, Any
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

mcp = FastMCP("g-shell")

@mcp.tool()
async def execute_gas_code(
    code: str,
    function_name: str,
    args: List[Any] = None,
    properties: Dict[str, Any] = None
) -> Dict[str, Any]:
    """
    Execute Google Apps Script (GAS) code in a secure virtual environment.
    
    Args:
        code: GAS code to execute
        function_name: Name of the function to execute
        args: List of arguments to pass to the function (optional)
        properties: Script properties (optional)
        
    Returns:
        Dict[str, Any]: GAS execution result
    """
    try:
        # Get settings from environment variables
        gas_url = os.getenv('GAS_URL')
        gas_api_key = os.getenv('GAS_API_KEY')
        
        if not gas_url:
            return {"error": "GAS_URL is not set"}
        
        # Prepare request data
        request_data = {
            "apiKey": gas_api_key,
            "data": {
                "code": code,
                "functionName": function_name,
                "args": args or [],
                "properties": properties or {}
            }
        }
        
        # Send request to GAS
        response = requests.post(gas_url, json=request_data)
        response.raise_for_status()
        
        return response.json()
        
    except requests.exceptions.RequestException as e:
        return {
            "error": f"HTTP request error: {str(e)}"
        }
    except Exception as e:
        return {
            "error": f"Execution error: {str(e)}"
        }

if __name__ == "__main__":
    mcp.run(transport='stdio')
