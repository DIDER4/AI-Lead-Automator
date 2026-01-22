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
from src.services.knowledge_base import KnowledgeBaseService
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


def render_sidebar(data_manager: DataManager, kb_stats: dict):
    """Render sidebar navigation and stats"""
    st.sidebar.title(f"{Constants.PAGE_ICON} {Constants.APP_NAME}")
    st.sidebar.markdown("---")
    
    # Navigation
    page = st.sidebar.radio(
        "Navigation",
        [
            "Home",
            "Settings",
            "User Profile",
            "Knowledge Base",
            "Lead Chat",
            "Dashboard"
        ]
    )
    
    # Quick stats
    st.sidebar.markdown("---")
    st.sidebar.markdown("### Quick Stats")
    
    leads = data_manager.load_all()
    st.sidebar.metric("Total Leads", len(leads))
    
    if leads:
        avg_score = sum(l.lead_score for l in leads) / len(leads)
        st.sidebar.metric("Avg Score", f"{avg_score:.0f}")
    
    # KB stats
    if kb_stats['total_documents'] > 0:
        st.sidebar.metric("KB Documents", kb_stats['total_documents'])
    
    # System info
    st.sidebar.markdown("---")
    st.sidebar.markdown(f"""
    <small>
    <strong>100% Local & Secure</strong><br>
    All data stored on your computer<br>
    API keys encrypted with Fernet<br><br>
    <strong>Version:</strong> {Constants.APP_VERSION}<br>
    <strong>Powered by:</strong><br>
    Firecrawl | AI | Streamlit
    </small>
    """, unsafe_allow_html=True)
    
    return page


def main():
    """Main application entry point"""
    try:
        # Configure page
        configure_page()
        
        # Initialize core managers
        config_manager = SecureConfigManager()
        data_manager = DataManager()
        logger.info("Core managers initialized")
        
        # Initialize Knowledge Base Service
        try:
            kb_service = KnowledgeBaseService()
            kb_stats = kb_service.get_stats()
            logger.info("Knowledge Base Service initialized successfully")
        except Exception as e:
            logger.warning(f"Knowledge Base Service failed to initialize: {e}")
            kb_service = None
            kb_stats = {'total_documents': 0, 'total_chunks': 0, 'doc_types': {}}
        
        ui_pages = UIPages(config_manager, data_manager)
        
        # Render sidebar and get selected page
        page = render_sidebar(data_manager, kb_stats)
        
        # Route to appropriate page
        if page == "Home":
            logger.debug("Rendering Home page")
            ui_pages.render_home()
        
        elif page == "Settings":
            logger.debug("Rendering Settings page")
            ui_pages.render_settings()
        
        elif page == "User Profile":
            logger.debug("Rendering User Profile page")
            ui_pages.render_profile()
        
        elif page == "Knowledge Base":
            logger.debug("Rendering Knowledge Base page")
            if kb_service:
                ui_pages.render_knowledge_base(kb_service)
            else:
                st.error("Knowledge Base service failed to initialize. Check logs for details.")
        
        elif page == "Lead Chat":
            logger.debug("Rendering Lead Chat page")
            # Pass KB service to Lead Chat for RAG integration
            if kb_service:
                st.session_state['kb_service'] = kb_service
            ui_pages.render_lead_chat()
        
        elif page == "Dashboard":
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
