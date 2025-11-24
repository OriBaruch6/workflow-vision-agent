# workflow-vision-agent

An **AI-powered agent** that automatically navigates web applications and captures screenshots to demonstrate how to complete tasks in real-time.

## 🤖 AI-Powered Understanding

This agent uses **Large Language Models (LLMs)** to understand questions naturally, without requiring specific formats. It can:

- **Understand any question format** - "How do I create a project in Linear?", "I need to filter a database on Notion", etc.
- **Extract URLs intelligently** - Finds URLs in markdown links, plain text, or infers from app names
- **Understand actions** - Breaks down complex tasks into steps automatically
- **Work with context** - Understands what you want to do, not just keywords

### High-Level Flow

• Agent A sends a question to Agent B (this system) asking how to perform a task in a web application
• **AI understands the question** - Extracts app name, URL, action, and breaks it into steps
• Agent B opens a browser and navigates to the application
• Once on the page, Agent B finds the relevant UI elements like buttons or form fields
• Agent B performs the necessary actions such as clicking or filling forms
• Agent B detects when the UI state changes significantly
• Agent B captures screenshots at each important moment
• Finally, Agent B returns to Agent A with a complete sequence of screenshots, step descriptions, and UI state information

### Core Strategy

1. **AI Understands the Question** - LLM extracts app, action, URL, and breaks down into steps
2. **Navigate to the App** - Open the browser and go to the starting URL
3. **Find UI Elements** - Locate buttons, forms, and interactive elements
4. **Execute Step by Step** - Perform each action and wait for UI changes
5. **Capture States** - Take screenshots whenever the UI changes significantly
6. **Return the Workflow** - Provide Agent A with a complete sequence of screenshots

## Setup

### Prerequisites

- Python 3.9 or higher
- Anthropic API key - Get one at https://console.anthropic.com/

### Installation

1. Create virtual environment:
```bash
python3 -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate
```

2. Install dependencies:
```bash
pip install -r requirements.txt
playwright install chromium
```

3. Set your API key:
```bash
export ANTHROPIC_API_KEY="your-api-key-here"
```

4. Install package:
```bash
pip install -e .
```

## Usage

### Basic Example

```python
from workflow_vision_agent import TaskParser, BrowserController

# AI understands any question format
parser = TaskParser(use_ai=True)
result = parser.parse_question("How do I create a project in Linear?")

print(f"App: {result['app_name']}")
print(f"URL: {result['url']}")
print(f"Action: {result['action']}")
print(f"Steps: {result['steps']}")

# Navigate and capture
controller = BrowserController()
controller.start_browser()
controller.go_to_url(result['url'])
controller.take_screenshot("initial_page")
controller.close_browser()
```

### Without AI (Fallback Mode)

If no API key is set, the system falls back to rule-based parsing:

```python
parser = TaskParser(use_ai=False)  # Uses regex-based parsing
```

## Architecture

### Components

1. **AI Task Parser** - Uses LLM to understand questions and extract information
2. **Browser Controller** - Manages browser instance and navigation
3. **Element Finder** - Finds UI elements on the page (buttons, forms, etc.)
4. **Action Executor** - Performs actions (clicks, form filling, etc.) - *Coming soon*
5. **State Detector** - Detects when the UI has changed significantly - *Coming soon*
6. **Screenshot Manager** - Organizes and stores screenshots - *Coming soon*
7. **Workflow Orchestrator** - Coordinates all components - *Coming soon*

## Project Structure

```
workflow-vision-agent/
├── workflow_vision_agent/
│   ├── ai/                    # AI/LLM integration
│   │   ├── __init__.py
│   │   └── llm_client.py     # LLM client for understanding
│   ├── browser/               # Browser automation
│   │   ├── __init__.py
│   │   └── controller.py
│   ├── parser/               # Task parsing
│   │   ├── __init__.py
│   │   └── task_parser.py    # AI-powered parser
│   ├── elements/             # Element finding
│   │   ├── __init__.py
│   │   └── finder.py
│   ├── tests/                # Tests
│   └── __init__.py
├── requirements.txt
├── pyproject.toml
└── README.md
```

## How AI Works

The AI agent uses LLMs to:

1. **Understand Questions**: Parses natural language questions to extract:
   - App name (Linear, Notion, GitHub, etc.)
   - URL (from markdown, plain text, or inferred)
   - Action (what the user wants to do)
   - Steps (breaks down complex actions)

2. **Example AI Understanding**:
   - Input: "I want to create a new project with dependencies in Linear"
   - AI Output:
     ```json
     {
       "app_name": "linear",
       "url": "https://linear.app",
       "action": "create project with dependencies",
       "steps": [
         "Find and click create project button",
         "Fill project name and details",
         "Add dependencies",
         "Submit form"
       ]
     }
     ```

## Configuration

### Model Selection

```python
from workflow_vision_agent.ai import LLMClient

# Default model (Claude 3.5 Sonnet)
client = LLMClient()

# Use different Claude model
client = LLMClient(model="claude-3-opus-20240229")  # More capable
client = LLMClient(model="claude-3-haiku-20240307")  # Faster/cheaper
```

## Next Steps

- [ ] Add Action Executor
- [ ] Add State Detector with Vision AI
- [ ] Add Workflow Orchestrator
- [ ] Add Vision AI for element finding
- [ ] Add error recovery with AI

See `AI_INTEGRATION.md` for detailed AI integration strategy.
