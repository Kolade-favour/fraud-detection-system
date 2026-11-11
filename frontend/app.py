
import streamlit as st
import requests
import html
import plotly.graph_objects as go

# ==================================================
# 1. PAGE CONFIGURATION
# ==================================================

st.set_page_config(
    page_title="FraudGuard | Fraud Intelligence",
    page_icon="🛡️",
    layout="wide",
    initial_sidebar_state="expanded"
)

API_BASE_URL = "http://localhost:8007"


# ==================================================
# 2. APPLICATION STYLING
# ==================================================

st.markdown("""
<style>

/* APPLICATION BACKGROUND */

.stApp {
    background-color: #F3F6FA;
}

.main .block-container {
    padding-top: 2rem;
    padding-bottom: 2rem;
    max-width: 1500px;
}

/* SIDEBAR */

section[data-testid="stSidebar"] {
    background-color: #142338;
}

section[data-testid="stSidebar"] h1,
section[data-testid="stSidebar"] h2,
section[data-testid="stSidebar"] h3,
section[data-testid="stSidebar"] p,
section[data-testid="stSidebar"] label,
section[data-testid="stSidebar"] span {
    color: #E5EDF5 !important;
}

section[data-testid="stSidebar"] [data-testid="stCaptionContainer"] {
    color: #94A3B8 !important;
}

section[data-testid="stSidebar"] [data-testid="stAlert"] p {
    color: #FFFFFF !important;
}

/* MAIN WORKSPACE */

.main h1,
.main h2,
.main h3 {
    color: #172B4D !important;
}

.main [data-testid="stCaptionContainer"] {
    color: #64748B !important;
}

/* KPI CARDS */

.dashboard-card {
    background: #FFFFFF;
    border: 1px solid #E2E8F0;
    border-radius: 14px;
    padding: 20px;
    min-height: 125px;
    margin-bottom: 18px;
    box-sizing: border-box;
}

.card-label {
    color: #64748B;
    font-size: 12px;
    font-weight: 500;
    margin-bottom: 12px;
    letter-spacing: 0.3px;
}

.card-value {
    color: #172B4D;
    font-size: 30px;
    font-weight: 700;
    line-height: 1.2;
}

.fraud-value {
    color: #E5484D;
}

.card-description {
    color: #64748B;
    font-size: 13px;
    margin-top: 8px;
}

/* INFORMATION PANELS */

.dashboard-panel {
    background: #FFFFFF;
    border: 1px solid #E2E8F0;
    border-radius: 14px;
    padding: 20px;
    margin-bottom: 20px;
    box-sizing: border-box;
}

.panel-title {
    color: #172B4D;
    font-size: 16px;
    font-weight: 650;
    margin-bottom: 20px;
}

/* PREDICTION DISTRIBUTION */

.bar-row {
    display: flex;
    align-items: center;
    gap: 12px;
    margin-bottom: 18px;
}

.bar-track {
    flex: 1;
    height: 13px;
    background: #EDF1F7;
    border-radius: 20px;
    overflow: hidden;
}

.bar-fill {
    height: 100%;
    border-radius: 20px;
}

.legitimate-bar {
    background: #2563EB;
}

.fraud-bar {
    background: #E5484D;
}

.bar-label {
    width: 85px;
    color: #475569;
    font-size: 13px;
    flex-shrink: 0;
}

.bar-value {
    width: 65px;
    text-align: right;
    color: #172B4D;
    font-size: 13px;
    font-weight: 600;
    flex-shrink: 0;
}

/* PROCESSING STATUS */

.status-item {
    margin-bottom: 18px;
}

.status-heading {
    display: flex;
    justify-content: space-between;
    color: #475569;
    font-size: 13px;
    margin-bottom: 8px;
}

.status-heading strong {
    color: #172B4D;
}

.status-track {
    width: 100%;
    height: 10px;
    background: #EDF1F7;
    border-radius: 20px;
    overflow: hidden;
}

.status-fill {
    height: 100%;
    border-radius: 20px;
}

.processed-fill {
    background: #16A34A;
}

.pending-fill {
    background: #F59E0B;
}

.failed-fill {
    background: #E5484D;
}

/* PANEL FOOTER */

.panel-footer {
    border-top: 1px solid #E2E8F0;
    padding-top: 13px;
    margin-top: 18px;
    color: #64748B;
    font-size: 12px;
}

/* STREAMLIT HEADER */

[data-testid="stHeader"] {
    background-color: transparent;
}


/* =========================================
   FRAUD ALERTS - SUMMARY CARDS
========================================= */
.alert-summary-card {
    background: #FFFFFF;
    border: 1px solid #E2E8F0;
    border-radius: 14px;
    padding: 20px;
    min-height: 126px;
    box-sizing: border-box;
}
.alert-summary-label {
    color: #64748B;
    font-size: 12px;
    font-weight: 650;
    letter-spacing: 0.45px;
}
.alert-summary-value {
    color: #172B4D;
    font-size: 30px;
    font-weight: 700;
    line-height: 1.2;
    margin-top: 12px;
}
.alert-summary-value.warning { color: #D97706; }
.alert-summary-value.success { color: #16A34A; }
.alert-summary-description {
    color: #64748B;
    font-size: 12px;
    margin-top: 7px;
}

/* PROBABILITY DISTRIBUTION */
.probability-panel {
    background: #FFFFFF;
    border: 1px solid #E2E8F0;
    border-radius: 14px;
    padding: 23px;
    box-sizing: border-box;
}
.probability-title {
    color: #172B4D;
    font-size: 16px;
    font-weight: 650;
    margin-bottom: 23px;
}
.probability-item { margin-bottom: 20px; }
.probability-heading {
    display: flex;
    justify-content: space-between;
    align-items: center;
    gap: 12px;
    margin-bottom: 9px;
    font-size: 13px;
}
.probability-label { color: #475569; font-weight: 500; }
.probability-count { color: #172B4D; font-weight: 650; }
.probability-track {
    height: 11px;
    width: 100%;
    background: #EDF1F7;
    border-radius: 20px;
    overflow: hidden;
}
.probability-fill { height: 100%; border-radius: 20px; }
.probability-low { background: #2563EB; }
.probability-medium { background: #F59E0B; }
.probability-high { background: #E5484D; }
.probability-footer {
    border-top: 1px solid #E2E8F0;
    padding-top: 14px;
    margin-top: 8px;
    color: #64748B;
    font-size: 12px;
}

/* CUSTOM ALERT TABLE */
.alert-table-container {
    background: #FFFFFF;
    border: 1px solid #E2E8F0;
    border-radius: 14px;
    overflow: hidden;
}
.alert-table-scroll { width: 100%; overflow-x: auto; }
.alert-table {
    width: 100%;
    min-width: 850px;
    border-collapse: collapse;
    font-size: 13px;
}
.alert-table thead { background: #F8FAFC; }
.alert-table th {
    color: #64748B;
    font-size: 11px;
    font-weight: 700;
    letter-spacing: 0.35px;
    text-align: left;
    padding: 16px 15px;
    border-bottom: 1px solid #E2E8F0;
    white-space: nowrap;
}
.alert-table td {
    color: #334155;
    padding: 17px 15px;
    border-bottom: 1px solid #EDF1F7;
    white-space: nowrap;
}
.alert-table tbody tr { transition: background 0.15s ease; }
.alert-table tbody tr:hover { background: #F8FAFC; }
.alert-table tbody tr:last-child td { border-bottom: none; }
.prediction-id { color: #172B4D; font-weight: 700; }
.probability-value { color: #DC3545; font-weight: 700; }
.risk-badge, .review-badge {
    display: inline-block;
    padding: 5px 10px;
    border-radius: 20px;
    font-size: 11px;
    font-weight: 650;
}
.risk-high { background: #FEE2E2; color: #B91C1C; }
.risk-medium { background: #FEF3C7; color: #92400E; }
.risk-neutral { background: #E2E8F0; color: #475569; }
.reviewed-badge { background: #DCFCE7; color: #166534; }
.unreviewed-badge { background: #FEF3C7; color: #92400E; }
.alert-table-footer {
    padding: 13px 16px;
    background: #F8FAFC;
    border-top: 1px solid #E2E8F0;
    color: #64748B;
    font-size: 12px;
}
.alert-empty {
    padding: 36px 20px;
    text-align: center;
    color: #64748B;
    font-size: 13px;
}


/* =========================================
   TRANSACTION INVESTIGATION
========================================= */

.investigation-kpi {
    background: #FFFFFF;
    border: 1px solid #E2E8F0;
    border-radius: 14px;
    padding: 19px;
    min-height: 118px;
    box-sizing: border-box;
}

.investigation-kpi-label {
    color: #64748B;
    font-size: 11px;
    font-weight: 700;
    letter-spacing: .4px;
}

.investigation-kpi-value {
    color: #172B4D;
    font-size: 27px;
    font-weight: 750;
    margin-top: 11px;
    line-height: 1.2;
}

.investigation-kpi-value.fraud {
    color: #DC3545;
}

.investigation-kpi-note {
    color: #64748B;
    font-size: 12px;
    margin-top: 6px;
}

.investigation-panel {
    background: #FFFFFF;
    border: 1px solid #E2E8F0;
    border-radius: 14px;
    padding: 21px;
    margin-bottom: 16px;
    box-sizing: border-box;
}

.investigation-panel-title {
    color: #172B4D;
    font-size: 16px;
    font-weight: 700;
    margin-bottom: 17px;
}

.investigation-detail-row {
    display: flex;
    justify-content: space-between;
    align-items: flex-start;
    gap: 15px;
    padding: 12px 0;
    border-bottom: 1px solid #EDF1F7;
}

.investigation-detail-row:last-child {
    border-bottom: none;
}

.investigation-detail-label {
    color: #64748B;
    font-size: 12px;
}

.investigation-detail-value {
    color: #172B4D;
    font-size: 12px;
    font-weight: 600;
    text-align: right;
    overflow-wrap: anywhere;
}

.investigation-badge {
    display: inline-block;
    background: #FEE2E2;
    color: #B91C1C;
    border-radius: 20px;
    padding: 7px 12px;
    font-size: 11px;
    font-weight: 700;
}

.shap-row {
    display: grid;
    grid-template-columns: 55px minmax(80px, 1fr) 75px;
    align-items: center;
    gap: 12px;
    margin: 14px 0;
}

.shap-feature {
    color: #172B4D;
    font-size: 12px;
    font-weight: 650;
}

.shap-track {
    width: 100%;
    height: 10px;
    background: #EDF1F7;
    border-radius: 20px;
    overflow: hidden;
}

.shap-fill {
    height: 100%;
    border-radius: 20px;
}

.shap-positive {
    background: #E5484D;
}

.shap-negative {
    background: #2563EB;
}

.shap-number {
    color: #475569;
    font-size: 11px;
    text-align: right;
    font-weight: 600;
}

.shap-legend {
    display: flex;
    flex-wrap: wrap;
    gap: 18px;
    margin-top: 22px;
    padding-top: 15px;
    border-top: 1px solid #E2E8F0;
    color: #64748B;
    font-size: 11px;
}

.legend-dot {
    display: inline-block;
    width: 8px;
    height: 8px;
    border-radius: 50%;
    margin-right: 5px;
}

.history-item {
    padding: 14px 0;
    border-bottom: 1px solid #EDF1F7;
}

.history-item:last-child {
    border-bottom: none;
}

.history-outcome {
    color: #172B4D;
    font-size: 13px;
    font-weight: 700;
    margin-bottom: 5px;
}

.history-meta {
    color: #64748B;
    font-size: 12px;
    margin-top: 4px;
    overflow-wrap: anywhere;
}


</style>
""", unsafe_allow_html=True)


# ==================================================
# 3. SIDEBAR NAVIGATION
# ==================================================


def open_investigation(prediction_id):
    st.session_state["selected_prediction_id"] = prediction_id
    st.session_state["selected_page"] = "Investigation"


with st.sidebar:

    st.markdown("# 🛡️ FraudGuard")

    st.caption("FRAUD OPERATIONS & INTELLIGENCE")

    st.divider()

    st.markdown("### WORKSPACE")

    selected_page = st.radio(
        "Navigation",
        [
            "Overview",
            "Fraud Alerts",
            "Investigation",
            "Monitoring & Insights",
            "Analyst Decisions"
        ],
        label_visibility="collapsed",
        key="selected_page"
    )

    st.divider()

    # Check FastAPI connection

    try:

        health_response = requests.get(
            f"{API_BASE_URL}/health",
            timeout=3
        )

        if health_response.status_code == 200:
            st.success("API Connected")
        else:
            st.error("API Unavailable")

    except requests.RequestException:

        st.error("API Disconnected")

    st.caption("FraudGuard v1.0")


# ==================================================
# 4. MAIN WORKSPACE HEADER
# ==================================================

st.markdown(
    f"##### WORKSPACE / {selected_page.upper()}"
)

st.title(selected_page)

st.caption(
    "Fraud detection, transaction monitoring and investigation."
)

st.divider()


# ==================================================
# 5. PAGE ROUTING
# ==================================================


# ==================================================
# OVERVIEW PAGE
# ==================================================

if selected_page == "Overview":

    try:

        # ------------------------------------------
        # FETCH DASHBOARD DATA
        # ------------------------------------------

        response = requests.get(
            f"{API_BASE_URL}/dashboard/summary",
            timeout=10
        )

        response.raise_for_status()

        api_data = response.json()

        summary = api_data["dashboard_summary"]

        # ------------------------------------------
        # EXTRACT METRICS
        # ------------------------------------------

        raw_transactions = summary["total_raw_transactions"]

        simulated_transactions = summary[
            "total_simulated_transactions"
        ]

        total_predictions = summary["total_predictions"]

        fraud_predictions = summary["fraud_predictions"]

        legitimate_predictions = summary[
            "legitimate_predictions"
        ]

        pending_transactions = summary["pending_transactions"]

        failed_transactions = summary["failed_transactions"]

        # ------------------------------------------
        # CALCULATE PROCESSING COUNTS
        # ------------------------------------------

        processed_transactions = (
            simulated_transactions
            - pending_transactions
            - failed_transactions
        )

        # ------------------------------------------
        # CALCULATE PERCENTAGES
        # ------------------------------------------

        fraud_rate = (
            fraud_predictions / total_predictions * 100
            if total_predictions else 0
        )

        legitimate_rate = (
            legitimate_predictions / total_predictions * 100
            if total_predictions else 0
        )

        processed_rate = (
            processed_transactions / simulated_transactions * 100
            if simulated_transactions else 0
        )

        pending_rate = (
            pending_transactions / simulated_transactions * 100
            if simulated_transactions else 0
        )

        failed_rate = (
            failed_transactions / simulated_transactions * 100
            if simulated_transactions else 0
        )

        # ------------------------------------------
        # SYSTEM OVERVIEW
        # ------------------------------------------

        st.subheader("System Overview")

        st.caption(
            "Transaction volume and fraud detection summary."
        )

        # ------------------------------------------
        # KPI CARDS
        # ------------------------------------------

        col1, col2 = st.columns(2, gap="medium")

        with col1:

            st.html(f"""
                <div class="dashboard-card">

                    <div class="card-label">
                        TOTAL TRANSACTIONS
                    </div>

                    <div class="card-value">
                        {raw_transactions:,}
                    </div>

                    <div class="card-description">
                        Dataset records
                    </div>

                </div>
            """)

        with col2:

            st.html(f"""
                <div class="dashboard-card">

                    <div class="card-label">
                        FRAUD PREDICTIONS
                    </div>

                    <div class="card-value fraud-value">
                        {fraud_predictions:,}
                    </div>

                    <div class="card-description">
                        Model classifications
                    </div>

                </div>
            """)

        # ------------------------------------------
        # PREDICTION DISTRIBUTION
        # ------------------------------------------

        st.markdown("### Prediction Distribution")

        st.html(f"""
            <div class="dashboard-panel">

                <div class="panel-title">
                    Prediction distribution
                </div>

                <div class="bar-row">

                    <div class="bar-track">

                        <div
                            class="bar-fill legitimate-bar"
                            style="width: {legitimate_rate:.4f}%;">
                        </div>

                    </div>

                    <div class="bar-label">
                        Legitimate
                    </div>

                    <div class="bar-value">
                        {legitimate_predictions:,}
                    </div>

                </div>

                <div class="bar-row">

                    <div class="bar-track">

                        <div
                            class="bar-fill fraud-bar"
                            style="width: {fraud_rate:.4f}%;">
                        </div>

                    </div>

                    <div class="bar-label">
                        Fraud
                    </div>

                    <div class="bar-value">
                        {fraud_predictions:,}
                    </div>

                </div>

                <div class="panel-footer">
                    Fraud predictions account for
                    {fraud_rate:.2f}% of all model predictions.
                </div>

            </div>
        """)

        # ------------------------------------------
        # TRANSACTION PROCESSING
        # ------------------------------------------

        st.markdown("### Transaction Processing")

        st.html(f"""
            <div class="dashboard-panel">

                <div class="panel-title">
                    Simulation processing status
                </div>

                <!-- PROCESSED -->

                <div class="status-item">

                    <div class="status-heading">

                        <span>Processed</span>

                        <strong>
                            {processed_transactions:,}
                        </strong>

                    </div>

                    <div class="status-track">

                        <div
                            class="status-fill processed-fill"
                            style="width: {processed_rate:.4f}%;">
                        </div>

                    </div>

                </div>

                <!-- PENDING -->

                <div class="status-item">

                    <div class="status-heading">

                        <span>Pending</span>

                        <strong>
                            {pending_transactions:,}
                        </strong>

                    </div>

                    <div class="status-track">

                        <div
                            class="status-fill pending-fill"
                            style="width: {pending_rate:.4f}%;">
                        </div>

                    </div>

                </div>

                <!-- FAILED -->

                <div class="status-item">

                    <div class="status-heading">

                        <span>Failed</span>

                        <strong>
                            {failed_transactions:,}
                        </strong>

                    </div>

                    <div class="status-track">

                        <div
                            class="status-fill failed-fill"
                            style="width: {failed_rate:.4f}%;">
                        </div>

                    </div>

                </div>

                <div class="panel-footer">
                    {simulated_transactions:,}
                    simulated transactions in total.
                </div>

            </div>
        """)

    # ----------------------------------------------
    # ERROR HANDLING
    # ----------------------------------------------

    except requests.RequestException as error:

        st.error(
            f"Unable to retrieve dashboard data: {error}"
        )

    except (KeyError, ValueError, TypeError) as error:

        st.error(
            f"Unexpected dashboard API response: {error}"
        )



# ==================================================
# FRAUD ALERTS PAGE
# ==================================================

elif selected_page == "Fraud Alerts":

    st.subheader("Fraud Alert Centre")
    st.caption(
        "Review, filter and investigate transactions flagged by the model."
    )

    try:
        # Fetch alerts from FastAPI
        response = requests.get(
            f"{API_BASE_URL}/alerts",
            params={"limit": 200, "offset": 0},
            timeout=10
        )
        response.raise_for_status()

        api_data = response.json()
        alerts = api_data.get("alerts", [])

        # Derive review status from the latest analyst outcome
        for alert in alerts:
            alert["review_status"] = (
                "Reviewed"
                if alert.get("analyst_outcome") is not None
                else "Unreviewed"
            )

        total_alerts = len(alerts)
        reviewed_alerts = sum(
            alert["review_status"] == "Reviewed"
            for alert in alerts
        )
        unreviewed_alerts = total_alerts - reviewed_alerts

        # ------------------------------------------
        # SUMMARY CARDS
        # ------------------------------------------

        st.markdown("### Alert Summary")

        metric1, metric2, metric3 = st.columns(3, gap="medium")

        summary_cards = [
            (
                metric1,
                "TOTAL ALERTS",
                total_alerts,
                "Fraud predictions returned by the API",
                ""
            ),
            (
                metric2,
                "UNREVIEWED",
                unreviewed_alerts,
                "Awaiting analyst review",
                "warning"
            ),
            (
                metric3,
                "REVIEWED",
                reviewed_alerts,
                "Have an analyst decision recorded",
                "success"
            )
        ]

        for column, label, value, description, value_class in summary_cards:
            with column:
                st.html(f"""
                    <div class="alert-summary-card">
                        <div class="alert-summary-label">{label}</div>
                        <div class="alert-summary-value {value_class}">
                            {value:,}
                        </div>
                        <div class="alert-summary-description">
                            {description}
                        </div>
                    </div>
                """)

        st.markdown("### Fraud Probability Distribution")

        # Values are model fraud probabilities between 0 and 1.
        probability_ranges = [
            ("0–50%", 0.0, 0.50, "probability-low"),
            ("50–75%", 0.50, 0.75, "probability-medium"),
            ("75–100%", 0.75, 1.0000001, "probability-high")
        ]

        distribution_html = """
            <div class="probability-panel">
                <div class="probability-title">
                    Fraud probability overview
                </div>
        """

        for label, lower, upper, color_class in probability_ranges:
            count = sum(
                lower <= float(alert.get("fraud_probability", 0)) < upper
                for alert in alerts
            )
            share = (count / total_alerts * 100) if total_alerts else 0

            distribution_html += f"""
                <div class="probability-item">
                    <div class="probability-heading">
                        <span class="probability-label">{label}</span>
                        <span class="probability-count">
                            {count:,} alerts ({share:.1f}%)
                        </span>
                    </div>
                    <div class="probability-track">
                        <div
                            class="probability-fill {color_class}"
                            style="width: {share:.2f}%;">
                        </div>
                    </div>
                </div>
            """

        distribution_html += f"""
                <div class="probability-footer">
                    Distribution of the {total_alerts:,} fraud predictions
                    currently returned by the API.
                </div>
            </div>
        """

        st.html(distribution_html)

        st.markdown("### Alert Queue")
        st.caption(
            "Search and filter model predictions before opening an investigation."
        )

        # ------------------------------------------
        # SEARCH AND FILTER CONTROLS
        # ------------------------------------------

        filter_col1, filter_col2 = st.columns([2, 1], gap="medium")

        with filter_col1:
            search_id = st.text_input(
                "Search prediction ID",
                placeholder="Enter a prediction ID...",
                key="alert_search"
            )

        with filter_col2:
            status_filter = st.selectbox(
                "Review status",
                ["All statuses", "Unreviewed", "Reviewed"],
                key="alert_status_filter"
            )

        filtered_alerts = alerts.copy()

        if search_id.strip():
            filtered_alerts = [
                alert for alert in filtered_alerts
                if search_id.strip() in str(alert.get("prediction_id", ""))
            ]

        if status_filter != "All statuses":
            filtered_alerts = [
                alert for alert in filtered_alerts
                if alert["review_status"] == status_filter
            ]

        # ------------------------------------------
        # PAGINATION
        # ------------------------------------------

        page_size = 10
        total_filtered = len(filtered_alerts)
        total_pages = max(
            1,
            (total_filtered + page_size - 1) // page_size
        )

        page_col1, page_col2 = st.columns([3, 1])

        with page_col2:
            current_page = st.selectbox(
                "Page",
                options=list(range(1, total_pages + 1)),
                index=0,
                key="alert_page_selector"
            )

        start_index = (current_page - 1) * page_size
        page_alerts = filtered_alerts[start_index:start_index + page_size]

        # ------------------------------------------
        # CUSTOM HTML TABLE
        # ------------------------------------------

        if page_alerts:
            table_rows = ""

            for alert in page_alerts:
                prediction_id = html.escape(
                    str(alert.get("prediction_id", "N/A"))
                )

                amount = float(alert.get("amount") or 0)
                fraud_probability = (
                    float(alert.get("fraud_probability") or 0) * 100
                )

                risk_level = str(
                    alert.get("risk_level") or "Unassigned"
                )
                risk_lower = risk_level.lower()

                if risk_lower in ("high", "critical"):
                    risk_class = "risk-high"
                elif risk_lower == "medium":
                    risk_class = "risk-medium"
                else:
                    risk_class = "risk-neutral"

                review_status = alert["review_status"]
                review_class = (
                    "reviewed-badge"
                    if review_status == "Reviewed"
                    else "unreviewed-badge"
                )

                prediction_time = html.escape(
                    str(alert.get("prediction_timestamp") or "Unavailable")
                )

                table_rows += f"""
                    <tr>
                        <td>
                            <span class="prediction-id">#{prediction_id}</span>
                        </td>
                        <td>{amount:,.2f}</td>
                        <td>
                            <span class="probability-value">
                                {fraud_probability:.2f}%
                            </span>
                        </td>
                        <td>
                            <span class="risk-badge {risk_class}">
                                {html.escape(risk_level.title())}
                            </span>
                        </td>
                        <td>{prediction_time}</td>
                        <td>
                            <span class="review-badge {review_class}">
                                {review_status}
                            </span>
                        </td>
                    </tr>
                """

            table_html = f"""
                <div class="alert-table-container">
                    <div class="alert-table-scroll">
                        <table class="alert-table">
                            <thead>
                                <tr>
                                    <th>PREDICTION ID</th>
                                    <th>AMOUNT</th>
                                    <th>FRAUD PROBABILITY</th>
                                    <th>RISK LEVEL</th>
                                    <th>PREDICTION TIME</th>
                                    <th>REVIEW STATUS</th>
                                </tr>
                            </thead>
                            <tbody>
                                {table_rows}
                            </tbody>
                        </table>
                    </div>
                    <div class="alert-table-footer">
                        Showing {len(page_alerts)} of {total_filtered:,}
                        matching alerts.
                    </div>
                </div>
            """

            st.html(table_html)

            # --------------------------------------
            # OPEN INVESTIGATION
            # --------------------------------------

            st.markdown("### Investigate an Alert")

            prediction_ids = [
                alert["prediction_id"]
                for alert in page_alerts
            ]

            selected_prediction = st.selectbox(
                "Select prediction",
                prediction_ids,
                format_func=lambda value: f"Prediction #{value}",
                key="selected_alert_id"
            )

            st.button(
                "Open Investigation",
                type="primary",
                on_click=open_investigation,
                args=(selected_prediction,),
                key="open_investigation_button"
            )

        else:
            st.html("""
                <div class="alert-table-container">
                    <div class="alert-empty">
                        No fraud alerts match the current search and filters.
                    </div>
                </div>
            """)

    except requests.RequestException as error:
        st.error(f"Unable to retrieve fraud alerts: {error}")

    except (KeyError, ValueError, TypeError) as error:
        st.error(f"Unexpected fraud alert response: {error}")




# ==================================================
# TRANSACTION INVESTIGATION PAGE
# ==================================================

elif selected_page == "Investigation":

    import json
    import html

    st.subheader("Transaction Investigation")

    st.caption(
        "Examine model predictions, understand feature contributions "
        "and record analyst findings."
    )

    # ----------------------------------------------
    # PREDICTION ID INPUT
    # ----------------------------------------------

    remembered_id = st.session_state.get(
        "selected_prediction_id", ""
    )

    default_id = str(remembered_id) if remembered_id else ""

    search_col, action_col = st.columns([3, 1])

    with search_col:
        prediction_id_input = st.text_input(
            "Prediction ID",
            value=default_id,
            placeholder="Enter a prediction ID, e.g. 646",
            key="investigation_prediction_id"
        )

    with action_col:
        st.write("")
        st.write("")

        load_investigation = st.button(
            "Load Investigation",
            type="primary",
            use_container_width=True
        )

    should_load = load_investigation or bool(default_id)

    if should_load and prediction_id_input.strip():

        try:

            prediction_id = int(prediction_id_input.strip())

            # --------------------------------------
            # FETCH INVESTIGATION
            # --------------------------------------

            response = requests.get(
                f"{API_BASE_URL}/alerts/{prediction_id}",
                timeout=15
            )

            response.raise_for_status()

            payload = response.json()

            investigation = payload.get(
                "investigation",
                payload.get("data", payload)
            )

            transaction = investigation.get("transaction", {})
            prediction = investigation.get("prediction", {})

            analyst_history = investigation.get(
                "analyst_history", []
            ) or []

            if not prediction and "fraud_probability" in investigation:
                prediction = investigation

            # --------------------------------------
            # PARSE JSON FIELDS
            # --------------------------------------

            top_features = prediction.get("top_features")
            shap_data = prediction.get("shap_values")

            # API returns these database JSON columns as strings.
            if isinstance(top_features, str):
                top_features = json.loads(top_features)

            if isinstance(shap_data, str):
                shap_data = json.loads(shap_data)

            if not isinstance(top_features, list):
                top_features = []

            if not isinstance(shap_data, dict):
                shap_data = {}

            # Extract all SHAP contributions.
            shap_features = shap_data.get("shap_values", [])

            if not isinstance(shap_features, list):
                shap_features = []

            # Fallback: derive top features from all SHAP values.
            if not top_features and shap_features:

                top_features = sorted(
                    shap_features,
                    key=lambda item: abs(float(item.get("shap_value", 0))),
                    reverse=True
                )[:10]

            # --------------------------------------
            # NORMALIZE SHAP DATA
            # --------------------------------------

            normalized_features = []

            for item in shap_features:

                if not isinstance(item, dict):
                    continue

                try:
                    normalized_features.append({
                        "feature": str(item.get("feature", "Unknown")),
                        "feature_value": float(
                            item.get("feature_value", 0)
                        ),
                        "shap_value": float(
                            item.get("shap_value", 0)
                        )
                    })

                except (TypeError, ValueError):
                    continue

            normalized_features.sort(
                key=lambda item: abs(item["shap_value"]),
                reverse=True
            )

            # --------------------------------------
            # EXTRACT PREDICTION INFORMATION
            # --------------------------------------

            fraud_probability = float(
                prediction.get("fraud_probability") or 0
            )

            legitimate_probability = float(
                prediction.get("legitimate_probability")
                if prediction.get("legitimate_probability") is not None
                else 1 - fraud_probability
            )

            threshold = float(
                prediction.get("decision_threshold_used") or 0.30
            )

            amount = float(
                transaction.get(
                    "amount",
                    transaction.get("Amount", 0)
                ) or 0
            )

            transaction_time = transaction.get(
                "transaction_time",
                transaction.get("Time", "Unavailable")
            )

            predicted_class = prediction.get(
                "predicted_class", "Unavailable"
            )

            model_version = prediction.get(
                "model_version", "Unavailable"
            )

            risk_level = prediction.get(
                "risk_level", "Unassigned"
            )

            prediction_timestamp = prediction.get(
                "prediction_timestamp", "Unavailable"
            )

            # --------------------------------------
            # INVESTIGATION HEADER
            # --------------------------------------

            st.divider()

            header_left, header_right = st.columns([3, 1])

            with header_left:

                st.markdown(f"### Prediction #{prediction_id}")

                st.caption(
                    f"Prediction timestamp: {prediction_timestamp}"
                )

            with header_right:

                st.html(f"""
                    <span class="investigation-badge">
                        {html.escape(str(risk_level).upper())} RISK
                    </span>
                """)

            # --------------------------------------
            # PREDICTION SUMMARY
            # --------------------------------------

            st.markdown("### Prediction Summary")

            kpi1, kpi2, kpi3 = st.columns(3, gap="medium")

            kpis = [
                (
                    kpi1,
                    "FRAUD PROBABILITY",
                    f"{fraud_probability * 100:.2f}%",
                    "fraud",
                    "Model-estimated fraud probability"
                ),
                (
                    kpi2,
                    "TRANSACTION AMOUNT",
                    f"{amount:,.2f}",
                    "",
                    "Amount recorded in the source dataset"
                ),
                (
                    kpi3,
                    "DECISION THRESHOLD",
                    f"{threshold * 100:.0f}%",
                    "",
                    "Threshold used for classification"
                )
            ]

            for column, label, value, value_class, note in kpis:

                with column:

                    st.html(f"""
                        <div class="investigation-kpi">

                            <div class="investigation-kpi-label">
                                {label}
                            </div>

                            <div class="investigation-kpi-value {value_class}">
                                {value}
                            </div>

                            <div class="investigation-kpi-note">
                                {note}
                            </div>

                        </div>
                    """)

            # --------------------------------------
            # TRANSACTION INFORMATION
            # --------------------------------------

            st.markdown("### Transaction Information")

            left_panel, right_panel = st.columns(2, gap="medium")

            transaction_fields = [
                (
                    "Simulation ID",
                    transaction.get("simulation_id", "Unavailable")
                ),
                (
                    "Source record ID",
                    transaction.get("source_record_id", "Unavailable")
                ),
                (
                    "Simulation time",
                    transaction.get("replayed_at", "Unavailable")
                ),
                (
                    "Processing status",
                    transaction.get("processing_status", "Unavailable")
                ),
                (
                    "Dataset transaction time",
                    transaction_time
                ),
                (
                    "Amount",
                    f"{amount:,.2f}"
                )
            ]

            model_fields = [
                ("Prediction ID", prediction_id),
                ("Predicted class", predicted_class),
                ("Fraud probability", f"{fraud_probability:.6f}"),
                ("Legitimate probability", f"{legitimate_probability:.6f}"),
                ("Decision threshold", f"{threshold:.2f}"),
                ("Model version", model_version),
                ("Prediction time", prediction_timestamp)
            ]

            with left_panel:

                transaction_html = """
                    <div class="investigation-panel">
                        <div class="investigation-panel-title">
                            Source transaction
                        </div>
                """

                for label, value in transaction_fields:

                    transaction_html += f"""
                        <div class="investigation-detail-row">

                            <span class="investigation-detail-label">
                                {html.escape(str(label))}
                            </span>

                            <span class="investigation-detail-value">
                                {html.escape(str(value))}
                            </span>

                        </div>
                    """

                transaction_html += "</div>"

                st.html(transaction_html)

            with right_panel:

                model_html = """
                    <div class="investigation-panel">
                        <div class="investigation-panel-title">
                            Model assessment
                        </div>
                """

                for label, value in model_fields:

                    model_html += f"""
                        <div class="investigation-detail-row">

                            <span class="investigation-detail-label">
                                {html.escape(str(label))}
                            </span>

                            <span class="investigation-detail-value">
                                {html.escape(str(value))}
                            </span>

                        </div>
                    """

                model_html += "</div>"

                st.html(model_html)

            # --------------------------------------
            # SHAP MODEL EXPLANATION
            # --------------------------------------

            st.markdown("### Model Explanation")

            st.caption(
                "SHAP explains how individual features contribute "
                "to the model's output. Positive values push towards "
                "fraud; negative values push away from fraud."
            )

            if normalized_features:

                # ----------------------------------
                # 1. SHAP FEATURE IMPORTANCE
                # ----------------------------------

                st.markdown("#### SHAP Feature Importance")

                st.caption(
                    "Top 10 features ranked by absolute SHAP contribution."
                )

                importance_features = normalized_features[:10]

                max_abs_shap = max(
                    abs(item["shap_value"])
                    for item in importance_features
                ) or 1

                shap_html = """
                    <div class="investigation-panel">
                        <div class="investigation-panel-title">
                            Top feature contributions
                        </div>
                """

                for item in importance_features:

                    value = item["shap_value"]

                    width = abs(value) / max_abs_shap * 100

                    direction_class = (
                        "shap-positive"
                        if value > 0
                        else "shap-negative"
                    )

                    shap_html += f"""
                        <div class="shap-row">

                            <div class="shap-feature">
                                {html.escape(item["feature"])}
                            </div>

                            <div class="shap-track">
                                <div
                                    class="shap-fill {direction_class}"
                                    style="width: {width:.2f}%">
                                </div>
                            </div>

                            <div class="shap-number">
                                {value:+.4f}
                            </div>

                        </div>
                    """

                shap_html += """
                    <div class="shap-legend">

                        <span>
                            <i class="legend-dot"
                               style="background:#E5484D"></i>
                            Pushes towards fraud
                        </span>

                        <span>
                            <i class="legend-dot"
                               style="background:#2563EB"></i>
                            Pushes away from fraud
                        </span>

                    </div>
                    </div>
                """

                st.html(shap_html)

                # ----------------------------------
                # 2. SHAP WATERFALL PLOT
                # ----------------------------------

                st.markdown("#### SHAP Waterfall Plot")

                st.caption(
                    "Shows how the baseline model output changes "
                    "as each feature contribution is added. "
                    "Features are ordered by absolute contribution."
                )

                base_value = shap_data.get("base_value")

                if base_value is not None:

                    try:

                        base_value = float(base_value)

                        # Order features by absolute contribution.
                        waterfall_features = sorted(
                            normalized_features,
                            key=lambda item: abs(item["shap_value"]),
                            reverse=True
                        )

                        # Calculate cumulative model output.
                        cumulative = base_value

                        waterfall_rows = []

                        for item in waterfall_features:

                            start_value = cumulative

                            cumulative += item["shap_value"]

                            waterfall_rows.append({
                                "feature": item["feature"],
                                "contribution": item["shap_value"],
                                "start": start_value,
                                "end": cumulative
                            })

                        final_output = cumulative

                        # ----------------------------------
                        # CREATE PLOTLY WATERFALL
                        # ----------------------------------

                        # waterfall_rows already contains the
                        # ordered feature contributions and
                        # their cumulative start/end values.

                        feature_names = [
                            row["feature"]
                            for row in waterfall_rows
                        ]

                        contributions = [
                            row["contribution"]
                            for row in waterfall_rows
                        ]

                        final_output = (
                            base_value + sum(contributions)
                        )

                        x_labels = (
                            ["Baseline"]
                            + feature_names
                            + ["Final output"]
                        )

                        y_values = (
                            [base_value]
                            + contributions
                            + [final_output]
                        )

                        measures = (
                            ["absolute"]
                            + ["relative"] * len(contributions)
                            + ["total"]
                        )

                        fig = go.Figure(
                            go.Waterfall(
                                orientation="v",
                                measure=measures,
                                x=x_labels,
                                y=y_values,

                                text=[
                                    f"{base_value:+.4f}"
                                ] + [
                                    f"{value:+.4f}"
                                    for value in contributions
                                ] + [
                                    f"{final_output:+.4f}"
                                ],

                                textposition="outside",

                                connector={
                                    "line": {
                                        "color": "#94A3B8",
                                        "width": 1
                                    }
                                },

                                increasing={
                                    "marker": {
                                        "color": "#E5484D"
                                    }
                                },

                                decreasing={
                                    "marker": {
                                        "color": "#2563EB"
                                    }
                                },

                                totals={
                                    "marker": {
                                        "color": "#172B4D"
                                    }
                                },

                                hovertemplate=(
                                    "<b>%{x}</b><br>"
                                    "Value: %{y:.5f}"
                                    "<extra></extra>"
                                )
                            )
                        )

                        fig.update_layout(
                            title={
                                "text": "SHAP Waterfall Plot",
                                "x": 0.02
                            },

                            height=650,

                            margin={
                                "l": 65,
                                "r": 35,
                                "t": 70,
                                "b": 150
                            },

                            paper_bgcolor="#FFFFFF",
                            plot_bgcolor="#FFFFFF",

                            font={
                                "family": "Arial",
                                "color": "#172B4D",
                                "size": 11
                            },

                            showlegend=False,

                            xaxis={
                                "tickangle": -45,
                                "showgrid": False
                            },

                            yaxis={
                                "title": "Model output (raw log-odds)",
                                "gridcolor": "#EDF1F7",
                                "zeroline": True,
                                "zerolinecolor": "#94A3B8"
                            }
                        )

                        st.plotly_chart(
                            fig,
                            use_container_width=True,
                            config={
                                "displayModeBar": False
                            }
                        )

                        st.caption(
                            f"Baseline: {base_value:.4f} | "
                            f"Final raw model output: {final_output:.4f} | "
                            f"Fraud probability: "
                            f"{fraud_probability * 100:.4f}%"
                        )


                    except (TypeError, ValueError) as error:

                        st.warning(
                            f"Unable to construct the SHAP waterfall plot: {error}"
                        )

                else:

                    st.info(
                        "SHAP baseline value is unavailable. "
                        "The waterfall plot cannot be constructed."
                    )

                # ----------------------------------
                # 3. FEATURE CONTRIBUTION DETAILS
                # ----------------------------------

                with st.expander(
                    "View all 30 feature values and SHAP contributions"
                ):

                    feature_rows = [
                        {
                            "Feature": item["feature"],
                            "Feature value": item["feature_value"],
                            "SHAP contribution": item["shap_value"]
                        }
                        for item in normalized_features
                    ]

                    st.dataframe(
                        feature_rows,
                        use_container_width=True,
                        hide_index=True
                    )

                st.info(
                    "SHAP values are expressed in the model's raw "
                    "output (log-odds) scale, not as percentage-point "
                    "changes in fraud probability."
                )

            else:

                st.info(
                    "SHAP contribution data is not available for this prediction."
                )

            # --------------------------------------
            # AI EXPLANATION PLACEHOLDER
            # --------------------------------------

            explanation = (
                prediction.get("explanation")
                or investigation.get("explanation")
            )

            st.markdown("### Analyst Explanation")

            if explanation:

                st.markdown(explanation)

            else:

                st.caption(
                    "An AI-generated narrative is not available yet. "
                    "The SHAP evidence above is the current explanation source."
                )

            # --------------------------------------
            # ANALYST REVIEW
            # --------------------------------------

            st.markdown("### Analyst Review")

            st.caption(
                "Record an outcome. Submitting creates an auditable decision record."
            )

            with st.form(key=f"decision_form_{prediction_id}"):

                outcome_label = st.selectbox(
                    "Investigation outcome",
                    [
                        "Confirmed fraud",
                        "Legitimate transaction",
                        "Needs further review"
                    ]
                )

                analyst_name = st.text_input(
                    "Reviewer",
                    placeholder="Enter analyst name or team"
                )

                analyst_notes = st.text_area(
                    "Investigation notes",
                    placeholder="Document the evidence supporting your decision...",
                    height=110
                )

                submit_decision = st.form_submit_button(
                    "Submit Analyst Decision",
                    type="primary"
                )

            if submit_decision:

                outcome_mapping = {
                    "Confirmed fraud": "confirmed_fraud",
                    "Legitimate transaction": "legitimate_transaction",
                    "Needs further review": "needs_further_review"
                }

                if not analyst_name.strip():

                    st.warning(
                        "Enter the reviewer before submitting the decision."
                    )

                elif not analyst_notes.strip():

                    st.warning(
                        "Add investigation notes before submitting the decision."
                    )

                else:

                    decision_payload = {
                        "prediction_id": prediction_id,
                        "analyst_outcome": outcome_mapping[outcome_label],
                        "notes": analyst_notes.strip(),
                        "reviewer": analyst_name.strip()
                    }

                    try:

                        decision_response = requests.post(
                            f"{API_BASE_URL}/decisions",
                            json=decision_payload,
                            timeout=15
                        )

                        decision_response.raise_for_status()

                        st.success(
                            "Analyst decision recorded successfully."
                        )

                        st.rerun()

                    except requests.RequestException as error:

                        st.error(
                            f"Unable to submit analyst decision: {error}"
                        )

            # --------------------------------------
            # DECISION HISTORY
            # --------------------------------------

            st.markdown("### Decision History")

            if analyst_history:

                history_html = """
                    <div class="investigation-panel">
                """

                for decision in analyst_history:

                    outcome = html.escape(
                        str(
                            decision.get(
                                "analyst_outcome", "Decision"
                            )
                        )
                    )

                    reviewer = html.escape(
                        str(
                            decision.get(
                                "reviewer", "Unspecified reviewer"
                            )
                        )
                    )

                    decision_time = html.escape(
                        str(
                            decision.get(
                                "decision_timestamp", "Time unavailable"
                            )
                        )
                    )

                    notes = html.escape(
                        str(
                            decision.get(
                                "notes", "No notes recorded"
                            )
                        )
                    )

                    history_html += f"""
                        <div class="history-item">

                            <div class="history-outcome">
                                {outcome.replace("_", " ").title()}
                            </div>

                            <div class="history-meta">
                                {reviewer} · {decision_time}
                            </div>

                            <div class="history-meta">
                                {notes}
                            </div>

                        </div>
                    """

                history_html += "</div>"

                st.html(history_html)

            else:

                st.html("""
                    <div class="investigation-panel">
                        <div class="alert-empty">
                            No analyst decisions have been recorded
                            for this prediction.
                        </div>
                    </div>
                """)

            # --------------------------------------
            # ALL AVAILABLE TRANSACTION FEATURES
            # --------------------------------------

            with st.expander(
                "View all available transaction features"
            ):

                feature_values = transaction.get("features", {})

                if not isinstance(feature_values, dict):
                    feature_values = {}

                feature_values = {
                    **feature_values,
                    "Time": transaction_time,
                    "Amount": amount
                }

                if feature_values:

                    st.json(feature_values)

                else:

                    st.caption(
                        "Transaction feature values were not included "
                        "in the API response."
                    )

        # ------------------------------------------
        # ERROR HANDLING
        # ------------------------------------------

        except ValueError:

            st.error(
                "Prediction ID must be a valid integer."
            )

        except requests.HTTPError as error:

            if (
                error.response is not None
                and error.response.status_code == 404
            ):

                st.error(
                    f"Prediction #{prediction_id_input} was not found."
                )

            else:

                st.error(
                    f"Investigation request failed: {error}"
                )

        except requests.RequestException as error:

            st.error(
                f"Unable to retrieve investigation data: {error}"
            )

        except (KeyError, TypeError, AttributeError, json.JSONDecodeError) as error:

            st.error(
                f"Unexpected investigation API response: {error}"
            )

    else:

        st.html("""
            <div class="investigation-panel">

                <div class="investigation-panel-title">
                    Start an investigation
                </div>

                <div style="color:#64748B;font-size:13px;line-height:1.7;">

                    Enter a prediction ID above, or open an alert
                    from the Fraud Alerts page.

                    Transaction details, model assessment,
                    SHAP evidence and analyst history
                    will appear here.

                </div>

            </div>
        """)



# ==================================================
# MONITORING & INSIGHTS PAGE
# ==================================================

elif selected_page == "Monitoring & Insights":

    st.subheader("System Monitoring")

    st.caption(
        "Monitor transaction processing, prediction coverage "
        "and model classification outcomes."
    )

    try:

        # ------------------------------------------
        # FETCH MONITORING DATA
        # ------------------------------------------

        response = requests.get(
            f"{API_BASE_URL}/dashboard/summary",
            timeout=10
        )

        response.raise_for_status()

        api_data = response.json()

        summary = api_data["dashboard_summary"]

        # ------------------------------------------
        # EXTRACT SYSTEM METRICS
        # ------------------------------------------

        raw_transactions = int(
            summary["total_raw_transactions"]
        )

        simulated_transactions = int(
            summary["total_simulated_transactions"]
        )

        total_predictions = int(
            summary["total_predictions"]
        )

        fraud_predictions = int(
            summary["fraud_predictions"]
        )

        legitimate_predictions = int(
            summary["legitimate_predictions"]
        )

        pending_transactions = int(
            summary["pending_transactions"]
        )

        failed_transactions = int(
            summary["failed_transactions"]
        )

        processed_transactions = max(
            simulated_transactions
            - pending_transactions
            - failed_transactions,
            0
        )

        # ------------------------------------------
        # CALCULATE MONITORING METRICS
        # ------------------------------------------

        prediction_coverage = (
            total_predictions / simulated_transactions * 100
            if simulated_transactions else 0
        )

        fraud_rate = (
            fraud_predictions / total_predictions * 100
            if total_predictions else 0
        )

        legitimate_rate = (
            legitimate_predictions / total_predictions * 100
            if total_predictions else 0
        )

        processed_rate = (
            processed_transactions / simulated_transactions * 100
            if simulated_transactions else 0
        )

        pending_rate = (
            pending_transactions / simulated_transactions * 100
            if simulated_transactions else 0
        )

        failed_rate = (
            failed_transactions / simulated_transactions * 100
            if simulated_transactions else 0
        )

        unpredicted_transactions = max(
            simulated_transactions - total_predictions,
            0
        )

        # ------------------------------------------
        # REFRESH CONTROL
        # ------------------------------------------

        refresh_col, status_col = st.columns([1, 3])

        with refresh_col:

            if st.button(
                "Refresh Monitoring Data",
                type="primary",
                use_container_width=True
            ):
                st.rerun()

        with status_col:

            st.caption(
                "Metrics are retrieved from the live FastAPI dashboard endpoint."
            )

        st.divider()

        # ------------------------------------------
        # SYSTEM HEALTH SUMMARY
        # ------------------------------------------

        st.markdown("### System Health")

        st.caption(
            "Current cumulative transaction processing statistics."
        )

        metric_columns = st.columns(4, gap="medium")

        monitoring_metrics = [
            (
                "SIMULATED TRANSACTIONS",
                simulated_transactions,
                "Registered simulation events",
                ""
            ),
            (
                "TOTAL PREDICTIONS",
                total_predictions,
                "Model inference results",
                ""
            ),
            (
                "PENDING TRANSACTIONS",
                pending_transactions,
                "Awaiting processing",
                "pending"
            ),
            (
                "FAILED TRANSACTIONS",
                failed_transactions,
                "Processing failures",
                "fraud"
            )
        ]

        for column, metric in zip(
            metric_columns,
            monitoring_metrics
        ):

            label, value, description, value_class = metric

            with column:

                st.html(f"""
                    <div class="dashboard-card">

                        <div class="card-label">
                            {label}
                        </div>

                        <div class="card-value {value_class}">
                            {value:,}
                        </div>

                        <div class="card-description">
                            {description}
                        </div>

                    </div>
                """)

        st.divider()

        # ------------------------------------------
        # TRANSACTION PROCESSING MONITOR
        # ------------------------------------------

        st.markdown("### Transaction Processing Monitor")

        st.caption(
            "Breakdown of simulated transactions by processing status."
        )

        processing_html = f"""
            <div class="dashboard-panel">

                <div class="panel-title">
                    Processing status distribution
                </div>

                <div class="status-item">

                    <div class="status-heading">
                        <span>Processed</span>
                        <strong>
                            {processed_transactions:,}
                            ({processed_rate:.2f}%)
                        </strong>
                    </div>

                    <div class="status-track">
                        <div
                            class="status-fill processed-fill"
                            style="width: {min(processed_rate, 100):.2f}%;">
                        </div>
                    </div>

                </div>

                <div class="status-item">

                    <div class="status-heading">
                        <span>Pending</span>
                        <strong>
                            {pending_transactions:,}
                            ({pending_rate:.2f}%)
                        </strong>
                    </div>

                    <div class="status-track">
                        <div
                            class="status-fill pending-fill"
                            style="width: {min(pending_rate, 100):.2f}%;">
                        </div>
                    </div>

                </div>

                <div class="status-item">

                    <div class="status-heading">
                        <span>Failed</span>
                        <strong>
                            {failed_transactions:,}
                            ({failed_rate:.2f}%)
                        </strong>
                    </div>

                    <div class="status-track">
                        <div
                            class="status-fill failed-fill"
                            style="width: {min(failed_rate, 100):.2f}%;">
                        </div>
                    </div>

                </div>

                <div class="panel-footer">
                    Total simulated transactions:
                    {simulated_transactions:,}
                </div>

            </div>
        """

        st.html(processing_html)

        # ------------------------------------------
        # PREDICTION COVERAGE
        # ------------------------------------------

        st.markdown("### Prediction Coverage")

        coverage_html = f"""
            <div class="dashboard-panel">

                <div class="panel-title">
                    Simulation-to-inference coverage
                </div>

                <div class="status-item">

                    <div class="status-heading">
                        <span>Transactions with predictions</span>
                        <strong>
                            {total_predictions:,}
                            ({min(prediction_coverage, 100):.2f}%)
                        </strong>
                    </div>

                    <div class="status-track">
                        <div
                            class="status-fill processed-fill"
                            style="width: {min(prediction_coverage, 100):.2f}%;">
                        </div>
                    </div>

                </div>

                <div class="status-item">

                    <div class="status-heading">
                        <span>Transactions without predictions</span>
                        <strong>
                            {unpredicted_transactions:,}
                        </strong>
                    </div>

                    <div class="status-track">
                        <div
                            class="status-fill pending-fill"
                            style="width: {min(
                                unpredicted_transactions / simulated_transactions * 100
                                if simulated_transactions else 0,
                                100
                            ):.2f}%;">
                        </div>
                    </div>

                </div>

                <div class="panel-footer">
                    Prediction coverage is calculated using total predictions
                    divided by total simulated transactions.
                </div>

            </div>
        """

        st.html(coverage_html)

        st.divider()

        # ------------------------------------------
        # MODEL CLASSIFICATION INSIGHTS
        # ------------------------------------------

        st.markdown("### Model Classification Insights")

        st.caption(
            "Distribution of transactions classified by the fraud detection model."
        )

        fraud_col, legitimate_col = st.columns(
            2,
            gap="medium"
        )

        with fraud_col:

            st.html(f"""
                <div class="dashboard-card">

                    <div class="card-label">
                        FRAUD PREDICTIONS
                    </div>

                    <div class="card-value fraud-value">
                        {fraud_predictions:,}
                    </div>

                    <div class="card-description">
                        {fraud_rate:.4f}% of all predictions
                    </div>

                </div>
            """)

        with legitimate_col:

            st.html(f"""
                <div class="dashboard-card">

                    <div class="card-label">
                        LEGITIMATE PREDICTIONS
                    </div>

                    <div class="card-value">
                        {legitimate_predictions:,}
                    </div>

                    <div class="card-description">
                        {legitimate_rate:.4f}% of all predictions
                    </div>

                </div>
            """)

        # ------------------------------------------
        # CLASS DISTRIBUTION
        # ------------------------------------------

        classification_html = f"""
            <div class="dashboard-panel">

                <div class="panel-title">
                    Prediction class distribution
                </div>

                <div class="bar-row">

                    <div class="bar-track">
                        <div
                            class="bar-fill fraud-bar"
                            style="width: {fraud_rate:.4f}%;">
                        </div>
                    </div>

                    <div class="bar-label">
                        Fraud
                    </div>

                    <div class="bar-value">
                        {fraud_predictions:,}
                    </div>

                </div>

                <div class="bar-row">

                    <div class="bar-track">
                        <div
                            class="bar-fill legitimate-bar"
                            style="width: {legitimate_rate:.4f}%;">
                        </div>
                    </div>

                    <div class="bar-label">
                        Legitimate
                    </div>

                    <div class="bar-value">
                        {legitimate_predictions:,}
                    </div>

                </div>

                <div class="panel-footer">
                    Total model predictions: {total_predictions:,}
                </div>

            </div>
        """

        st.html(classification_html)

        # ------------------------------------------
        # AUTOMATED MONITORING OBSERVATIONS
        # ------------------------------------------

        st.markdown("### Operational Observations")

        if failed_transactions > 0:

            st.warning(
                f"{failed_transactions:,} simulated transactions "
                "have failed processing. These require operational attention."
            )

        else:

            st.success(
                "No failed simulated transactions are currently reported."
            )

        if pending_transactions > 0:

            st.warning(
                f"{pending_transactions:,} transactions are still pending."
            )

        else:

            st.success(
                "No pending simulated transactions are currently reported."
            )

        if prediction_coverage < 100 and simulated_transactions > 0:

            st.info(
                f"{unpredicted_transactions:,} simulated transactions "
                "do not yet have corresponding prediction records."
            )

        elif simulated_transactions > 0:

            st.success(
                "Every simulated transaction currently has a prediction record."
            )

        if total_predictions > 0:

            st.caption(
                f"The model has classified {total_predictions:,} transactions. "
                f"Fraud classifications account for {fraud_rate:.4f}% "
                "of those predictions."
            )

        # ------------------------------------------
        # MONITORING SCOPE
        # ------------------------------------------

        with st.expander("Monitoring metrics and limitations"):

            st.markdown("""
            **Metrics currently available**

            - Raw dataset transaction count.
            - Simulated transaction count.
            - Total model predictions.
            - Fraud and legitimate prediction counts.
            - Pending and failed transaction counts.
            - Prediction coverage.

            **Not yet implemented**

            - Data drift monitoring.
            - Model performance monitoring using verified labels.
            - Inference latency and throughput measurements.
            - Historical time-series monitoring.
            - Global SHAP feature importance across predictions.

            These require additional backend instrumentation,
            historical records or dedicated monitoring endpoints.
            """)

    # ----------------------------------------------
    # ERROR HANDLING
    # ----------------------------------------------

    except requests.RequestException as error:

        st.error(
            f"Unable to retrieve monitoring data: {error}"
        )

    except (KeyError, ValueError, TypeError) as error:

        st.error(
            f"Unexpected monitoring API response: {error}"
        )



# ==================================================
# ANALYST DECISIONS PAGE
# ==================================================

elif selected_page == "Analyst Decisions":

    st.subheader("Analyst Decisions")

    st.caption(
        "Review recorded investigation outcomes and monitor "
        "the status of fraud alerts."
    )

    try:

        # ------------------------------------------
        # FETCH FRAUD ALERTS AND LATEST DECISIONS
        # ------------------------------------------

        response = requests.get(
            f"{API_BASE_URL}/alerts",
            params={
                "limit": 100,
                "offset": 0
            },
            timeout=10
        )

        response.raise_for_status()

        api_data = response.json()

        # Support common API response structures
        if isinstance(api_data, list):

            alerts = api_data

        elif isinstance(api_data, dict):

            alerts = (
                api_data.get("alerts")
                or api_data.get("data")
                or api_data.get("results")
                or api_data.get("items")
                or []
            )

        else:

            alerts = []

        if not isinstance(alerts, list):

            raise ValueError(
                "The alerts endpoint did not return a list of records."
            )

        # ------------------------------------------
        # NORMALIZE DECISION INFORMATION
        # ------------------------------------------

        decision_records = []

        for alert in alerts:

            if not isinstance(alert, dict):
                continue

            prediction_id = alert.get("prediction_id")

            if prediction_id is None:
                continue

            outcome = (
                alert.get("analyst_outcome")
                or alert.get("latest_analyst_outcome")
                or alert.get("decision_outcome")
            )

            if outcome:

                outcome_label = str(outcome).replace("_", " ").title()

                review_status = "Reviewed"

            else:

                outcome_label = "Awaiting review"

                review_status = "Pending"

            probability = alert.get("fraud_probability")

            try:

                probability = (
                    float(probability)
                    if probability is not None
                    else None
                )

            except (TypeError, ValueError):

                probability = None

            decision_records.append({

                "prediction_id": prediction_id,

                "fraud_probability": probability,

                "outcome": outcome_label,

                "review_status": review_status,

                "prediction_timestamp": (
                    alert.get("prediction_timestamp")
                    or alert.get("created_at")
                ),

                "reviewer": (
                    alert.get("reviewer")
                    or alert.get("latest_reviewer")
                ),

                "decision_timestamp": (
                    alert.get("decision_timestamp")
                    or alert.get("latest_decision_timestamp")
                )

            })

        # ------------------------------------------
        # CALCULATE DECISION METRICS
        # ------------------------------------------

        total_alerts = len(decision_records)

        reviewed_records = [
            record
            for record in decision_records
            if record["review_status"] == "Reviewed"
        ]

        pending_records = [
            record
            for record in decision_records
            if record["review_status"] == "Pending"
        ]

        reviewed_count = len(reviewed_records)

        pending_count = len(pending_records)

        review_rate = (
            reviewed_count / total_alerts * 100
            if total_alerts else 0
        )

        # ------------------------------------------
        # REFRESH CONTROL
        # ------------------------------------------

        if st.button(
            "Refresh Decisions",
            type="primary"
        ):

            st.rerun()

        st.divider()

        # ------------------------------------------
        # DECISION KPI CARDS
        # ------------------------------------------

        st.markdown("### Review Overview")

        metric_columns = st.columns(4, gap="medium")

        decision_metrics = [

            (
                "TOTAL FRAUD ALERTS",
                total_alerts,
                "Alerts returned by the API",
                ""
            ),

            (
                "REVIEWED ALERTS",
                reviewed_count,
                "Alerts with recorded outcomes",
                "processed"
            ),

            (
                "PENDING REVIEW",
                pending_count,
                "Alerts without recorded outcomes",
                "pending"
            ),

            (
                "REVIEW COMPLETION",
                f"{review_rate:.1f}%",
                "Percentage of alerts reviewed",
                ""
            )

        ]

        for column, metric in zip(
            metric_columns,
            decision_metrics
        ):

            label, value, description, value_class = metric

            with column:

                st.html(f"""
                    <div class="dashboard-card">

                        <div class="card-label">
                            {label}
                        </div>

                        <div class="card-value {value_class}">
                            {value}
                        </div>

                        <div class="card-description">
                            {description}
                        </div>

                    </div>
                """)

        st.divider()

        # ------------------------------------------
        # FILTERS
        # ------------------------------------------

        st.markdown("### Decision Records")

        search_col, filter_col = st.columns(
            [2, 1]
        )

        with search_col:

            search_term = st.text_input(
                "Search by prediction ID",
                placeholder="Enter prediction ID..."
            )

        with filter_col:

            status_filter = st.selectbox(
                "Review status",
                [
                    "All",
                    "Reviewed",
                    "Pending"
                ]
            )

        filtered_records = decision_records.copy()

        if search_term.strip():

            filtered_records = [

                record
                for record in filtered_records

                if search_term.strip()
                in str(record["prediction_id"])

            ]

        if status_filter != "All":

            filtered_records = [

                record
                for record in filtered_records

                if record["review_status"] == status_filter

            ]

        # ------------------------------------------
        # CUSTOM DECISION TABLE
        # ------------------------------------------

        if filtered_records:

            table_rows = ""

            for record in filtered_records:

                prediction_id = html.escape(
                    str(record["prediction_id"])
                )

                outcome = html.escape(
                    str(record["outcome"])
                )

                probability = record["fraud_probability"]

                probability_text = (
                    f"{probability * 100:.4f}%"
                    if probability is not None
                    else "Unavailable"
                )

                prediction_time = html.escape(
                    str(record["prediction_timestamp"] or "Unavailable")
                )

                reviewer = html.escape(
                    str(record["reviewer"] or "Unavailable")
                )

                decision_time = html.escape(
                    str(record["decision_timestamp"] or "Unavailable")
                )

                if record["review_status"] == "Reviewed":

                    status_html = """
                        <span class="decision-status reviewed">
                            Reviewed
                        </span>
                    """

                else:

                    status_html = """
                        <span class="decision-status pending">
                            Pending
                        </span>
                    """

                table_rows += f"""
                    <tr>

                        <td>#{prediction_id}</td>

                        <td>{probability_text}</td>

                        <td>{status_html}</td>

                        <td>{outcome}</td>

                        <td>{reviewer}</td>

                        <td>{prediction_time}</td>

                    </tr>
                """

            table_html = f"""
                <div class="dashboard-panel">

                    <div class="panel-title">
                        Analyst review records
                    </div>

                    <div style="
                        width:100%;
                        overflow-x:auto;
                    ">

                        <table style="
                            width:100%;
                            border-collapse:collapse;
                            font-size:12px;
                            color:#172B4D;
                            min-width:850px;
                        ">

                            <thead>

                                <tr style="
                                    background:#F8FAFC;
                                    text-align:left;
                                ">

                                    <th style="padding:13px;">Prediction ID</th>
                                    <th style="padding:13px;">Fraud probability</th>
                                    <th style="padding:13px;">Status</th>
                                    <th style="padding:13px;">Latest outcome</th>
                                    <th style="padding:13px;">Reviewer</th>
                                    <th style="padding:13px;">Prediction time</th>

                                </tr>

                            </thead>

                            <tbody>

                                {table_rows}

                            </tbody>

                        </table>

                    </div>

                    <div class="panel-footer">
                        Showing {len(filtered_records):,} of
                        {total_alerts:,} available fraud alerts.
                    </div>

                </div>
            """

            st.html(table_html)

        else:

            st.info(
                "No records match the selected search and filter."
            )

        # ------------------------------------------
        # DECISION OUTCOME BREAKDOWN
        # ------------------------------------------

        st.markdown("### Recorded Outcome Breakdown")

        outcome_counts = {}

        for record in reviewed_records:

            outcome = record["outcome"]

            outcome_counts[outcome] = (
                outcome_counts.get(outcome, 0) + 1
            )

        if outcome_counts:

            outcome_columns = st.columns(
                max(len(outcome_counts), 1)
            )

            for column, (outcome, count) in zip(
                outcome_columns,
                outcome_counts.items()
            ):

                with column:

                    st.html(f"""
                        <div class="dashboard-card">

                            <div class="card-label">
                                {html.escape(outcome.upper())}
                            </div>

                            <div class="card-value">
                                {count:,}
                            </div>

                            <div class="card-description">
                                Recorded analyst outcomes
                            </div>

                        </div>
                    """)

        else:

            st.info(
                "No analyst outcomes have been recorded for "
                "the currently retrieved alerts."
            )

        # ------------------------------------------
        # WORKFLOW GUIDANCE
        # ------------------------------------------

        st.markdown("### Review Workflow")

        st.html("""
            <div class="dashboard-panel">

                <div class="panel-title">
                    How to review a fraud alert
                </div>

                <div class="status-item">
                    <strong>1. Identify the prediction</strong>
                    <div class="card-description">
                        Find the prediction ID in the records above.
                    </div>
                </div>

                <div class="status-item">
                    <strong>2. Investigate the transaction</strong>
                    <div class="card-description">
                        Open Transaction Investigation and load the
                        corresponding prediction ID.
                    </div>
                </div>

                <div class="status-item">
                    <strong>3. Examine model evidence</strong>
                    <div class="card-description">
                        Review fraud probability, transaction features
                        and SHAP contributions.
                    </div>
                </div>

                <div class="status-item">
                    <strong>4. Record an analyst outcome</strong>
                    <div class="card-description">
                        Submit the investigation outcome, reviewer
                        and supporting notes.
                    </div>
                </div>

            </div>
        """)

        with st.expander("About these decision records"):

            st.markdown("""
            - Reviewed means the alert has a recorded analyst outcome.
            - Pending means no analyst outcome is currently available.
            - The table displays the latest outcome exposed by the
              alerts API.
            - Multiple submissions for one prediction remain separate
              audit records in the backend.
            - This page does not display the complete historical
              decision audit log.
            """)

    # ----------------------------------------------
    # ERROR HANDLING
    # ----------------------------------------------

    except requests.RequestException as error:

        st.error(
            f"Unable to retrieve analyst decisions: {error}"
        )

    except (KeyError, ValueError, TypeError) as error:

        st.error(
            f"Unexpected analyst decisions API response: {error}"
        )

