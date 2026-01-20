"""
Streamlit UI Components
Reusable UI components for the application
"""

import streamlit as st
import plotly.graph_objects as go
import plotly.express as px
import pandas as pd
from typing import List

from src.models.lead import Lead
from src.config import Constants


def render_hero_section():
    """Render hero section with gradient background"""
    st.markdown("""
    <style>
    .hero-section {
        background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
        padding: 3rem;
        border-radius: 10px;
        color: white;
        text-align: center;
        margin-bottom: 2rem;
    }
    .hero-title {
        font-size: 3rem;
        font-weight: bold;
        margin-bottom: 1rem;
    }
    .hero-subtitle {
        font-size: 1.3rem;
        opacity: 0.9;
    }
    </style>
    
    <div class="hero-section">
        <div class="hero-title"> AI Lead Automator</div>
        <div class="hero-subtitle">
            Intelligent Lead Generation & Qualification Platform<br>
            Powered by Firecrawl & AI
        </div>
    </div>
    """, unsafe_allow_html=True)


def render_workflow_cards():
    """Render workflow explanation cards"""
    st.markdown("""
    <style>
    .workflow-card {
        background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
        padding: 1.5rem;
        border-radius: 10px;
        border-left: 4px solid rgba(255, 255, 255, 0.5);
        margin: 1rem 0;
        color: white;
    }
    .workflow-number {
        background: rgba(255, 255, 255, 0.3);
        color: white;
        border-radius: 50%;
        width: 40px;
        height: 40px;
        display: inline-flex;
        align-items: center;
        justify-content: center;
        font-weight: bold;
        font-size: 1.2rem;
        margin-right: 1rem;
    }
    .workflow-card strong {
        color: white;
    }
    </style>
    """, unsafe_allow_html=True)
    
    col1, col2 = st.columns(2)
    
    with col1:
        st.markdown("""
        <div class="workflow-card">
            <span class="workflow-number">1</span>
            <strong>Define Your Profile</strong><br>
            Set up your company details, value proposition, and ICP
        </div>
        <div class="workflow-card">
            <span class="workflow-number">2</span>
            <strong>Scrape with Firecrawl</strong><br>
            Enter prospect URLs and extract accurate content
        </div>
        """, unsafe_allow_html=True)
    
    with col2:
        st.markdown("""
        <div class="workflow-card">
            <span class="workflow-number">3</span>
            <strong>AI Analysis</strong><br>
            AI analyzes leads and generates personalized outreach
        </div>
        <div class="workflow-card">
            <span class="workflow-number">4</span>
            <strong>Export & Engage</strong><br>
            Export qualified leads with GDPR-safe options
        </div>
        """, unsafe_allow_html=True)


def render_lead_card(lead: Lead):
    """Render a single lead card with styling"""
    color = lead.score_color
    
    st.markdown(f"""
    <div style="background: linear-gradient(135deg, #{color}22 0%, #{color}11 100%); 
                padding: 1rem; border-radius: 10px; border-left: 4px solid {color};">
        <h3>{lead.company_name}</h3>
        <strong>Score:</strong> {lead.lead_score}/100 - {lead.qualification_status}<br>
        <strong>Industry:</strong> {lead.industry}<br>
        <strong>URL:</strong> <a href="{lead.url}" target="_blank">{lead.url}</a>
    </div>
    """, unsafe_allow_html=True)
    
    st.markdown(f"**Score Rationale:**\n{lead.score_rationale}")
    st.markdown(f"**Key Insights:**\n{lead.key_insights}")
    st.markdown(f"**ICP Fit Analysis:**\n{lead.fit_analysis}")
    
    with st.expander("Personalized Email Draft"):
        st.text_area("Email", value=lead.personalized_email, height=200, 
                     key=f"email_{lead.id}")
    
    with st.expander("SMS Draft"):
        st.text_area("SMS", value=lead.sms_draft, height=80, 
                     key=f"sms_{lead.id}")


def create_pie_chart(leads: List[Lead]) -> go.Figure:
    """Create qualification pie chart"""
    qualified = sum(1 for l in leads if l.is_qualified)
    disqualified = len(leads) - qualified
    
    fig = go.Figure(data=[go.Pie(
        labels=['Qualified (≥70)', 'Disqualified (<70)'],
        values=[qualified, disqualified],
        hole=0.4,
        marker_colors=['#10b981', '#ef4444']
    )])
    fig.update_layout(height=300, showlegend=True)
    return fig


def create_score_histogram(leads: List[Lead]) -> go.Figure:
    """Create score distribution histogram"""
    scores = [l.lead_score for l in leads]
    
    fig = px.histogram(
        x=scores,
        nbins=10,
        color_discrete_sequence=['#667eea'],
        labels={'x': 'Lead Score', 'y': 'Count'}
    )
    fig.update_layout(
        height=300,
        showlegend=False,
        xaxis_title="Lead Score",
        yaxis_title="Count"
    )
    return fig


def create_industry_bar_chart(leads: List[Lead]) -> go.Figure:
    """Create industry breakdown bar chart"""
    industries = {}
    for lead in leads:
        industries[lead.industry] = industries.get(lead.industry, 0) + 1
    
    # Sort and take top 10
    sorted_industries = sorted(industries.items(), key=lambda x: x[1], reverse=True)[:10]
    
    fig = px.bar(
        x=[count for _, count in sorted_industries],
        y=[industry for industry, _ in sorted_industries],
        orientation='h',
        color_discrete_sequence=['#764ba2'],
        labels={'x': 'Number of Leads', 'y': 'Industry'}
    )
    fig.update_layout(height=400, showlegend=False)
    return fig


def render_metrics_row(leads: List[Lead]):
    """Render key metrics in columns"""
    col1, col2, col3, col4 = st.columns(4)
    
    with col1:
        st.metric("Total Leads", len(leads))
    
    with col2:
        qualified = sum(1 for l in leads if l.is_qualified)
        rate = (qualified / len(leads) * 100) if leads else 0
        st.metric("Qualified (70+)", qualified, delta=f"{rate:.0f}%")
    
    with col3:
        avg_score = sum(l.lead_score for l in leads) / len(leads) if leads else 0
        st.metric("Average Score", f"{avg_score:.1f}")
    
    with col4:
        from datetime import datetime
        today = datetime.now().strftime('%Y-%m-%d')
        today_leads = sum(1 for l in leads if l.timestamp[:10] == today)
        st.metric("Added Today", today_leads)


def render_sidebar_stats(leads: List[Lead]):
    """Render statistics in sidebar"""
    st.sidebar.markdown("### Quick Stats")
    st.sidebar.metric("Total Leads", len(leads))
    
    if leads:
        avg_score = sum(l.lead_score for l in leads) / len(leads)
        st.sidebar.metric("Avg Score", f"{avg_score:.0f}")


def show_success(message: str):
    """Show success message with icon"""
    st.success(f"✅ {message}")


def show_error(message: str):
    """Show error message with icon"""
    st.error(f"❌ {message}")


def show_warning(message: str):
    """Show warning message with icon"""
    st.warning(f"⚠️ {message}")


def show_info(message: str):
    """Show info message with icon"""
    st.info(f"ℹ️ {message}")
