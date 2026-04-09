import streamlit as st
import pandas as pd
from main import run

st.set_page_config(page_title="QA AI Copilot", layout="wide")

st.title("🧠 QA + Dev AI Copilot")

user_input = st.text_area("Enter Requirement / Ticket")

if st.button("🚀 Run Analysis"):

    if not user_input:
        st.warning("Enter input first")
    else:
        with st.spinner("Processing..."):
            output = run(user_input)

        result = output["result"]
        pii = output["pii_report"]

        col1, col2 = st.columns(2)
        col1.metric("Testcases", len(result["testcases"]))
        col2.metric("PII Masked", pii["count"])

        tab1, tab2, tab3 = st.tabs([
            "🔐 PII",
            "🧪 Testcases",
            "🧐 Critic"
        ])

        with tab1:
            if pii["count"] > 0:
                st.success("Sensitive data masked")
            else:
                st.info("No PII found")

        with tab2:
            data = []
            for tc in result["testcases"]:
                data.append({
                    "ID": tc["id"],
                    "Title": tc["title"],
                    "Steps": "\n".join(tc["steps"]),
                    "Expected": "\n".join(tc["expected"])
                })

            df = pd.DataFrame(data)
            st.dataframe(df)

            st.download_button(
                "Download CSV",
                df.to_csv(index=False),
                "testcases.csv"
            )

        with tab3:
            st.json(result["critic"])