import streamlit as st
from streamlit_option_menu import option_menu
from utils.ui import load_css, load_lottieurl
from pages_impl import home, stocks, indices, forex, funds, crypto, portfolio, analysis, tools, macro

# Page Config
st.set_page_config(
    page_title="BorsaPY Dashboard",
    page_icon="📈",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Load Styles
load_css("assets/style.css")

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
            "Hisse Senetleri", 
            "Endeksler", 
            "Döviz & Altın", 
            "Yatırım Fonları",
            "Makroekonomi",
            "Kripto",
            "Portföy",
            "Teknik Analiz",
            "Araçlar (Beta)"
        ],
        icons=[
            "house", 
            "graph-up-arrow", 
            "list-ol", 
            "currency-exchange", 
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
            "icon": {"color": "#00d2ff", "font-size": "16px"}, 
            "nav-link": {"font-size": "14px", "text-align": "left", "margin":"0px", "--hover-color": "rgba(255,255,255,0.1)"},
            "nav-link-selected": {"background-color": "rgba(0, 210, 255, 0.15)", "border-left": "3px solid #00d2ff"},
        }
    )
    
    st.markdown("---")
    st.caption("Developed with ❤️ using borsapy")

# Routing
if selected == "Ana Sayfa":
    home.app()
elif selected == "Hisse Senetleri":
    stocks.app()
elif selected == "Endeksler":
    indices.app()
elif selected == "Döviz & Altın":
    forex.app()
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
