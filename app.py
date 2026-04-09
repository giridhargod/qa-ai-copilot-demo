import streamlit as st
import pandas as pd
from main import run
from file_processor import process_file

uploaded_file = st.file_uploader(
    "Upload screenshot / PDF / DOCX",
    type=["png", "jpg", "jpeg", "pdf", "docx"]
)

st.set_page_config(page_title="QA AI Copilot", layout="wide")

st.title("QA AI Copilot")

user_input = st.text_area("💬 Ask your QA Copilot (Paste ticket / requirement / scenario)")

final_input = ""

if uploaded_file:
    file_text = process_file(uploaded_file)
    final_input = file_text
else:
    final_input = user_input

if st.button("Run Analysis"):

    if not user_input:
        st.warning("Enter input first")
    else:
        with st.spinner("Processing..."):
            st.markdown("### 🤖 Copilot Response")
            output = run(user_input)

        result = output["result"]
        pii = output["pii_report"]

        col1, col2 = st.columns(2)
        col1.metric("Testcases", len(result["testcases"]))
        col2.metric("PII Masked", pii["count"])

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
    if pii["count"] > 0:
        st.success("Sensitive data masked")
    else:
        st.info("No PII found")

# ---------------------------
# TAB 2 - IMPACT
# ---------------------------
with tab2:
    st.json(output.get("impact", {}))

# ---------------------------
# TAB 3 - TESTCASES
# ---------------------------
with tab3:
    data = []
    for tc in result["testcases"]:
        data.append({
            "ID": tc["id"],
            "Title": tc["title"],
            "Steps": "\n".join([f"{i+1}. {step}" for i, step in enumerate(tc["steps"])]),
            "Expected": "\n".join([f"{i+1}. {exp}" for i, exp in enumerate(tc["expected"])])
        })

    df = pd.DataFrame(data)
    st.dataframe(df, use_container_width=True)

    st.download_button(
        "Download CSV",
        df.to_csv(index=False),
        "testcases.csv"
    )

# ---------------------------
# TAB 4 - CRITIC
# ---------------------------
with tab4:
    st.json(result["critic"])

output = run(final_input)

st.info(
    "This app understands your requirement, generates testcases, "
    "and reviews coverage like a QA lead."
)