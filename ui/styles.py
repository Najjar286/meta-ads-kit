"""Windows 11 Design Language — CSS theme tokens for dark/light mode with glassmorphism."""
import streamlit as st


LIGHT_CSS = """
<style>
:root {
    --font-family: 'Segoe UI Variable', 'Segoe UI', -apple-system, BlinkMacSystemFont, sans-serif;
    --font-mono: 'Cascadia Code', 'JetBrains Mono', 'Fira Code', 'Consolas', monospace;
    --bg-primary: #FAFAFA;
    --bg-secondary: #FFFFFF;
    --bg-tertiary: #F0F0F0;
    --bg-quaternary: #E8E8E8;
    --bg-accent: #005FB8;
    --bg-glass: rgba(0,0,0,0.02);
    --bg-glass-hover: rgba(0,0,0,0.04);
    --bg-glass-active: rgba(0,0,0,0.06);
    --text-primary: #1A1A1A;
    --text-secondary: #616161;
    --text-tertiary: #9E9E9E;
    --text-inverse: #FFFFFF;
    --border: #D1D1D1;
    --border-light: #E0E0E0;
    --border-focus: #005FB8;
    --success: #107C10;
    --warning: #F2C811;
    --danger: #D13438;
    --info: #0078D7;
    --accent-primary: #005FB8;
    --accent-secondary: #107C10;
    --accent-purple: #8764B8;
    --accent-orange: #CA5010;
    --shadow: 0px 2px 8px rgba(0,0,0,0.08);
    --shadow-lg: 0px 4px 16px rgba(0,0,0,0.12);
    --shadow-xl: 0px 8px 32px rgba(0,0,0,0.15);
    --glass-shadow: 0 8px 32px rgba(0,0,0,0.08);
    --glass-blur: blur(12px);
    --glass-border: rgba(0,0,0,0.06);
    --radius: 8px;
    --radius-sm: 4px;
    --radius-lg: 12px;
    --radius-xl: 16px;
    --space-xs: 4px; --space-sm: 8px; --space-md: 16px;
    --space-lg: 24px; --space-xl: 32px; --space-2xl: 48px;
    --transition-fast: 150ms cubic-bezier(0.4, 0, 0.2, 1);
    --transition-normal: 250ms cubic-bezier(0.4, 0, 0.2, 1);
    --transition-slow: 400ms cubic-bezier(0.4, 0, 0.2, 1);
}
</style>
"""

DARK_CSS = """
<style>
:root {
    --font-family: 'Segoe UI Variable', 'Segoe UI', -apple-system, BlinkMacSystemFont, sans-serif;
    --font-mono: 'Cascadia Code', 'JetBrains Mono', 'Fira Code', 'Consolas', monospace;
    --bg-primary: #0D0D0D;
    --bg-secondary: #1A1A1A;
    --bg-tertiary: #252525;
    --bg-quaternary: #303030;
    --bg-accent: #60CDFF;
    --bg-glass: rgba(255,255,255,0.03);
    --bg-glass-hover: rgba(255,255,255,0.06);
    --bg-glass-active: rgba(255,255,255,0.09);
    --text-primary: #F0F0F0;
    --text-secondary: #A0A0A0;
    --text-tertiary: #606060;
    --text-inverse: #0D0D0D;
    --border: #333333;
    --border-light: #404040;
    --border-focus: #60CDFF;
    --success: #6CCB5F;
    --warning: #FCE100;
    --danger: #FF6F6F;
    --info: #60CDFF;
    --accent-primary: #60CDFF;
    --accent-secondary: #6CCB5F;
    --accent-purple: #C08AFF;
    --accent-orange: #FF8C42;
    --shadow: 0px 2px 8px rgba(0,0,0,0.24);
    --shadow-lg: 0px 4px 16px rgba(0,0,0,0.32);
    --shadow-xl: 0px 8px 32px rgba(0,0,0,0.5);
    --glass-shadow: 0 8px 32px rgba(0,0,0,0.4);
    --glass-blur: blur(12px);
    --glass-border: rgba(255,255,255,0.06);
    --radius: 8px;
    --radius-sm: 4px;
    --radius-lg: 12px;
    --radius-xl: 16px;
    --space-xs: 4px; --space-sm: 8px; --space-md: 16px;
    --space-lg: 24px; --space-xl: 32px; --space-2xl: 48px;
    --transition-fast: 150ms cubic-bezier(0.4, 0, 0.2, 1);
    --transition-normal: 250ms cubic-bezier(0.4, 0, 0.2, 1);
    --transition-slow: 400ms cubic-bezier(0.4, 0, 0.2, 1);
}
</style>
"""

BASE_CSS = """
<style>
/* === Base resets === */
.stApp { font-family: var(--font-family); background: var(--bg-primary); }
.stApp > header { background: transparent !important; }
.stMainBlockContainer { padding-top: 1rem; }

/* === Buttons === */
.stButton > button {
    border-radius: var(--radius-sm);
    font-family: var(--font-family);
    transition: all var(--transition-fast);
    font-weight: 500;
}
.stButton > button:hover { transform: scale(1.01); }
.stButton > button:active { transform: scale(0.98); }

/* === Inputs === */
.stTextInput > div > div > input { border-radius: var(--radius-sm); font-family: var(--font-family); }
.stSelectbox > div > div > div { border-radius: var(--radius-sm); }
.stMultiSelect > div > div > div { border-radius: var(--radius-sm); }
.stDateInput > div > div > input { border-radius: var(--radius-sm); }
.stDataFrame { border-radius: var(--radius); border: 1px solid var(--border); }
.stExpander { border-radius: var(--radius); border: 1px solid var(--border); }

/* === Metric cards === */
div[data-testid="stMetric"] {
    background: var(--bg-secondary);
    border-radius: var(--radius);
    padding: var(--space-md);
    box-shadow: var(--shadow);
    border: 1px solid var(--border);
    transition: all var(--transition-normal);
}
div[data-testid="stMetric"]:hover { box-shadow: var(--shadow-lg); transform: translateY(-1px); }
div[data-testid="stMetric"] > div:first-child { color: var(--text-secondary); font-size: 13px; }
div[data-testid="stMetric"] > div:nth-child(2) { color: var(--text-primary); font-size: 24px; font-weight: 600; }

/* === Sidebar === */
section[data-testid="stSidebar"] {
    background: var(--bg-secondary);
    border-right: 1px solid var(--border);
    backdrop-filter: var(--glass-blur);
}
section[data-testid="stSidebar"] .stButton > button { width: 100%; justify-content: flex-start; }

/* === Tabs === */
.stTabs [data-baseweb="tab-list"] { gap: 0; border-bottom: 1px solid var(--border); }
.stTabs [data-baseweb="tab"] { font-family: var(--font-family); transition: all var(--transition-fast); }
.stTabs [aria-selected="true"] { border-bottom-color: var(--accent-primary) !important; }

/* === Progress === */
.stProgress > div > div > div > div { background: var(--bg-accent); }

/* === Notifications === */
div[data-testid="stNotification"] { border-radius: var(--radius); }

/* === Scrollbar === */
::-webkit-scrollbar { width: 6px; height: 6px; }
::-webkit-scrollbar-track { background: transparent; }
::-webkit-scrollbar-thumb { background: var(--border); border-radius: 3px; }
::-webkit-scrollbar-thumb:hover { background: var(--text-tertiary); }

/* === W11 Card System === */
.w11-card {
    background: var(--bg-secondary);
    border-radius: var(--radius-lg);
    padding: var(--space-md);
    box-shadow: var(--shadow);
    border: 1px solid var(--border);
    transition: all var(--transition-normal);
    backdrop-filter: var(--glass-blur);
}
.w11-card:hover { box-shadow: var(--shadow-lg); border-color: var(--border-light); }
.w11-card-header {
    font-size: 13px;
    color: var(--text-secondary);
    margin-bottom: var(--space-sm);
    font-weight: 500;
    text-transform: uppercase;
    letter-spacing: 0.5px;
}
.w11-card-value {
    font-size: 28px;
    font-weight: 700;
    color: var(--text-primary);
    line-height: 1.2;
}
.w11-card-delta-positive { color: var(--success); font-size: 13px; font-weight: 500; }
.w11-card-delta-negative { color: var(--danger); font-size: 13px; font-weight: 500; }
.w11-card-delta-neutral { color: var(--text-tertiary); font-size: 13px; }

/* === Badges === */
.w11-badge {
    display: inline-block;
    padding: 2px 10px;
    border-radius: var(--radius-sm);
    font-size: 12px;
    font-weight: 600;
    letter-spacing: 0.3px;
}
.w11-badge-good { background: rgba(108,203,95,0.15); color: var(--success); }
.w11-badge-warn { background: rgba(252,225,0,0.15); color: var(--warning); }
.w11-badge-bad { background: rgba(255,111,111,0.15); color: var(--danger); }
.w11-badge-info { background: rgba(96,205,255,0.15); color: var(--info); }

/* === Empty state === */
.w11-empty-state {
    text-align: center;
    padding: var(--space-2xl) var(--space-md);
    color: var(--text-tertiary);
}
.w11-empty-state-icon { font-size: 56px; margin-bottom: var(--space-md); opacity: 0.6; }
.w11-empty-state-text { font-size: 16px; font-weight: 500; }

/* === Error boundary === */
.w11-error-boundary {
    padding: var(--space-md);
    border: 1px solid rgba(255,111,111,0.3);
    border-radius: var(--radius);
    background: rgba(255,111,111,0.05);
    color: var(--danger);
    margin: var(--space-sm) 0;
}

/* === Glass card === */
.genius-card {
    background: var(--bg-glass);
    backdrop-filter: var(--glass-blur);
    border: 1px solid var(--glass-border);
    border-radius: var(--radius-lg);
    padding: var(--space-lg);
    box-shadow: var(--glass-shadow);
    transition: all var(--transition-normal);
}
.genius-card:hover { box-shadow: var(--shadow-xl); border-color: var(--border-light); }

/* === KPI special === */
.genius-kpi {
    background: var(--bg-secondary);
    border: 1px solid var(--border);
    border-radius: var(--radius-lg);
    padding: var(--space-lg);
    position: relative;
    overflow: hidden;
}
.genius-kpi::before {
    content: '';
    position: absolute;
    top: 0; left: 0; right: 0;
    height: 3px;
    background: linear-gradient(90deg, var(--accent-primary), var(--accent-secondary));
}

/* === Loading skeleton === */
@keyframes shimmer {
    0% { opacity: 0.3; }
    50% { opacity: 1.0; }
    100% { opacity: 0.3; }
}
.w11-skeleton {
    background: var(--bg-tertiary);
    border-radius: var(--radius-sm);
    animation: shimmer 1.5s ease-in-out infinite;
}

/* === Toast === */
.genius-toast {
    position: fixed;
    bottom: 24px;
    right: 24px;
    padding: var(--space-md) var(--space-lg);
    border-radius: var(--radius);
    box-shadow: var(--shadow-xl);
    z-index: 9999;
    animation: slideUp 0.3s ease-out;
    max-width: 400px;
}
@keyframes slideUp {
    from { transform: translateY(20px); opacity: 0; }
    to { transform: translateY(0); opacity: 1; }
}

/* === Page transitions === */
@keyframes fadeIn {
    from { opacity: 0; transform: translateY(8px); }
    to { opacity: 1; transform: translateY(0); }
}
.stMainBlockContainer > div { animation: fadeIn 0.3s ease-out; }

/* === Divider === */
hr { border-color: var(--border) !important; opacity: 0.5; }

/* === Links === */
a { color: var(--accent-primary); }
a:hover { color: var(--accent-primary); opacity: 0.8; }
</style>
"""


def inject_theme_css(theme: str = "dark") -> None:
    """Inject theme CSS into the Streamlit app."""
    css = BASE_CSS
    if theme == "dark":
        css += DARK_CSS
    else:
        css += LIGHT_CSS
    st.markdown(css, unsafe_allow_html=True)
