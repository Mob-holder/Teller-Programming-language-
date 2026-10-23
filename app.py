import streamlit as st
import subprocess
import tempfile
import os
from streamlit_ace import st_ace

st.set_page_config(page_title="Teller IDE", page_icon="⚡", layout="wide", initial_sidebar_state="collapsed")

# Aggressive CSS to kill all Streamlit default UI, padding, and headers
st.markdown("""
<style>
    /* Nuke Streamlit's default margins and headers */
    header {visibility: hidden !important;}
    footer {visibility: hidden !important;}
    .block-container {
        padding: 0 !important;
        margin: 0 !important;
        max-width: 100% !important;
    }
    
    /* Professional IDE Base Layout */
    .ide-container {
        display: flex;
        flex-direction: column;
        height: 100vh;
        background-color: #0e1117;
        font-family: -apple-system, BlinkMacSystemFont, "Segoe UI", Roboto, sans-serif;
    }
    .top-navbar {
        display: flex;
        align-items: center;
        justify-content: space-between;
        background-color: #161b22;
        border-bottom: 1px solid #30363d;
        padding: 10px 20px;
    }
    .brand-group {
        display: flex;
        align-items: center;
        gap: 12px;
    }
    .tt-logo {
        background: #cc1414; color: #fff; font-weight: 900; font-size: 18px;
        padding: 4px 10px; border-radius: 6px; box-shadow: 0 2px 8px rgba(204, 20, 20, 0.4);
    }
    .brand-title { color: #c9d1d9; font-size: 18px; font-weight: bold; margin: 0; }
    
    .editor-section {
        display: flex;
        flex-direction: column;
        flex: 1;
        padding: 15px 20px;
    }
    .tab-bar {
        display: flex;
        background-color: #0e1117;
        border-bottom: 1px solid #30363d;
    }
    .active-tab {
        background-color: #161b22;
        color: #e6edf3;
        border-top: 2px solid #cc1414;
        border-right: 1px solid #30363d;
        border-left: 1px solid #30363d;
        padding: 8px 16px;
        font-family: 'Courier New', monospace;
        font-size: 13px;
        font-weight: bold;
    }
    .terminal-section {
        background-color: #06090e;
        border-top: 1px solid #30363d;
        padding: 15px 20px;
        min-height: 250px;
        font-family: 'SFMono-Regular', Consolas, monospace;
        color: #5af78e;
        white-space: pre-wrap;
    }
    .stderr-text { color: #ff5c57; }
</style>
""", unsafe_allow_html=True)

# Top Navigation Bar
st.markdown("""
<div class="ide-container">
    <div class="top-navbar">
        <div class="brand-group">
            <div class="tt-logo">TT</div>
            <p class="brand-title">TELLER IDE</p>
        </div>
        <div style="color:#8b949e; font-size:13px;">Official Compiler</div>
    </div>
    <div class="editor-section">
        <div class="tab-bar">
            <div class="active-tab">main.tt</div>
        </div>
""", unsafe_allow_html=True)

default_script = """workspace.start

# 1. Define a Function
store.function InitPlayer(Name)
    store.var {
        var("player") = "Ghost"
        var("coins") = 100
    }
end

# 2. Call Function & Add Bonus Loop
InitPlayer(Name)
block[1]

load(coins) : add(25)
block[2]

# 3. Print out a loop
system.console()
do text.print("Initializing System...") [1,3]
output(text.string) {
    text.print("Welcome "__player__", you have "__coins__" coins!")
}
block[3]

workspace.end"""

# Auto-formats indents properly. Popups disabled by default in st_ace for Ruby mode.
user_code = st_ace(
    value=default_script,
    language="ruby", 
    theme="tomorrow_night_eighties",
    keybinding="vscode",
    font_size=14,
    tab_size=4,
    show_gutter=True,
    wrap=True,
    auto_update=True,
    min_lines=18,
    key="teller_editor"
)

# IDE Controls (Run & Stdin)
col1, col2 = st.columns([1, 8])
with col1:
    run_btn = st.button("▶ Run", type="primary", use_container_width=True)
with col2:
    user_stdin = st.text_input("Console Input (Stdin)", value="", label_visibility="collapsed", placeholder="Type input here if script asks for it...")

st.markdown("</div>", unsafe_allow_html=True) # Close editor-section

# Terminal Execution
if run_btn:
    temp_dir = tempfile.mkdtemp()
    temp_source_path = os.path.join(temp_dir, "main.tt")
    
    with open(temp_source_path, "w", encoding="utf-8") as f:
        f.write(user_code)

    try:
        proc = subprocess.run(
            ["python", "teller.py", temp_source_path],
            input=user_stdin,
            capture_output=True,
            text=True,
            timeout=5
        )

        raw_stdout = proc.stdout.replace(temp_source_path, "main.tt")
        raw_stderr = proc.stderr.replace(temp_source_path, "main.tt")

        if proc.returncode != 0 or raw_stderr:
            err = raw_stderr if raw_stderr else raw_stdout
            st.markdown(f'<div class="terminal-section stderr-text">Terminal\n\n{err}</div>', unsafe_allow_html=True)
        else:
            out = raw_stdout if raw_stdout else "[Program executed successfully]"
            st.markdown(f'<div class="terminal-section">Terminal\n\n{out}</div>', unsafe_allow_html=True)

    except subprocess.TimeoutExpired:
        st.markdown('<div class="terminal-section stderr-text">FatalError: Execution timed out.</div>', unsafe_allow_html=True)
    finally:
        if os.path.exists(temp_source_path): os.remove(temp_source_path)
        if os.path.exists(temp_dir): os.rmdir(temp_dir)
else:
    st.markdown('<div class="terminal-section" style="color:#8b949e;">Terminal\n\nWaiting for execution...</div>', unsafe_allow_html=True)

st.markdown("</div>", unsafe_allow_html=True) # Close ide-container
