import streamlit as st
from streamlit_option_menu import option_menu
from utils.ui import load_css, load_lottieurl
from pages_impl import home, stocks, indices, forex, funds, crypto, portfolio, analysis, tools, macro, viop, bonds, ai_assistant

# Page Config
st.set_page_config(
    page_title="BorsaPY Dashboard",
    page_icon="📈",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Load Styles
css_content = load_css("assets/style.css")
if css_content:
    st.markdown(f'<style>{css_content}</style>', unsafe_allow_html=True)

# Sidebar Navigation
with st.sidebar:
    # Logo Area (Text for now, could be image)
    st.markdown("""
        <div style='text-align: center; padding: 20px;'>
            <h2 style='color: #00d2ff; margin:0;'>BorsaPY</h2>
            <p style='font-size: 12px; opacity: 0.7;'>v2.0 Pro Dashboard</p>
        </div>
    """, unsafe_allow_html=True)
    
    selected = option_menu(
        menu_title=None,
        options=[
            "Ana Sayfa", 
            "🤖 AI Asistan",
            "Hisse Senetleri", 
            "Endeksler", 
            "VIOP",
            "Döviz & Altın", 
            "Tahvil & Bono",
            "Yatırım Fonları",
            "Makroekonomi",
            "Kripto",
            "Portföy",
            "Teknik Analiz",
            "Araçlar (Beta)"
        ],
        icons=[
            "house", 
            "robot",
            "graph-up-arrow", 
            "list-ol", 
            "graph-up",
            "currency-exchange", 
            "cash-coin",
            "piggy-bank",
            "globe", 
            "currency-bitcoin",
            "briefcase",
            "activity",
            "tools"
        ],
        menu_icon="cast",
        default_index=0,
        styles={
            "container": {"padding": "0!important", "background-color": "transparent"},
            "icon": {"color": "#a1a1aa", "font-size": "16px"}, 
            "nav-link": {"font-size": "14px", "text-align": "left", "margin":"0px", "--hover-color": "#18181b", "color": "#a1a1aa"},
            "nav-link-selected": {"background-color": "#18181b", "border-left": "3px solid #3b82f6", "color": "#f4f4f5"},
        }
    )
    
    st.markdown("---")
    st.caption("Developed with ❤️ using borsapy")

# Routing
if selected == "Ana Sayfa":
    home.app()
elif selected == "🤖 AI Asistan":
    ai_assistant.app()
elif selected == "Hisse Senetleri":
    stocks.app()
elif selected == "Endeksler":
    indices.app()
elif selected == "VIOP":
    viop.app()
elif selected == "Döviz & Altın":
    forex.app()
elif selected == "Tahvil & Bono":
    bonds.app()
elif selected == "Yatırım Fonları":
    funds.app()
elif selected == "Makroekonomi":
    macro.app()
elif selected == "Kripto":
    crypto.app()
elif selected == "Portföy":
    portfolio.app()
elif selected == "Teknik Analiz":
    analysis.app()
elif selected == "Araçlar (Beta)":
    tools.app()
