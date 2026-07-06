#app/streamlit_app.py
import sys
from pathlib import Path

ROOT_DIR = Path(__file__).resolve().parent.parent

sys.path.append(str(ROOT_DIR))

import streamlit as st
import pandas as pd

from workflows.workflow import WorkflowOrchestrator
from services.file_service import resolve_input

st.set_page_config(
    page_title="QA AI Copilot",
    layout="wide"
)

st.title("🧠 QA AI Copilot")
st.caption(
    "AI-Powered Requirement Analysis, Impact Assessment, "
    "Test Design, Traceability and QA Evaluation Platform"
)

uploaded_file = st.file_uploader(
    "📂 Upload PDF / DOCX / Screenshot",
    type=["pdf", "docx", "png", "jpg", "jpeg"]
)

user_input = st.text_area(
    "Requirement / User Story / Feature Description",
    height=250
)

if st.button("🚀 Run Analysis"):

    final_input = resolve_input(uploaded_file, user_input)

    if not final_input:

        st.warning(
            "Please provide input."
        )

    else:

        with st.spinner(
            "Running QA AI Copilot..."
        ):

            workflow = WorkflowOrchestrator()

            result = workflow.run(
                final_input
            )

        st.success(
            "Analysis Completed"
        )

        dashboard1, dashboard2, dashboard3, dashboard4 = st.columns(4)

        dashboard1.metric(
            "Requirements",
            len(result.requirements)
        )

        dashboard2.metric(
            "Test Cases",
            len(result.testcases)
        )

        dashboard3.metric(
            "Coverage %",
            result.coverage_metrics.get(
                "coverage_percentage",
                0
            )
        )

        dashboard4.metric(
            "Quality Score",
            result.evaluation_metrics.get(
                "quality_score",
                0
            )
        )

        tabs = st.tabs([
            "📊 Dashboard",
            "🔐 PII",
            "📋 Requirements",
            "📈 Impact Analysis",
            "🧪 Test Cases",
            "🔗 Traceability",
            "📊 Coverage",
            "📏 Evaluation",
            "🧐 Critic Review",
            "📜 Execution Log"
        ])

        # Dashboard
        with tabs[0]:

            st.subheader(
                "Workflow Metrics"
            )

            st.json(
                result.workflow_metrics
            )

        # PII
        with tabs[1]:

            st.json(
                result.pii_report
            )

        # Requirements
        with tabs[2]:

            if result.requirements:

                st.dataframe(
                    pd.DataFrame(
                        result.requirements
                    ),
                    use_container_width=True
                )

            else:

                st.info(
                    "No requirements extracted"
                )

        # Impact Analysis
        with tabs[3]:

            st.json(
                result.impact_analysis
            )

        # Test Cases
        with tabs[4]:

            if result.testcases:

                testcase_rows = []

                for tc in result.testcases:

                    testcase_rows.append(
                        {
                            "ID": tc.get("id"),
                            "Title": tc.get("title"),
                            "Priority": tc.get(
                                "priority"
                            ),
                            "Expected Result": tc.get(
                                "expected_result"
                            )
                        }
                    )

                df = pd.DataFrame(
                    testcase_rows
                )

                st.dataframe(
                    df,
                    use_container_width=True
                )

                st.download_button(
                    "⬇ Download CSV",
                    df.to_csv(
                        index=False
                    ),
                    "testcases.csv"
                )

            else:

                st.warning(
                    "No test cases generated"
                )

        # Traceability
        with tabs[5]:

            traceability_rows = []

            for item in result.traceability_matrix:

                traceability_rows.append(
                    {
                        "Requirement ID":
                        item.requirement_id,

                        "Requirement":
                        item.requirement_text,

                        "Test Cases":
                        ", ".join(
                            item.testcase_ids
                        )
                    }
                )

            st.dataframe(
                pd.DataFrame(
                    traceability_rows
                ),
                use_container_width=True
            )

        # Coverage
        with tabs[6]:

            st.json(
                result.coverage_metrics
            )

        # Evaluation
        with tabs[7]:

            st.json(
                result.evaluation_metrics
            )

        # Critic
        with tabs[8]:

            st.json(
                result.critic_reviews
            )

        # Execution Log
        with tabs[9]:

            execution_rows = []

            for item in result.execution_log:

                execution_rows.append(
                    {
                        "Agent":
                        item.agent_name,

                        "Status":
                        item.status,

                        "Executed At":
                        item.executed_at
                    }
                )

            st.dataframe(
                pd.DataFrame(
                    execution_rows
                ),
                use_container_width=True
            )