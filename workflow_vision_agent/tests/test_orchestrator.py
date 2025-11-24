"""
Tests for workflow orchestrator.
"""

from workflow_vision_agent.orchestrator import WorkflowOrchestrator


def test_orchestrator_initialization():
    """Test orchestrator initialization."""
    orchestrator = WorkflowOrchestrator(headless=True, use_ai=False)
    assert orchestrator is not None, "Orchestrator should be created"
    assert orchestrator.headless is True, "Should set headless mode"
    assert orchestrator.use_ai is False, "Should set use_ai flag"
    print("✓ Orchestrator initialization test passed")


def test_orchestrator_question_parsing():
    """Test that orchestrator can parse questions."""
    orchestrator = WorkflowOrchestrator(headless=True, use_ai=False)
    
    # Test question parsing (without executing)
    parsed = orchestrator._understand_question("How do I create a project in Linear?")
    assert isinstance(parsed, dict), "Should return dictionary"
    assert "url" in parsed or "app_name" in parsed, "Should have URL or app_name"
    
    print("✓ Orchestrator question parsing test passed")


if __name__ == "__main__":
    test_orchestrator_initialization()
    test_orchestrator_question_parsing()

