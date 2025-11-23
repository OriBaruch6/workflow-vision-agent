"""
Tests for task parser.
"""

from workflow_vision_agent.parser import TaskParser


def test_task_parser():
    """Test the task parser."""
    parser = TaskParser()
    
    # Test 1: Parse question with markdown link
    result = parser.parse_question("How do I create a project in [Linear](https://linear.app/test916/team/TES/active)?")
    assert result["app_name"] == "linear", "Should extract app name"
    assert result["url"] == "https://linear.app/test916/team/TES/active", "Should extract URL"
    assert result["action"] is not None, "Should extract action"
    assert parser.is_valid_task(result), "Task should be valid"
    
    # Test 2: Parse question with plain URL
    result = parser.parse_question("I want to create user on CNN website https://cnn.com")
    assert result["url"] == "https://cnn.com", "Should extract plain URL"
    assert result["app_name"] == "cnn", "Should extract app name from URL"
    
    # Test 3: Invalid task (no URL)
    result = parser.parse_question("How do I do something?")
    assert not parser.is_valid_task(result), "Task without URL should be invalid"
    
    print("✓ Task parser tests passed")


if __name__ == "__main__":
    test_task_parser()

