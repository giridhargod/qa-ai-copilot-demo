from crewai import Task
from agents import ui_agent


def create_tasks(sanitized_input):

    combined_task = Task(
        description=f"""
        Analyze the UI and generate COMPLETE output in STRICT JSON:

        {{
          "ui_analysis": "Detailed UI analysis",
          "testcases": [
            {{
              "id": 1,
              "scenario": "",
              "steps": "",
              "expected": ""
            }}
          ],
          "critic": "Feedback on testcases"
        }}

        Input:
        {sanitized_input}

        RULES:
        - Return ONLY JSON
        - Minimum 5 testcases
        - Do NOT include explanations
        """,
        agent=ui_agent
    )

    return [combined_task]