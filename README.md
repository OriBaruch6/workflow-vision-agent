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
6. **Return the Workflow** - Provide Agent A with a sequence of screenshots showing the complete process 

## Architecture

### Components

1. **AI Task Parser** - Uses LLM to understand questions and extract information
2. **Browser Controller** - Manages browser instance and navigation
3. **Element Finder** - Finds UI elements on the page (buttons, forms, etc.)
4. **Action Executor** - Performs actions (clicks, form filling, etc.)
5. **State Detector** - Detects when the UI has changed significantly
6. **Screenshot Manager** - Organizes and stores screenshots
7. **Workflow Orchestrator** - Coordinates all components to complete the task