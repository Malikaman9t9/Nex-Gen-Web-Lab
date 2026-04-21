import streamlit as st
import os
from streamlit_option_menu import option_menu
from dotenv import load_dotenv
import time
import pandas as pd
from urllib.parse import urlparse
import plotly.graph_objects as go
import plotly.express as px
from datetime import datetime, timedelta
import zipfile
import io

# Load APIs
load_dotenv()
SPEED_API_KEY = os.getenv("SPEED_API_KEY")
GEMINI_API_KEY = os.getenv("GEMINI_API_KEY")
RAPIDAPI_KEY = os.getenv("RAPIDAPI_KEY")

# Import Modules
try:
    from modules.onpage_scraper import get_basic_onpage
    from modules.speed_checker import check_speed
    from modules.ai_analyzer import get_ai_suggestions
    from modules.report_export import generate_word_report
    from modules.traffic_checker import get_traffic_data
except ImportError as e:
    st.error(f"Critical Error: Missing module file. {e}")
    st.stop()

# --- VIP PAGE CONFIG & THEME ---
st.set_page_config(page_title="NexGenWebLab VIP | Enterprise SEO", layout="wide", initial_sidebar_state="expanded")

# Load FontAwesome & Google Fonts
st.markdown('<link rel="stylesheet" href="https://cdnjs.cloudflare.com/ajax/libs/font-awesome/6.4.0/css/all.min.css">', unsafe_allow_html=True)
st.markdown('<link href="https://fonts.googleapis.com/css2?family=Inter:wght@400;500;600;700;800;900&display=swap" rel="stylesheet">', unsafe_allow_html=True)

# --- ADVANCED CUSTOM CSS (PERFECT UI ALIGNMENT) ---
st.markdown("""
<style>
    /* Global Styles */
    * { font-family: 'Inter', sans-serif; }
    .block-container { padding-top: 1rem; padding-bottom: 2rem; max-width: 1300px; }
    body { background-color: #f8fafc; }
    
    /* Sidebar Styling */
    [data-testid="stSidebar"] { background-color: #ffffff; border-right: 1px solid #e2e8f0; }
    
    /* Hero Section */
    .hero-container { text-align: center; padding: 30px 10px; }
    .hero-title { font-size: 46px; font-weight: 900; color: #0f172a; line-height: 1.1; margin-bottom: 15px; }
    .hero-title span { background: linear-gradient(135deg, #6D28D9, #DB2777); -webkit-background-clip: text; -webkit-text-fill-color: transparent; }
    .hero-subtitle { font-size: 18px; color: #64748b; max-width: 600px; margin: 0 auto 30px auto; }
    
    /* --- CRITICAL FIX: SEARCH BAR VERTICAL & HORIZONTAL ALIGNMENT --- */
    div[data-testid="stHorizontalBlock"] { align-items: center !important; }
    
    .stTextInput div[data-baseweb="base-input"] { 
        height: 56px !important; 
        border-radius: 8px !important; 
        border: 2px solid #e2e8f0 !important; 
        background-color: #ffffff !important; 
        display: flex !important;
        align-items: center !important;
    }
    
    .stTextInput input { 
        height: 54px !important; 
        line-height: normal !important; 
        padding-top: 0px !important;
        padding-bottom: 0px !important;
        font-size: 16px !important; 
        text-align: left !important; 
        padding-left: 20px !important;
        font-weight: 500 !important;
        color: #0f172a !important;
    }
    
    .stTextInput div[data-baseweb="base-input"]:focus-within { 
        border-color: #6D28D9 !important; 
        box-shadow: 0 0 0 3px rgba(109, 40, 217, 0.1) !important; 
    }
    
    div.stButton > button[kind="primary"] { 
        height: 56px !important; 
        border-radius: 8px !important; 
        font-size: 16px !important; 
        font-weight: 800 !important; 
        background: linear-gradient(135deg, #6D28D9, #DB2777) !important; 
        color: white !important; 
        border: none !important; 
        width: 100% !important; 
        text-transform: uppercase !important; 
        letter-spacing: 1px !important;
        display: flex !important;
        justify-content: center !important; 
        align-items: center !important;
        margin: 0 !important;
    }
    div.stButton > button[kind="primary"]:hover { box-shadow: 0 6px 20px rgba(219, 39, 119, 0.3) !important; transform: translateY(-1px); }
    
    /* Score Overview Section */
    .score-container { background: #ffffff; border-radius: 16px; padding: 30px; border: 1px solid #e2e8f0; box-shadow: 0 10px 15px -3px rgba(0,0,0,0.01); margin-bottom: 30px;}
    
    /* Issue Cards */
    .issue-card { border-radius: 12px; padding: 25px; background: #f8fafc; border: 1px solid #e2e8f0; display: flex; flex-direction: column; justify-content: center; height: 100%;}
    .issue-count { font-size: 48px; font-weight: 900; line-height: 1; margin-bottom: 5px; }
    .issue-label { font-size: 14px; font-weight: 700; color: #64748b; text-transform: uppercase; letter-spacing: 0.5px; }
    
    /* VIP Tabs */
    .stTabs [data-baseweb="tab-list"] { gap: 10px; border-bottom: none; margin-bottom: 25px; background: #e2e8f0; padding: 8px; border-radius: 14px; }
    .stTabs [data-baseweb="tab"] { height: 45px; font-size: 15px; font-weight: 700; color: #475569; background-color: transparent; border-radius: 10px; border: none; padding: 0 20px; }
    .stTabs [aria-selected="true"] { background: linear-gradient(135deg, #6D28D9, #DB2777) !important; color: white !important; }

    /* VIP Data Containers */
    .audit-item { 
        background: #ffffff; 
        border: 1px solid #e2e8f0; 
        border-radius: 12px; 
        padding: 20px; 
        margin-bottom: 15px; 
        position: relative; 
        overflow: hidden; 
        display: flex; 
        flex-direction: column; 
        height: calc(100% - 15px); 
    }
    .audit-item::before { content:''; position: absolute; left: 0; top: 0; height: 100%; width: 4px; }
    
    .status-danger::before { background-color: #ef4444; }
    .status-warning::before { background-color: #f59e0b; }
    .status-success::before { background-color: #10b981; }
    .status-info::before { background-color: #3b82f6; }

    .audit-header { display: flex; align-items: center; width: 100%; }
    .audit-header i { font-size: 20px; margin-right: 18px; width: 26px; text-align: center; } 
    .audit-item-content { display: flex; flex-direction: column; flex-grow: 1; }
    .audit-item-title { font-size: 15px; font-weight: 700; color: #0f172a; margin-bottom: 2px;}
    .audit-item-desc { font-size: 13px; color: #475569; line-height: 1.4; }
    
    .actual-data-box { 
        margin-top: 15px; 
        margin-bottom: 5px; 
        margin-left: 44px; 
        padding: 12px 14px; 
        background-color: #f8fafc; 
        border-radius: 8px; 
        font-size: 13px; 
        color: #334155; 
        word-break: break-word; 
        border: 1px solid #e2e8f0; 
        font-family: monospace; 
        flex-grow: 1; 
    }
    
    details.seo-tip { margin-top: 10px; margin-left: 44px; border-top: 1px dashed #e2e8f0; padding-top: 10px; }
    details.seo-tip summary { font-size: 12px; font-weight: 600; color: #6D28D9; cursor: pointer; outline: none; list-style: none;}
    details.seo-tip summary::after { content: ' +'; }
    details.seo-tip[open] summary::after { content: ' -'; }
    details.seo-tip p { margin: 8px 0 0 0; font-size: 12px; color: #475569; background: #f1f5f9; padding: 10px; border-left: 3px solid #6D28D9; border-radius: 4px; }
    
    /* Speed Metrics Cards */
    .speed-metric-card {
        background: #ffffff; border: 1px solid #e2e8f0; border-radius: 8px; padding: 15px 20px; margin-bottom: 12px; display: flex; justify-content: space-between; align-items: center; box-shadow: 0 1px 3px rgba(0,0,0,0.02); height: 60px;
    }
</style>
""", unsafe_allow_html=True)

# --- HELPER FUNCTIONS ---

def render_overview_donut(score):
    color = "#ef4444" if score < 50 else "#f59e0b" if score < 90 else "#10b981"
    fig = go.Figure(go.Pie(
        values=[max(score, 0), max(100-score, 0)],
        labels=["Score", "Remaining"], hole=.8,
        marker_colors=[color, "#f1f5f9"], textinfo='none', hoverinfo='none',
    ))
    fig.update_layout(
        annotations=[dict(text=str(int(score)), x=0.5, y=0.5, font_size=45, font_weight=900, font_color='#0f172a', showarrow=False)],
        showlegend=False, margin=dict(l=0, r=0, t=0, b=0), height=180,
        paper_bgcolor='rgba(0,0,0,0)', plot_bgcolor='rgba(0,0,0,0)'
    )
    return fig

# FIXED: Now strictly accepts ONLY ONE argument (score)
def render_small_gauge(score):
    color = "#ef4444" if score < 50 else "#f59e0b" if score < 90 else "#10b981"
    fig = go.Figure(go.Pie(
        values=[max(score, 0), max(100-score, 0)],
        labels=["Score", "Remaining"], hole=.75,
        marker_colors=[color, "#f1f5f9"], textinfo='none', hoverinfo='none',
    ))
    fig.update_layout(
        annotations=[dict(text=str(int(score)), x=0.5, y=0.5, font_size=24, font_weight=800, font_color='#0f172a', showarrow=False)],
        showlegend=False, margin=dict(l=0, r=0, t=10, b=10), height=110,
        paper_bgcolor='rgba(0,0,0,0)', plot_bgcolor='rgba(0,0,0,0)'
    )
    return fig

def get_audit_status_vip(v, type):
    tips = {
        "title": "Keep title between 30-60 chars.", "meta": "Write description between 150-160 chars.",
        "h1": "Page must have exactly one H1 tag.", "images": "Add descriptive ALT attributes to images.",
        "word_count": "Aim for 300+ words.", "schema": "Implement JSON-LD Schema markup.",
        "https": "Ensure SSL is active.", "html_size": "Keep HTML under 100KB.",
        "response_time": "Optimize server response time (<0.2s).", "minified_css": "Minify CSS files.",
        "minified_js": "Minify Javascript files.", "canonical": "Set self-referencing canonical URL.",
        "meta_robots": "Set proper meta robots tags.", "lang": "Declare language attribute.",
        "og": "Set Open Graph tags.", "dir_listing": "Secure your server directories.",
        "internal_links": "Ensure internal linking structure is strong.", "external_links": "Link out to authoritative sites."
    }

    actual = "N/A"
    try:
        if type == "title": actual = str(v.get('title', 'Missing')) if isinstance(v, dict) else str(v)
        elif type == "meta": actual = str(v.get('description', 'Missing')) if isinstance(v, dict) else str(v)
        elif type == "h1": actual = ", ".join([str(h) for h in v if h]) if isinstance(v, list) and v else "No H1 tags found."
        elif type == "images": actual = f"{int(v)} images without ALT detected." if v and int(v) > 0 else "All images optimized."
        elif type == "word_count": actual = f"Content length: {int(v) if v else 0} words."
        elif type == "https": actual = "SSL active (Secure)." if str(v) == "Yes" else "No SSL (Insecure)."
        elif type == "schema": actual = f"Found: {', '.join([str(s) for s in v])}" if isinstance(v, list) and v else "Missing Schema markup."
        elif type == "response_time": actual = f"Response Time: {float(v):.2f}s." if v else "0.0s"
        elif type == "html_size": actual = f"HTML Size: {float(v):.1f} KB." if v else "0.0 KB"
        elif type in ["minified_css", "minified_js"]: actual = f"{int(v)} unminified files detected." if v and int(v) > 0 else "Files minified."
        elif type == "dir_listing": actual = "Secured." if str(v) == "Yes" else "Exposed!"
        elif type in ["canonical", "meta_robots", "lang", "og", "internal_links", "external_links"]: actual = str(v) if v else "Missing/0"
        
        if len(actual) > 90: actual = actual[:87] + "..."

        if type == "title": 
            if isinstance(v, dict) and "Missing" not in v.get('title', 'Missing'): return ("fa-solid fa-heading", f"Title Tag ({v.get('title_count', 0)} chars)", "success", tips['title'], actual)
            return ("fa-solid fa-heading", "Missing Title Tag", "danger", tips['title'], actual)
        elif type == "meta": 
            if isinstance(v, dict) and "Missing" not in v.get('description', 'Missing'): return ("fa-solid fa-paragraph", f"Meta Desc ({v.get('desc_count', 0)} chars)", "success", tips['meta'], actual)
            return ("fa-solid fa-paragraph", "Missing Meta Description", "danger", tips['meta'], actual)
        elif type == "h1": 
            if v and isinstance(v, list) and "Missing" not in v: return ("fa-solid fa-h", "H1 Tag Present", "success", tips['h1'], actual)
            return ("fa-solid fa-h", "Missing H1 Heading", "danger", tips['h1'], actual)
        elif type == "images": 
            if v and int(v) > 0: return ("fa-solid fa-image", f"{int(v)} Images missing ALT", "warning", tips['images'], actual)
            return ("fa-solid fa-image", "Image Alts Optimized", "success", tips['images'], actual)
        elif type == "word_count": 
            if int(v if v else 0) < 300: return ("fa-solid fa-file-lines", f"Low Content ({int(v if v else 0)} words)", "warning", tips['word_count'], actual)
            return ("fa-solid fa-file-lines", f"Good Content ({int(v if v else 0)} words)", "success", tips['word_count'], actual)
        elif type == "schema": 
            if v and "Missing" not in str(v): return ("fa-solid fa-diagram-next", "Schema Found", "success", tips['schema'], actual)
            return ("fa-solid fa-diagram-next", "Missing Schema Markup", "danger", tips['schema'], actual)
        elif type == "https": 
            if str(v) == "Yes": return ("fa-solid fa-lock", "Secured (HTTPS)", "success", tips['https'], actual)
            return ("fa-solid fa-lock-open", "Unsecured (HTTP)", "danger", tips['https'], actual)
        elif type == "response_time":
            if float(v if v else 0) > 0.5: return ("fa-solid fa-stopwatch", f"Slow Server ({float(v if v else 0):.2f}s)", "warning", tips['response_time'], actual)
            return ("fa-solid fa-stopwatch", f"Fast Server ({float(v if v else 0):.2f}s)", "success", tips['response_time'], actual)
        elif type == "html_size":
            if float(v if v else 0) > 100: return ("fa-solid fa-code", f"Large HTML ({float(v if v else 0):.1f} KB)", "warning", tips['html_size'], actual)
            return ("fa-solid fa-code", f"Optimal HTML ({float(v if v else 0):.1f} KB)", "success", tips['html_size'], actual)
        elif type == "minified_css":
            if int(v if v else 0) > 0: return ("fa-solid fa-file-code", f"{int(v if v else 0)} Unminified CSS", "warning", tips['minified_css'], actual)
            return ("fa-solid fa-file-code", "CSS Minified", "success", tips['minified_css'], actual)
        elif type == "minified_js":
            if int(v if v else 0) > 0: return ("fa-solid fa-file-code", f"{int(v if v else 0)} Unminified JS", "warning", tips['minified_js'], actual)
            return ("fa-solid fa-file-code", "JS Minified", "success", tips['minified_js'], actual)
        elif type == "dir_listing":
            if str(v) == "Yes": return ("fa-solid fa-folder-minus", "Directory Secured", "success", tips['dir_listing'], actual)
            return ("fa-solid fa-folder-tree", "Directory Exposed", "danger", tips['dir_listing'], actual)
        elif type == "canonical": return ("fa-solid fa-link", "Canonical URL", "info", tips['canonical'], actual)
        elif type == "meta_robots": return ("fa-solid fa-robot", "Meta Robots", "info", tips['meta_robots'], actual)
        elif type == "lang": return ("fa-solid fa-language", "HTML Language", "info", tips['lang'], actual)
        elif type == "og": return ("fa-solid fa-share-nodes", "Open Graph Tags", "info", tips['og'], actual)
        elif type == "internal_links": return ("fa-solid fa-link", "Internal Links", "info", tips['internal_links'], actual)
        elif type == "external_links": return ("fa-solid fa-external-link", "External Links", "info", tips['external_links'], actual)
        else: return ("fa-solid fa-circle-info", "SEO Factor", "info", "N/A", actual)
    except Exception as e:
        return ("fa-solid fa-triangle-exclamation", "Extraction Error", "danger", f"Error: {e}", "N/A")

def render_audit_card_vip(label, data):
    icon, message, status_class, tip, actual_data = data
    html = f"""
    <div class="audit-item status-{status_class}">
        <div class="audit-header">
            <i class="{icon}" style="color:var(--text-color);"></i>
            <div class="audit-item-content">
                <span class="audit-item-title">{label}</span>
                <span class="audit-item-desc">{message}</span>
            </div>
        </div>
        <div class="actual-data-box">{actual_data}</div>
        <details class="seo-tip"><summary>How to fix</summary><p>{tip}</p></details>
    </div>
    """
    return html.replace('\n', '')

def render_speed_metric(label, data_obj):
    score = data_obj.get('score', 0)
    value = data_obj.get('value', 'N/A')
    if score >= 0.9: color, icon = "#10b981", "fa-solid fa-circle-check"
    elif score >= 0.5: color, icon = "#f59e0b", "fa-solid fa-square-minus"
    else: color, icon = "#ef4444", "fa-solid fa-triangle-exclamation"

    html = f"""
    <div class="speed-metric-card">
        <div style="display: flex; align-items: center;">
            <i class="{icon}" style="color: {color}; font-size: 16px; margin-right: 12px; width: 16px;"></i>
            <span style="font-size: 14px; font-weight: 700; color: #334155;">{label}</span>
        </div>
        <span style="font-size: 16px; font-weight: 900; color: {color};">{value}</span>
    </div>
    """
    return html.replace('\n', '')

def calculate_ov_vip(onpage, speed):
    critical, warnings, passed = 0, 0, 0
    if not onpage: return 0, 0, 0, 0

    h_alt = onpage.get('missing_alt', 0)
    w_count = onpage.get('word_count', 0)
    html_s = onpage.get('html_size_kb', 0.0)
    resp_t = onpage.get('response_time', 0.0)
    un_css = onpage.get('unminified_css', 0)
    un_js = onpage.get('unminified_js', 0)

    if "Missing" in onpage.get('title', 'Missing') or "Blocked" in str(onpage.get('title', '')): critical += 1
    else: passed += 1
    if "Missing" in onpage.get('description', 'Missing') or "Blocked" in str(onpage.get('description', '')): critical += 1
    else: passed += 1
    if not onpage.get('h1', []) or "Blocked" in str(onpage.get('h1', [])): critical += 1
    else: passed += 1
    if h_alt > 0: warnings += 1
    else: passed += 1
    if w_count < 300: warnings += 1
    else: passed += 1
    if not onpage.get('schema', None) or "Blocked" in str(onpage.get('schema', '')): critical += 1
    else: passed += 1
    if onpage.get('is_https', 'No') == "No": critical += 1
    else: passed += 1
    if html_s > 100: warnings += 1
    else: passed += 1
    if resp_t > 0.5: warnings += 1
    else: passed += 1
    if un_css > 0: warnings += 1
    else: passed += 1
    if un_js > 0: warnings += 1
    else: passed += 1
    if onpage.get('dir_listing_secured', 'No') == "No": critical += 1
    else: passed += 1

    onpage_score = 100 - (critical * 9) - (warnings * 3)
    m_speed = speed['mobile'].get('performance', 50) if speed else 50
    d_speed = speed['desktop'].get('performance', 50) if speed else 50
    speed_avg = (m_speed + d_speed) / 2
    
    final_score = int((max(onpage_score, 0) + speed_avg) / 2)
    return final_score, critical, warnings, passed

# --- SIDEBAR ---
with st.sidebar:
    if os.path.exists("logo.png"):
        st.image("logo.png", use_container_width=True)
    elif os.path.exists("logo.jpg"):
        st.image("logo.jpg", use_container_width=True)
    else:
        st.markdown('<div class="sidebar-brand">NexGen<span class="brand-gradient">WebLab</span></div>', unsafe_allow_html=True)
        st.markdown("<div style='text-align:center; color:#94a3b8; font-size:10px; margin-top:-10px;'>Place 'logo.png' in folder to replace this</div>", unsafe_allow_html=True)
        
    st.markdown("<div style='text-align:center; color:#64748b; font-size:12px; margin-bottom:20px; margin-top: 10px;'>Enterprise SEO Suite v2.0</div>", unsafe_allow_html=True)
    
    menu_selection = option_menu(
        menu_title=None,
        options=["Site Auditor", "Bulk Analysis"],
        icons=["search", "file-earmark-spreadsheet"],
        default_index=0,
        styles={
            "container": {"padding": "0!important", "background-color": "transparent"},
            "icon": {"color": "#94a3b8", "font-size": "18px"}, 
            "nav-link": {"font-size": "15px", "text-align": "left", "margin":"0px", "color":"#475569", "font-weight":"600", "height":"50px", "border-radius":"10px"},
            "nav-link-selected": {"background": "linear-gradient(135deg, rgba(109, 40, 217, 0.07), rgba(219, 39, 119, 0.07))", "color": "#6D28D9", "border-left": "4px solid #DB2777"},
        }
    )

# --- MAIN CONTENT ---
if menu_selection == "Site Auditor":
    
    st.markdown("""
    <div class="hero-container">
        <div class="hero-title">Professional <span>SEO Auditor</span></div>
        <div class="hero-subtitle">Instantly analyze technical roadblocks, optimize on-page elements, and uncover real-time traffic insights for any website.</div>
    </div>
    """, unsafe_allow_html=True)
    
    with st.form("audit_form", border=False):
        col_input, col_btn = st.columns([7.5, 2.5], gap="small")
        with col_input: 
            target_url = st.text_input("Target URL", label_visibility="collapsed", placeholder="https://arabiansquare.ae")
        with col_btn: 
            run_button = st.form_submit_button("ANALYZE NOW", type="primary", use_container_width=True)
    
    st.markdown("<div style='margin-top: 20px;'></div>", unsafe_allow_html=True)

    if run_button and target_url:
        progress_bar = st.progress(0, text="Initializing Audit Engine...")
        
        progress_bar.progress(15, text="Scraping SEO Architecture...")
        onpage_data = get_basic_onpage(target_url)
        
        if not onpage_data:
            st.warning("⚠️ The website blocked our On-Page Scraper (Security Protection). Speed and Traffic metrics will still be analyzed.")
            onpage_data = {
                'title': 'Data Blocked', 'title_count': 0, 'description': 'Data Blocked', 'desc_count': 0,
                'h1': ['Blocked'], 'missing_alt': 0, 'word_count': 0, 'schema': 'Blocked',
                'is_https': 'Yes' if target_url.startswith('https') else 'No',
                'html_size_kb': 0, 'response_time': 0, 'unminified_css': 0, 'unminified_js': 0,
                'has_noindex': 'Unknown', 'dir_listing_secured': 'Unknown', 'canonical': 'Unknown',
                'meta_robots': 'Unknown', 'lang': 'Unknown', 'og_title': 'Unknown',
                'internal_links': 0, 'external_links': 0
            }

        progress_bar.progress(45, text="Fetching Core Web Vitals...")
        speed_data = check_speed(target_url, SPEED_API_KEY)
        
        progress_bar.progress(70, text="Connecting Traffic API...")
        traffic_data = get_traffic_data(target_url, RAPIDAPI_KEY)
        
        progress_bar.progress(85, text="Syncing AI Recommendations...")
        m_perf = speed_data['mobile'].get('performance', 0) if speed_data else 0
        d_perf = speed_data['desktop'].get('performance', 0) if speed_data else 0
        combined_data = {**onpage_data, 'mobile_speed': m_perf, 'desktop_speed': d_perf}
        ai_suggestions = get_ai_suggestions(combined_data, GEMINI_API_KEY)
        
        progress_bar.progress(95, text="Finalizing Dashboard...")
        ov_score, crit_count, warn_count, pass_count = calculate_ov_vip(onpage_data, speed_data)
        
        progress_bar.progress(100, text="Complete.")
        time.sleep(0.3) 
        progress_bar.empty()
        
        st.markdown("<h3 style='text-align: center; color: #0f172a; margin-bottom: 25px; font-weight: 800;'>Audit Overview</h3>", unsafe_allow_html=True)
        ov_col1, ov_col2 = st.columns([1, 2], gap="large")
        with ov_col1: 
            st.plotly_chart(render_overview_donut(ov_score), use_container_width=True, config={'displayModeBar': False}, key="main_donut")
        with ov_col2:
            ic1, ic2, ic3 = st.columns(3)
            with ic1: st.markdown(f"""<div class="issue-card" style="border-top: 4px solid #ef4444;"><span class="issue-count" style="color:#ef4444;">{crit_count}</span><span class="issue-label">Critical</span></div>""", unsafe_allow_html=True)
            with ic2: st.markdown(f"""<div class="issue-card" style="border-top: 4px solid #f59e0b;"><span class="issue-count" style="color:#f59e0b;">{warn_count}</span><span class="issue-label">Warnings</span></div>""", unsafe_allow_html=True)
            with ic3: st.markdown(f"""<div class="issue-card" style="border-top: 4px solid #10b981;"><span class="issue-count" style="color:#10b981;">{pass_count}</span><span class="issue-label">Passed</span></div>""", unsafe_allow_html=True)
        
        st.markdown("<hr style='border-top: 1px solid #e2e8f0; margin: 40px 0;'>", unsafe_allow_html=True)

        tab1, tab2, tab3, tab4, tab5 = st.tabs(["On-Page Data", "Speed Vitals", "Traffic Analytics", "AI Strategy", "Document Export"])
        
        with tab1:
            h_col1, h_col2 = st.columns(2, gap="large")
            with h_col1: st.markdown("<h5 style='color: #0f172a; margin-bottom: 10px; border-bottom: 2px solid #e2e8f0; padding-bottom: 10px;'>Content & Performance</h5>", unsafe_allow_html=True)
            with h_col2: st.markdown("<h5 style='color: #0f172a; margin-bottom: 10px; border-bottom: 2px solid #e2e8f0; padding-bottom: 10px;'>Technical & Advanced</h5>", unsafe_allow_html=True)
            
            pairs = [
                (("Title Tag", get_audit_status_vip(onpage_data, "title")), ("Canonical URL", get_audit_status_vip(onpage_data.get('canonical', 'Missing'), "canonical"))),
                (("Meta Description", get_audit_status_vip(onpage_data, "meta")), ("Meta Robots", get_audit_status_vip(onpage_data.get('meta_robots', 'Missing'), "meta_robots"))),
                (("H1 Heading", get_audit_status_vip(onpage_data.get('h1', []), "h1")), ("HTML Language", get_audit_status_vip(onpage_data.get('lang', 'Missing'), "lang"))),
                (("Content Length", get_audit_status_vip(onpage_data.get('word_count', 0), "word_count")), ("Open Graph Check", get_audit_status_vip(onpage_data.get('og_title', 'Missing'), "og"))),
                (("Image Alt Attributes", get_audit_status_vip(onpage_data.get('missing_alt', 0), "images")), ("Schema.org Markup", get_audit_status_vip(onpage_data.get('schema', []), "schema"))),
                (("Server Response Time", get_audit_status_vip(onpage_data.get('response_time', 0.0), "response_time")), ("SSL Protocol (HTTPS)", get_audit_status_vip(onpage_data.get('is_https', 'No'), "https"))),
                (("Total HTML Size", get_audit_status_vip(onpage_data.get('html_size_kb', 0.0), "html_size")), ("Directory Listing", get_audit_status_vip(onpage_data.get('dir_listing_secured', 'No'), "dir_listing"))),
                (("CSS Minification", get_audit_status_vip(onpage_data.get('unminified_css', 0), "minified_css")), ("Internal Links", get_audit_status_vip(onpage_data.get('internal_links', 0), "internal_links"))),
                (("JS Minification", get_audit_status_vip(onpage_data.get('unminified_js', 0), "minified_js")), ("External Links", get_audit_status_vip(onpage_data.get('external_links', 0), "external_links")))
            ]
            
            for left_item, right_item in pairs:
                c1, c2 = st.columns(2, gap="large")
                with c1: st.markdown(render_audit_card_vip(*left_item), unsafe_allow_html=True)
                with c2: st.markdown(render_audit_card_vip(*right_item), unsafe_allow_html=True)

        with tab2:
            if speed_data:
                st.markdown("<h4 style='color: #0f172a; margin-bottom: 25px; text-align: center;'>Mobile Device Analysis</h4>", unsafe_allow_html=True)
                m_gauges = st.columns(4)
                
                # --- FIXED: REMOVED SECOND ARGUMENT FROM GAUGE FUNCTION CALLS ---
                with m_gauges[0]: 
                    st.plotly_chart(render_small_gauge(speed_data['mobile'].get('performance', 0)), use_container_width=True, config={'displayModeBar': False}, key="m_g1")
                    st.markdown("<div style='text-align:center; font-size:14px; font-weight:700; color:#475569; margin-top:-15px;'>Performance</div>", unsafe_allow_html=True)
                with m_gauges[1]: 
                    st.plotly_chart(render_small_gauge(speed_data['mobile'].get('accessibility', 0)), use_container_width=True, config={'displayModeBar': False}, key="m_g2")
                    st.markdown("<div style='text-align:center; font-size:14px; font-weight:700; color:#475569; margin-top:-15px;'>Accessibility</div>", unsafe_allow_html=True)
                with m_gauges[2]: 
                    st.plotly_chart(render_small_gauge(speed_data['mobile'].get('best-practices', 0)), use_container_width=True, config={'displayModeBar': False}, key="m_g3")
                    st.markdown("<div style='text-align:center; font-size:14px; font-weight:700; color:#475569; margin-top:-15px;'>Best Practices</div>", unsafe_allow_html=True)
                with m_gauges[3]: 
                    st.plotly_chart(render_small_gauge(speed_data['mobile'].get('seo', 0)), use_container_width=True, config={'displayModeBar': False}, key="m_g4")
                    st.markdown("<div style='text-align:center; font-size:14px; font-weight:700; color:#475569; margin-top:-15px;'>SEO Score</div>", unsafe_allow_html=True)
                
                st.markdown("<div style='margin-top: 35px;'></div>", unsafe_allow_html=True)
                
                m_metrics = speed_data['mobile'].get('metrics', {})
                sm_col1, sm_col2 = st.columns(2, gap="large")
                with sm_col1:
                    st.markdown(render_speed_metric("First Contentful Paint (FCP)", m_metrics.get('fcp', {})), unsafe_allow_html=True)
                    st.markdown(render_speed_metric("Total Blocking Time (TBT)", m_metrics.get('tbt', {})), unsafe_allow_html=True)
                    st.markdown(render_speed_metric("Speed Index", m_metrics.get('si', {})), unsafe_allow_html=True)
                with sm_col2:
                    st.markdown(render_speed_metric("Largest Contentful Paint (LCP)", m_metrics.get('lcp', {})), unsafe_allow_html=True)
                    st.markdown(render_speed_metric("Cumulative Layout Shift (CLS)", m_metrics.get('cls', {})), unsafe_allow_html=True)

                st.markdown("<hr style='border-top: 1px dashed #cbd5e1; margin: 50px 0;'>", unsafe_allow_html=True)

                st.markdown("<h4 style='color: #0f172a; margin-bottom: 25px; text-align: center;'>Desktop Device Analysis</h4>", unsafe_allow_html=True)
                d_gauges = st.columns(4)
                with d_gauges[0]: 
                    st.plotly_chart(render_small_gauge(speed_data['desktop'].get('performance', 0)), use_container_width=True, config={'displayModeBar': False}, key="d_g1")
                    st.markdown("<div style='text-align:center; font-size:14px; font-weight:700; color:#475569; margin-top:-15px;'>Performance</div>", unsafe_allow_html=True)
                with d_gauges[1]: 
                    st.plotly_chart(render_small_gauge(speed_data['desktop'].get('accessibility', 0)), use_container_width=True, config={'displayModeBar': False}, key="d_g2")
                    st.markdown("<div style='text-align:center; font-size:14px; font-weight:700; color:#475569; margin-top:-15px;'>Accessibility</div>", unsafe_allow_html=True)
                with d_gauges[2]: 
                    st.plotly_chart(render_small_gauge(speed_data['desktop'].get('best-practices', 0)), use_container_width=True, config={'displayModeBar': False}, key="d_g3")
                    st.markdown("<div style='text-align:center; font-size:14px; font-weight:700; color:#475569; margin-top:-15px;'>Best Practices</div>", unsafe_allow_html=True)
                with d_gauges[3]: 
                    st.plotly_chart(render_small_gauge(speed_data['desktop'].get('seo', 0)), use_container_width=True, config={'displayModeBar': False}, key="d_g4")
                    st.markdown("<div style='text-align:center; font-size:14px; font-weight:700; color:#475569; margin-top:-15px;'>SEO Score</div>", unsafe_allow_html=True)
                
                st.markdown("<div style='margin-top: 35px;'></div>", unsafe_allow_html=True)
                
                d_metrics = speed_data['desktop'].get('metrics', {})
                sd_col1, sd_col2 = st.columns(2, gap="large")
                with sd_col1:
                    st.markdown(render_speed_metric("First Contentful Paint (FCP)", d_metrics.get('fcp', {})), unsafe_allow_html=True)
                    st.markdown(render_speed_metric("Total Blocking Time (TBT)", d_metrics.get('tbt', {})), unsafe_allow_html=True)
                    st.markdown(render_speed_metric("Speed Index", d_metrics.get('si', {})), unsafe_allow_html=True)
                with sd_col2:
                    st.markdown(render_speed_metric("Largest Contentful Paint (LCP)", d_metrics.get('lcp', {})), unsafe_allow_html=True)
                    st.markdown(render_speed_metric("Cumulative Layout Shift (CLS)", d_metrics.get('cls', {})), unsafe_allow_html=True)

        with tab3:
            if traffic_data and traffic_data['status'] == "Live Data":
                raw_sim = traffic_data['raw_data']
                graph_col1, graph_col2 = st.columns(2)
                with graph_col1:
                    st.markdown("<p style='text-align:center; font-weight:700;'>Visits Trend (Simulated)</p>", unsafe_allow_html=True)
                    visits_num = raw_sim.get("EstimatedMonthlyVisits", 5000)
                    dates = [(datetime.now() - timedelta(days=30*i)).strftime("%b") for i in range(5, -1, -1)]
                    sim_data = [int(visits_num * (0.9 + 0.02*i)) for i in range(6)]
                    fig_trend = px.line(x=dates, y=sim_data, labels={'x':'Month', 'y':'Visits'})
                    fig_trend.update_layout(margin=dict(l=20, r=20, t=20, b=20), height=250)
                    st.plotly_chart(fig_trend, use_container_width=True, key="t_trend")
                with graph_col2:
                    st.markdown("<p style='text-align:center; font-weight:700;'>Traffic Sources</p>", unsafe_allow_html=True)
                    sources = raw_sim.get("Traffic", {}).get("Sources", {})
                    s_labels = ['Search', 'Direct', 'Social']
                    s_values = [sources.get("Search", 1), sources.get("Direct", 1), sources.get("Social", 1)]
                    fig_source = px.pie(values=s_values, names=s_labels, hole=0.5)
                    fig_source.update_layout(margin=dict(l=10, r=10, t=10, b=10), height=250)
                    st.plotly_chart(fig_source, use_container_width=True, key="t_source")
            else:
                st.warning("Traffic data not available or API rate limit hit.")

        with tab4:
            st.markdown("<h4 style='color: #0f172a; margin-bottom: 20px;'>AI Action Plan</h4>", unsafe_allow_html=True)
            if ai_suggestions and isinstance(ai_suggestions, list):
                for item in ai_suggestions:
                    clean_text = item.get('text', '').replace('```json', '').replace('```html', '').replace('```', '').strip()
                    st.markdown(f"""
                    <div style="background: #ffffff; border: 1px solid #e2e8f0; border-radius: 12px; padding: 20px; margin-bottom: 15px; border-left: 4px solid #6D28D9; box-shadow: 0 2px 4px rgba(0,0,0,0.02);">
                        <h5 style="color: #0f172a; margin-top: 0; margin-bottom: 10px; font-size: 16px;"><i class="{item.get('icon', 'fa-solid fa-lightbulb')}" style="color: #DB2777; margin-right: 10px;"></i>{item.get('title', 'Recommendation')}</h5>
                        <div style='color: #475569; font-size: 14px;'>{clean_text}</div>
                    </div>
                    """, unsafe_allow_html=True)
            else:
                st.error("AI recommendations failed to generate.")

        with tab5:
            if run_button and onpage_data:
                word_file = generate_word_report(target_url, onpage_data, speed_data, ai_suggestions)
                st.download_button(
                    label="Download Professional Audit Report (.DOCX)",
                    data=word_file, file_name=f"NexGenWebLab_Audit.docx",
                    mime="application/vnd.openxmlformats-officedocument.wordprocessingml.document",
                    type="primary", use_container_width=True
                )

elif menu_selection == "Bulk Analysis":
    st.markdown("""
    <div class="hero-container">
        <div class="hero-title">Bulk <span>Outreach</span> Engine</div>
    </div>
    """, unsafe_allow_html=True)
    
    st.markdown('<div class="score-container">', unsafe_allow_html=True)
    uploaded_file = st.file_uploader("Upload .xlsx file", type=["xlsx"])
    st.markdown('</div>', unsafe_allow_html=True)
    
    if uploaded_file is not None:
        try:
            df = pd.read_excel(uploaded_file, header=None)
            valid_urls = []
            for col in df.columns:
                cells = df[col].dropna().astype(str).tolist()
                for cell in cells:
                    cleaned_url = cell.strip()
                    if cleaned_url.startswith('http'):
                        if cleaned_url not in valid_urls: valid_urls.append(cleaned_url)
            
            total_urls = len(valid_urls)
            if total_urls > 0:
                st.success(f"Found {total_urls} unique URLs.")
                if st.button("Generate Bulk ZIP Reports", type="primary"):
                    st.info("Bulk generation started...")
                    prog = st.progress(0)
                    for i in range(5):
                        time.sleep(0.2)
                        prog.progress((i+1)*20)
                    st.success("Simulation complete.")
            else:
                st.error("No valid URLs found in file.")
        except Exception as e:
            st.error(f"Error reading file: {e}")