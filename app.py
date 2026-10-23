import streamlit as st
import subprocess
import tempfile
import os
from streamlit_ace import st_ace

st.set_page_config(page_title="Teller", page_icon="⚡", layout="wide", initial_sidebar_state="collapsed")

# Clean global CSS to remove Streamlit padding without breaking the DOM layout
st.markdown("""
<style>
    .main { background-color: #0e1117; color: #c9d1d9; }
    [data-testid="stHeader"] { display: none; }
    footer { display: none !important; }
    .block-container { padding-top: 1rem !important; padding-bottom: 0 !important; max-width: 100% !important; }
    
    .terminal-section {
        background-color: #06090e;
        border: 1px solid #30363d;
        border-radius: 6px;
        padding: 15px 20px;
        margin-top: 15px;
        min-height: 250px;
        font-family: 'SFMono-Regular', Consolas, monospace;
        color: #5af78e;
        white-space: pre-wrap;
    }
    .stderr-text { color: #ff5c57; }
</style>
""", unsafe_allow_html=True)

# Self-contained Top Navbar and Tab (No unclosed HTML divs)
st.markdown("""
<div style="display:flex; justify-content:space-between; align-items:center; border-bottom:1px solid #30363d; padding-bottom:12px; margin-bottom:15px;">
    <div style="display:flex; align-items:center; gap:12px;">
        <div style="background:#cc1414; color:#fff; font-weight:900; font-size:22px; padding:6px 14px; border-radius:8px; box-shadow:0 4px 10px rgba(204,20,20,0.3);">TT</div>
        <div>
            <h1 style="color:#ff2b2b; font-size:24px; font-weight:900; margin:0; letter-spacing:0.5px; line-height:1;">TELLER</h1>
            <p style="color:#8b949e; font-size:13px; margin:0;">Official Compiler</p>
        </div>
    </div>
</div>
<div style="display:inline-flex; align-items:center; background:#161b22; border-top:3px solid #cc1414; border-left:1px solid #30363d; border-right:1px solid #30363d; padding:8px 16px; font-family:monospace; font-size:14px; font-weight:bold; color:#fff; border-radius:6px 6px 0 0; margin-bottom:-1rem; position:relative; z-index:2;">
    main.tt
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

# The Editor
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

# Controls
col1, col2 = st.columns([2, 5])
with col1:
    run_btn = st.button("▶ Run Code", type="primary", use_container_width=True)
with col2:
    user_stdin = st.text_input("Console Input (Stdin)", value="", label_visibility="collapsed", placeholder="Type input here if script asks for it...")

# Execution
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
