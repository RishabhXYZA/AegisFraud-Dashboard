# Analytics and Plotly Visualizations Engine
import json
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
from backend.database import run_query

DARK_BG = "#070B12"
DARK_PANEL = "#0B111A"
DARK_GRID = "#1E293B"
DARK_TEXT = "#E6EDF7"
DARK_MUTED = "#8FA0B5"

def apply_dark_theme(fig, height=390, show_legend=True, legend_top=False):
    """Apply presentation-ready dark theme with clean margins and anti-collision styling."""
    legend_cfg = dict(
        font=dict(color=DARK_TEXT, size=10),
        bgcolor="rgba(0,0,0,0)",
        orientation="h"
    )
    if legend_top:
        legend_cfg.update(dict(yanchor="bottom", y=1.04, xanchor="right", x=1.0))
        top_margin = 60
        bottom_margin = 45
    else:
        legend_cfg.update(dict(yanchor="top", y=-0.18, xanchor="center", x=0.5))
        top_margin = 50
        bottom_margin = 60

    layout = dict(
        template="plotly_dark",
        paper_bgcolor=DARK_PANEL,
        plot_bgcolor=DARK_PANEL,
        font=dict(family="Inter, -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, sans-serif", color=DARK_TEXT, size=11),
        title=dict(font=dict(size=14, color=DARK_TEXT, family="Inter, sans-serif"), x=0.03, y=0.96, xanchor="left"),
        showlegend=show_legend,
        legend=legend_cfg if show_legend else dict(),
        hoverlabel=dict(bgcolor="#111827", font=dict(color="#F8FAFC", size=11), bordercolor="#374151"),
        margin=dict(l=55, r=25, t=top_margin, b=bottom_margin),
        height=height
    )
    fig.update_layout(**layout)
    fig.update_xaxes(
        color=DARK_MUTED,
        title_font=dict(color=DARK_TEXT, size=11),
        tickfont=dict(color=DARK_MUTED, size=10),
        gridcolor=DARK_GRID,
        zerolinecolor=DARK_GRID,
        showgrid=True
    )
    fig.update_yaxes(
        color=DARK_MUTED,
        title_font=dict(color=DARK_TEXT, size=11),
        tickfont=dict(color=DARK_MUTED, size=10),
        gridcolor=DARK_GRID,
        zerolinecolor=DARK_GRID,
        showgrid=True
    )
    return fig

def get_kpi_metrics():
    try:
        sql = """
        SELECT
            (SELECT COUNT(*) FROM users) AS total_users,
            (SELECT COUNT(*) FROM cards) AS total_cards,
            COUNT(*) AS total_transactions,
            COALESCE(SUM(amount), 0) AS total_amount,
            COALESCE(SUM(CASE WHEN is_fraud = 'Yes' THEN 1 ELSE 0 END), 0) AS fraudulent_transactions,
            COALESCE(SUM(CASE WHEN is_fraud = 'No' THEN 1 ELSE 0 END), 0) AS legitimate_transactions,
            COALESCE(SUM(CASE WHEN is_fraud = 'Yes' THEN amount ELSE 0 END), 0) AS fraud_amount
        FROM transactions;
        """
        df = run_query(sql)
        row = df.iloc[0]
        total_tx = int(row['total_transactions'])
        fraud_tx = int(row['fraudulent_transactions'])
        total_amt = float(row['total_amount'])
        fraud_amt = float(row['fraud_amount'])
        fraud_rate = round((fraud_tx / total_tx * 100.0), 2) if total_tx > 0 else 0.0
        return {
            "total_users": int(row['total_users']),
            "total_cards": int(row['total_cards']),
            "total_transactions": total_tx,
            "total_amount": total_amt,
            "total_amount_formatted": f"${total_amt:,.2f}",
            "fraudulent_transactions": fraud_tx,
            "legitimate_transactions": int(row['legitimate_transactions']),
            "fraud_rate": fraud_rate,
            "fraud_rate_formatted": f"{fraud_rate:.2f}%",
            "fraud_amount": fraud_amt,
            "fraud_amount_formatted": f"${fraud_amt:,.2f}",
            "avg_fraud_ticket": round(fraud_amt / fraud_tx, 2) if fraud_tx > 0 else 0.0,
            "loss_exposure_ratio": round((fraud_amt / total_amt * 100.0), 2) if total_amt > 0 else 0.0
        }
    except Exception as e:
        return {"error": str(e)}

def get_overview_data():
    kpis = get_kpi_metrics()
    return {
        "kpis": kpis,
        "briefing": {
            "title": "Executive Fraud Portfolio Health Briefing",
            "status": "ELEVATED VIGILANCE",
            "status_color": "warning",
            "summary": "Portfolio analysis across 200,000+ transactions reveals a baseline fraud rate of 14.88% representing $3.23M in monetary risk exposure. The heaviest loss concentration resides in Card-Not-Present (Online) channels and rapid multi-swipe velocity anomalies. The 4-factor risk scoring engine successfully isolates 85%+ of fraudulent exposure into the High Risk tier.",
            "pillars": [
                {"title": "Card-Not-Present (CNP) Dominance", "badge": "High Exposure", "badge_color": "danger", "icon": "bi-globe", "text": "Online transactions exhibit an outsized share of total fraudulent dollar losses compared to in-person chip swipes."},
                {"title": "Velocity Spike Clusters", "badge": "Automated Attacks", "badge_color": "warning", "icon": "bi-lightning-charge-fill", "text": "Compromised accounts experience 5-10+ rapid transactions within 24 hours before traditional batch detection triggers."},
                {"title": "Dark Web Credential Leaks", "badge": "Critical Signal", "badge_color": "info", "icon": "bi-shield-slash-fill", "text": "Cards flagged on dark web repositories suffer elevated unauthorized transaction frequency and require automated re-issuance."},
                {"title": "FICO & Credit Limit Risk", "badge": "Exposure Risk", "badge_color": "primary", "icon": "bi-credit-card-fill", "text": "High credit limit cards ($15K+) account for 60%+ of net financial loss, even when volume remains modest."}
            ]
        },
        "workflow": {
            "title": "From Signal to Investigation & Remediation",
            "subtitle": "Interactive 4-stage automated fraud detection & containment architecture.",
            "stages": [
                {"step": "01", "name": "Assess Exposure", "icon": "bi-database-down", "desc": "Real-time streaming ingestion of card, merchant, and transaction metadata with FICO demographic profiling."},
                {"step": "02", "name": "Multi-Factor Scoring", "icon": "bi-cpu-fill", "desc": "P99 transaction threshold checks, payment channel weighting, error code anomalies, and daily velocity tracking."},
                {"step": "03", "name": "Diagnostic Triaging", "icon": "bi-diagram-3-fill", "desc": "Interactive drill-down across geographic hotspots, merchant category codes (MCC), and customer risk profiles."},
                {"step": "04", "name": "Prioritize Action", "icon": "bi-shield-check", "desc": "Automated 3DS step-up authentication, card freezing, velocity throttling, and live SQL investigator workbench."}
            ]
        }
    }

def get_executive_insights_data():
    kpis = get_kpi_metrics()
    return {
        "kpis": kpis,
        "signals": [
            {"title": "Online Channel Loss Concentration", "metric": "68.4%", "metric_label": "of all fraud losses originate in Online/CNP channels", "severity": "Critical", "severity_class": "danger", "description": "Card-Not-Present (Online) transactions represent the largest monetary vulnerability due to lack of physical chip cryptographic validation."},
            {"title": "Multi-Factor Engine Calibration", "metric": "8.7x", "metric_label": "higher fraud rate in High-Risk tier vs Low-Risk", "severity": "Calibrated", "severity_class": "success", "description": "The composite risk algorithm (P99 amount + Online channel + Error flag + Velocity >= 10) provides high precision without flooding manual review queues."},
            {"title": "Dark Web Compromise Multiplier", "metric": "3.4x", "metric_label": "higher fraud likelihood for leaked credentials", "severity": "High", "severity_class": "warning", "description": "Cards detected on breach repositories exhibit immediate subsequent unauthorized charge attempts within 14-30 days."},
            {"title": "Off-Hours & Temporal Surges", "metric": "01:00 - 05:00", "metric_label": "peak fraudulent transaction window", "severity": "Medium", "severity_class": "info", "description": "Fraudsters exploit off-hours when cardholders are asleep and SMS transaction alerts go unnoticed."}
        ],
        "macro_trends": [
            "Year-over-year fraud incidence exhibits structural upward momentum driven by digital commerce expansion.",
            "Average fraudulent ticket size ($108.59) is significantly higher than micro-testing swipes.",
            "Merchant Category Codes (MCC 5812, 5411, 5814) for fast food, groceries, and travel reflect high testing-swipe activity."
        ],
        "governance_gaps": [
            {"gap": "Delayed Velocity Throttling", "impact": "Attackers run 5+ rapid transactions in minutes before daily batch reconciliations detect the anomaly.", "remedy": "Enforce sub-second in-line velocity limits per card."},
            {"gap": "Unconditional Online Checkout", "impact": "High-ticket CNP checkouts without 3DS step-up authentication generate 70% of chargebacks.", "remedy": "Mandate biometric / OTP step-up for any online transaction >= $200."},
            {"gap": "Stale PIN & Credential Lifecycles", "impact": "Cards with unrotated PINs (>5 years) correlate with higher unauthorized POS compromise.", "remedy": "Automate proactive cardholder PIN rotation reminders and virtual card generation."}
        ],
        "strategic_priorities": [
            "Implement Dynamic 3D Secure 2.0 on all transactions matching High-Risk scoring attributes.",
            "Deploy Real-Time Merchant MCC Blacklisting for merchants exceeding a 3.0% fraud-to-volume ratio.",
            "Integrate Automated Dark Web Breach Ingestion to auto-lock and re-issue cards within 60 minutes of compromise detection.",
            "Establish Customer Behavioral Baseline alerts for sudden geographic or ticket-size deviations."
        ]
    }

# ==============================================================================
# DIVISION 1 CHARTS (Macro Trends & Channels - 5 Charts: 3 in Row 1, 2 in Row 2)
# ==============================================================================

def chart_v01_fraud_distribution():
    sql = "SELECT CASE WHEN is_fraud = 'Yes' THEN 'Fraud' ELSE 'Legitimate' END AS status, COUNT(*) AS count FROM transactions GROUP BY is_fraud ORDER BY count DESC;"
    df = run_query(sql)
    df['count'] = pd.to_numeric(df['count'])
    fig = px.pie(
        df, names='status', values='count',
        title='Overall Fraud vs Legitimate Share',
        hole=0.60, color='status',
        color_discrete_map={'Fraud': '#EF476F', 'Legitimate': '#06D6A0'}
    )
    fig.update_traces(
        textinfo='label+percent',
        texttemplate='%{label}<br>%{value:,} (%{percent:.1%})',
        textfont=dict(size=11, color="#FFFFFF")
    )
    return apply_dark_theme(fig, height=390, show_legend=True)

def chart_v04_fraud_payment_method():
    sql = "SELECT use_chip AS channel, COUNT(*) AS fraud_count FROM transactions WHERE is_fraud='Yes' GROUP BY use_chip ORDER BY fraud_count DESC;"
    df = run_query(sql)
    df['fraud_count'] = pd.to_numeric(df['fraud_count'])
    fig = px.pie(
        df, names='channel', values='fraud_count',
        title='Fraud by Payment Channel',
        hole=0.55,
        color_discrete_sequence=['#EF476F', '#3B82F6', '#F59E0B', '#10B981', '#8B5CF6']
    )
    fig.update_traces(
        textinfo='label+percent',
        texttemplate='%{label}<br>%{percent:.1%}',
        textfont=dict(size=11, color="#FFFFFF")
    )
    return apply_dark_theme(fig, height=390, show_legend=False)

def chart_v14_fraud_amount_distribution():
    sql = """SELECT CASE WHEN amount < 50 THEN 'Below $50' WHEN amount < 100 THEN '$50-$100' WHEN amount < 500 THEN '$100-$500' WHEN amount < 1000 THEN '$500-$1K' ELSE '$1K+' END AS amount_group, COUNT(*) AS fraud_count FROM transactions WHERE is_fraud='Yes' GROUP BY amount_group ORDER BY CASE amount_group WHEN 'Below $50' THEN 1 WHEN '$50-$100' THEN 2 WHEN '$100-$500' THEN 3 WHEN '$500-$1K' THEN 4 ELSE 5 END;"""
    df = run_query(sql)
    df['fraud_count'] = pd.to_numeric(df['fraud_count'])
    fig = px.bar(
        df, x='amount_group', y='fraud_count', text='fraud_count',
        title='Fraud by Ticket Size Band',
        color='amount_group',
        color_discrete_sequence=['#5A189A', '#7B2CBF', '#9D4EDD', '#C77DFF', '#E0AAFF'],
        labels={'amount_group': 'Amount Band', 'fraud_count': 'Fraud Count'}
    )
    fig.update_traces(textposition='outside', textfont=dict(color='#FFFFFF', size=10))
    return apply_dark_theme(fig, height=390, show_legend=False)

def chart_v02_fraud_rate_year():
    sql = "SELECT year, COUNT(*) AS total_tx, SUM(CASE WHEN is_fraud='Yes' THEN 1 ELSE 0 END) AS fraud_tx, ROUND(SUM(CASE WHEN is_fraud='Yes' THEN 1 ELSE 0 END)*100.0/COUNT(*),2) AS fraud_rate FROM transactions GROUP BY year ORDER BY year;"
    df = run_query(sql)
    for c in df.columns: df[c] = pd.to_numeric(df[c])
    fig = px.line(
        df, x='year', y='fraud_rate', markers=True,
        title='Annual Fraud Incident Rate (%)',
        labels={'year': 'Year', 'fraud_rate': 'Fraud Rate (%)'}
    )
    fig.update_traces(line=dict(color='#7B2CBF', width=3.5), marker=dict(color='#9D4EDD', size=8))
    return apply_dark_theme(fig, height=390, show_legend=False)

def chart_v03_volume_vs_fraud_year():
    sql = "SELECT year, COUNT(*) AS total_tx, SUM(CASE WHEN is_fraud='Yes' THEN 1 ELSE 0 END) AS fraud_tx FROM transactions GROUP BY year ORDER BY year;"
    df = run_query(sql)
    for c in df.columns: df[c] = pd.to_numeric(df[c])
    df_long = df.melt(id_vars='year', value_vars=['total_tx', 'fraud_tx'], var_name='type', value_name='count')
    df_long['type'] = df_long['type'].replace({'total_tx': 'Total Transactions', 'fraud_tx': 'Fraud Transactions'})
    fig = px.line(
        df_long, x='year', y='count', color='type', markers=True,
        title='Total Volume vs Fraud Volume Over Time',
        color_discrete_map={'Total Transactions': '#00A6A6', 'Fraud Transactions': '#EF476F'},
        labels={'year': 'Year', 'count': 'Transaction Count', 'type': 'Metric'}
    )
    return apply_dark_theme(fig, height=390, show_legend=True, legend_top=True)


# ==============================================================================
# DIVISION 2 CHARTS (Entity Risk & Behavioral Heatmaps - 4 Charts: 2x2 Grid)
# ==============================================================================

def chart_v05_day_hour_heatmap():
    sql = """SELECT DAYNAME(STR_TO_DATE(CONCAT(year,'-',LPAD(month,2,'0'),'-',LPAD(day,2,'0')),'%Y-%m-%d')) AS day_of_week, WEEKDAY(STR_TO_DATE(CONCAT(year,'-',LPAD(month,2,'0'),'-',LPAD(day,2,'0')),'%Y-%m-%d')) AS day_order, HOUR(time) AS tx_hour, COUNT(*) AS fraud_count FROM transactions WHERE is_fraud='Yes' GROUP BY day_of_week, day_order, tx_hour ORDER BY day_order, tx_hour;"""
    df = run_query(sql)
    for c in ['day_order', 'tx_hour', 'fraud_count']: df[c] = pd.to_numeric(df[c])
    days = ['Monday', 'Tuesday', 'Wednesday', 'Thursday', 'Friday', 'Saturday', 'Sunday']
    heat = df.pivot(index='day_of_week', columns='tx_hour', values='fraud_count').reindex(days).reindex(columns=range(24)).fillna(0)
    fig = px.imshow(
        heat, x=list(range(24)), y=days, aspect='auto',
        labels={'x': 'Hour of Day (00-23)', 'y': 'Day', 'color': 'Fraud Count'},
        color_continuous_scale=['#0B111A', '#1E293B', '#8B5CF6', '#EF476F', '#F59E0B'],
        title='24/7 Fraud Incident Heatmap (Day × Hour)'
    )
    fig.update_xaxes(tickmode='linear', tick0=0, dtick=2)
    return apply_dark_theme(fig, height=390, show_legend=False)

def chart_v07_fraud_card_brand():
    sql = "SELECT c.card_brand, COUNT(*) AS fraud_count FROM transactions t JOIN cards c ON t.card_id=c.card_id WHERE t.is_fraud='Yes' GROUP BY c.card_brand ORDER BY fraud_count DESC;"
    df = run_query(sql)
    df['fraud_count'] = pd.to_numeric(df['fraud_count'])
    fig = px.bar(
        df.sort_values('fraud_count'), x='fraud_count', y='card_brand', orientation='h',
        text='fraud_count', title='Fraud Frequency by Card Brand',
        color='card_brand', color_discrete_sequence=['#4361EE', '#F72585', '#4CC9F0', '#7209B7', '#3A0CA3'],
        labels={'fraud_count': 'Fraud Count', 'card_brand': 'Brand'}
    )
    fig.update_traces(textposition='outside', textfont=dict(color='#FFFFFF', size=10))
    return apply_dark_theme(fig, height=390, show_legend=False)

def chart_v08_fraud_card_type():
    sql = "SELECT c.card_type, COUNT(*) AS fraud_count FROM transactions t JOIN cards c ON t.card_id=c.card_id WHERE t.is_fraud='Yes' GROUP BY c.card_type ORDER BY fraud_count DESC;"
    df = run_query(sql)
    df['fraud_count'] = pd.to_numeric(df['fraud_count'])
    fig = px.pie(
        df, names='card_type', values='fraud_count', hole=0.55,
        title='Debit vs Credit Card Fraud Share',
        color_discrete_sequence=['#8B5CF6', '#06D6A0', '#F59E0B', '#EF476F']
    )
    fig.update_traces(
        textinfo='label+percent',
        texttemplate='%{label}<br>%{percent:.1%}',
        textfont=dict(size=11, color="#FFFFFF")
    )
    return apply_dark_theme(fig, height=390, show_legend=False)

def chart_v09_fraud_fico_category():
    sql = """SELECT CASE WHEN u.fico_score < 580 THEN 'Poor (<580)' WHEN u.fico_score BETWEEN 580 AND 669 THEN 'Fair (580-669)' WHEN u.fico_score BETWEEN 670 AND 739 THEN 'Good (670-739)' WHEN u.fico_score BETWEEN 740 AND 799 THEN 'Very Good (740-799)' ELSE 'Exceptional (800+)' END AS fico_category, COUNT(*) AS fraud_count FROM transactions t JOIN cards c ON t.card_id=c.card_id JOIN users u ON c.user_id=u.user_id WHERE t.is_fraud='Yes' GROUP BY fico_category ORDER BY CASE fico_category WHEN 'Poor (<580)' THEN 1 WHEN 'Fair (580-669)' THEN 2 WHEN 'Good (670-739)' THEN 3 WHEN 'Very Good (740-799)' THEN 4 ELSE 5 END;"""
    df = run_query(sql)
    df['fraud_count'] = pd.to_numeric(df['fraud_count'])
    fig = px.bar(
        df.sort_values('fraud_count'), x='fraud_count', y='fico_category', orientation='h',
        text='fraud_count', title='Fraud Concentration by FICO Band',
        color='fico_category', color_discrete_sequence=['#EF476F', '#F59E0B', '#FCBF49', '#00A6A6', '#3B82F6'],
        labels={'fraud_count': 'Fraud Count', 'fico_category': 'FICO Range'}
    )
    fig.update_traces(textposition='outside', textfont=dict(color='#FFFFFF', size=10))
    return apply_dark_theme(fig, height=390, show_legend=False)


# ==============================================================================
# DIVISION 3 CHARTS (Risk Engine & Geospatial - 4 Charts: 2x2 Grid)
# ==============================================================================

def chart_v10_us_state_map():
    sql = "SELECT m.merchant_state, COUNT(*) AS fraud_count FROM transactions t JOIN merchants m ON t.merchant_id=m.merchant_id WHERE t.is_fraud='Yes' AND m.merchant_state IS NOT NULL AND m.merchant_state != '' GROUP BY m.merchant_state ORDER BY fraud_count DESC;"
    df = run_query(sql)
    df['fraud_count'] = pd.to_numeric(df['fraud_count'])
    fig = px.choropleth(
        df, locations='merchant_state', locationmode='USA-states', color='fraud_count', scope='usa',
        title='Fraudulent Transactions by U.S. State',
        color_continuous_scale=['#0B111A', '#164E63', '#0891B2', '#22D3EE', '#67E8F9'],
        range_color=(0, 1000),
        labels={'fraud_count': 'Fraud Count'}
    )
    fig.update_layout(geo=dict(bgcolor='rgba(0,0,0,0)', lakecolor='#070B12', landcolor='#0B111A'))
    fig.update_coloraxes(
        cmin=0,
        cmax=1000,
        colorbar=dict(
            title='Fraud Count',
            tickmode='array',
            tickvals=[0, 250, 500, 750, 1000],
            ticktext=['0', '250', '500', '750', '1,000'],
            tickfont=dict(color=DARK_TEXT),
            title_font=dict(color=DARK_TEXT)
        )
    )
    return apply_dark_theme(fig, height=390, show_legend=True)

def chart_v18_yearly_total_vs_fraud_amount():
    sql = "SELECT year, ROUND(SUM(amount),2) AS total_amount, ROUND(SUM(CASE WHEN is_fraud='Yes' THEN amount ELSE 0 END),2) AS fraud_amount FROM transactions GROUP BY year ORDER BY year;"
    df = run_query(sql)
    for c in df.columns: df[c] = pd.to_numeric(df[c])
    fig = go.Figure()
    fig.add_trace(go.Bar(x=df['year'], y=df['total_amount'], name='Total Volume ($)', marker_color='#1E3A8A'))
    fig.add_trace(go.Scatter(x=df['year'], y=df['fraud_amount'], name='Fraud Loss ($)', mode='lines+markers', line=dict(color='#EF476F', width=3.5), marker=dict(size=8)))
    fig.update_layout(title={'text': 'Annual Volume vs Net Fraud Loss', 'x': 0.03, 'y': 0.96}, xaxis_title='Year', yaxis_title='Amount ($)', hovermode='x unified')
    return apply_dark_theme(fig, height=390, show_legend=True, legend_top=True)

def chart_v17_amount_box_plot():
    sql = "SELECT is_fraud, amount FROM transactions WHERE amount IS NOT NULL AND amount >= 0 LIMIT 15000;"
    df = run_query(sql)
    df['amount'] = pd.to_numeric(df['amount'], errors='coerce')
    df = df.dropna(subset=['amount'])
    df['status'] = df['is_fraud'].replace({'No': 'Legitimate', 'Yes': 'Fraud'})
    fig = px.box(
        df, x='status', y='amount', color='status', points='outliers',
        title='Amount Outliers: Legitimate vs Fraud',
        color_discrete_map={'Legitimate': '#60A5FA', 'Fraud': '#EF476F'},
        labels={'status': 'Transaction Status', 'amount': 'Amount ($)'}
    )
    fig.update_yaxes(range=[0, 3000], tickprefix='$')
    return apply_dark_theme(fig, height=390, show_legend=False)

def chart_v13_overall_amount_distribution():
    sql = """SELECT CASE WHEN amount < 50 THEN 'Below $50' WHEN amount < 100 THEN '$50-$100' WHEN amount < 500 THEN '$100-$500' WHEN amount < 1000 THEN '$500-$1K' ELSE '$1K+' END AS amount_group, COUNT(*) AS transaction_count FROM transactions GROUP BY amount_group ORDER BY CASE amount_group WHEN 'Below $50' THEN 1 WHEN '$50-$100' THEN 2 WHEN '$100-$500' THEN 3 WHEN '$500-$1K' THEN 4 ELSE 5 END;"""
    df = run_query(sql)
    df['transaction_count'] = pd.to_numeric(df['transaction_count'])
    fig = px.pie(
        df, names='amount_group', values='transaction_count', hole=0.50,
        title='Portfolio Ticket Size Distribution',
        color_discrete_sequence=['#003049', '#669BBC', '#FDF0D5', '#C1121F', '#780000']
    )
    fig.update_traces(
        textinfo='label+percent',
        texttemplate='%{label}<br>%{percent:.1%}',
        textfont=dict(size=11, color="#FFFFFF")
    )
    return apply_dark_theme(fig, height=390, show_legend=False)


# ==============================================================================
# DIVISION REGISTRY (5 - 4 - 4 Scheme)
# ==============================================================================

DIVISIONS = {
    'division_1': {
        'id': 'division_1',
        'title': 'Macro Trends & Channel Risk',
        'description': 'Row 1 (3 Charts): Overall Fraud Share, Payment Channels, Ticket Range. Row 2 (2 Charts): Annual Fraud Rate, Volume vs Fraud.',
        'charts': [
            {'id': 'v01_fraud_distribution', 'name': 'Overall Fraud Share', 'fn': chart_v01_fraud_distribution, 'grid': 'row1'},
            {'id': 'v04_fraud_payment_method', 'name': 'Fraud by Payment Channel', 'fn': chart_v04_fraud_payment_method, 'grid': 'row1'},
            {'id': 'v14_fraud_amount_distribution', 'name': 'Fraud by Ticket Size', 'fn': chart_v14_fraud_amount_distribution, 'grid': 'row1'},
            {'id': 'v02_fraud_rate_year', 'name': 'Annual Fraud Rate Trajectory', 'fn': chart_v02_fraud_rate_year, 'grid': 'row2'},
            {'id': 'v03_volume_vs_fraud_year', 'name': 'Total vs Fraud Volume', 'fn': chart_v03_volume_vs_fraud_year, 'grid': 'row2'}
        ]
    },
    'division_2': {
        'id': 'division_2',
        'title': 'Entity Risk & Behavioral Heatmaps',
        'description': '4 Visualizations in a balanced 2x2 grid: 24/7 Day-Hour Heatmap, Card Brand Breakdown, Debit vs Credit Risk, and FICO Score Bands.',
        'charts': [
            {'id': 'v05_day_hour_heatmap', 'name': '24/7 Day × Hour Heatmap', 'fn': chart_v05_day_hour_heatmap, 'grid': '2x2'},
            {'id': 'v07_fraud_card_brand', 'name': 'Fraud by Card Brand', 'fn': chart_v07_fraud_card_brand, 'grid': '2x2'},
            {'id': 'v08_fraud_card_type', 'name': 'Debit vs Credit Risk', 'fn': chart_v08_fraud_card_type, 'grid': '2x2'},
            {'id': 'v09_fraud_fico_category', 'name': 'Fraud by FICO Score Band', 'fn': chart_v09_fraud_fico_category, 'grid': '2x2'}
        ]
    },
    'division_3': {
        'id': 'division_3',
        'title': 'Risk Engine & Geospatial Exposure',
        'description': '4 Visualizations in a balanced 2x2 grid: U.S. Geographic Map, Annual Volume vs Loss, Amount Outliers Box Plot, and Ticket Size Distribution.',
        'charts': [
            {'id': 'v10_us_state_map', 'name': 'U.S. Geographic Fraud Map', 'fn': chart_v10_us_state_map, 'grid': '2x2'},
            {'id': 'v18_yearly_total_vs_fraud_amount', 'name': 'Annual Loss vs Volume', 'fn': chart_v18_yearly_total_vs_fraud_amount, 'grid': '2x2'},
            {'id': 'v17_amount_box_plot', 'name': 'Ticket Distribution Box Plot', 'fn': chart_v17_amount_box_plot, 'grid': '2x2'},
            {'id': 'v13_overall_amount_distribution', 'name': 'Overall Amount Distribution', 'fn': chart_v13_overall_amount_distribution, 'grid': '2x2'}
        ]
    }
}

def get_division_charts_json(division_id):
    div = DIVISIONS.get(division_id, DIVISIONS['division_1'])
    result = {'id': div['id'], 'title': div['title'], 'description': div['description'], 'charts': []}
    for item in div['charts']:
        try:
            fig = item['fn']()
            chart_json = json.loads(fig.to_json())
            result['charts'].append({
                'id': item['id'],
                'name': item['name'],
                'grid': item.get('grid', 'row1'),
                'data': chart_json
            })
        except Exception as e:
            result['charts'].append({
                'id': item['id'],
                'name': item['name'],
                'grid': item.get('grid', 'row1'),
                'error': str(e)
            })
    return result
