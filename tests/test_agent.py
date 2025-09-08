from unittest.mock import patch

from nano_code.agent import CodingAgent
from nano_code.local import LocalEnvironment
from nano_code.openai_client import OpenAIClient


def test_successful_completion_with_confirmation():
    """Test agent completes successfully when user confirms all actions."""
    with patch(
        "nano_code.agent.prompt_session.prompt", side_effect=["", ""]
    ):  # Confirm action with Enter, then no new task
        agent = CodingAgent(
            model=OpenAIClient(
                outputs=["Finishing\n```bash\necho 'COMPLETE_TASK_AND_SUBMIT_FINAL_OUTPUT'\necho 'completed'\n```"]
            ),
            env=LocalEnvironment(),
        )

        exit_status, result = agent.run("Test completion with confirmation")
        assert exit_status == "Submitted"
        assert result == "completed\n"
        assert agent.model.n_calls == 1