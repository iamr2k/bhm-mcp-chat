# BharatMatrimony MCP Search

An [MCP (Model Context Protocol)](https://modelcontextprotocol.io/) server that lets you search BharatMatrimony profiles directly from **VS Code GitHub Copilot Chat**. Built with [FastMCP](https://github.com/jlowin/fastmcp).

Ask Copilot things like:
- *"Find girls aged 25-30 in Kerala"*
- *"Search for engineers from Nair caste in Thiruvananthapuram"*
- *"Show me profiles with Ph.D education who are never married"*

The LLM understands all the search filters and translates your natural language queries into structured API calls.

---

## Features

| Tool | Description |
|------|-------------|
| `configure_auth` | Set your bearer token and session ID (credentials stored locally in `.env`) |
| `get_auth_status` | Check if auth is configured without revealing secrets |
| `search_profiles` | Search profiles with 20+ filters — age, height, religion, caste, education, stars (nakshatra), state, occupation, and more |

### Search Filters

The `search_profiles` tool exposes all major BharatMatrimony search parameters with rich descriptions so the LLM can use them intelligently:

| Parameter | Example Values |
|-----------|---------------|
| `age_min` / `age_max` | `22`, `35` |
| `height_min` / `height_max` | `FT4_IN7_139CM`, `FT5_IN9_175CM`, `FT6_IN0_182CM` |
| `religion` | `HINDU`, `MUSLIM`, `CHRISTIAN`, `SIKH`, `JAIN`, `ANY` |
| `mother_tongue` | `MALAYALAM`, `TAMIL`, `KANNADA`, `TELUGU`, `HINDI`, etc. |
| `marital_status` | `NEVER_MARRIED`, `DIVORCED`, `WIDOWED` |
| `states` | `KERALA`, `KARNATAKA`, `TAMIL_NADU`, `MAHARASHTRA`, etc. |
| `education_category` | `BACHELORS_ENGINEERING`, `MASTERS_MEDICINE_GENERAL`, `DOCTORATES`, etc. |
| `stars` (nakshatra) | `ROHINI`, `ASHWINI`, `REVATHI`, `SHRAVAN_THIRUVONAM`, etc. (all 27) |
| `caste` | `ANY`, `NAIR`, `EZHAVA`, `NAMBOOTHIRI`, `PILLAI`, etc. |
| `drinking` / `smoking` | `NEVER`, `OCCASIONALLY`, `NOT_SPECIFIED`, `ANY` |
| `eating` | `VEGETARIAN`, `NON_VEGETARIAN`, `EGGETARIAN`, `ANY` |
| `physical_status` | `NORMAL`, `PHYSICALLY_CHALLENGED`, `ANY` |
| `page` / `results_per_page` | Pagination support (default 20 per page) |

---

## Prerequisites

- Python 3.10+
- A BharatMatrimony account (to obtain API credentials)
- VS Code with GitHub Copilot Chat

---

## Installation

### Option 1: Clone from GitHub

```bash
git clone https://github.com/yourname/bhm-mcp-chat.git
cd bhm-mcp-chat
python -m venv .venv
source .venv/bin/activate   # Linux/Mac
# .venv\Scripts\activate    # Windows
pip install -r requirements.txt
```

### Option 2: Install via pip

```bash
pip install bhm-mcp-chat
```

### Option 3: Run directly with uvx (no install needed)

```bash
uvx bhm-mcp-chat
```

---

## VS Code Configuration

Add the MCP server to your project's `.vscode/mcp.json`:

### If cloned from GitHub

```json
{
  "servers": {
    "bhm-search": {
      "command": "${workspaceFolder}/.venv/bin/python",
      "args": ["server.py"],
      "cwd": "${workspaceFolder}"
    }
  }
}
```

### If installed via pip

```json
{
  "servers": {
    "bhm-search": {
      "command": "bhm-mcp",
      "args": []
    }
  }
}
```

### If using uvx

```json
{
  "servers": {
    "bhm-search": {
      "command": "uvx",
      "args": ["bhm-mcp-chat"]
    }
  }
}
```

After adding the config, restart VS Code or reload the window. The MCP server will appear in Copilot's tool list.

---

## Getting Your Credentials

The tool needs your BharatMatrimony session credentials. Here's how to get them:

1. **Log in** to [bharatmatrimony.com](https://bharatmatrimony.com) in your browser
2. Open **DevTools** (press `F12`) → go to the **Network** tab
3. Perform any **profile search** on the website
4. Find the GraphQL request to `g.bharatmatrimony.com` in the network log
5. From the **Request Headers**, copy these values:

| Header | What it is |
|--------|-----------|
| `bearer` | Your JWT authentication token (long string starting with `eyJ...`) |
| `sessionId` | Your session ID (e.g. `01KMD5TWE3...`) |
| `src` | Your encrypted user ID (optional, for `enc_id`) |

> **Note:** These tokens expire periodically. You'll need to update them when they expire.

---

## Usage

### First-time setup (in Copilot Chat)

Just tell Copilot your credentials:

> *"Configure my BharatMatrimony auth. Bearer token is eyJ... and session ID is 01KMD..."*

Copilot will call the `configure_auth` tool, which saves credentials locally to `.env` (never committed to git).

### Searching profiles

Ask naturally:

> *"Find girls aged 25-30 in Kerala who are engineers"*

> *"Search for Nair profiles in Thiruvananthapuram with masters degree"*

> *"Show me never-married Hindu profiles from Kerala, page 2"*

> *"Find profiles with compatible nakshatras — Rohini, Revathi, or Thiruvonam"*

Copilot translates your query into the right API parameters and returns formatted results with name, age, education, occupation, income, location, caste, and verification status.

### Example output

```
Total: 4,292 matches

1. Aiswarya Nair — 27, 5'3", Ph.D, Professor (₹30L), Thiruvananthapuram, Nair ✅
2. Anju Anand — 28, 5'4", M.Tech, Civil Engineer (₹5L), Kollam, Nair ✅
3. Varsha S — 27, 5'4", B.Tech, Software Professional, Thiruvananthapuram, Ezhava ✅
...
```

---

## Manual setup (alternative to Copilot)

You can also configure credentials by copying the example env file:

```bash
cp .env.example .env
```

Then edit `.env` with your values:

```env
BHM_USER_ID=E9819315
BHM_ENC_ID=your_enc_id_here
BHM_BEARER_TOKEN=your_bearer_token_here
BHM_SESSION_ID=your_session_id_here
```

---

## Project Structure

```
bhm-mcp-chat/
├── server.py          # MCP server with 3 tools (configure_auth, get_auth_status, search_profiles)
├── pyproject.toml     # Package config for pip install / PyPI distribution
├── requirements.txt   # Python dependencies
├── .vscode/
│   └── mcp.json       # VS Code MCP server configuration
├── .env.example       # Template for credentials
├── .env               # Your actual credentials (git-ignored)
└── .gitignore
```

---

## How It Works

```
┌──────────────────┐     stdio/JSON-RPC      ┌─────────────────┐     HTTPS/GraphQL     ┌─────────────────────┐
│  VS Code Copilot │ ◄──────────────────────► │  FastMCP Server │ ──────────────────►   │ BharatMatrimony API │
│  (Chat Agent)    │    MCP Protocol          │  (server.py)    │                       │ g.bharatmatrimony.com│
└──────────────────┘                          └─────────────────┘                       └─────────────────────┘
                                                     │
                                                     ▼
                                                  .env file
                                              (auth credentials)
```

1. Copilot discovers the MCP tools via `.vscode/mcp.json`
2. User asks a natural language question
3. Copilot selects the right tool and fills in parameters
4. The server calls BharatMatrimony's GraphQL API
5. Results are returned as structured JSON for Copilot to present

---

## Distribution

| Method | Command | Best For |
|--------|---------|----------|
| **GitHub** | `git clone` + `pip install -r requirements.txt` | Developers, private sharing |
| **PyPI** | `pip install bhm-mcp-chat` | Public distribution |
| **uvx** | `uvx bhm-mcp-chat` (zero-install) | Easiest for end users |

To publish to PyPI:

```bash
pip install build twine
python -m build
twine upload dist/*
```

---

## Security Notes

- Credentials are stored **locally** in `.env` and **never committed** to git (`.gitignore` includes `.env`)
- The `get_auth_status` tool only reports whether credentials are set — it **never exposes** token values
- Tokens expire periodically and must be refreshed from the browser

---

## License

MIT
