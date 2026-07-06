#tests/test_critic_reviews.py
from agents.requirement_readiness_agent import RequirementReadinessAgent
from agents.critic_agent import CriticAgent
from models.workflow_state import WorkflowState


def test_two_critics_do_not_overwrite_each_other():
    state = WorkflowState()
    state.sanitized_input = (
        "Administrator shall login using Email and Password."
    )

    state = RequirementReadinessAgent().execute(state)

    assert "requirement_readiness" in state.critic_reviews

    fake_testcase_critic_result = {"approved": True, "notes": "ok"}
    CriticAgent(llm_service=None).store_result(
        state, fake_testcase_critic_result
    )

    assert "testcase" in state.critic_reviews
    assert len(state.critic_reviews) == 2
    assert state.critic_reviews["testcase"] == fake_testcase_critic_result


if __name__ == "__main__":
    test_two_critics_do_not_overwrite_each_other()
    print("test_two_critics_do_not_overwrite_each_other passed")
