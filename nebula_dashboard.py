import streamlit as st
import pandas as pd
import json
import plotly.express as px
from datetime import datetime
from config import CONFIG

st.set_page_config(page_title="Project Nebula Dashboard", layout="wide")

def load_events():
    events = []
    try:
        event_log_path = CONFIG["event_log_path"]
        with open(event_log_path, "r") as f:
            for line in f:
                events.append(json.loads(line))
    except FileNotFoundError:
        return pd.DataFrame()
    return pd.DataFrame(events)

st.title("🌌 Project Nebula: Cerebral Cortex Monitor")
st.sidebar.header("System Controls")
st.sidebar.markdown("---")

df = load_events()

if df.empty:
    st.warning("No events recorded yet. Process a signal to see data.")
else:
    # Convert timestamp to datetime object
    df['timestamp'] = pd.to_datetime(df['timestamp'])
    
    # Main Metrics
    last_event = df.iloc[-1]
    col1, col2, col3, col4 = st.columns(4)
    
    # Extract data (now flat in the new schema)
    # If old data exists, attempt recovery, but prioritize new ones
    if 'final_score' not in df.columns:
        df['final_score'] = df['physics'].apply(lambda x: x.get('final_score', 0) if isinstance(x, dict) else 0)
    if 'state' not in df.columns:
        df['state'] = df['physics'].apply(lambda x: x.get('resulting_state', 'Unknown') if isinstance(x, dict) else 'Unknown')
    if 'alignment_score' not in df.columns:
        df['alignment_score'] = df['physics'].apply(lambda x: x.get('raw_alignment', 0) if isinstance(x, dict) else 0)
    if 'dominant_attractor' not in df.columns:
        df['dominant_attractor'] = df['physics'].apply(lambda x: x.get('dominant_attractor', 'Unknown') if isinstance(x, dict) else 'Unknown')

    with col1:
        st.metric("Current State", df['state'].iloc[-1])
    with col2:
        st.metric("Dominant Identity", df['dominant_attractor'].iloc[-1].title())
    with col3:
        st.metric("Total Signals", len(df))
    with col4:
        st.metric("Avg Alignment", f"{round(df['alignment_score'].mean() * 100, 1)}%")

    # Gráfico de Evolución Temporal
    c1, c2 = st.columns(2)
    with c1:
        st.subheader("Trajectory Alignment Over Time")
        fig_trend = px.line(df, x='timestamp', y='final_score', 
                            title="Final Score Flow",
                            markers=True,
                            color_discrete_sequence=["#BC13FE"])
        fig_trend.add_hline(y=0.5, line_dash="dash", line_color="green", annotation_text="Friction Threshold")
        fig_trend.add_hline(y=-0.5, line_dash="dash", line_color="red", annotation_text="Black Hole Threshold")
        st.plotly_chart(fig_trend, use_container_width=True)

    with c2:
        st.subheader("Attractor Competition")
        # Prepare data for attractor area chart
        alignments_list = []
        for idx, row in df.iterrows():
            # Attempt to get from physics_params first (new schema)
            params = row.get('physics_params', {})
            alignments = {}
            if isinstance(params, dict):
                alignments = params.get('all_alignments', {})
            
            # If not there, try in 'physics' (previous transition schema)
            if not alignments:
                physics = row.get('physics', {})
                if isinstance(physics, dict):
                    alignments = physics.get('all_alignments', {})

            if alignments:
                alignments['timestamp'] = row['timestamp']
                alignments_list.append(alignments)
        
        if alignments_list:
            alignments_df = pd.DataFrame(alignments_list)
            melted_alignments = alignments_df.melt(id_vars=['timestamp'], var_name='Attractor', value_name='Alignment')
            
            fig_attractors = px.area(melted_alignments, x='timestamp', y='Alignment', color='Attractor',
                                     title="Identity Gravitational Pull",
                                     color_discrete_sequence=px.colors.qualitative.Vivid)
            st.plotly_chart(fig_attractors, use_container_width=True)
        else:
            st.info("No multi-alignment data available yet.")

    # Distribución de Estados y Categorías
    c1, c2 = st.columns(2)
    with c1:
        st.subheader("State Distribution")
        fig_pie = px.pie(df, names='state', color='state',
                         color_discrete_map={"Friction": "#BC13FE", "Degenerate Matter": "#FFA500", "Black Hole": "#333333"})
        st.plotly_chart(fig_pie)
    
    with c2:
        st.subheader("Impact by Category")
        fig_bar = px.bar(df, x='category', y='final_score', color='state')
        st.plotly_chart(fig_bar)

    # Análisis de Frecuencia y Duración
    st.divider()
    st.subheader("Frequency & Duration Analysis")
    col_f1, col_f2 = st.columns(2)
    with col_f1:
        fig_freq = px.histogram(df, x='category', color='state', title="Signal Frequency by Category", barmode='group')
        st.plotly_chart(fig_freq, use_container_width=True)
    with col_f2:
        # Asegurarnos de que duration existe y es numérica
        if 'duration' in df.columns:
            fig_dur = px.box(df, x='state', y='duration', color='state', title="Duration Distribution by State")
            st.plotly_chart(fig_dur, use_container_width=True)

    # Benchmark Comparison (Sprint 3 Phase B)
    st.divider()
    st.subheader("🤖 Semantic Engine Benchmark (TF-IDF vs MiniLM)")
    
    comp_data = []
    for idx, row in df.iterrows():
        params = row.get('physics_params', {})
        if isinstance(params, dict) and 'multi_backend_comparison' in params:
            comp = params['multi_backend_comparison']
            action = row.get('action_text', row.get('content', 'Unknown'))
            
            # Get dominant attractor and score for each
            tfidf_dom = max(comp['tfidf'], key=comp['tfidf'].get)
            tfidf_score = comp['tfidf'][tfidf_dom]
            
            minilm_dom = max(comp['minilm'], key=comp['minilm'].get)
            minilm_score = comp['minilm'][minilm_dom]
            
            comp_data.append({
                "Timestamp": row['timestamp'],
                "Action": action,
                "TF-IDF Dom": tfidf_dom,
                "TF-IDF Score": round(tfidf_score, 3),
                "MiniLM Dom": minilm_dom,
                "MiniLM Score": round(minilm_score, 3),
                "Agreement": tfidf_dom == minilm_dom
            })
    
    if comp_data:
        comp_df = pd.DataFrame(comp_data)
        
        c_b1, c_b2 = st.columns([3, 1])
        with c_b1:
            st.dataframe(comp_df.sort_values(by='Timestamp', ascending=False), use_container_width=True)
        with c_b2:
            agreement_rate = comp_df['Agreement'].mean()
            st.metric("Engine Agreement", f"{round(agreement_rate * 100, 1)}%")
            st.write("Agreement indicates if both engines choose the same dominant attractor.")
    else:
        st.info("No comparison data available yet. Process new signals to generate benchmark data.")

    # Identity Drift Monitor (Sprint 4 Phase B)
    st.divider()
    st.subheader("🪐 Identity Drift & Global Dominance")
    
    drift_data = []
    for idx, row in df.iterrows():
        params = row.get('physics_params', {})
        if isinstance(params, dict) and 'identity_snapshot' in params:
            snapshot = params['identity_snapshot']
            drift_data.append({
                "timestamp": row['timestamp'],
                "drift_delta": snapshot.get('drift_delta', 0),
                "global_dominant_identity": row.get('global_dominant_identity', 'Unknown')
            })
    
    if drift_data:
        drift_df = pd.DataFrame(drift_data)
        
        d_col1, d_col2 = st.columns(2)
        with d_col1:
            fig_drift = px.line(drift_df, x='timestamp', y='drift_delta', title="Identity Drift Delta (Centroid Movement)", markers=True)
            st.plotly_chart(fig_drift, use_container_width=True)
        with d_col2:
            fig_global = px.histogram(df, x='timestamp', color='global_dominant_identity', 
                                      title="Evolution of Global Identity Dominance",
                                      color_discrete_map={"engineering": "#BC13FE", "fitness": "#00FF00", "culinary": "#FFA500"})
            st.plotly_chart(fig_global, use_container_width=True)
    else:
        st.info("No identity drift data available yet. Process new signals to observe identity movement.")

    # Event Inspector (Observability)
    st.sidebar.subheader("Event Inspector")
    event_ids = df['event_id'].tolist()
    selected_event_id = st.sidebar.selectbox("Inspect Signal ID", event_ids[::-1])
    
    if selected_event_id:
        st.divider()
        st.subheader(f"🔍 Event Inspector: {selected_event_id}")
        event_data = df[df['event_id'] == selected_event_id].iloc[0]
        
        ci1, ci2 = st.columns([1, 2])
        with ci1:
            st.write("**Core Data**")
            display_data = {k: v for k, v in event_data.to_dict().items() if k not in ['physics_params', 'physics', 'all_alignments']}
            st.json(display_data)
        with ci2:
            st.write("**Physics & Semantic Trace**")
            physics_info = event_data.get('physics_params', event_data.get('physics', {}))
            st.json(physics_info)
            st.write("**Action Content**")
            st.info(event_data.get('action_text', event_data.get('content', 'No content')))

    # Tabla de Eventos Crudos
    st.divider()
    st.subheader("Event Horizon (Raw Logs)")
    st.dataframe(df.sort_values(by='timestamp', ascending=False), use_container_width=True)

if st.sidebar.button("Refresh Data"):
    st.rerun()