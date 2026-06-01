#app.py
import streamlit as st
import pandas as pd
from main import run
from file_processor import process_file

# ---------------------------
# PAGE CONFIG (MUST BE FIRST)
# ---------------------------
st.set_page_config(page_title="QA + Dev AI Copilot", layout="wide")

st.title("🧠 QA + Dev AI Copilot")

# ---------------------------
# INPUTS
# ---------------------------
uploaded_file = st.file_uploader(
    "📂 Upload screenshot / PDF / DOCX",
    type=["png", "jpg", "jpeg", "pdf", "docx"]
)

user_input = st.text_area(
    "💬 Ask your QA Copilot (Paste ticket / requirement / scenario)"
)

# ---------------------------
# RUN BUTTON
# ---------------------------
if st.button("🚀 Run Analysis"):

    # Decide input source
    final_input = ""

    if uploaded_file:
        final_input = process_file(uploaded_file)
    else:
        final_input = user_input

    if not final_input:
        st.warning("Please provide input (text or file)")
    else:
        with st.spinner("Processing..."):
            st.markdown("### 🤖 Copilot Response")
            output = run(final_input)

        result = output.get("result", {})
        pii = output.get("pii_report", {})
        impact = output.get("impact", {})

        # ---------------------------
        # METRICS
        # ---------------------------
        col1, col2 = st.columns(2)
        col1.metric("Testcases", len(result.get("testcases", [])))
        col2.metric("PII Masked", pii.get("count", 0))

        # ---------------------------
        # TABS
        # ---------------------------
        tab1, tab2, tab3, tab4 = st.tabs([
            "🔐 PII",
            "📊 Impact Analysis",
            "🧪 Testcases",
            "🧐 Critic"
        ])

        # ---------------------------
        # TAB 1 - PII
        # ---------------------------
        with tab1:
            if pii.get("count", 0) > 0:
                st.success("Sensitive data masked")
            else:
                st.info("No PII found")

        # ---------------------------
        # TAB 2 - IMPACT
        # ---------------------------
        with tab2:
            st.json(impact)

        # ---------------------------
        # TAB 3 - TESTCASES
        # ---------------------------
        with tab3:
            testcases = result.get("testcases", [])

            if testcases:
                data = []
                for tc in testcases:
                    data.append({
                        "ID": tc.get("id"),
                        "Title": tc.get("title"),
                        "Steps": "\n".join(
                            [f"{i+1}. {step}" for i, step in enumerate(tc.get("steps", []))]
                        ),
                        "Expected": "\n".join(
                            [f"{i+1}. {exp}" for i, exp in enumerate(tc.get("expected", []))]
                        )
                    })

                df = pd.DataFrame(data)
                st.dataframe(df, use_container_width=True)

                st.download_button(
                    "⬇ Download CSV",
                    df.to_csv(index=False),
                    "testcases.csv"
                )
            else:
                st.warning("No testcases generated")

        # ---------------------------
        # TAB 4 - CRITIC
        # ---------------------------
        with tab4:
            st.json(result.get("critic", {}))

        # ---------------------------
        # INFO
        # ---------------------------
        st.info(
            "This Copilot understands your requirement, analyzes impact, "
            "generates structured testcases, and reviews QA coverage."
        )