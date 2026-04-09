# main.py

import os
import json
from dotenv import load_dotenv
from openai import OpenAI
from agents import (
    UI_AGENT_PROMPT,
    TESTCASE_AGENT_PROMPT,
    CRITIC_AGENT_PROMPT,
    IMPACT_AGENT_PROMPT
)
from pii_processor import process_pii

load_dotenv()

client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))

MODEL = "gpt-4o-mini"


# ---------------------------
# Helper
# ---------------------------
def call_llm(prompt):
    response = client.chat.completions.create(
        model=MODEL,
        messages=[
            {"role": "system", "content": prompt},
        ],
        temperature=0.2
    )
    return response.choices[0].message.content


def extract_json(text):
    try:
        return json.loads(text)
    except:
        try:
            start = text.index("{")
            end = text.rindex("}") + 1
            return json.loads(text[start:end])
        except:
            return {}


# ---------------------------
# MAIN
# ---------------------------
def run(user_input):

    # 🔐 PII Processing
    pii = process_pii(user_input)
    sanitized = pii["sanitized"]

    # ---------------------------
    # 🧠 UI ANALYSIS
    # ---------------------------
    ui_prompt = f"""
{UI_AGENT_PROMPT}

Input:
{sanitized}
"""
    ui_raw = call_llm(ui_prompt)
    ui_data = extract_json(ui_raw)
    ui_analysis = ui_data.get("ui_analysis", "")

    # ---------------------------
    # 📊 IMPACT ANALYSIS
    # ---------------------------
    impact_prompt = f"""
{IMPACT_AGENT_PROMPT}

Input:
{sanitized}
"""
    impact_raw = call_llm(impact_prompt)
    impact_data = extract_json(impact_raw)

    # ---------------------------
    # 🧪 TESTCASE GENERATION
    # ---------------------------
    tc_prompt = f"""
{TESTCASE_AGENT_PROMPT}

Input:
{ui_analysis}
"""
    tc_raw = call_llm(tc_prompt)
    tc_data = extract_json(tc_raw)
    testcases = tc_data.get("testcases", [])

    # ---------------------------
    # 🧐 CRITIC REVIEW
    # ---------------------------
    critic_prompt = f"""
{CRITIC_AGENT_PROMPT}

Testcases:
{testcases}
"""
    critic_raw = call_llm(critic_prompt)
    critic_data = extract_json(critic_raw)

    # ---------------------------
    # ✅ FINAL OUTPUT
    # ---------------------------
    return {
        "pii_report": pii,
        "impact": impact_data,   # ✅ separate (important)
        "result": {
            "testcases": testcases,
            "critic": critic_data
        }
    }