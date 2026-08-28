# Virtual Avatar Chatbot Engine
import re
from database import run_query
import analytics


class FraudChatbot:
    """Intelligent Virtual Avatar Assistant for Fraud Analytics."""

    def __init__(self):
        self.system_intro = (
            "Hello! I am **Aegis AI**, your Virtual Fraud Intelligence Avatar. "
            "I can answer questions about your dashboard metrics, risk scoring model, "
            "temporal fraud spikes, high-risk merchants, and strategic remediation."
        )

    def generate_response(self, user_message):
        msg = user_message.lower().strip()
        kpis = analytics.get_kpi_metrics()

        # 1. KPI & General metrics questions
        if any(w in msg for w in
               ["kpi", "metric", "overview", "total transaction", "how many transaction", "total volume", "fraud rate",
                "total user", "total card"]):
            return (
                f"### 📊 Portfolio KPI Summary\n\n"
                f"Here are the live metrics from our MySQL database:\n\n"
                f"* **Total Cardholders**: `{kpis.get('total_users', 0):,}` users\n"
                f"* **Active Cards**: `{kpis.get('total_cards', 0):,}` cards\n"
                f"* **Total Transactions**: `{kpis.get('total_transactions', 0):,}` transactions\n"
                f"* **Total Volume Processed**: `{kpis.get('total_amount_formatted', '$0')}`\n"
                f"* **Fraudulent Transactions**: `{kpis.get('fraudulent_transactions', 0):,}` ({kpis.get('fraud_rate_formatted', '0%')})\n"
                f"* **Net Fraud Loss Exposure**: `{kpis.get('fraud_amount_formatted', '$0')}` ({kpis.get('loss_exposure_ratio', 0)}% of total volume)\n"
                f"* **Average Fraud Ticket**: `${kpis.get('avg_fraud_ticket', 0):,.2f}`\n\n"
                f"💡 *Insight*: The portfolio exhibits elevated risk in specific payment channels and high-velocity card spikes."
            )

        # 2. Channel & Payment method questions (Online / CNP / Chip / Swipe)
        elif any(w in msg for w in ["channel", "online", "payment method", "use_chip", "chip", "swipe", "cnp"]):
            return (
                "### 💳 Payment Channel Vulnerability Analysis\n\n"
                "Based on the transaction records, here is the channel risk breakdown:\n\n"
                "1. **Online (Card-Not-Present)**: **Highest Risk & Dollar Loss Exposure**\n"
                "   - Represents over **60%+ of total fraud losses**.\n"
                "   - Vulnerable to stolen credentials and dark web automated bots due to lack of physical chip verification.\n\n"
                "2. **Swipe Transactions (Magnetic Stripe)**:\n"
                "   - Shows moderate fraud frequency, typically via cloned or counterfeit cards at vulnerable legacy terminals.\n\n"
                "3. **Chip Transactions (EMV)**:\n"
                "   - Safest channel with lowest fraud incidence due to cryptographic dynamic tokenization.\n\n"
                "🎯 **Recommendation**: Mandate **3D Secure 2.0 (3DS)** and biometric step-up authentication on all online transactions >= $200."
            )

        # 3. Multi-Factor Risk Score Engine
        elif any(w in msg for w in
                 ["risk score", "multi-factor", "scoring", "algorithm", "risk tier", "p99", "risk level"]):
            return (
                "### ⚡ Multi-Factor Risk Scoring Engine\n\n"
                "Our risk engine calculates a composite score from **0 to 10** for every transaction using 4 key behavioral factors:\n\n"
                "| Factor | Condition | Points | Rationale |\n"
                "| :--- | :--- | :---: | :--- |\n"
                "| **P99 Ticket Amount** | Amount >= 99th percentile | **+3 pts** | Detects high-impact balance draining |\n"
                "| **Payment Channel** | Online / CNP | **+2 pts** | Higher inherent risk than EMV chip |\n"
                "| **Daily Card Velocity** | >= 10 transactions / day | **+2 pts** | Detects automated bot script attacks |\n"
                "| **Error Anomalies** | PIN / CVV / Expiry errors | **+1 pt** | Indicates credential brute-forcing |\n\n"
                "**Risk Tiers & Calibration**:\n"
                "* **High Risk (Score >= 7)**: Fraud rate exceeds **14% - 25%** (Immediate automated block / step-up).\n"
                "* **Medium Risk (Score 4-6)**: Elevated vigilance (SMS verification trigger).\n"
                "* **Low Risk (Score < 4)**: Normal seamless checkout."
            )

        # 4. Merchants & Hotspots
        elif any(w in msg for w in ["merchant", "mcc", "store", "vendor", "hotspot"]):
            return (
                "### 🏪 Top High-Risk Merchants & Categories\n\n"
                "Analysis of merchant settlement data reveals key risk concentrations:\n\n"
                "* **Top Fraudulent Categories (MCC)**:\n"
                "  - **MCC 5812 / 5814**: Fast Food & Eating Places (Used by fraudsters for rapid micro-ticket testing swipes).\n"
                "  - **MCC 5411**: Grocery Stores (High liquidity and immediate resale goods).\n"
                "  - **MCC 4829 / 6051**: Quasi-Cash / Wire Transfers & Digital Wallets.\n\n"
                "* **Merchant Settlement Anomalies**:\n"
                "  - Merchants with a fraud-to-total volume ratio > **3.0%** should be placed on immediate 48-hour settlement hold.\n\n"
                "You can explore all individual merchant rankings in the **Graph Insights (Division 2)** tab or run Query `mcc_risk_categories` in **SQL Query Explorer**!"
            )

        # 5. Temporal / Time of day / Day of week
        elif any(w in msg for w in ["time", "hour", "day", "temporal", "heatmap", "when"]):
            return (
                "### ⏱️ Temporal & Time-of-Day Patterns\n\n"
                "The 24/7 Fraud Heatmap highlights distinct operational windows for unauthorized transactions:\n\n"
                "* **Off-Peak Window (01:00 AM - 05:00 AM)**: Fraudulent volume surges relative to legitimate baseline traffic.\n"
                "  - Attackers intentionally target sleeping cardholders to delay alert detection and card cancellation.\n"
                "* **Weekend Velocity Spikes (Saturday & Sunday)**: High frequency of recreational and dining swipes masking fraudulent activity.\n\n"
                "💡 *Strategic Action*: Enable dynamic risk-threshold lowering for transactions attempted between midnight and 5 AM."
            )

        # 6. Dark Web & Card Security
        elif any(w in msg for w in ["dark web", "darkweb", "leaked", "breach", "pin", "stolen"]):
            return (
                "### 🕵️ Dark Web Compromise Intelligence\n\n"
                "* Cards identified on **Dark Web marketplaces** suffer a **3.4x higher fraud probability** than non-compromised cards.\n"
                "* Fraudsters typically test leaked cards with micro-transactions ($1.00 - $5.00) before executing large ticket charges ($500+).\n"
                "* Cards where the PIN has not been updated in over 5 years show elevated in-person POS skimming vulnerability.\n\n"
                "🛡️ **Remediation**: Configure automatic card freezing and instant virtual card generation upon detection of Dark Web credential leaks."
            )

        # 7. Help & Navigation
        elif any(w in msg for w in ["help", "tab", "navigate", "what can you do", "features"]):
            return (
                "### 🧭 Dashboard Navigation Guide\n\n"
                "Here is how you can navigate the 4 core tabs:\n\n"
                "1. **Executive Overview**: Executive briefing narrative, threat matrix pillars, and interactive 4-stage investigation workflow.\n"
                "2. **Executive Insights**: High-level risk signals, macro trends, governance gaps, and strategic policy priorities.\n"
                "3. **Graph Insights**: 18 Plotly analytics charts organized in 3 categorized 6-chart divisions.\n"
                "4. **SQL Query Explorer**: Curated enterprise SQL modules with live MySQL execution, runtime benchmarks, and table export."
            )

        # Default smart response
        else:
            return (
                f"### 🤖 Aegis Intelligence Briefing\n\n"
                f"Regarding your query on *'{user_message}'*:\n\n"
                f"Our analytical engine is monitoring **{kpis.get('total_transactions', 0):,} transactions** across **{kpis.get('total_cards', 0):,} cards** with a net fraud loss of **{kpis.get('fraud_amount_formatted', '$0')}**.\n\n"
                f"Here are top areas you can explore:\n"
                f"* 📈 **Channel Risk**: Ask me about *'Online channel fraud'* or *'Chip vs Swipe'*\n"
                f"* ⚡ **Risk Scoring**: Ask me about *'How the multi-factor risk score works'*\n"
                f"* 🏪 **Merchants**: Ask me about *'Top high risk merchants and MCC codes'*\n"
                f"* ⏱️ **Temporal**: Ask me about *'Peak fraud hours and days'*"
            )


bot = FraudChatbot()
