import streamlit as st
from openai import OpenAI
import os
import json

# ✅ Initialize OpenAI client
client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))

# ✅ Streamlit Page Config
st.set_page_config(page_title="AlphaPulse - Behavioral Trading Assistant", layout="wide")

# ✅ Sidebar Inputs
st.sidebar.header("Trading Setup")
tickers = st.sidebar.text_area("Enter Tickers (comma-separated):", "AAPL, MSFT")
targets = st.sidebar.text_area("Enter Target Prices (e.g., AAPL=220, MSFT=400):", "AAPL=220, MSFT=400")
risk_amount = st.sidebar.number_input("Risk Per Trade ($):", min_value=100, value=1000, step=100)
stop_pct = st.sidebar.slider("Stop Loss %", 5, 50, 20)
target_pct = st.sidebar.slider("Target Profit %", 10, 200, 80)
strategy_pref = st.sidebar.selectbox("Strategy Preference", ["Auto", "Calls Only", "Puts Only", "Debit Spread", "Credit Spread"])

# ✅ Convert target prices into a dictionary
target_dict = {}
for pair in targets.split(","):
    if "=" in pair:
        t, v = pair.split("=")
        target_dict[t.strip().upper()] = float(v.strip())

# ✅ Main UI
st.title("📈 AlphaPulse - Behavioral Trading Assistant")
st.markdown("Generate AI-driven stock & options trade analysis with OCO levels and behavioral checks.")

if st.button("Generate Trade Analysis"):
    with st.spinner("Analyzing your tickers..."):
        # ✅ Create Prompt
        prompt = f"""
        Analyze the following trade setup based on behavioral investing principles and options strategy logic.

        Tickers: {tickers}
        Target Prices: {target_dict}
        Risk per Trade: ${risk_amount}
        OCO Rule: Stop {stop_pct}%, Target {target_pct}%
        Strategy Preference: {strategy_pref}

        For each ticker:
        1. Fetch current price and compute:
           Entry price, Stop-loss, Target price (use Baird target if conservative).
        2. Position sizing = Risk ÷ (Entry - Stop).
        3. Apply behavioral investing checklist:
           Risk allocation, Trend confirmation (RSI, EMA), Risk/Reward ≥ 1:2.
        4. Options analysis:
           Suggest best strategy (call, put, spread).
           Provide strike, expiry, premium, delta.
           Set OCO exits: stop (-50%), target (+100%).
        5. Return:
           - Human-readable summary
           - JSON object with trade details
        """

        # ✅ Call OpenAI API with the new method
        response = client.chat.completions.create(
            model="gpt-4.1",
            messages=[
                {"role": "system", "content": "You are AlphaPulse, an AI Behavioral Trading Assistant. Always provide detailed reasoning and JSON output."},
                {"role": "user", "content": prompt}
            ],
            temperature=0.3
        )

        result = response.choices[0].message.content

    # ✅ Display Output
    st.subheader("AI Analysis Summary")
    st.write(result)

    # ✅ Extract JSON
    try:
        json_part = result[result.index("{"):result.rindex("}")+1]
        parsed_json = json.loads(json_part)
        st.subheader("📦 Structured Trade Plan (JSON)")
        st.json(parsed_json)
    except:
        st.warning("Could not extract JSON. Please check the output above.")

# ✅ Footer
st.markdown("---")
st.caption("Powered by AlphaPulse AI | Behavioral Trading Assistant")

