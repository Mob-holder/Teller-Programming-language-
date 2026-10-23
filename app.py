import streamlit as st
import subprocess
import tempfile
import os
from streamlit_ace import st_ace

st.set_page_config(page_title="Teller", page_icon="⚡", layout="wide", initial_sidebar_state="collapsed")

# VS Code Clone CSS Injection
st.markdown("""
<style>
    /* Nuke Streamlit's defaults */
    [data-testid="stHeader"] { display: none; }
    footer { display: none !important; }
    .block-container { padding: 0 !important; max-width: 100% !important; height: 100vh; display: flex; flex-direction: column; overflow: hidden; background-color: #1e1e1e; }
    body { background-color: #1e1e1e; color: #cccccc; font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif; }
    
    /* Layout Grid */
    .vscode-layout { display: flex; flex: 1; height: calc(100vh - 22px); width: 100%; overflow: hidden; }
    
    /* Activity Bar (Far Left) */
    .activity-bar { width: 48px; background-color: #333333; display: flex; flex-direction: column; align-items: center; padding-top: 15px; border-right: 1px solid #252526; z-index: 10; }
    .activity-icon { width: 24px; height: 24px; background-color: #858585; margin-bottom: 20px; border-radius: 4px; opacity: 0.8; }
    .activity-icon.active { border-left: 2px solid #ffffff; border-radius: 0; background-color: #ffffff; opacity: 1; }
    
    /* Explorer Sidebar */
    .explorer-sidebar { width: 200px; background-color: #252526; display: flex; flex-direction: column; }
    .explorer-title { font-size: 11px; text-transform: uppercase; color: #cccccc; padding: 10px 20px; letter-spacing: 0.5px; }
    .explorer-item { padding: 4px 20px 4px 30px; font-size: 13px; color: #cccccc; cursor: pointer; display: flex; align-items: center; gap: 6px; }
    .explorer-item.active { background-color: #37373d; color: #ffffff; }
    .tt-icon { color: #cc1414; font-weight: bold; font-family: monospace; font-size: 14px; }
    
    /* Main Editor Area */
    .editor-area { flex: 1; display: flex; flex-direction: column; background-color: #1e1e1e; min-width: 0; }
    
    /* Editor Tabs */
    .tabs-container { display: flex; background-color: #2d2d2d; border-bottom: 1px solid #1e1e1e; overflow-x: auto; }
    .tab { background-color: #1e1e1e; color: #ffffff; padding: 8px 16px; font-size: 13px; border-top: 1px solid #007acc; border-right: 1px solid #2d2d2d; display: flex; align-items: center; gap: 6px; cursor: default; }
    
    /* Terminal Area */
    .terminal-container { height: 260px; background-color: #1e1e1e; border-top: 1px solid #333333; display: flex; flex-direction: column; }
    .terminal-header { display: flex; background-color: #1e1e1e; border-bottom: 1px solid #333333; }
    .terminal-tab { color: #e7e7e7; padding: 8px 16px; font-size: 12px; text-transform: uppercase; border-bottom: 1px solid #e7e7e7; cursor: default; }
    .terminal-output { flex: 1; padding: 10px 16px; font-family: 'Consolas', 'Courier New', monospace; font-size: 13px; overflow-y: auto; color: #cccccc; white-space: pre-wrap; }
    .stdout-text { color: #4af626; }
    .stderr-text { color: #f48771; }
    
    /* Blue Status Bar */
    .status-bar { height: 22px; background-color: #007acc; color: #ffffff; display: flex; justify-content: space-between; align-items: center; padding: 0 10px; font-size: 12px; position: fixed; bottom: 0; left: 0; right: 0; z-index: 100; }
    .status-item { display: flex; align-items: center; gap: 6px; cursor: default; }
    .status-item:hover { background-color: rgba(255,255,255,0.1); }
</style>
""", unsafe_allow_html=True)

# Layout Structure (Sidebar + Editor + Terminal)
st.markdown("""
<div class="vscode-layout">
    <!-- Activity Bar -->
    <div class="activity-bar">
        <div class="activity-icon active" style="mask: url('data:image/svg+xml;utf8,<svg viewBox=\"0 0 24 24\" xmlns=\"http://www.w3.org/2000/svg\"><path d=\"M4 4h6v6H4V4zm10 0h6v6h-6V4zM4 14h6v6H4v-6zm10 0h6v6h-6v-6z\"/></svg>') no-repeat center; -webkit-mask: url('data:image/svg+xml;utf8,<svg viewBox=\"0 0 24 24\" xmlns=\"http://www.w3.org/2000/svg\"><path d=\"M4 4h6v6H4V4zm10 0h6v6h-6V4zM4 14h6v6H4v-6zm10 0h6v6h-6v-6z\"/></svg>') no-repeat center;"></div>
    </div>
    
    <!-- Explorer Sidebar -->
    <div class="explorer-sidebar">
        <div class="explorer-title">Explorer</div>
        <div style="font-weight: bold; font-size: 11px; padding: 5px 20px; color: #cccccc;">TELLER PROJECT</div>
        <div class="explorer-item active">
            <span class="tt-icon">⚡</span> main.tt
        </div>
        <div class="explorer-item">
            <span style="color:#007acc; font-family:monospace; font-weight:bold;">{}</span> Guidebook.md
        </div>
    </div>
    
    <!-- Editor Area -->
    <div class="editor-area">
        <div class="tabs-container">
            <div class="tab">
                <span class="tt-icon">⚡</span> main.tt
            </div>
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

# Streamlit Ace (The Editor)
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
    min_lines=22,
    key="teller_editor"
)

# Terminal / Controls Section
st.markdown("""
        <div class="terminal-container">
            <div class="terminal-header">
                <div class="terminal-tab">TERMINAL</div>
            </div>
""", unsafe_allow_html=True)

col1, col2 = st.columns([1, 8])
with col1:
    st.markdown("<div style='padding-left:15px; padding-top:10px;'>", unsafe_allow_html=True)
    run_btn = st.button("▶ Run Code", type="primary", use_container_width=True)
    st.markdown("</div>", unsafe_allow_html=True)
with col2:
    st.markdown("<div style='padding-right:15px; padding-top:10px;'>", unsafe_allow_html=True)
    user_stdin = st.text_input("Stdin", value="", label_visibility="collapsed", placeholder="Terminal Input (if required by input.console)...")
    st.markdown("</div>", unsafe_allow_html=True)

# Execution Logic
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
            st.markdown(f'<div class="terminal-output stderr-text">{err}</div>', unsafe_allow_html=True)
        else:
            out = raw_stdout if raw_stdout else "[Execution finished with no output]"
            st.markdown(f'<div class="terminal-output stdout-text">{out}</div>', unsafe_allow_html=True)

    except subprocess.TimeoutExpired:
        st.markdown('<div class="terminal-output stderr-text">FatalError: Execution timed out.</div>', unsafe_allow_html=True)
    finally:
        if os.path.exists(temp_source_path): os.remove(temp_source_path)
        if os.path.exists(temp_dir): os.rmdir(temp_dir)
else:
    st.markdown('<div class="terminal-output">user@teller-studio:~/project$ Waiting for execution...</div>', unsafe_allow_html=True)

# Close Editor Area, Layout, and add Status Bar
st.markdown("""
        </div> <!-- End Terminal -->
    </div> <!-- End Editor Area -->
</div> <!-- End VS Code Layout -->

<!-- Blue Status Bar (Fixed to bottom like VS Code) -->
<div class="status-bar">
    <div style="display:flex; gap:15px;">
        <div class="status-item">⚡ Teller Compiler Active</div>
        <div class="status-item">✖ 0  ⚠ 0</div>
    </div>
    <div style="display:flex; gap:15px;">
        <div class="status-item">Ln 1, Col 1</div>
        <div class="status-item">Spaces: 4</div>
        <div class="status-item">UTF-8</div>
        <div class="status-item">Teller (.tt)</div>
    </div>
</div>
""", unsafe_allow_html=True)

# Hidden Guidebook (To keep it accessible without breaking the layout)
with st.sidebar:
    st.markdown("### 📖 Teller Guidebook")
    st.markdown("""
    **Variables:** `store.var { var("name") = value }`  
    **Input:** `input.console("...") { number.val = [var_name] }`  
    **Functions:** `store.function Name()`  
    **Loops:** `do text.print("...") [1,5]`  
    """)
