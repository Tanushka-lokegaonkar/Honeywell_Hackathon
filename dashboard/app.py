import os
import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go

# -----------------------------------------------------------------------------
# 1. PAGE CONFIGURATION & THEMING
# -----------------------------------------------------------------------------
st.set_page_config(
    page_title="Behavior Anomaly Detection System",
    page_icon="🛡️",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Custom CSS for SOC Operations Center Styling
st.markdown("""
<style>
    /* Metric Card Styling */
    [data-testid="stMetricValue"] {
        font-size: 1.8rem !important;
        font-weight: 700;
    }
    
    /* Clean Card Containers */
    div.css-1r6slb0, div.stCard {
        border-radius: 8px;
        padding: 15px;
        background-color: #1E222A;
    }
    
    /* Alert Status Badges */
    .badge-critical {
        background-color: #FF4B4B;
        color: white;
        padding: 4px 8px;
        border-radius: 4px;
        font-weight: bold;
    }
    .badge-warning {
        background-color: #FFAA00;
        color: black;
        padding: 4px 8px;
        border-radius: 4px;
        font-weight: bold;
    }
    .badge-normal {
        background-color: #00CC96;
        color: white;
        padding: 4px 8px;
        border-radius: 4px;
    }
</style>
""", unsafe_allow_html=True)

# -----------------------------------------------------------------------------
# 2. DATA LOADING & PREPARATION
# -----------------------------------------------------------------------------
@st.cache_data(ttl=60)
def load_data():
    results_path = "data/models/explained_results.csv"
    importance_path = "data/models/feature_importance.csv"
    
    if not os.path.exists(results_path):
        st.error(f"Missing file: `{results_path}`. Run model inference first.")
        st.stop()
        
    df = pd.read_csv(results_path)
    df["timestamp"] = pd.to_datetime(df["timestamp"])
    
    # Load feature importance if present
    importance_df = pd.DataFrame()
    if os.path.exists(importance_path):
        importance_df = pd.read_csv(importance_path)
        
    return df, importance_df

df, importance_df = load_data()

# -----------------------------------------------------------------------------
# 3. SIDEBAR CONTROLS & FILTERS
# -----------------------------------------------------------------------------
st.sidebar.image("https://img.icons8.com/color/96/shield.png", width=64)
st.sidebar.title("SOC Sentinel")
st.sidebar.caption("AI-Powered Behavioral Anomaly Detection")

st.sidebar.markdown("---")

page = st.sidebar.radio(
    "Navigation",
    ["Overview Dashboard", "Live Alerts Queue", "Entity Deep Dive", "Threat Analytics"],
    index=0
)

st.sidebar.markdown("---")
st.sidebar.subheader("Global Filters")

# Sidebar Date & Entity Filters
min_date, max_date = df["timestamp"].min().date(), df["timestamp"].max().date()
date_range = st.sidebar.date_input(
    "Date Range",
    value=(min_date, max_date),
    min_value=min_date,
    max_value=max_date
)

# Apply filters
if isinstance(date_range, tuple) and len(date_range) == 2:
    start_dt, end_dt = pd.to_datetime(date_range[0]), pd.to_datetime(date_range[1]) + pd.Timedelta(days=1)
    filtered_df = df[(df["timestamp"] >= start_dt) & (df["timestamp"] < end_dt)]
else:
    filtered_df = df.copy()

# Color palette definition for charts
COLOR_PALETTE = {
    "background": "rgba(0,0,0,0)",
    "text": "#E0E0E0",
    "primary": "#6366F1",
    "danger": "#EF4444",
    "warning": "#F59E0B",
    "success": "#10B981"
}

# -----------------------------------------------------------------------------
# 4. PAGE 1: OVERVIEW DASHBOARD
# -----------------------------------------------------------------------------
if page == "Overview Dashboard":
    st.header("📊 Security Operations Overview")
    st.caption("Real-time behavioral monitoring and entity risk scoring.")
    
    # Summary Metrics Row
    total_events = len(filtered_df)
    alerts = (filtered_df["prediction"] == "anomaly").sum()
    critical_alerts = (filtered_df["risk_score"] >= 80).sum()
    unique_entities = filtered_df["entity_id"].nunique()

    m1, m2, m3, m4 = st.columns(4)
    m1.metric("Total Events Logged", f"{total_events:,}")
    m2.metric("Flagged Anomalies", f"{alerts:,}", delta=f"{(alerts/total_events*100):.1f}% rate" if total_events > 0 else "0%")
    m3.metric("High-Risk Threats (≥80)", f"{critical_alerts:,}", delta_color="inverse")
    m4.metric("Monitored Entities", f"{unique_entities:,}")
    
    st.markdown("---")
    
    col_left, col_right = st.columns([1, 1])
    
    with col_left:
        st.subheader("Risk Score Distribution")
        fig_dist = px.histogram(
            filtered_df,
            x="risk_score",
            nbins=30,
            color="prediction",
            color_discrete_map={"normal": "#3B82F6", "anomaly": "#EF4444"},
            marginal="box",
            template="plotly_dark"
        )
        fig_dist.update_layout(paper_bgcolor=COLOR_PALETTE["background"], plot_bgcolor=COLOR_PALETTE["background"])
        st.plotly_chart(fig_dist, use_container_width=True)

    with col_right:
        st.subheader("Anomalies by Threat Category")
        anomalies_df = filtered_df[filtered_df["prediction"] == "anomaly"]
        if not anomalies_df.empty:
            fig_pie = px.pie(
                anomalies_df,
                names="attack_type",
                hole=0.4,
                color_discrete_sequence=px.colors.qualitative.Bold,
                template="plotly_dark"
            )
            fig_pie.update_layout(paper_bgcolor=COLOR_PALETTE["background"])
            st.plotly_chart(fig_pie, use_container_width=True)
        else:
            st.info("No anomalies detected in selected time range.")

    st.subheader("Top High-Risk Entities")
    top_entities = (
        filtered_df.groupby("entity_id")["risk_score"]
        .agg(["mean", "max", "count"])
        .reset_index()
        .sort_values(by="mean", ascending=False)
        .head(10)
    )
    top_entities.columns = ["Entity ID", "Avg Risk Score", "Peak Risk Score", "Event Count"]
    
    fig_bar = px.bar(
        top_entities,
        x="Entity ID",
        y="Avg Risk Score",
        color="Peak Risk Score",
        color_continuous_scale="Reds",
        template="plotly_dark",
        text_auto=".1f"
    )
    fig_bar.update_layout(paper_bgcolor=COLOR_PALETTE["background"], plot_bgcolor=COLOR_PALETTE["background"])
    st.plotly_chart(fig_bar, use_container_width=True)

# -----------------------------------------------------------------------------
# 5. PAGE 2: LIVE ALERTS QUEUE
# -----------------------------------------------------------------------------
elif page == "Live Alerts Queue":
    st.header("🚨 Live Alert Investigation Queue")
    
    alerts_df = filtered_df[filtered_df["prediction"] == "anomaly"].sort_values(by="risk_score", ascending=False)
    
    a1, a2, a3, a4 = st.columns(4)
    a1.metric("Active Alerts", len(alerts_df))
    a2.metric("Critical Threshold (≥90)", len(alerts_df[alerts_df["risk_score"] >= 90]))
    a3.metric("Impacted Entities", alerts_df["entity_id"].nunique() if not alerts_df.empty else 0)
    a4.metric("Average Anomaly Score", f"{alerts_df['risk_score'].mean():.1f}" if not alerts_df.empty else "0.0")
    
    st.markdown("---")
    
    # Severity Quick Filters
    severity_filter = st.radio(
        "Filter Severity",
        ["All Alerts", "Critical (≥80)", "Moderate (<80)"],
        horizontal=True
    )
    
    if severity_filter == "Critical (≥80)":
        display_alerts = alerts_df[alerts_df["risk_score"] >= 80]
    elif severity_filter == "Moderate (<80)":
        display_alerts = alerts_df[alerts_df["risk_score"] < 80]
    else:
        display_alerts = alerts_df
        
    st.dataframe(
        display_alerts[[
            "timestamp", "entity_id", "attack_type", "risk_score", "reasons"
        ]],
        column_config={
            "timestamp": st.column_config.DatetimeColumn("Event Time", format="YYYY-MM-DD HH:mm:ss"),
            "entity_id": "Entity ID",
            "attack_type": st.column_config.TextColumn("Tactical Classification"),
            "risk_score": st.column_config.ProgressColumn("Risk Level", min_value=0, max_value=100, format="%.1f"),
            "reasons": st.column_config.TextColumn("SHAP Explanation / Drivers", width="large")
        },
        use_container_width=True,
        hide_index=True
    )

# -----------------------------------------------------------------------------
# 6. PAGE 3: ENTITY DEEP DIVE
# -----------------------------------------------------------------------------
elif page == "Entity Deep Dive":
    st.header("🔍 Entity Behavioral Deep Dive")
    
    selected_entity = st.selectbox(
        "Select Entity ID to Profile",
        sorted(filtered_df["entity_id"].unique())
    )
    
    entity_history = filtered_df[filtered_df["entity_id"] == selected_entity].sort_values("timestamp")
    
    col_hist_left, col_hist_right = st.columns([1, 2])
    
    with col_hist_left:
        st.subheader("Profile Summary")
        st.markdown(f"**Entity:** `{selected_entity}`")
        st.markdown(f"**Total Observed Sessions:** {len(entity_history)}")
        st.markdown(f"**Max Risk Score Recorded:** {entity_history['risk_score'].max():.1f}")
        st.markdown(f"**Total Flagged Anomalies:** {(entity_history['prediction'] == 'anomaly').sum()}")
        
    with col_hist_right:
        st.subheader("Temporal Risk Trend")
        fig_line = px.line(
            entity_history,
            x="timestamp",
            y="risk_score",
            markers=True,
            color="prediction",
            color_discrete_map={"normal": "#10B981", "anomaly": "#EF4444"},
            template="plotly_dark"
        )
        fig_line.add_hline(y=80, line_dash="dash", line_color="red", annotation_text="High Risk Threshold")
        fig_line.update_layout(paper_bgcolor=COLOR_PALETTE["background"], plot_bgcolor=COLOR_PALETTE["background"])
        st.plotly_chart(fig_line, use_container_width=True)

    st.subheader("Recent Activity Trail")
    st.dataframe(
        entity_history.tail(25),
        use_container_width=True,
        hide_index=True
    )

# -----------------------------------------------------------------------------
# 7. PAGE 4: THREAT ANALYTICS
# -----------------------------------------------------------------------------
elif page == "Threat Analytics":
    st.header("📈 Macro Attack Analytics & Feature Importance")
    
    t1, t2 = st.tabs(["Pattern Distribution", "Model Interpretability"])
    
    with t1:
        col_t1, col_t2 = st.columns([1, 1])
        
        with col_t1:
            st.subheader("Attack Frequency Taxonomy")
            attack_counts = (
                filtered_df[filtered_df["prediction"] == "anomaly"]["attack_type"]
                .value_counts()
                .reset_index(name="count")
            )
            fig_attack = px.bar(
                attack_counts,
                x="attack_type",
                y="count",
                color="count",
                color_continuous_scale="Purples",
                template="plotly_dark"
            )
            fig_attack.update_layout(paper_bgcolor=COLOR_PALETTE["background"], plot_bgcolor=COLOR_PALETTE["background"])
            st.plotly_chart(fig_attack, use_container_width=True)
            
        with col_t2:
            st.subheader("Temporal Anomaly Volume")
            timeline = (
                filtered_df[filtered_df["prediction"] == "anomaly"]
                .set_index("timestamp")
                .resample("1h")
                .size()
                .reset_index(name="alerts")
            )
            fig_time = px.area(
                timeline,
                x="timestamp",
                y="alerts",
                color_discrete_sequence=["#EF4444"],
                template="plotly_dark"
            )
            fig_time.update_layout(paper_bgcolor=COLOR_PALETTE["background"], plot_bgcolor=COLOR_PALETTE["background"])
            st.plotly_chart(fig_time, use_container_width=True)

    with t2:
        st.subheader("Global Feature Importance Drivers")
        if not importance_df.empty:
            importance_sorted = importance_df.sort_values(by="Importance", ascending=True)
            fig_imp = px.bar(
                importance_sorted,
                x="Importance",
                y="Feature",
                orientation="h",
                color="Importance",
                color_continuous_scale="Blues",
                template="plotly_dark"
            )
            fig_imp.update_layout(paper_bgcolor=COLOR_PALETTE["background"], plot_bgcolor=COLOR_PALETTE["background"])
            st.plotly_chart(fig_imp, use_container_width=True)
        else:
            st.info("Feature importance dataset not found in `data/models/feature_importance.csv`.")