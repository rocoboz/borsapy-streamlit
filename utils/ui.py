import streamlit as st
from html import escape
import json
import requests

def load_css(file_name):
    with open(file_name) as f:
        st.markdown(f'<style>{f.read()}</style>', unsafe_allow_html=True)

def load_lottieurl(url: str):
    try:
        r = requests.get(url, timeout=6)
        r.raise_for_status()
    except requests.RequestException:
        return None
    return r.json()

def render_header(title, subtitle=None):
    safe_title = escape(str(title))
    safe_subtitle = escape(str(subtitle)) if subtitle else None
    st.markdown(f"""
    <div class="animate-fade-in" style="margin-bottom: 24px;">
        <h1 style="color: #2d3748; margin-bottom: 4px;">{safe_title}</h1>
        {f'<p style="font-size: 16px; color: #718096; margin-top: 0;">{safe_subtitle}</p>' if safe_subtitle else ''}
    </div>
    """, unsafe_allow_html=True)

def metric_card(label, value, delta=None, color="normal", icon=None):
    safe_label = escape(str(label))
    safe_value = escape(str(value))
    delta_html = ""
    if delta:
        safe_delta = escape(str(delta))
        is_negative = str(delta).strip().startswith("-")
        delta_color = "#e53e3e" if is_negative else "#48bb78"
        arrow = "▼" if is_negative else "▲"
        delta_html = f'<div style="color: {delta_color}; font-size: 0.85em; margin-top: 8px; font-weight: 600;">{arrow} {safe_delta}</div>'
    
    # We apply the card-header-dark class to the label for the "modern flat" look
    header_html = f'<div class="card-header-dark">{safe_label}</div>'

    icon_html = f'<div style="position: absolute; top: 12px; right: 20px; font-size: 1.2em; color: rgba(255,255,255,0.8);">{escape(str(icon))}</div>' if icon else ""

    html_content = f"""<div class="custom-card animate-fade-in" style="padding-top: 48px;">
{header_html}
{icon_html}
<div style="font-size: 2.2em; font-weight: 700; color: #2d3748; line-height: 1.1;">{safe_value}</div>
{delta_html}
</div>"""
    st.markdown(html_content, unsafe_allow_html=True)

def apply_chart_style(fig):
    """Applies the Light Modern theme to Plotly figures."""
    fig.update_layout(
        paper_bgcolor='rgba(0,0,0,0)',
        plot_bgcolor='rgba(0,0,0,0)',
        font=dict(family="Outfit, sans-serif", color="#4a5568"),
        xaxis=dict(
            gridcolor='rgba(0,0,0,0.05)',
            zerolinecolor='rgba(0,0,0,0.05)'
        ),
        yaxis=dict(
            gridcolor='rgba(0,0,0,0.05)',
            zerolinecolor='rgba(0,0,0,0.05)'
        ),
        margin=dict(l=20, r=20, t=40, b=20),
        hoverlabel=dict(
            bgcolor="#ffffff",
            font_size=14,
            font_family="Outfit"
        )
    )
    return fig
