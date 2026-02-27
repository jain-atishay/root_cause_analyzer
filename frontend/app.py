import streamlit as st
import requests
import os

BACKEND_URL = os.getenv("BACKEND_URL", "http://localhost:8000")

st.set_page_config(page_title="Root Cause Analyzer", layout="wide", initial_sidebar_state="collapsed")

# Custom CSS: dark, minimal, professional
st.markdown("""
<style>
    /* Base */
    @import url('https://fonts.googleapis.com/css2?family=IBM+Plex+Sans:wght@400;500;600&family=IBM+Plex+Mono:wght@400;500&display=swap');
    
    .stApp {
        background: #0d1117;
    }
    .main .block-container {
        padding: 2rem 3rem;
        max-width: 1200px;
    }
    
    /* Typography */
    h1 {
        font-family: 'IBM Plex Sans', sans-serif !important;
        font-weight: 600 !important;
        font-size: 1.5rem !important;
        color: #e6edf3 !important;
        letter-spacing: -0.02em;
    }
    h2, h3 {
        font-family: 'IBM Plex Sans', sans-serif !important;
        font-weight: 500 !important;
        color: #8b949e !important;
        font-size: 0.9rem !important;
        text-transform: uppercase;
        letter-spacing: 0.05em;
        margin-top: 1.5rem !important;
    }
    p, span, label {
        font-family: 'IBM Plex Sans', sans-serif !important;
        color: #8b949e !important;
    }
    
    /* Tabs */
    .stTabs [data-baseweb="tab-list"] {
        gap: 0.5rem;
    }
    .stTabs [data-baseweb="tab"] {
        font-family: 'IBM Plex Sans', sans-serif !important;
        font-weight: 500 !important;
        color: #8b949e !important;
    }
    .stTabs [aria-selected="true"] {
        color: #58a6ff !important;
    }
    
    /* Inputs - dark theme */
    .stTextArea textarea, .stTextInput input {
        background: #161b22 !important;
        border: 1px solid #30363d !important;
        color: #e6edf3 !important;
    }
    .stSelectbox > div {
        background: #161b22 !important;
    }
    
    /* Buttons */
    .stButton > button {
        font-family: 'IBM Plex Sans', sans-serif !important;
        font-weight: 500 !important;
        background: #21262d !important;
        border: 1px solid #30363d !important;
        color: #e6edf3 !important;
        border-radius: 6px;
    }
    .stButton > button:hover {
        background: #30363d !important;
        border-color: #8b949e !important;
    }
    
    /* Cards for log results */
    .log-card {
        background: #161b22;
        border: 1px solid #30363d;
        border-radius: 6px;
        padding: 1rem 1.25rem;
        margin-bottom: 0.5rem;
        font-family: 'IBM Plex Mono', monospace;
        font-size: 0.85rem;
    }
    .log-message {
        color: #e6edf3;
        word-break: break-word;
    }
    .log-meta {
        color: #8b949e;
        font-size: 0.8rem;
        margin-top: 0.5rem;
    }
    .log-distance {
        color: #58a6ff;
        font-size: 0.75rem;
    }
    .level-ERROR { color: #f85149; }
    .level-WARN { color: #d29922; }
    .level-INFO { color: #58a6ff; }
    
    /* Summary box */
    .summary-box {
        background: #161b22;
        border-left: 3px solid #58a6ff;
        padding: 1rem 1.25rem;
        margin: 1rem 0;
        border-radius: 0 6px 6px 0;
    }
    
    /* Cluster header */
    .cluster-header {
        background: #21262d;
        padding: 0.75rem 1rem;
        border-radius: 6px;
        margin: 1rem 0 0.5rem 0;
        font-weight: 500;
        color: #e6edf3;
    }
    
    /* Footer */
    footer {
        margin-top: 2rem;
        padding-top: 1rem;
        border-top: 1px solid #21262d;
        font-size: 0.75rem;
        color: #6e7681;
    }
</style>
""", unsafe_allow_html=True)

# Header
st.title("Log Root Cause Analyzer")
st.caption("Vector search · structured filtering · deployment correlation")

tab1, tab2, tab3, tab4 = st.tabs(["Analyze", "Clusters", "Correlation", "Ingest"])

# ------------ ANALYZE TAB ------------
with tab1:
    query = st.text_area(
        "Log message",
        height=80,
        placeholder="Paste an error or log line to find similar past incidents",
        key="analyze_query",
    )

    col1, col2, col3 = st.columns([2, 2, 1])
    with col1:
        level_filter = st.selectbox("Level", ["", "ERROR", "WARN", "INFO"], key="analyze_level")
    with col2:
        service_filter = st.text_input("Service", placeholder="e.g. api-gateway", key="analyze_service")
    with col3:
        top_k = st.number_input("Matches", min_value=1, max_value=20, value=5, key="analyze_top_k")

    if st.button("Analyze", key="analyze_btn"):
        if not query.strip():
            st.error("Enter a log message.")
        else:
            with st.spinner(""):
                try:
                    response = requests.post(
                        f"{BACKEND_URL}/analyze",
                        json={
                            "log_message": query,
                            "top_k": top_k,
                            "level": level_filter or None,
                            "service": service_filter or None,
                        },
                        timeout=60,
                    )
                    response.raise_for_status()
                    data = response.json()

                    if data.get("summary"):
                        st.markdown("**Summary**")
                        st.markdown(
                            f'<div class="summary-box">{data["summary"]}</div>',
                            unsafe_allow_html=True,
                        )

                    st.markdown("**Similar logs**")
                    for idx, log in enumerate(data.get("root_causes", []), start=1):
                        level = log.get("level", "")
                        msg = log.get("message", "")
                        trunc = msg[:80] + "…" if len(msg) > 80 else msg
                        level_class = f"level-{level}" if level in ("ERROR", "WARN", "INFO") else ""
                        html = f"""
                        <div class="log-card">
                            <div class="log-message">{msg}</div>
                            <div class="log-meta">
                                <span class="{level_class}">{level or "—"}</span> · {log.get('service') or "—"} · {str(log.get('timestamp', ''))[:19]}
                            </div>
                            <div class="log-distance">distance: {round(log.get('distance', 0), 4)}</div>
                        </div>
                        """
                        st.markdown(html, unsafe_allow_html=True)

                except Exception as e:
                    st.error(str(e))

# ------------ CLUSTERS TAB ------------
with tab2:
    st.caption("Group logs by embedding similarity to surface failure patterns")

    col1, col2 = st.columns(2)
    with col1:
        n_clusters = st.slider("Clusters", 2, 10, 5, key="cluster_n")
    with col2:
        cluster_level = st.selectbox("Level filter", ["", "ERROR", "WARN", "INFO"], key="cluster_level")

    if st.button("Run clustering", key="cluster_btn"):
        with st.spinner(""):
            try:
                response = requests.post(
                    f"{BACKEND_URL}/cluster",
                    json={"n_clusters": n_clusters, "level": cluster_level or None},
                    timeout=60,
                )
                response.raise_for_status()
                data = response.json()
                clusters = data.get("clusters", [])

                for c in clusters:
                    st.markdown(
                        f'<div class="cluster-header">Cluster {c["cluster_id"]} · {c["size"]} logs</div>',
                        unsafe_allow_html=True,
                    )
                    for log in c.get("logs", []):
                        level = log.get("level", "")
                        level_class = f"level-{level}" if level in ("ERROR", "WARN", "INFO") else ""
                        st.markdown(
                            f'<div class="log-card"><span class="{level_class}">{level or "—"}</span> · <strong>{log.get("service")}</strong> — {log.get("message", "")}</div>',
                            unsafe_allow_html=True,
                        )

            except Exception as e:
                st.error(str(e))

# ------------ DEPLOYMENTS TAB ------------
with tab3:
    st.caption("Logs occurring after deployments for a given service")

    service = st.text_input("Service", placeholder="e.g. api-gateway", key="correlate_service")

    if st.button("Correlate", key="corr_btn"):
        if not service.strip():
            st.error("Enter a service name.")
        else:
            with st.spinner(""):
                try:
                    response = requests.get(
                        f"{BACKEND_URL}/correlate", params={"service": service}, timeout=30
                    )
                    response.raise_for_status()
                    data = response.json()
                    logs = data.get("deployment_logs", [])

                    if not logs:
                        st.info(f"No post-deployment logs for {service}.")
                    else:
                        for log in logs:
                            level = log.get("level", "")
                            level_class = f"level-{level}" if level in ("ERROR", "WARN", "INFO") else ""
                            st.markdown(
                                f'<div class="log-card">'
                                f'<div class="log-message">{log.get("message", "")}</div>'
                                f'<div class="log-meta"><span class="{level_class}">{level}</span> · {log.get("timestamp", "")} · v{log.get("version", "")} @ {str(log.get("deployed_at", ""))[:19]}</div>'
                                f'</div>',
                                unsafe_allow_html=True,
                            )

                except Exception as e:
                    st.error(str(e))

# ------------ INGEST TAB ------------
with tab4:
    st.caption("Load sample data into the database")

    col1, col2 = st.columns(2)
    with col1:
        if st.button("Ingest logs", key="ingest_logs"):
            try:
                r = requests.post(
                    f"{BACKEND_URL}/ingest",
                    json={"file_path": "sample_logs.jsonl"},
                    timeout=120,
                )
                r.raise_for_status()
                st.success("Logs ingested.")
            except Exception as e:
                st.error(str(e))
    with col2:
        if st.button("Ingest deployments", key="ingest_deployments"):
            try:
                r = requests.post(
                    f"{BACKEND_URL}/ingest/deployments",
                    json={"file_path": "sample_deployments.json"},
                    timeout=30,
                )
                r.raise_for_status()
                st.success("Deployments ingested.")
            except Exception as e:
                st.error(str(e))

st.markdown(
    '<footer>Python · FastAPI · pgvector · PostgreSQL · Streamlit</footer>',
    unsafe_allow_html=True,
)
