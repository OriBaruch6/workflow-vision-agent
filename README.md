# workflow-vision-agent

An AI agent that automatically navigates web applications and captures screenshots to demonstrate how to complete tasks in real-time.

### High-Level Flow

• Agent A sends a question to Agent B (this system) asking how to perform a task in a web application
• Agent B parses the question to extract the app name, the action to perform, and the starting URL
• Agent B opens a browser and navigates to the application
• Once on the page, Agent B breaks down the requested action into individual steps
• For each step, Agent B finds the relevant UI elements like buttons or form fields
• Agent B performs the necessary actions such as clicking or filling forms
• Agent B detects when the UI state changes significantly
• Agent B captures screenshots at each important moment
• Finally, Agent B returns to Agent A with a complete sequence of screenshots, step descriptions, and UI state information

### Core Strategy

1. **Parse the Question** - Extract what app, what action, and what URL we're working with
2. **Navigate to the App** - Open the browser and go to the starting URL
3. **Understand the Task** - Break down the action into steps
4. **Execute Step by Step** - Perform each action and wait for UI changes
5. **Capture States** - Take screenshots whenever the UI changes significantly
6. **Return the Workflow** - Provide Agent A with a sequence of screenshots showing the complete process 

## Architecture

### Components

1. **Task Parser** - Extracts app name, action, and URL from questions
2. **Browser Controller** - Manages browser instance and navigation
3. **Element Finder** - Finds UI elements on the page (buttons, forms, etc.)
4. **Action Executor** - Performs actions (clicks, form filling, etc.)
5. **State Detector** - Detects when the UI has changed significantly
6. **Screenshot Manager** - Organizes and stores screenshots
7. **Workflow Orchestrator** - Coordinates all components to complete the task