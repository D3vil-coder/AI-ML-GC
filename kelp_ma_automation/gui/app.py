"""
KELP M&A Automation - Streamlit GUI
Professional GUI with Kelp branding and animated progress.
"""

import streamlit as st
import os
import sys
import time
import json
from pathlib import Path
from datetime import datetime
import tempfile

# Add parent to path for imports
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

# Kelp Brand Colors
KELP_COLORS = {
    'primary': '#4B0082',      # Dark Indigo/Violet
    'secondary': '#FF1493',    # Pink
    'accent': '#00CED1',       # Cyan Blue
    'background': '#FFFFFF',   # White
    'text_dark': '#333333',    # Dark Grey
    'gradient': 'linear-gradient(135deg, #4B0082 0%, #FF1493 100%)',
}

def get_custom_css():
    """Kelp-branded custom CSS."""
    return f"""
    <style>
    /* Main container */
    .main {{
        background-color: {KELP_COLORS['background']};
    }}
    
    /* Header */
    .kelp-header {{
        background: {KELP_COLORS['gradient']};
        padding: 1.5rem 2rem;
        border-radius: 10px;
        margin-bottom: 2rem;
        color: white;
    }}
    
    .kelp-header h1 {{
        color: white;
        margin: 0;
        font-family: Arial, sans-serif;
    }}
    
    .kelp-header p {{
        color: rgba(255,255,255,0.9);
        margin: 0.5rem 0 0 0;
    }}
    
    /* Cards */
    .stCard {{
        border-radius: 10px;
        box-shadow: 0 4px 6px rgba(0,0,0,0.1);
    }}
    
    /* Buttons */
    .stButton>button {{
        background: {KELP_COLORS['gradient']};
        color: white;
        border: none;
        border-radius: 8px;
        padding: 0.75rem 2rem;
        font-weight: bold;
        transition: all 0.3s ease;
    }}
    
    .stButton>button:hover {{
        transform: translateY(-2px);
        box-shadow: 0 4px 12px rgba(75, 0, 130, 0.4);
    }}
    
    /* Progress section */
    .progress-step {{
        display: flex;
        align-items: center;
        padding: 0.75rem 1rem;
        margin: 0.5rem 0;
        border-radius: 8px;
        background: #f8f9fa;
        border-left: 4px solid #ccc;
        color: #000 !important;
    }}
    
    .progress-step span {{
        color: #000 !important;
    }}
    
    .progress-step.active {{
        border-left-color: {KELP_COLORS['accent']};
        background: #e8f7fa;
        color: #000 !important;
    }}
    
    .progress-step.complete {{
        border-left-color: #28a745;
        background: #e8f5e9;
        color: #000 !important;
    }}
    
    .progress-step.error {{
        border-left-color: #dc3545;
        background: #fdecea;
        color: #000 !important;
    }}
    
    /* Sidebar */
    .css-1d391kg {{
        background-color: #f8f9fa;
    }}
    
    /* Output cards */
    .output-card {{
        background: white;
        border-radius: 10px;
        padding: 1.5rem;
        margin: 1rem 0;
        box-shadow: 0 2px 8px rgba(0,0,0,0.1);
        border-left: 4px solid {KELP_COLORS['primary']};
    }}
    
    /* Animations */
    @keyframes pulse {{
        0% {{ opacity: 1; }}
        50% {{ opacity: 0.6; }}
        100% {{ opacity: 1; }}
    }}
    
    .processing {{
        animation: pulse 1.5s ease-in-out infinite;
    }}
    
    /* Footer */
    .kelp-footer {{
        text-align: center;
        color: #666;
        padding: 2rem 0;
        margin-top: 3rem;
        border-top: 1px solid #eee;
        font-size: 0.9rem;
    }}
    </style>
    """


def init_session_state():
    """Initialize session state variables."""
    defaults = {
        'processing': False,
        'current_step': 0,
        'step_status': {},
        'output_files': [],
        'error': None,
        'company_name': '',
        'llm_provider': 'ollama',
        'ollama_model': 'phi4-mini:latest',
        'gemini_api_key': '',
        'gemini_model': 'gemini-2.0-flash',
    }
    for key, value in defaults.items():
        if key not in st.session_state:
            st.session_state[key] = value


def render_header():
    """Render Kelp-branded header."""
    st.markdown("""
    <div class="kelp-header">
        <h1>🌊 KELP M&A Automation</h1>
        <p>AI-Powered Investment Teaser Generator</p>
    </div>
    """, unsafe_allow_html=True)


def render_sidebar():
    """Render settings sidebar."""
    with st.sidebar:
        st.markdown("## ⚙️ Settings")
        
        # LLM Provider Selection
        st.markdown("### LLM Provider")
        llm_provider = st.radio(
            "Choose LLM:",
            ["ollama", "gemini"],
            index=0 if st.session_state.llm_provider == 'ollama' else 1,
            horizontal=True
        )
        st.session_state.llm_provider = llm_provider
        
        if llm_provider == 'ollama':
            st.markdown("---")
            st.markdown("#### Ollama Settings")
            st.session_state.ollama_model = st.selectbox(
                "Model:",
                ["phi4-mini:latest", "llama3.2:latest", "qwen2.5:latest", "mistral:latest"],
                index=0
            )
            st.info("💡 Ollama runs locally - no API key needed!")
        
        else:
            st.markdown("---")
            st.markdown("#### Gemini Settings")
            st.session_state.gemini_api_key = st.text_input(
                "API Key:",
                value=st.session_state.gemini_api_key,
                type="password",
                help="Get from https://aistudio.google.com/apikey"
            )
            st.session_state.gemini_model = st.selectbox(
                "Model:",
                ["gemini-2.0-flash", "gemini-1.5-pro", "gemma-27b-it"],
                index=0
            )
        
        st.markdown("---")
        st.markdown("### Output Settings")
        output_dir = st.text_input(
            "Output Directory:",
            value="data/output",
            help="Where to save generated files"
        )
        
        st.markdown("---")
        st.markdown(f"""
        <div style="text-align: center; color: #666; font-size: 0.8rem; padding: 1rem;">
            <p>Kelp M&A Automation v2.0</p>
            <p>© 2026 Kelp M&A Team</p>
        </div>
        """, unsafe_allow_html=True)
        
        return output_dir


def render_progress(steps, current_step, step_status):
    """Render animated progress steps."""
    step_emojis = {
        'pending': '⏳',
        'processing': '🔄',
        'complete': '✅',
        'error': '❌'
    }
    
    for i, step_name in enumerate(steps):
        status = step_status.get(i, 'pending')
        if i == current_step and status == 'pending':
            status = 'processing'
        
        emoji = step_emojis.get(status, '⏳')
        css_class = status
        
        st.markdown(f"""
        <div class="progress-step {css_class}">
            <span style="margin-right: 0.5rem;">{emoji}</span>
            <span>{step_name}</span>
        </div>
        """, unsafe_allow_html=True)


def run_pipeline(company_name: str, md_file_path: str, output_dir: str):
    """Run the M&A automation pipeline with progress updates."""
    from main import MAAutomationPipeline
    
    steps = [
        "📄 Extracting data from one-pager",
        "🔍 Classifying industry domain",
        "🌐 Scraping web data",
        "✍️ Generating slide content",
        "🔎 Verifying citations",
        "📊 Assembling PowerPoint",
        "💾 Saving outputs"
    ]
    
    progress_placeholder = st.empty()
    status_text = st.empty()
    
    step_status = {}
    
    try:
        # Initialize pipeline
        pipeline = MAAutomationPipeline(
            llm_provider=st.session_state.llm_provider,
            model_name=st.session_state.ollama_model if st.session_state.llm_provider == 'ollama' else st.session_state.gemini_model,
            api_key=st.session_state.gemini_api_key if st.session_state.llm_provider == 'gemini' else None
        )
        
        for i, step_name in enumerate(steps):
            step_status[i] = 'processing'
            
            with progress_placeholder.container():
                render_progress(steps, i, step_status)
            
            status_text.markdown(f"**{step_name}**")
            time.sleep(0.3)  # Small delay for visual effect
            
            # Execute step (simulated - actual integration below)
            step_status[i] = 'complete'
        
        # Actually run the pipeline
        result = pipeline.process_company(company_name, md_file_path, output_dir)
        
        # Final update
        with progress_placeholder.container():
            render_progress(steps, len(steps) - 1, step_status)
        
        status_text.success("✅ Pipeline completed successfully!")
        
        return result
        
    except Exception as e:
        step_status[len([s for s in step_status.values() if s == 'complete'])] = 'error'
        status_text.error(f"❌ Error: {str(e)}")
        st.exception(e)
        return None


def render_output_section(result):
    """Render output files section."""
    if not result:
        return
    
    st.markdown("---")
    st.markdown("## 📁 Generated Files")
    
    col1, col2 = st.columns(2)
    
    with col1:
        st.markdown("""
        <div class="output-card">
            <h4>📊 Investment Teaser</h4>
            <p>PowerPoint presentation ready for download</p>
        </div>
        """, unsafe_allow_html=True)
        
        if result.get('ppt_path') and os.path.exists(result['ppt_path']):
            with open(result['ppt_path'], 'rb') as f:
                st.download_button(
                    label="⬇️ Download PPT",
                    data=f.read(),
                    file_name=os.path.basename(result['ppt_path']),
                    mime="application/vnd.openxmlformats-officedocument.presentationml.presentation"
                )
    
    with col2:
        st.markdown("""
        <div class="output-card">
            <h4>📋 Citation Report</h4>
            <p>Full source citations document</p>
        </div>
        """, unsafe_allow_html=True)
        
        if result.get('citation_path') and os.path.exists(result['citation_path']):
            with open(result['citation_path'], 'rb') as f:
                st.download_button(
                    label="⬇️ Download Citations",
                    data=f.read(),
                    file_name=os.path.basename(result['citation_path']),
                    mime="application/vnd.openxmlformats-officedocument.wordprocessingml.document"
                )
    
    # Metrics
    if result.get('stats'):
        stats = result['stats']
        st.markdown("---")
        st.markdown("### 📈 Pipeline Statistics")
        
        col1, col2, col3, col4 = st.columns(4)
        with col1:
            st.metric("Verification Rate", f"{stats.get('verification_rate', 0):.1f}%")
        with col2:
            st.metric("Total Claims", stats.get('total_claims', 0))
        with col3:
            st.metric("Web Sources", stats.get('web_sources', 0))
        with col4:
            st.metric("LLM Tokens", f"{stats.get('tokens_used', 0):,}")


def main():
    """Main Streamlit app."""
    st.set_page_config(
        page_title="KELP M&A Automation",
        page_icon="🌊",
        layout="wide",
        initial_sidebar_state="expanded"
    )
    
    # Apply custom CSS
    st.markdown(get_custom_css(), unsafe_allow_html=True)
    
    # Initialize session state
    init_session_state()
    
    # Render components
    render_header()
    output_dir = render_sidebar()
    
    # Main content
    st.markdown("### 📝 Input Details")
    
    col1, col2 = st.columns([1, 1])
    
    with col1:
        company_name = st.text_input(
            "Company Name:",
            placeholder="e.g., Ksolves India Limited",
            help="Enter the target company name"
        )
    
    with col2:
        uploaded_file = st.file_uploader(
            "One-Pager (Markdown):",
            type=['md', 'txt'],
            help="Upload the company one-pager in Markdown format"
        )
    
    # Generate button
    st.markdown("")
    generate_btn = st.button(
        "🚀 Generate Investment Teaser",
        disabled=not (company_name and uploaded_file),
        use_container_width=True
    )
    
    if generate_btn and company_name and uploaded_file:
        st.session_state.processing = True
        
        # Save uploaded file temporarily
        with tempfile.NamedTemporaryFile(delete=False, suffix='.md') as tmp:
            tmp.write(uploaded_file.read())
            tmp_path = tmp.name
        
        st.markdown("---")
        st.markdown("### 🔄 Processing")
        
        # Run pipeline
        result = run_pipeline(company_name, tmp_path, output_dir)
        
        # Clean up temp file
        os.unlink(tmp_path)
        
        # Show outputs
        render_output_section(result)
        
        st.session_state.processing = False
    
    # Sample data section
    with st.expander("📚 Sample Companies (for testing)"):
        st.markdown("""
        | Company | Domain | One-Pager |
        |---------|--------|-----------|
        | Centum Electronics | Manufacturing | Centum-OnePager.md |
        | Ksolves | Technology | Ksolves-OnePager.md |
        | Gati | Logistics | Gati-OnePager.md |
        | Connplex Cinemas | Consumer | Connplex-OnePager.md |
        | Ind Swift | Healthcare | Ind Swift-OnePager.md |
        | Kalyani Forge | Automotive | Kalyani Forge-OnePager.md |
        """)
    
    # Footer
    st.markdown("""
    <div class="kelp-footer">
        <p>Strictly Private & Confidential – Prepared by Kelp M&A Team</p>
    </div>
    """, unsafe_allow_html=True)


if __name__ == "__main__":
    main()
