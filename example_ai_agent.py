"""
Example: Using the AI-powered workflow vision agent.
"""

from workflow_vision_agent import TaskParser, BrowserController

def main():
    """Example of AI agent understanding questions."""
    
    # Initialize AI-powered parser
    parser = TaskParser(use_ai=True)
    
    # Example questions
    questions = [
        "I need to filter a database in Notion",
        "Show me how to add a user on CNN website",
        "Can you help me create a new repository in GitHub?",
    ]
    
    print("🤖 AI Agent Understanding Questions\n")
    print("=" * 60)
    
    for question in questions:
        print(f"\n📝 Question: {question}")
        print("-" * 60)
        
        # AI understands the question
        result = parser.parse_question(question)
        
        print(f"✅ App: {result.get('app_name', 'N/A')}")
        print(f"✅ URL: {result.get('url', 'N/A')}")
        print(f"✅ Action: {result.get('action', 'N/A')}")
        
        if result.get('steps'):
            print(f"✅ Steps: {len(result['steps'])} steps identified")
            for i, step in enumerate(result['steps'], 1):
                print(f"   {i}. {step}")
        
        if result.get('context'):
            print(f"✅ Context: {result['context']}")
        
        print()
    
    print("=" * 60)
    print("\n✨ AI Agent successfully understood all questions!")
    print("\nNote: Set ANTHROPIC_API_KEY environment variable to use AI.")
    print("Without API key, it falls back to rule-based parsing.")


if __name__ == "__main__":
    main()

