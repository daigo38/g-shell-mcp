# G-Shell MCP Server

G-Shell MCP is a Model Context Protocol (MCP) server for efficiently executing and managing Google Apps Script (GAS). 

This tool allows you to interact with Google Sheets, Google Forms, and other Google services through GAS. When integrated with LLMs (e.g., Claude), it enables natural language operations.

> **Try it Now!**
>
> G-Shell is a feature integrated into GASSISTANT, an AI-powered GAS editor.
> Want to try it immediately? Visit [GASSISTANT](https://www.gassistant.app)!

## Features

- Execute and manage GAS projects
- Edit and manipulate Google Sheets
- Create and manage Google Forms
- Integrate with other Google services

## Installation

### Prerequisites

- Python 3.6+
- Anthropic Claude Desktop app (or Cursor)
- UV (Python package manager) - Install with: `curl -LsSf https://astral.sh/uv/install.sh | sh`

### Setup Steps

1. **Clone the Repository**

```bash
git clone https://github.com/daigo38/g-shell-mcp.git
cd g-shell-mcp
```

2. **Configure pyproject.toml and Install Dependencies**

Set up pyproject.toml:
```bash
uv venv
source .venv/bin/activate  # Unix/macOS
.venv\Scripts\activate     # Windows
uv pip install .
```

3. **Configure MCP Server**

Configure the following JSON with appropriate {{PATH}} values:

```json
{
  "mcpServers": {
    "g-shell": {
      "command": "{{PATH_TO_UV}}", // Output of `which uv`
      "args": [
        "--directory",
        "{{PATH_TO_SRC}}/g-shell-mcp", // Path to repository
        "run",
        "main.py"
      ]
    }
  }
}
```

For **Claude**, save as `claude_desktop_config.json` at:
```
~/Library/Application Support/Claude/claude_desktop_config.json
```

For **Cursor**, save as `mcp.json` at:
```
~/.cursor/mcp.json
```

## GAS Environment Setup

1. Create a new Google Apps Script project.

2. Set up Script Properties:
   - Open project settings (⚙️ icon)
   - Select "Script Properties" tab
   - Click "Add Property"
   - Enter `API_KEY` as property name
   - Set a value for API key (recommend using a complex string for security)
   - Click "Save"

   > **CRITICAL SECURITY WARNING**
   >
   > NEVER share or expose your API key and Web App URL.
   > If these credentials are leaked, attackers can perform ANY action that your GAS script is capable of,
   > including potentially destructive operations like:
   > - Deleting all files in your Google Drive
   > - Accessing and modifying all your Google Sheets
   > - Sending emails through your account
   > 
   > Always treat these credentials with the highest level of security.

3. Add the following code to your project:

<details>
<summary>GAS Code (Click to expand)</summary>

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

4. Configure the manifest file (appsscript.json):

<details>
<summary>appsscript.json (Click to expand)</summary>

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

</details>

5. Deploy as Web App:
   - Click "Deploy" button
   - Select "New deployment"
   - Choose "Web app" as type
   - Configure settings:
     - "Execute as" → yourself
     - "Who has access" → anyone
   - Click "Deploy"
   - Authorize if prompted
   - Copy the "Web app URL" shown after deployment

6. Set Environment Variables:
   - Create `.env` file by copying `.env.example`:
     ```bash
     cp .env.example .env
     ```
   - Edit `.env` file with these values:
     ```bash
     # GAS Settings
     GAS_API_KEY=API key from step 2
     GAS_URL=Web app URL from step 5
     ```

## Usage

G-Shell MCP server provides the following tools:
- **execute_gas**: Execute GAS scripts

## License

Released under the MIT License. See [LICENSE](LICENSE) file for details.
