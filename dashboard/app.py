import streamlit as st
import pandas as pd
import plotly.express as px

st.set_page_config(
    page_title="Behavior Anomaly Detection",
    page_icon="🛡️",
    layout="wide"
)

st.title("🛡️ User Behavior Anomaly Detection System")

df = pd.read_csv("data/models/explained_results.csv")

st.sidebar.title("Navigation")

page = st.sidebar.radio(
    "Select Page",
    [
        "Dashboard",
        "Live Alerts",
        "Entity History",
        "Attack Analytics"
    ]
)

if page == "Dashboard":
    total_events = len(df)

    alerts = (df["prediction"] == "anomaly").sum()

    high_risk = (df["risk_score"] > 80).sum()

    entities = df["entity_id"].nunique()

    c1, c2, c3, c4 = st.columns(4)

    c1.metric("Total Events", total_events)

    c2.metric("Alerts", alerts)

    c3.metric("High Risk", high_risk)

    c4.metric("Entities", entities)

    fig = px.histogram(
        df,
        x="risk_score",
        nbins=30,
        title="Risk Score Distribution"
    )

    st.plotly_chart(fig, use_container_width=True)

    fig = px.pie(
        df[df["label"] == "anomaly"],
        names="attack_type",
        title="Attack Breakdown"
    )

    st.plotly_chart(fig, use_container_width=True)

    top_users = (
            df.groupby("entity_id")["risk_score"]
            .mean()
            .sort_values(ascending=False)
            .head(10)
            .reset_index()
        )

    fig = px.bar(
        top_users,
        x="entity_id",
        y="risk_score",
        title="Top Risky Users"
    )

    st.plotly_chart(fig, use_container_width=True)

if page == "Live Alerts":
    alerts = df[df["prediction"] == "anomaly"]

    alerts = alerts.sort_values(
        "risk_score",
        ascending=False
    )

    col1, col2, col3, col4 = st.columns(4)

    col1.metric("🚨 Active Alerts", len(alerts))

    col2.metric(
        "🔥 Critical",
        len(alerts[alerts["risk_score"] >= 90])
    )

    col3.metric(
        "👥 Affected Users",
        alerts["entity_id"].nunique()
    )

    col4.metric(
        "⚠️ Avg Risk",
        f"{alerts['risk_score'].mean():.1f}"
    )

    display = alerts[
        [
            "timestamp",
            "entity_id",
            "attack_type",
            "risk_score",
            "reasons"
        ]
    ].copy()

    display["risk_score"] = display["risk_score"].round(2)

    st.dataframe(
        display,
        use_container_width=True,
        hide_index=True
    )

if page == "Entity History":
    user = st.selectbox(

    "Select User",

    sorted(df["entity_id"].unique())

    )

    history = df[
        df["entity_id"] == user
    ]

    st.write(history.tail(20))

    fig = px.line(

    history,

    x="timestamp",

    y="risk_score",

    title="Risk Trend"

    )

    st.plotly_chart(fig)

if page == "Attack Analytics":
    attack_counts = (
        df["attack_type"]
        .value_counts()
        .rename_axis("attack_type")
        .reset_index(name="count")
    )

    fig = px.bar(
        attack_counts,
        x="attack_type",
        y="count",
        title="Attack Types"
    )

    st.plotly_chart(fig, use_container_width=True)

    heat = (
        df.groupby(
            [
                "day_of_week",
                "hour_of_day"
            ]
        ).size().reset_index(name="count")
    )

    fig = px.density_heatmap(

    heat,

    x="hour_of_day",

    y="day_of_week",

    z="count"

    )

    st.plotly_chart(fig)

    importance = pd.read_csv(
        "data/models/feature_importance.csv"
    )

    fig = px.bar(

    importance,

    x="Importance",

    y="Feature",

    orientation="h"

    )

    st.plotly_chart(fig)

    timeline = (
        df[df["prediction"]=="anomaly"]
        .groupby("timestamp")
        .size()
        .reset_index(name="alerts")
    )

    fig = px.line(
        timeline,
        x="timestamp",
        y="alerts",
        title="Alerts Over Time"
    )

    st.plotly_chart(fig, use_container_width=True)