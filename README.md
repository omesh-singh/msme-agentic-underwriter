# MSME Agentic Underwriter

A credit intelligence terminal for MSME lending — built on Account Aggregator data.

🔗 **[Try the live app](https://msme-agentic-underwriter.streamlit.app)**

---

## What's inside

Pick a borrower persona from the sidebar, run the audit, and the engine produces a full decisioning output — verdict, recommended limit, risk-adjusted pricing, and a Gemini-generated credit memo — in seconds.

Three personas are pre-loaded, each representing a distinct borrower archetype and a different outcome:

| Persona | What to look for |
|---------|-----------------|
| 🏪 Prime Retailer (Alpha) | Clean data, all gates pass |
| 📊 GST-Divergent Unit | Watch the integrity haircut fire |
| ⚠️ Distressed Trader | Two independent decline triggers |

---

## Under the hood

The engine runs a multi-layer audit on verified bank statement data — behavioural risk metrics, GST cross-referencing, policy gate evaluation, and commercial structuring — before handing off to AI for narrative synthesis.

The decisioning logic is proprietary. Reach out if you'd like to know more.

---

## Built with

Streamlit · DuckDB · Altair · Google Gemini · Python

---

## Author

[Omesh Kumar Singh](https://www.linkedin.com/in/omeshksingh/) — reach out on LinkedIn for questions, feedback, or collaboration.

---

*Demonstration tool. Not intended for production credit decisions.*
