# streamlit_dashboard.py
import streamlit as st
import pandas as pd
import numpy as np
import plotly.express as px
import plotly.graph_objects as go
from plotly.subplots import make_subplots
import time
from datetime import datetime, timedelta
import json
from risk_scoring_agent import RiskScoringSystem, AgentStatus, RiskLevel, generate_sample_data
import threading
import random
import streamlit as st
import time
@st.cache_data(ttl=5)
def fetch_data():
    return generate_sample_data()

data = fetch_data()
st.dataframe(data)



# Configure page
st.set_page_config(
    page_title="Risk Agent Health Dashboard",
    page_icon="🎯",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Custom CSS for better styling
st.markdown("""
<style>
    .metric-card {
        background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
        padding: 1rem;
        border-radius: 10px;
        color: white;
        margin: 0.5rem 0;
    }
    .status-healthy { color: #28a745; }
    .status-warning { color: #ffc107; }
    .status-critical { color: #dc3545; }
    .status-offline { color: #6c757d; }
    .risk-low { background-color: #d4edda; color: #155724; }
    .risk-medium { background-color: #fff3cd; color: #856404; }
    .risk-high { background-color: #f8d7da; color: #721c24; }
    .risk-critical { background-color: #f5c6cb; color: #721c24; }
</style>
""", unsafe_allow_html=True)

# Initialize session state
if 'system' not in st.session_state:
    st.session_state.system = RiskScoringSystem()
    # Add agents
    for i in range(3):
        st.session_state.system.add_agent(f"agent_{i+1}")
    st.session_state.system.start_all_agents()

if 'auto_generate' not in st.session_state:
    st.session_state.auto_generate = False

if 'generation_thread' not in st.session_state:
    st.session_state.generation_thread = None

def generate_assessments():
    """Generate risk assessments in background"""
    while st.session_state.auto_generate:
        try:
            agent_id = random.choice(list(st.session_state.system.agents.keys()))
            agent = st.session_state.system.agents[agent_id]
            sample_data = generate_sample_data()
            agent.assess_risk(sample_data)
            time.sleep(random.uniform(1, 3))
        except Exception as e:
            print(f"Error generating assessment: {e}")
            time.sleep(1)

def get_status_color(status: AgentStatus) -> str:
    """Get color for agent status"""
    colors = {
        AgentStatus.HEALTHY: "#28a745",
        AgentStatus.WARNING: "#ffc107", 
        AgentStatus.CRITICAL: "#dc3545",
        AgentStatus.OFFLINE: "#6c757d"
    }
    return colors.get(status, "#6c757d")

def get_risk_color(risk_level: RiskLevel) -> str:
    """Get color for risk level"""
    colors = {
        RiskLevel.LOW: "#28a745",
        RiskLevel.MEDIUM: "#ffc107",
        RiskLevel.HIGH: "#fd7e14",
        RiskLevel.CRITICAL: "#dc3545"
    }
    return colors.get(risk_level, "#6c757d")

# Main dashboard
st.title("🎯 Risk Scoring Agent Health Dashboard")

# Sidebar controls
st.sidebar.header("🛠️ Controls")

# Auto-generate toggle
auto_generate = st.sidebar.toggle(
    "Auto-generate assessments",
    value=st.session_state.auto_generate,
    help="Automatically generate risk assessments for testing"
)

if auto_generate != st.session_state.auto_generate:
    st.session_state.auto_generate = auto_generate
    if auto_generate:
        st.session_state.generation_thread = threading.Thread(
            target=generate_assessments, daemon=True
        )
        st.session_state.generation_thread.start()

# Manual assessment button
if st.sidebar.button("🎲 Generate Single Assessment"):
    agent_id = random.choice(list(st.session_state.system.agents.keys()))
    agent = st.session_state.system.agents[agent_id]
    sample_data = generate_sample_data()
    assessment = agent.assess_risk(sample_data)
    st.sidebar.success(f"Generated assessment for {assessment.entity_id}")

# Refresh rate
refresh_rate = st.sidebar.selectbox(
    "Refresh rate (seconds)",
    options=[1, 5, 10, 30],
    index=1
)

# Auto-refresh
auto_refresh = st.sidebar.toggle("Auto-refresh", value=True)

# System overview
st.header("📊 System Overview")
system_health = st.session_state.system.get_system_health()

col1, col2, col3, col4 = st.columns(4)

with col1:
    st.metric(
        "Total Assessments",
        system_health['total_assessments'],
        delta=None
    )

with col2:
    st.metric(
        "Active Agents",
        f"{system_health['active_agents']}/{system_health['total_agents']}",
        delta=None
    )

with col3:
    st.metric(
        "Avg Response Time",
        f"{system_health['average_response_time']:.2f}s",
        delta=None
    )

with col4:
    uptime_hours = system_health['system_uptime'] / 3600
    st.metric(
        "System Uptime",
        f"{uptime_hours:.1f}h",
        delta=None
    )

# Agent health status
st.header("🏥 Agent Health Status")
agent_health = st.session_state.system.get_all_agent_health()

# Create agent health dataframe
agent_df = pd.DataFrame([
    {
        'Agent ID': agent.agent_id,
        'Status': agent.status.value,
        'Uptime (min)': agent.uptime / 60,
        'Response Time (s)': agent.response_time,
        'Error Rate (%)': agent.error_rate * 100,
        'Throughput (req/s)': agent.throughput,
        'CPU Usage (%)': agent.cpu_usage,
        'Memory Usage (%)': agent.memory_usage,
        'Active Assessments': agent.active_assessments,
        'Last Heartbeat': agent.last_heartbeat
    }
    for agent in agent_health
])

# Display agent status cards
cols = st.columns(len(agent_health))
for i, (col, agent) in enumerate(zip(cols, agent_health)):
    with col:
        status_color = get_status_color(agent.status)
        st.markdown(f"""
        <div style="
            border: 2px solid {status_color};
            border-radius: 10px;
            padding: 1rem;
            margin: 0.5rem 0;
            background: rgba(255,255,255,0.05);
        ">
            <h4 style="margin: 0; color: {status_color};">
                {agent.agent_id.upper()}
            </h4>
            <p style="margin: 0.5rem 0; color: {status_color};">
                <strong>Status:</strong> {agent.status.value.upper()}
            </p>
            <p style="margin: 0.2rem 0; font-size: 0.9rem;">
                <strong>Uptime:</strong> {agent.uptime/60:.1f}m
            </p>
            <p style="margin: 0.2rem 0; font-size: 0.9rem;">
                <strong>Response:</strong> {agent.response_time:.2f}s
            </p>
            <p style="margin: 0.2rem 0; font-size: 0.9rem;">
                <strong>Error Rate:</strong> {agent.error_rate*100:.1f}%
            </p>
            <p style="margin: 0.2rem 0; font-size: 0.9rem;">
                <strong>CPU:</strong> {agent.cpu_usage:.1f}%
            </p>
        </div>
        """, unsafe_allow_html=True)

# Detailed metrics table
st.subheader("📋 Detailed Agent Metrics")
st.dataframe(
    agent_df.style.format({
        'Uptime (min)': '{:.1f}',
        'Response Time (s)': '{:.2f}',
        'Error Rate (%)': '{:.1f}',
        'Throughput (req/s)': '{:.2f}',
        'CPU Usage (%)': '{:.1f}',
        'Memory Usage (%)': '{:.1f}',
        'Last Heartbeat': lambda x: x.strftime('%H:%M:%S')
    }),
    use_container_width=True
)

# Performance charts
st.header("📈 Performance Metrics")

col1, col2 = st.columns(2)

with col1:
    # Response time chart
    fig_response = px.bar(
        agent_df,
        x='Agent ID',
        y='Response Time (s)',
        title='Response Time by Agent',
        color='Status',
        color_discrete_map={
            'healthy': '#28a745',
            'warning': '#ffc107',
            'critical': '#dc3545',
            'offline': '#6c757d'
        }
    )
    fig_response.update_layout(height=400)
    st.plotly_chart(fig_response, use_container_width=True)

with col2:
    # System usage chart
    fig_usage = make_subplots(
        rows=1, cols=2,
        subplot_titles=('CPU Usage', 'Memory Usage'),
        specs=[[{"type": "indicator"}, {"type": "indicator"}]]
    )
    
    avg_cpu = agent_df['CPU Usage (%)'].mean()
    avg_memory = agent_df['Memory Usage (%)'].mean()
    
    fig_usage.add_trace(
        go.Indicator(
            mode="gauge+number",
            value=avg_cpu,
            title={'text': "Avg CPU %"},
            gauge={'axis': {'range': [None, 100]},
                   'bar': {'color': "darkblue"},
                   'bgcolor': "white",
                   'borderwidth': 2,
                   'bordercolor': "gray",
                   'steps': [{'range': [0, 50], 'color': 'lightgray'},
                            {'range': [50, 80], 'color': 'yellow'},
                            {'range': [80, 100], 'color': 'red'}]},
            domain={'x': [0, 0.5], 'y': [0, 1]}
        ),
        row=1, col=1
    )
    
    fig_usage.add_trace(
        go.Indicator(
            mode="gauge+number",
            value=avg_memory,
            title={'text': "Avg Memory %"},
            gauge={'axis': {'range': [None, 100]},
                   'bar': {'color': "darkgreen"},
                   'bgcolor': "white",
                   'borderwidth': 2,
                   'bordercolor': "gray",
                   'steps': [{'range': [0, 50], 'color': 'lightgray'},
                            {'range': [50, 80], 'color': 'yellow'},
                            {'range': [80, 100], 'color': 'red'}]},
            domain={'x': [0.5, 1], 'y': [0, 1]}
        ),
        row=1, col=2
    )
    
    fig_usage.update_layout(height=400)
    st.plotly_chart(fig_usage, use_container_width=True)

# Recent assessments
st.header("📊 Recent Risk Assessments")

# Collect recent assessments from all agents
all_assessments = []
for agent in st.session_state.system.agents.values():
    recent_assessments = agent.get_assessment_history(limit=50)
    for assessment in recent_assessments:
        all_assessments.append({
            'Agent ID': agent.agent_id,
            'Entity ID': assessment.entity_id,
            'Risk Score': assessment.risk_score,
            'Risk Level': assessment.risk_level.value,
            'Confidence': assessment.confidence,
            'Timestamp': assessment.timestamp,
            'Financial Exposure': assessment.factors.get('financial_exposure', 0),
            'Credit History': assessment.factors.get('credit_history', 0),
            'Market Volatility': assessment.factors.get('market_volatility', 0),
            'Regulatory Compliance': assessment.factors.get('regulatory_compliance', 0),
            'Operational Risk': assessment.factors.get('operational_risk', 0)
        })

if all_assessments:
    assessments_df = pd.DataFrame(all_assessments)
    assessments_df = assessments_df.sort_values('Timestamp', ascending=False)
    
    # Risk distribution chart
    col1, col2 = st.columns(2)
    
    with col1:
        risk_counts = assessments_df['Risk Level'].value_counts()
        fig_risk_dist = px.pie(
            values=risk_counts.values,
            names=risk_counts.index,
            title='Risk Level Distribution',
            color_discrete_map={
                'low': '#28a745',
                'medium': '#ffc107',
                'high': '#fd7e14',
                'critical': '#dc3545'
            }
        )
        st.plotly_chart(fig_risk_dist, use_container_width=True)
    
    with col2:
        # Risk score over time
        fig_risk_time = px.scatter(
            assessments_df.head(100),
            x='Timestamp',
            y='Risk Score',
            color='Risk Level',
            title='Risk Scores Over Time',
            color_discrete_map={
                'low': '#28a745',
                'medium': '#ffc107',
                'high': '#fd7e14',
                'critical': '#dc3545'
            }
        )
        st.plotly_chart(fig_risk_time, use_container_width=True)
    
    # Recent assessments table
    st.subheader("📋 Recent Assessments")
    st.dataframe(
        assessments_df.head(20).style.format({
            'Risk Score': '{:.3f}',
            'Confidence': '{:.2f}',
            'Financial Exposure': '{:.3f}',
            'Credit History': '{:.3f}',
            'Market Volatility': '{:.3f}',
            'Regulatory Compliance': '{:.3f}',
            'Operational Risk': '{:.3f}',
            'Timestamp': lambda x: x.strftime('%H:%M:%S')
        }),
        use_container_width=True
    )
    
    # Risk factor analysis
    st.subheader("🔍 Risk Factor Analysis")
    factor_cols = ['Financial Exposure', 'Credit History', 'Market Volatility', 
                   'Regulatory Compliance', 'Operational Risk']
    
    fig_factors = px.box(
        assessments_df.melt(
            id_vars=['Entity ID', 'Risk Level'],
            value_vars=factor_cols,
            var_name='Risk Factor',
            value_name='Score'
        ),
        x='Risk Factor',
        y='Score',
        color='Risk Level',
        title='Risk Factor Distribution by Risk Level'
    )
    fig_factors.update_layout(height=500)
    st.plotly_chart(fig_factors, use_container_width=True)

else:
    st.info("No risk assessments available yet. Enable auto-generation or create manual assessments to see data.")

# Real-time monitoring
if auto_refresh:
    time.sleep(refresh_rate)
    st.rerun()

# Footer
st.markdown("---")
st.markdown("🎯 Risk Scoring Agent Health Dashboard | Built with Streamlit")
#streamlit run "c:\Users\aditi\risk scoring dashboard\streamlit_dashboard.py"
