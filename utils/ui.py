import streamlit as st
import json
import requests

def load_css(file_name):
    with open(file_name) as f:
        st.markdown(f'<style>{f.read()}</style>', unsafe_allow_html=True)

def load_lottieurl(url: str):
    r = requests.get(url)
    if r.status_code != 200:
        return None
    return r.json()

def render_header(title, subtitle=None):
    st.markdown(f"""
    <div class="animate-fade-in">
        <h1 style="color: #00d2ff;">{title}</h1>
        {f'<p style="font-size: 18px; opacity: 0.8;">{subtitle}</p>' if subtitle else ''}
        <hr style="border-color: rgba(255,255,255,0.1);">
    </div>
    """, unsafe_allow_html=True)

def metric_card(label, value, delta=None, color="normal", icon=None):
    delta_html = ""
    if delta:
        # Determine color based on delta content (auto-detect negative sign)
        is_negative = str(delta).strip().startswith("-")
        delta_color = "#ff0055" if is_negative else "#00ff88"
        
        # Add arrow
        arrow = "▼" if is_negative else "▲"
        delta_html = f'<span style="color: {delta_color}; font-size: 0.85em; margin-left: 8px; font-weight: 500;">{arrow} {delta}</span>'
    
    icon_div = f'<div style="font-size: 1.5em; margin-bottom: 8px; color: #00d2ff;">{icon}</div>' if icon else ""

    html_content = f"""<div class="custom-card animate-fade-in">
{icon_div}
<div style="font-size: 0.85em; opacity: 0.6; margin-bottom: 6px; letter-spacing: 1px; text-transform: uppercase; font-weight: 600;">{label}</div>
<div style="font-size: 2em; font-weight: 800; background: linear-gradient(90deg, #fff, #a0c4ff); -webkit-background-clip: text; -webkit-text-fill-color: transparent; text-shadow: 0 0 20px rgba(0, 119, 255, 0.3);">{value} {delta_html}</div>
</div>"""
    st.markdown(html_content, unsafe_allow_html=True)

def apply_chart_style(fig):
    """Applies the Neo-Fintech theme to Plotly figures."""
    fig.update_layout(
        paper_bgcolor='rgba(0,0,0,0)',
        plot_bgcolor='rgba(0,0,0,0)',
        font=dict(family="Outfit, sans-serif", color="#a0a5b9"),
        xaxis=dict(
            gridcolor='rgba(255,255,255,0.05)',
            zerolinecolor='rgba(255,255,255,0.05)'
        ),
        yaxis=dict(
            gridcolor='rgba(255,255,255,0.05)',
            zerolinecolor='rgba(255,255,255,0.05)'
        ),
        hoverlabel=dict(
            bgcolor="#141928",
            bordercolor="rgba(255,255,255,0.1)",
            font=dict(color="white")
        ),
        margin=dict(l=20, r=20, t=40, b=20),
    )
    return fig
