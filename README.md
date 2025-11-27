# AI Web Agent System

An intelligent AI agent that automatically navigates web applications, understands what you want to do, and captures every step of the process with screenshots. Think of it as a smart assistant that can watch and learn how to use any website, then show you exactly how to do it.

## What We Do

Have you ever wanted to know "How do I create a project in Linear?" or "How can I subscribe to CNN?" but didn't want to click through the website yourself? Our AI agent does that for you. It:

- **Understands your question** - You ask in plain English what you want to accomplish
- **Navigates the website** - It opens the browser and goes to the right place
- **Makes smart decisions** - Uses AI vision to see the page and decide what to click or type
- **Captures everything** - Takes screenshots at each important step so you can see exactly what happened
- **Tells you when it's done** - Knows when your task is complete and what you got

## Our Mission

To make web automation accessible to everyone. Instead of writing complex scripts for each website, you just describe what you want in natural language, and our AI agent figures out how to do it. It works across different websites without needing special code for each one - it's truly generalizable.

## How We Do It

We combine several powerful technologies:

- **Playwright** - Controls a real browser (like Chrome) to interact with websites
- **Claude AI (Anthropic)** - Uses advanced vision capabilities to "see" screenshots and understand what's on the page
- **FastAPI** - Provides a clean API so other systems can use our agent
- **Pydantic** - Ensures all data is validated and type-safe

The magic happens when Claude looks at a screenshot, sees all the buttons and forms, and decides "I should click the Subscribe button" or "I need to type an email here" - just like a human would, but programmatically.

## The Flow: Step by Step

Here's exactly what happens when you ask our agent to do something:

1. **You ask a question** 
   - Example: "How can I log in to my Disney Plus account?"
   - The system receives this as a task description

2. **We understand your intent**
   - The AI analyzes your question to figure out:
     - Which website/app you're talking about (Disney Plus)
     - What you want to do (log in)
     - The base URL to start from

3. **We open the browser**
   - Playwright launches a browser and navigates to the website
   - We wait for the page to load completely

4. **We capture the initial state**
   - Take a full-page screenshot (saved as JPEG, compressed to save space)
   - Capture the DOM structure (all buttons, forms, links)
   - Save this as the first state in our dataset

5. **The AI decision loop begins**
   - **Extract elements**: Find all clickable buttons, links, and form fields on the page
   - **Ask Claude**: Send the screenshot + list of elements to Claude with your task
   - **Get decision**: Claude responds with:
     - What action to take (click, type, wait, scroll, or done)
     - Which element to interact with (CSS selector)
     - Whether the task is complete
     - Whether you got what you wanted
   - **Execute action**: Use Playwright to click the button or type the text
   - **Check for new state**: Did something change? (new page, modal appeared, form showed up)
   - **Capture if needed**: If it's a new state, take another screenshot
   - **Repeat**: Go back to step 5 until task is complete or max iterations reached

6. **We save everything**
   - All screenshots are organized in a dataset folder
   - Each state has metadata describing what happened
   - You get a complete visual walkthrough of the process

7. **We tell you the result**
   - Success or failure
   - How many states were captured
   - Where to find the screenshots

## Dataset File Naming

When we capture a workflow, we create a folder with a descriptive name and timestamp. Here's how files are organized:

### Folder Structure

```
datasets/
└── disneyplus_how_can_i_log_in_to_my_disney_plus_account__20251124_203227/
    ├── metadata.json                    # Complete workflow information
    ├── 001_state_20251124_203227.jpg    # First screenshot (initial page)
    ├── 001_dom_20251124_203227.json     # DOM snapshot of first state
    ├── 002_state_20251124_203315.jpg    # Second screenshot (after clicking login)
    ├── 002_dom_20251124_203315.json     # DOM snapshot of second state
    ├── 003_state_20251124_203353.jpg    # Third screenshot (login form appeared)
    └── 003_dom_20251124_203353.json     # DOM snapshot of third state
```

### File Naming Convention

- **Folder name**: `{app}_{task_description_sanitized}_{timestamp}`
  - Example: `disneyplus_how_can_i_log_in_to_my_disney_plus_account__20251124_203227`
  - The task description is converted to lowercase, spaces become underscores, special characters removed
  - Timestamp format: `YYYYMMDD_HHMMSS`

- **Screenshot files**: `{step_number:03d}_state_{timestamp}.jpg`
  - Example: `001_state_20251124_203227.jpg`, `002_state_20251124_203315.jpg`
  - Always saved as JPEG (compressed, typically 0.2-1.5 MB)
  - Numbered sequentially so you can see the order of steps
  - Timestamp shows exactly when each state was captured

- **DOM snapshot files**: `{step_number:03d}_dom_{timestamp}.json`
  - Example: `001_dom_20251124_203227.json`
  - Contains structured data about the page: all buttons, forms, links, their text, selectors
  - Useful for understanding what elements were available at each step

- **Metadata file**: `metadata.json`
  - Contains the complete workflow information:
    - Original task description
    - App name
    - Success status
    - Total number of states captured
    - List of all states with their actions
    - Duration of execution
    - Any error messages

### Example Dataset

For the question "How can I log in to my Disney Plus account?", you might get:

```
datasets/disneyplus_how_can_i_log_in_to_my_disney_plus_account__20251124_203227/
├── metadata.json
├── 001_state_20251124_203227.jpg    # Disney Plus homepage
├── 001_dom_20251124_203227.json
├── 002_state_20251124_203315.jpg    # After clicking "LOG IN" button
├── 002_dom_20251124_203315.json
├── 003_state_20251124_203353.jpg    # Login form appeared
├── 003_dom_20251124_203353.json
├── 004_state_20251124_203400.jpg    # Email field filled
├── 004_dom_20251124_203400.json
└── 005_state_20251124_203410.jpg    # Password field filled
```

Each screenshot shows a different stage of the login process, and the metadata tells you what action was taken to get from one state to the next.

## Installation

1. **Install Python dependencies:**
```bash
pip install -r requirements.txt
playwright install chromium
```

2. **Set up your Anthropic API key:**
```bash
export ANTHROPIC_API_KEY="your-api-key-here"
```

## Usage

### Command Line (CLI)

The simplest way to use the agent:

```bash
python main.py cli --app disneyplus --task "How can I log in to my Disney Plus account?"
```

Options:
- `--app`: Application name (disneyplus, cnn, linear, notion, etc.)
- `--task`: Your question in plain English
- `--url`: Base URL (optional, will use default from config if not provided)
- `--headless`: Run browser in background (no visible window)

### API Server

Start the FastAPI server to use it programmatically:

```bash
python main.py server --port 8000
```

Then make requests:

```bash
# Execute a workflow
curl -X POST "http://localhost:8000/api/execute" \
  -H "Content-Type: application/json" \
  -d '{
    "app": "cnn",
    "task_description": "How can I subscribe to CNN and what subscription plans are available?"
  }'

# List all captured workflows
curl "http://localhost:8000/api/workflows"

# Get details of a specific workflow
curl "http://localhost:8000/api/workflows/cnn_how_can_i_subscribe_to_cnn"
```

### Python Code

Use it directly in your Python code:

```python
from src.models.schemas import TaskInput
from src.agent import WorkflowExecutor

task = TaskInput(
    app="disneyplus",
    task_description="How can I log in to my Disney Plus account?"
)

executor = WorkflowExecutor(headless=False)
result = executor.execute(task)

print(f"Success: {result.success}")
print(f"States captured: {result.total_states}")
print(f"Duration: {result.duration_seconds:.2f}s")
```

## How State Detection Works

The system is smart about knowing when something important happened. It detects new states by watching for:

- **URL changes** - Navigated to a new page
- **Modal appearances** - A popup or dialog appeared (like a login form)
- **DOM structure changes** - The page layout changed significantly
- **Form visibility** - A form appeared or became visible
- **Success/error messages** - Confirmation messages or error alerts
- **Network activity** - Page finished loading all resources

When any of these happen, we capture a new screenshot so you can see the progression.

## Configuration

Edit `apps.yaml` to add new websites or configure existing ones:

```yaml
apps:
  disneyplus:
    base_url: "https://www.disneyplus.com"
    auth_required: false
  
  cnn:
    base_url: "https://www.cnn.com"
    auth_required: false
```

The configuration is lightweight - we don't hardcode workflows because the AI figures it out from the visual state.

## Error Handling

The system is robust and handles common issues:

- **Element not found**: Tries alternative selectors or asks AI for help
- **Overlay blocking click**: Falls back to JavaScript click to bypass overlays
- **Low AI confidence**: Logs warning but continues (you can see it in the reasoning)
- **Timeouts**: Uses lenient wait strategies (some sites are slow)
- **API errors**: Returns clear error messages in the metadata
- **Max iterations**: Prevents infinite loops (default: 50 iterations)

## Technical Requirements

- Python 3.11+
- Playwright (browser automation)
- Anthropic API key (for Claude AI)
- FastAPI (for API server mode)
- Pydantic (data validation)
- Pillow (image processing)

## License

MIT
