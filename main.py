from mcp.server.fastmcp import FastMCP
import subprocess
import json
import requests
import os
from typing import Optional, List, Dict, Any
from dotenv import load_dotenv

# 環境変数の読み込み
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
    Google Apps Script (GAS)のWebアプリにコードを送信して実行します。
    
    Args:
        code: 実行するGASコード
        function_name: 実行する関数名
        args: 関数に渡す引数のリスト（オプション）
        properties: スクリプトプロパティ（オプション）
        
    Returns:
        Dict[str, Any]: GASの実行結果
    """
    try:
        # 環境変数から設定を取得
        gas_url = os.getenv('GAS_URL')
        gas_api_key = os.getenv('GAS_API_KEY')
        
        if not gas_url:
            return {"error": "GAS_URLが設定されていません"}
        
        # リクエストデータの準備
        request_data = {
            "apiKey": gas_api_key,
            "data": {
                "code": code,
                "functionName": function_name,
                "args": args or [],
                "properties": properties or {}
            }
        }
        
        # GASにリクエスト送信
        response = requests.post(gas_url, json=request_data)
        response.raise_for_status()
        
        return response.json()
        
    except requests.exceptions.RequestException as e:
        return {
            "error": f"HTTPリクエストエラー: {str(e)}"
        }
    except Exception as e:
        return {
            "error": f"実行エラー: {str(e)}"
        }

if __name__ == "__main__":
    mcp.run(transport='stdio')
