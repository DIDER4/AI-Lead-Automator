"""
AI Lead Automator - Production-Ready Modular Architecture
Version: 2.0.0
Tech Stack: Streamlit, Firecrawl, OpenAI/Anthropic, Pandas, Plotly
Security: Fernet Encryption, Input Validation, GDPR Compliance
Author: Senior Python Security Architect
Date: January 2026

Architecture:
- Modular separation of concerns
- Security-first design with encryption
- Comprehensive error handling and logging
- GDPR compliance utilities
- Scalable and maintainable codebase
"""

import streamlit as st
from pathlib import Path
import sys

# Add src to path
sys.path.insert(0, str(Path(__file__).parent))

from src.config import Constants, get_logger
from src.security import SecureConfigManager
from src.services import DataManager
from src.ui import UIPages

# Initialize logger
logger = get_logger(__name__)


def configure_page():
    """Configure Streamlit page settings"""
    st.set_page_config(
        page_title=Constants.PAGE_TITLE,
        page_icon=Constants.PAGE_ICON,
        layout=Constants.LAYOUT,
        initial_sidebar_state="expanded"
    )
    
    logger.info(f"Starting {Constants.APP_NAME} v{Constants.APP_VERSION}")


def render_sidebar(data_manager: DataManager):
    """Render sidebar navigation and stats"""
    st.sidebar.title(f"{Constants.PAGE_ICON} {Constants.APP_NAME}")
    st.sidebar.markdown("---")
    
    # Navigation
    page = st.sidebar.radio(
        "Navigation",
        [
            "🏠 Home",
            "⚙️ Settings",
            "👤 User Profile",
            "💬 Lead Chat",
            "📊 Dashboard"
        ]
    )
    
    # Quick stats
    st.sidebar.markdown("---")
    st.sidebar.markdown("### 📊 Quick Stats")
    
    leads = data_manager.load_all()
    st.sidebar.metric("Total Leads", len(leads))
    
    if leads:
        avg_score = sum(l.lead_score for l in leads) / len(leads)
        st.sidebar.metric("Avg Score", f"{avg_score:.0f}")
    
    # System info
    st.sidebar.markdown("---")
    st.sidebar.markdown(f"""
    <small>
    <strong>🔒 100% Local & Secure</strong><br>
    All data stored on your computer<br>
    API keys encrypted with Fernet<br><br>
    <strong>Version:</strong> {Constants.APP_VERSION}<br>
    <strong>Powered by:</strong><br>
    Firecrawl |  AI |  Streamlit
    </small>
    """, unsafe_allow_html=True)
    
    return page


def main():
    """Main application entry point"""
    try:
        # Configure page
        configure_page()
        
        # Initialize core components
        config_manager = SecureConfigManager()
        data_manager = DataManager()
        ui_pages = UIPages(config_manager, data_manager)
        
        # Render sidebar and get selected page
        page = render_sidebar(data_manager)
        
        # Route to appropriate page
        if page == "🏠 Home":
            logger.debug("Rendering Home page")
            ui_pages.render_home()
        
        elif page == "⚙️ Settings":
            logger.debug("Rendering Settings page")
            ui_pages.render_settings()
        
        elif page == "👤 User Profile":
            logger.debug("Rendering User Profile page")
            ui_pages.render_profile()
        
        elif page == "💬 Lead Chat":
            logger.debug("Rendering Lead Chat page")
            ui_pages.render_lead_chat()
        
        elif page == "📊 Dashboard":
            logger.debug("Rendering Dashboard page")
            ui_pages.render_dashboard()
        
        else:
            st.error(f"Unknown page: {page}")
            logger.error(f"Unknown page requested: {page}")
    
    except Exception as e:
        logger.error(f"Application error: {e}", exc_info=True)
        st.error(f"An error occurred: {str(e)}")
        st.error("Check logs for details.")


if __name__ == "__main__":
    main()
