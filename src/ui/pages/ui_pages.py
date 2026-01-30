"""
Streamlit UI Pages Module
All page rendering logic consolidated
"""

import streamlit as st
import pandas as pd
import io
import time
from datetime import datetime

from src.config import AppConfig, get_logger
from src.security import SecureConfigManager
from src.services import DataManager, LeadAnalyzer
from src.ui.components import *
from src.utils import make_gdpr_safe

logger = get_logger(__name__)


class UIPages:
    """Container for all UI page rendering methods"""
    
    def __init__(self, 
                 config_manager: SecureConfigManager,
                 data_manager: DataManager):
        self.config_manager = config_manager
        self.data_manager = data_manager
    
    def render_home(self):
        """Render home page"""
        render_hero_section()
        
        # Check if in test mode (cached)
        config_dict = self.config_manager.load(use_cache=True)
        config = AppConfig(**config_dict) if config_dict else AppConfig()
        
        if not config.has_valid_firecrawl_key() or not config.has_valid_ai_key():
            st.warning(" **Test Mode Active** - Configure API keys in Settings to use real data. Currently using mock data for demonstration.")
        
        st.markdown("## How It Works")
        render_workflow_cards()
        
        # Features
        st.markdown("---")
        st.markdown("## Key Features")
        
        col1, col2, col3 = st.columns(3)
        
        with col1:
            st.markdown("""
            ### Secure
            - Encrypted API key storage
            - Local data processing
            - GDPR-compliant exports
            """)
        
        with col2:
            st.markdown("""
            ### Intelligent
            - AI-powered lead scoring
            - Personalized email generation
            - Industry analysis
            """)
        
        with col3:
            st.markdown("""
            ### Insightful
            - Visual analytics dashboard
            - Lead qualification tracking
            - Export to Excel/CSV
            """)
        
        # Stats
        leads = self.data_manager.load_all(use_cache=True)
        if leads:
            # Check if we're showing test data
            is_test_mode = not config.has_valid_firecrawl_key() or not config.has_valid_ai_key()
            if is_test_mode and any(lead.id and lead.id >= 9000 for lead in leads):
                st.info("📊 **Test Mode**: Stats below show sample data. Configure API keys in Settings for real data.")
            
            st.markdown("---")
            st.markdown("## Your Stats")
            render_metrics_row(leads)
    
    def render_settings(self):
        """Render settings page"""
        st.title("Settings & Security")
        st.markdown("Configure your API keys. All keys are encrypted locally.")
        
        # Load current config
        config_dict = self.config_manager.load()
        config = AppConfig(**config_dict) if config_dict else AppConfig()
        
        # Firecrawl
        with st.expander("Firecrawl API", expanded=True):
            col1, col2 = st.columns([3, 1])
            
            with col1:
                firecrawl_key = st.text_input(
                    "Firecrawl API Key",
                    value=config.firecrawl_api_key,
                    type="password",
                    help="Get from https://firecrawl.dev"
                )
            
            with col2:
                st.markdown("<br>", unsafe_allow_html=True)
                if st.button("Test", use_container_width=True):
                    analyzer = LeadAnalyzer(config, self.data_manager)
                    success, msg = analyzer.test_firecrawl_connection()
                    if success:
                        show_success(msg)
                    else:
                        show_error(msg)
        
        # AI Provider
        with st.expander(" AI Provider Configuration"):
            ai_provider = st.selectbox(
                "Select AI Provider",
                ["OpenAI", "Anthropic"],
                index=0 if config.ai_provider == "OpenAI" else 1
            )
            
            if ai_provider == "OpenAI":
                openai_key = st.text_input(
                    "OpenAI API Key",
                    value=config.openai_api_key,
                    type="password"
                )
                anthropic_key = config.anthropic_api_key
            else:
                anthropic_key = st.text_input(
                    "Anthropic API Key",
                    value=config.anthropic_api_key,
                    type="password"
                )
                openai_key = config.openai_api_key
        
        # Save
        st.markdown("---")
        col1, col2, col3 = st.columns([1, 1, 2])
        
        with col1:
            if st.button("Save Settings", type="primary", use_container_width=True):
                new_config_dict = {
                    'firecrawl_api_key': firecrawl_key,
                    'openai_api_key': openai_key,
                    'anthropic_api_key': anthropic_key,
                    'ai_provider': ai_provider,
                    'my_website': config.my_website,
                    'my_value_proposition': config.my_value_proposition,
                    'my_icp': config.my_icp
                }
                
                if self.config_manager.save(new_config_dict):
                    show_success("Settings saved securely!")
                    time.sleep(1)
                    st.rerun()
        
        with col2:
            if st.button("Reset", use_container_width=True):
                st.rerun()
        
        # Security info
        st.markdown("---")
        st.markdown("### Security Information")
        st.info("""
        **Data Protection:**
        - ✅ API keys encrypted with Fernet
        - ✅ Local storage only
        - ✅ No external data transmission (except API calls)
        """)
    
    def render_profile(self):
        """Render user profile page"""
        st.title("User Profile")
        st.markdown("Define your company profile to guide AI analysis.")
        
        config_dict = self.config_manager.load()
        config = AppConfig(**config_dict) if config_dict else AppConfig()
        
        my_website = st.text_input(
            "Company Website",
            value=config.my_website,
            placeholder="https://www.yourcompany.com"
        )
        
        my_value_proposition = st.text_area(
            "Value Proposition",
            value=config.my_value_proposition,
            placeholder="We help B2B SaaS companies scale...",
            height=120
        )
        
        my_icp = st.text_area(
            "Ideal Customer Profile (ICP)",
            value=config.my_icp,
            placeholder="B2B SaaS, 10-50 employees, Series A funded...",
            height=150
        )
        
        # Save
        st.markdown("---")
        col1, col2 = st.columns([1, 3])
        
        with col1:
            if st.button("Save Profile", type="primary", use_container_width=True):
                current = self.config_manager.load()
                current.update({
                    'my_website': my_website,
                    'my_value_proposition': my_value_proposition,
                    'my_icp': my_icp
                })
                
                if self.config_manager.save(current):
                    show_success("Profile saved!")
                    time.sleep(1)
                    st.rerun()
    
    def render_lead_chat(self):
        """Render lead chat page"""
        st.title("Lead Chat & Analyzer")
        
        config_dict = self.config_manager.load(use_cache=True)
        config = AppConfig(**config_dict) if config_dict else AppConfig()
        
        # Check if in test mode
        is_firecrawl_test = not config.has_valid_firecrawl_key()
        is_ai_test = not config.has_valid_ai_key()
        
        # Check if Knowledge Base is available
        kb_service = st.session_state.get('kb_service', None)
        kb_active = kb_service and kb_service.get_stats()['total_documents'] > 0
        
        if is_firecrawl_test or is_ai_test:
            test_components = []
            if is_firecrawl_test:
                test_components.append("**Firecrawl** (web scraping)")
            if is_ai_test:
                test_components.append("**AI Analysis** (lead scoring)")
            
            st.info(f"**TEST MODE ACTIVE**: Using mock data for {' and '.join(test_components)}. Configure real API keys in Settings for production use.")
        
        # Show KB status
        if kb_active:
            kb_stats = kb_service.get_stats()
            st.success(f"✨ **Knowledge Base Active**: {kb_stats['total_documents']} documents loaded. AI will use your company knowledge for personalized analysis.")
        else:
            st.info("💡 Upload documents to Knowledge Base for AI-powered analysis using your company information.")
        
        # Initialize analyzer with KB support
        analyzer = LeadAnalyzer(config, self.data_manager, knowledge_base=kb_service)
        
        # URL input
        st.markdown("### Prospect URL")
        col1, col2 = st.columns([3, 1])
        
        with col1:
            url_input = st.text_input(
                "Enter URL",
                placeholder="https://www.prospect-company.com",
                label_visibility="collapsed"
            )
        
        with col2:
            analyze_button = st.button("Analyze", type="primary", use_container_width=True)
        
        # Bulk input
        with st.expander("Bulk URL Input"):
            bulk_urls = st.text_area(
                "Multiple URLs (one per line)",
                placeholder="https://company1.com\nhttps://company2.com",
                height=150
            )
            analyze_bulk = st.button("Analyze All", type="primary")
        
        # Process single
        if analyze_button and url_input:
            with st.spinner("Processing..."):
                success, message, lead_id = analyzer.analyze_and_save(url_input)
                
                if success:
                    # Clear sidebar cache since we added new data
                    if "sidebar_quick_stats" in st.session_state:
                        del st.session_state["sidebar_quick_stats"]
                    
                    show_success(f"Lead #{lead_id} analyzed!")
                    lead = self.data_manager.get_lead(lead_id)
                    if lead:
                        st.markdown("---")
                        render_lead_card(lead)
                else:
                    show_error(message)
        
        # Process bulk
        if analyze_bulk and bulk_urls:
            urls = [u.strip() for u in bulk_urls.split('\n') if u.strip()]
            st.info(f"Processing {len(urls)} URLs...")
            
            progress = st.progress(0)
            status = st.empty()
            
            for idx, url in enumerate(urls):
                status.text(f"Processing {idx+1}/{len(urls)}: {url}")
                analyzer.analyze_and_save(url)
                progress.progress((idx + 1) / len(urls))
                time.sleep(1)
            
            # Clear sidebar cache since we added new data
            if "sidebar_quick_stats" in st.session_state:
                del st.session_state["sidebar_quick_stats"]
            
            status.empty()
            progress.empty()
            show_success(f"Processed {len(urls)} leads!")
        
        # Recent leads
        st.markdown("---")
        st.markdown("### Recent Analyses")
        
        leads = self.data_manager.load_all(use_cache=True)
        
        # Check if we're showing test data  
        if (is_firecrawl_test or is_ai_test) and any(lead.id and lead.id >= 9000 for lead in leads):
            st.info("📊 **Test Mode**: Recent analyses below show sample data to demonstrate functionality")
        
        recent = sorted(leads, key=lambda x: x.timestamp, reverse=True)[:5]
        
        if recent:
            for lead in recent:
                with st.expander(f"{lead.company_name} - Score: {lead.lead_score}"):
                    render_lead_card(lead)
        else:
            st.info("No analyses yet. Enter a URL above to start analyzing prospects.")
    
    def render_dashboard(self):
        """Render dashboard page"""
        st.title("Dashboard & Analytics")
        
        leads = self.data_manager.load_all(use_cache=True)
        
        # Check if we're showing test data
        config_dict = self.config_manager.load(use_cache=True)
        config = AppConfig(**config_dict) if config_dict else AppConfig()
        is_test_mode = not config.has_valid_firecrawl_key() or not config.has_valid_ai_key()
        
        if is_test_mode and any(lead.id and lead.id >= 9000 for lead in leads):
            st.info("📊 **Test Mode**: Showing sample data to demonstrate functionality. Configure API keys in Settings for real data.")
        
        if not leads:
            show_info("No leads yet. Go to Lead Chat to analyze prospects!")
            return
        
        # Metrics
        st.markdown("### Key Metrics")
        render_metrics_row(leads)
        
        # Charts
        st.markdown("---")
        col1, col2 = st.columns(2)
        
        with col1:
            st.markdown("### Lead Qualification")
            st.plotly_chart(create_pie_chart(leads), use_container_width=True)
        
        with col2:
            st.markdown("### Score Distribution")
            st.plotly_chart(create_score_histogram(leads), use_container_width=True)
        
        # Industry
        st.markdown("---")
        st.markdown("### Industry Breakdown")
        st.plotly_chart(create_industry_bar_chart(leads), use_container_width=True)
        
        # Table
        st.markdown("---")
        st.markdown("### All Leads")
        
        df = pd.DataFrame([l.to_dict() for l in leads])
        display_cols = ['company_name', 'lead_score', 'industry', 'recommended_action', 'url']
        available_cols = [c for c in display_cols if c in df.columns]
        
        if available_cols:
            df_display = df[available_cols].rename(columns={
                'company_name': 'Company',
                'lead_score': 'Score',
                'industry': 'Industry',
                'recommended_action': 'Action',
                'url': 'URL'
            })
            df_display = df_display.sort_values('Score', ascending=False)
            st.dataframe(df_display, use_container_width=True, height=400)
        
        # Export
        st.markdown("---")
        st.markdown("### Export Data")
        
        col1, col2, col3 = st.columns([1, 1, 2])
        
        with col1:
            gdpr_safe = st.checkbox("GDPR Safe Mode", value=False)
        
        with col2:
            export_format = st.selectbox("Format", ["Excel (.xlsx)", "CSV (.csv)"])
        
        export_df = make_gdpr_safe(df) if gdpr_safe else df
        
        if export_format == "Excel (.xlsx)":
            buffer = io.BytesIO()
            with pd.ExcelWriter(buffer, engine='openpyxl') as writer:
                export_df.to_excel(writer, index=False, sheet_name='Leads')
            buffer.seek(0)
            
            st.download_button(
                "📥 Download Excel",
                data=buffer,
                file_name=f"leads_{datetime.now().strftime('%Y%m%d_%H%M%S')}.xlsx",
                mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"
            )
        else:
            csv = export_df.to_csv(index=False)
            st.download_button(
                "📥 Download CSV",
                data=csv,
                file_name=f"leads_{datetime.now().strftime('%Y%m%d_%H%M%S')}.csv",
                mime="text/csv"
            )    
    def render_knowledge_base(self, knowledge_base_service):
        """Render Knowledge Base management page"""
        st.title("Knowledge Base")
        st.markdown("Upload company documents to enhance AI analysis with your own content.")
        
        if not knowledge_base_service:
            st.error("Knowledge Base service not initialized. Please restart the application.")
            return
        
        # Get statistics
        stats = knowledge_base_service.get_stats()
        
        # Display enhanced stats
        st.markdown("### Knowledge Base Statistics")
        
        # Show all metrics in one row if documents exist
        if stats['total_documents'] > 0:
            col1, col2, col3, col4 = st.columns(4)
            with col1:
                st.metric("Documents", stats['total_documents'])
            with col2:
                st.metric("Chunks", stats['total_chunks'])
            with col3:
                st.metric("Characters", f"{stats.get('total_characters', 0):,}")
            with col4:
                st.metric("Tokens", f"{stats.get('total_tokens', 0):,}")
            
            # Second row with additional metrics
            col1, col2 = st.columns(2)
            with col1:
                st.metric("Est. Cost", f"${stats.get('total_embedding_cost', 0):.4f}")
            with col2:
                doc_types = ", ".join([f"{k.upper()}: {v}" for k, v in stats['doc_types'].items()])
                st.metric("Document Types", doc_types if doc_types else "None")
        else:
            # If no documents, show minimal stats
            col1, col2 = st.columns(2)
            with col1:
                st.metric("Documents", 0)
            with col2:
                st.metric("Chunks", 0)
        
        st.markdown("---")
        
        # Upload section
        st.markdown("### Upload Documents")
        st.info("📄 Supported formats: PDF, TXT, DOCX | Documents will be chunked and embedded for semantic search")
        
        uploaded_file = st.file_uploader(
            "Choose a file",
            type=['pdf', 'txt', 'docx'],
            help="Upload documents containing company information, product details, case studies, etc."
        )
        
        if uploaded_file:
            col1, col2 = st.columns([3, 1])
            
            with col1:
                st.write(f"**File:** {uploaded_file.name}")
                st.write(f"**Size:** {uploaded_file.size / 1024:.1f} KB")
            
            with col2:
                if st.button("Upload & Index", type="primary", use_container_width=True):
                    with st.spinner("Processing document..."):
                        # Save temporary file
                        temp_path = f"data/temp_{uploaded_file.name}"
                        with open(temp_path, "wb") as f:
                            f.write(uploaded_file.getbuffer())
                        
                        # Add to knowledge base
                        success, message, document = knowledge_base_service.add_document(
                            temp_path,
                            uploaded_file.name
                        )
                        
                        # Clean up temp file
                        import os
                        if os.path.exists(temp_path):
                            os.remove(temp_path)
                        
                        if success:
                            st.success(f"✅ {message}")
                            st.info(f"Created {document.num_chunks} searchable chunks")
                            time.sleep(1)
                            st.rerun()
                        else:
                            st.error(f"❌ {message}")
        
        st.markdown("---")
        
        # Document list
        st.markdown("### Uploaded Documents")
        
        documents = knowledge_base_service.list_documents()
        
        if not documents:
            st.info("No documents uploaded yet. Upload your first document above.")
        else:
            for doc in documents:
                with st.expander(f"📄 {doc.filename} ({doc.get_display_size()})"):
                    col1, col2 = st.columns([3, 1])
                    
                    with col1:
                        st.write(f"**Type:** {doc.doc_type.upper()} • **Size:** {doc.get_display_size()}")
                        st.write(f"**Uploaded:** {doc.get_upload_date_formatted()}")
                        
                        # Enhanced metrics
                        metrics_col1, metrics_col2, metrics_col3 = st.columns(3)
                        with metrics_col1:
                            st.metric("Characters", doc.get_formatted_char_count())
                        with metrics_col2:
                            st.metric("Est. Tokens", doc.get_formatted_token_count())
                        with metrics_col3:
                            st.metric("Chunks", doc.num_chunks)
                        
                        # Additional info
                        st.write(f"**Avg chunk size:** {doc.avg_chunk_size:.0f} chars")
                        st.write(f"**Embedding cost estimate:** {doc.get_formatted_cost()} (if using OpenAI)")
                        st.write(f"**Last modified:** {doc.get_upload_date_formatted()}")
                        
                        # Full preview (collapsible)
                        if doc.content:
                            with st.expander("View full preview"):
                                st.text(doc.content[:1000] + "..." if len(doc.content) > 1000 else doc.content)
                    
                    with col2:
                        if st.button("🗑️ Delete", key=f"delete_{doc.id}", use_container_width=True):
                            success, message = knowledge_base_service.delete_document(doc.id)
                            if success:
                                st.success(message)
                                time.sleep(1)
                                st.rerun()
                            else:
                                st.error(message)
        
        # Test search section
        if documents:
            st.markdown("---")
            st.markdown("### Test Search")
            st.markdown("Try searching your knowledge base to see what context would be retrieved.")
            
            search_query = st.text_input("Enter search query", placeholder="e.g., product features, pricing, case studies")
            
            if search_query:
                with st.spinner("Searching..."):
                    results = knowledge_base_service.search(search_query, k=3)
                    
                    if results:
                        st.success(f"Found {len(results)} relevant chunks:")
                        for i, result in enumerate(results, 1):
                            st.markdown(f"**Result {i}** (Score: {result['score']:.3f}) - Source: {result['metadata'].get('source', 'Unknown')}")
                            st.text(result['content'][:400] + "..." if len(result['content']) > 400 else result['content'])
                            st.markdown("---")
                    else:
                        st.warning("No relevant results found")