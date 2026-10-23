import streamlit as st
import subprocess
import tempfile
import os
from streamlit_ace import st_ace

st.set_page_config(
    page_title="Teller Studio IDE",
    page_icon="⚡",
    layout="wide"
)

# Custom Dark OneCompiler / Studio Theme
st.markdown("""
<style>
    .main { background-color: #0e1117; color: #c9d1d9; }
    .header-bar {
        display: flex;
        align-items: center;
        gap: 16px;
        padding-bottom: 12px;
        border-bottom: 1px solid #30363d;
        margin-bottom: 18px;
    }
    .brand-title {
        color: #ff3333 !important;
        font-family: -apple-system, BlinkMacSystemFont, "Segoe UI", Roboto, sans-serif;
        font-size: 26px !important;
        font-weight: 800 !important;
        margin: 0 !important;
        letter-spacing: 0.5px;
    }
    .brand-subtitle {
        color: #8b949e !important;
        font-size: 13px !important;
        margin: 0 !important;
    }
    .file-tab {
        display: inline-flex;
        align-items: center;
        background: #161b22;
        border-top: 3px solid #ff2b2b;
        border-left: 1px solid #30363d;
        border-right: 1px solid #30363d;
        padding: 6px 18px;
        font-family: 'Courier New', monospace;
        font-size: 14px;
        color: #e6edf3;
        border-radius: 6px 6px 0 0;
        margin-bottom: -1px;
    }
    .terminal-box {
        background-color: #06090e;
        border: 1px solid #30363d;
        border-radius: 6px;
        padding: 16px;
        font-family: 'SFMono-Regular', Consolas, 'Liberation Mono', Menlo, monospace;
        font-size: 13.5px;
        line-height: 1.45;
        min-height: 240px;
        white-space: pre-wrap;
        box-shadow: inset 0 0 12px rgba(0,0,0,0.7);
    }
    .stdout-text { color: #5af78e; }
    .stderr-text { color: #ff5c57; }
</style>
""", unsafe_allow_html=True)

# Top Bar Header with TT Logo
logo_markup = ""
if os.path.exists("logo.svg"):
    with open("logo.svg", "r", encoding="utf-8") as f:
        logo_markup = f.read()

col_logo, col_text = st.columns([1, 14])
with col_logo:
    if logo_markup:
        st.components.v1.html(logo_markup, height=70, width=70)
    else:
        st.markdown("<h2 style='color:#cc1414;margin:0;'>TT</h2>", unsafe_allow_html=True)
with col_text:
    st.markdown('<p class="brand-title">TELLER STUDIO</p><p class="brand-subtitle">High-performance declarative language playground (.tt)</p>', unsafe_allow_html=True)

# Active File Tab
st.markdown('<div class="file-tab">📄 main.tt</div>', unsafe_allow_html=True)

default_code = """workspace.start

    # Step 1: Memory setup
    store.var {
        var("player") = "Champion"
        var("coins") = 100
    }
    block[1]

    # Step 2: Math operation via : link
    load(coins) : add(25)
    block[2]

    # Step 3: Screen output
    system.console()
    output(text.string) {
        text.print("Welcome __player__! Wallet balance: __coins__ Gold!")
    }
    block[3]

workspace.end"""

# Ace Code Editor Setup
code_input = st_ace(
    value=default_code,
    language="ruby",          # Provides clean syntax highlighting for strings, # notes, and keywords
    theme="tomorrow_night_eighties",
    keybinding="sublime",
    font_size=15,
    tab_size=4,
    show_gutter=True,
    wrap=True,
    auto_update=False,
    min_lines=18,
    key="teller_ide_editor"
)

# Run Button Bar
run_btn = st.button("▶ Run Code", type="primary")

st.markdown("#### Terminal Output")

if run_btn:
    # Save script to a temporary file named main.tt for clean compiler error traces
    temp_dir = tempfile.mkdtemp()
    temp_source_path = os.path.join(temp_dir, "main.tt")
    
    with open(temp_source_path, "w", encoding="utf-8") as f:
        f.write(code_input)

    try:
        proc = subprocess.run(
            ["python", "teller.py", temp_source_path],
            capture_output=True,
            text=True,
            timeout=5
        )

        # Clean raw path from output so tracebacks simply show 'main.tt'
        raw_stdout = proc.stdout.replace(temp_source_path, "main.tt")
        raw_stderr = proc.stderr.replace(temp_source_path, "main.tt")

        if proc.returncode != 0 or raw_stderr:
            err_msg = raw_stderr if raw_stderr else raw_stdout
            st.markdown(f'<div class="terminal-box stderr-text">{err_msg}</div>', unsafe_allow_html=True)
        else:
            out_msg = raw_stdout if raw_stdout else "[Program executed successfully with no output]"
            st.markdown(f'<div class="terminal-box stdout-text">{out_msg}</div>', unsafe_allow_html=True)

    except subprocess.TimeoutExpired:
        st.markdown('<div class="terminal-box stderr-text">FatalError: Execution timed out after 5.0 seconds.</div>', unsafe_allow_html=True)
    except Exception as exc:
        st.markdown(f'<div class="terminal-box stderr-text">InternalError: {exc}</div>', unsafe_allow_html=True)
    finally:
        if os.path.exists(temp_source_path):
            os.remove(temp_source_path)
        if os.path.exists(temp_dir):
            os.rmdir(temp_dir)
else:
    st.markdown('<div class="terminal-box" style="color:#545d68;">Click "▶ Run Code" to compile and run...</div>', unsafe_allow_html=True)
