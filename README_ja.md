# G-Shell MCP サーバー

G-Shell MCPは、Google Apps Script (GAS) を効率的に実行・管理するためのModel Context Protocol (MCP) サーバーです。

このツールを使用することで、Google SheetsやGoogle Forms、その他のGoogleサービスをGASを通じて操作することができます。LLM（例：Claude）と連携することで、自然言語での操作が可能になります。

> 🌟 **すぐに試してみる！**
>
> G-ShellはGASSISTANTというAI搭載のGASエディタに搭載された機能です。
> すぐ試したい場合、[GASSISTANT](https://www.gassistant.app)でお試しください！

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

### セットアップ手順

1. **リポジトリのクローン**

```bash
git clone https://github.com/daigo38/g-shell-mcp.git
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

   > ⚠️ **重要なセキュリティ警告**
   >
   > APIキーとWebアプリのURLは絶対に公開しないでください。
   > これらの認証情報が漏洩すると、GASスクリプトが実行可能な全ての操作が攻撃者によって実行される可能性があります。
   > 例えば以下のような破壊的な操作が可能になります：
   > - Google Drive内の全ファイルの削除
   > - 全てのGoogle Sheetsへのアクセスと改変
   > - あなたのアカウントを通じたメール送信
   > 
   > これらの認証情報は常に最高レベルのセキュリティで管理してください。

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
{{ ... }}
```

</details>

4. プロジェクトのマニフェストファイル（appsscript.json）を以下のように設定します：

<details>
<summary>appsscript.json（クリックで展開）</summary>

```json
{
  "timeZone": "Asia/Tokyo",
  "dependencies": {
{{ ... }}
```

</details>

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

## 使用方法

G-Shell MCPサーバーは以下のツールを提供します：
- **execute_gas**: GASスクリプトを実行

## ライセンス

MITライセンスの下で公開されています。詳細は[LICENSE](LICENSE)ファイルを参照してください。

---
[English version](README.md)
