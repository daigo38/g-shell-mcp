# G-Shell MCP Server

G-Shell MCPは、Google Apps Script (GAS) を効率的に実行・管理するためのModel Context Protocol (MCP) サーバーです。

このツールを使用することで、Google SheetsやGoogle Forms、その他のGoogleサービスをGASを通じて操作することができます。LLM（例：Claude）と連携することで、自然言語での操作が可能になります。

## 機能

- GASプロジェクトの実行と管理
- Google Sheetsの編集・操作
- Google Formsの作成・管理
- その他のGoogleサービスとの連携

## インストール

### 前提条件

- Python 3.6+
- Anthropic Claude Desktop アプリ（またはCursor）
- UV（Pythonパッケージマネージャー）- インストール方法: `curl -LsSf https://astral.sh/uv/install.sh | sh`

### インストール手順

1. **リポジトリのクローン**

```bash
git clone https://github.com/yourusername/g-shell-mcp.git
cd g-shell-mcp
```

2. **pyproject.tomlの設定と依存関係のインストール**

pyproject.tomlを設定します：
```bash
uv venv
source .venv/bin/activate  # Unix/macOS
.venv\Scripts\activate     # Windows
uv pip install .
```

3. **MCPサーバーの設定**

以下のJSONを適切な{{PATH}}の値で設定してください：

```json
{
  "mcpServers": {
    "g-shell": {
      "command": "{{PATH_TO_UV}}", // `which uv` の出力を入力
      "args": [
        "--directory",
        "{{PATH_TO_SRC}}/g-shell-mcp", // リポジトリのパスを入力
        "run",
        "main.py"
      ]
    }
  }
}
```

**Claude**の場合、このファイルを以下の場所に`claude_desktop_config.json`として保存：
```
~/Library/Application Support/Claude/claude_desktop_config.json
```

**Cursor**の場合、このファイルを以下の場所に`mcp.json`として保存：
```
~/.cursor/mcp.json
```

## GAS実行環境の設定

1. Google Apps Scriptプロジェクトを新規作成します。

2. スクリプトプロパティの設定:
   - プロジェクトの設定画面を開きます（⚙️アイコン）
   - 「スクリプトプロパティ」タブを選択
   - 「プロパティを追加」をクリック
   - プロパティ名に`API_KEY`を入力
   - 値に任意のAPI keyを設定（セキュリティのため、複雑な文字列を使用することを推奨）
   - 「保存」をクリック

3. 以下のコードをプロジェクトに追加します：

<details>
<summary>GASコード（クリックで展開）</summary>

```javascript
function doPost(e) {
  // Get API key from script properties
  const scriptProperties = PropertiesService.getScriptProperties();
  const API_KEY = scriptProperties.getProperty('API_KEY');
  
  const spreadsheet = SpreadsheetApp.getActiveSpreadsheet();

  // Parse POST data as JSON
  const contents = JSON.parse(e.postData.contents);
  const apiKey = contents.apiKey;
  const data = contents.data;
  const code = data.code;
  const functionName = data.functionName;
  const args = data.args;
  const properties = data.properties || {};

  // Verify API key
  if (apiKey !== API_KEY) {
    return errorResponse('Invalid API Key');
  }

  if (!code) {
    return errorResponse('No code provided');
  }
  if (!functionName) {
    return errorResponse('No functionName provided');
  }
  if (!args) {
    return errorResponse('No args provided');
  }

  let status = 'success';
  let result;
  const logs = [];

  // Define custom version of console.log
  const customConsole = {
    log: function(message) {
      logs.push(String(message));
    }
  };

  // Define custom version of Logger.log
  const customLogger = {
    log: function(message) {
      logs.push(String(message));
    }
  };

  // Create custom PropertiesService object
  const customPropertiesService = {
    scriptProperties: {
      properties: properties, // Use properties received from request
      getProperty: function(key) {
        return this.properties[key] || null;  // Return null if key doesn't exist
      }
    },
    getScriptProperties: function() {
      return this.scriptProperties;
    }
  };

  try {
    // Create new function using Function constructor
    const func = new Function('console', 'Logger', 'PropertiesService', 'args', code + `
      ; return typeof ${functionName} === "function" ? ${functionName}(...args) : "Function ${functionName} is not defined";`);
    // Execute function and get result
    result = func(customConsole, customLogger, customPropertiesService, args);
  } catch (error) {
    status = 'error';
    result = 'Error: ' + error.toString();
    logs.push(result);
  }

  // Record execution results and logs to spreadsheet
  let logSheet = spreadsheet.getSheetByName('Logs');

  if (!logSheet) {
    // Create Logs sheet if it doesn't exist
    logSheet = spreadsheet.insertSheet('Logs');
    logSheet.appendRow(['Timestamp', 'Request Code', 'Function Name', 'Arguments', 'Execution Logs', 'Execution Result']);
  }

  // Get timestamp
  const timestamp = new Date();

  // Add execution logs and results as a row
  logSheet.appendRow([timestamp, code, functionName, JSON.stringify(args, null, 2), logs.join('\n'), result]);

  // Include execution results and logs in response
  const response = {
    status: status,
    result: result,
    logs: logs
  };
  return ContentService.createTextOutput(JSON.stringify(response))
                       .setMimeType(ContentService.MimeType.JSON);
}

function errorResponse(message) {
  return ContentService.createTextOutput(JSON.stringify({
    status: 'error',
    message: 'Eval GAS: ' + message
  })).setMimeType(ContentService.MimeType.JSON);
}
```

</details>

4. プロジェクトのマニフェストファイル（appsscript.json）を以下のように設定します：

<details>
<summary>appsscript.json（クリックで展開）</summary>

```json
{
  "timeZone": "Asia/Tokyo",
  "dependencies": {
    "enabledAdvancedServices": [
      {
        "userSymbol": "AdSense",
        "version": "v2",
        "serviceId": "adsense"
      },
      {
        "userSymbol": "BigQuery",
        "version": "v2",
        "serviceId": "bigquery"
      },
      {
        "userSymbol": "Drive",
        "version": "v2",
        "serviceId": "drive"
      },
      {
        "userSymbol": "DriveActivity",
        "version": "v2",
        "serviceId": "driveactivity"
      },
      {
        "userSymbol": "Gmail",
        "version": "v1",
        "serviceId": "gmail"
      },
      {
        "userSymbol": "Analytics",
        "version": "v3",
        "serviceId": "analytics"
      },
      {
        "userSymbol": "Calendar",
        "version": "v3",
        "serviceId": "calendar"
      },
      {
        "userSymbol": "Chat",
        "version": "v1",
        "serviceId": "chat"
      },
      {
        "userSymbol": "Docs",
        "version": "v1",
        "serviceId": "docs"
      },
      {
        "userSymbol": "Sheets",
        "version": "v4",
        "serviceId": "sheets"
      },
      {
        "userSymbol": "Slides",
        "version": "v1",
        "serviceId": "slides"
      },
      {
        "userSymbol": "Tasks",
        "version": "v1",
        "serviceId": "tasks"
      },
      {
        "userSymbol": "YouTubeAnalytics",
        "version": "v2",
        "serviceId": "youtubeAnalytics"
      },
      {
        "userSymbol": "YouTube",
        "version": "v3",
        "serviceId": "youtube"
      }
    ]
  },
  "exceptionLogging": "STACKDRIVER",
  "runtimeVersion": "V8",
  "webapp": {
    "executeAs": "USER_DEPLOYING",
    "access": "ANYONE_ANONYMOUS"
  },
  "oauthScopes": [
    "https://www.googleapis.com/auth/script.external_request",
    "https://www.googleapis.com/auth/script.scriptapp",
    "https://www.googleapis.com/auth/script.send_mail",
    "https://www.googleapis.com/auth/spreadsheets",
    "https://www.googleapis.com/auth/drive",
    "https://www.googleapis.com/auth/gmail.modify",
    "https://www.googleapis.com/auth/calendar",
    "https://www.googleapis.com/auth/documents",
    "https://www.googleapis.com/auth/forms",
    "https://www.googleapis.com/auth/presentations",
    "https://www.googleapis.com/auth/userinfo.email",
    "https://www.googleapis.com/auth/userinfo.profile",
    "https://www.googleapis.com/auth/chat.messages",
    "https://www.googleapis.com/auth/chat.spaces",
    "https://www.googleapis.com/auth/adsense.readonly",
    "https://www.googleapis.com/auth/bigquery",
    "https://www.googleapis.com/auth/analytics.readonly",
    "https://www.googleapis.com/auth/drive.activity.readonly",
    "https://www.googleapis.com/auth/tasks",
    "https://www.googleapis.com/auth/youtube",
    "https://www.googleapis.com/auth/yt-analytics.readonly"
  ]
}
```

5. Webアプリとしてデプロイ:
   - 「デプロイ」ボタンをクリック
   - 「新しいデプロイ」を選択
   - 「種類の選択」で「Webアプリ」を選択
   - 以下の設定を行います：
     - 「次のユーザーとして実行」→ 自分
     - 「アクセスできるユーザー」→ 全員
   - 「デプロイ」をクリック
   - 認証を求められた場合は許可
   - デプロイ後に表示される「Webアプリ URL」をコピー

6. 環境変数の設定:
   - `.env.example`をコピーして`.env`ファイルを作成:
     ```bash
     cp .env.example .env
     ```
   - `.env`ファイルを編集し、以下の値を設定:
     ```bash
     # GAS設定
     GAS_API_KEY=手順2で設定したAPI key
     GAS_URL=手順5でコピーしたWebアプリ URL
     ```


</details>

## 使用方法

G-Shell MCPサーバーは以下のツールを提供します：

- **execute_gas**: GASスクリプトを実行


## ライセンス

MITライセンスの下で公開されています。詳細は[LICENSE](LICENSE)ファイルを参照してください。
