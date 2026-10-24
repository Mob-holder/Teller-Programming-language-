import streamlit as st
import subprocess
import tempfile
import os
from streamlit_ace import st_ace

st.set_page_config(page_title="Teller", page_icon="⚡", layout="wide", initial_sidebar_state="collapsed")

# Initialize Session State for Tabs and Output
if "active_tab" not in st.session_state:
    st.session_state.active_tab = "Code"
if "has_run" not in st.session_state:
    st.session_state.has_run = False
if "terminal_out" not in st.session_state:
    st.session_state.terminal_out = ""
if "is_error" not in st.session_state:
    st.session_state.is_error = False

# Clean Global CSS
st.markdown("""
<style>
    /* Dark Theme Base */
    .main { background-color: #0e1117; color: #c9d1d9; }
    [data-testid="stHeader"] { display: none; }
    footer { display: none !important; }
    .block-container { padding-top: 2rem !important; padding-bottom: 2rem !important; max-width: 1000px !important; }
    
    /* Segmented Control Buttons (Sticking Code & Output together) */
    div[data-testid="column"]:nth-child(1) { padding-right: 0 !important; }
    div[data-testid="column"]:nth-child(2) { padding-left: 0 !important; }
    div[data-testid="column"]:nth-child(1) button { 
        border-radius: 6px 0 0 6px !important; 
        border-right: none !important; 
        background-color: #161b22; 
        color: #c9d1d9;
    }
    div[data-testid="column"]:nth-child(2) button { 
        border-radius: 0 6px 6px 0 !important; 
        background-color: #161b22; 
        color: #c9d1d9;
    }
    
    /* File Tab */
    .file-tab-container {
        display: inline-flex; align-items: center; justify-content: space-between;
        background: #161b22; border-top: 3px solid #cc1414; 
        border-left: 1px solid #30363d; border-right: 1px solid #30363d;
        padding: 8px 16px; font-family: monospace; font-size: 14px; 
        font-weight: bold; color: #fff; border-radius: 6px 6px 0 0; 
        margin-bottom: -1rem; position: relative; z-index: 2;
        width: 180px;
    }
    .file-tt-icon {
        background-color: #cc1414; color: white; padding: 2px 5px; 
        border-radius: 3px; font-size: 10px; font-weight: 900; margin-right: 8px;
    }
    .file-add-btn {
        color: #8b949e; cursor: pointer; font-size: 16px; margin-left: auto;
    }
    .file-add-btn:hover { color: #fff; }
    
    /* Terminal Styles */
    .terminal-section {
        background-color: #06090e; border: 1px solid #30363d; border-radius: 6px;
        padding: 15px 20px; margin-top: 15px; min-height: 350px;
        font-family: 'SFMono-Regular', Consolas, monospace; white-space: pre-wrap;
    }
    .stdout-text { color: #5af78e; }
    .stderr-text { color: #ff5c57; }
</style>
""", unsafe_allow_html=True)

# Top Navbar (TT Logo + Title + Segmented Control)
col_logo, col_btn1, col_btn2, col_space = st.columns([4, 1.5, 1.5, 2])

with col_logo:
    st.markdown("""
    <div style="display:flex; align-items:center; gap:12px; margin-bottom: 20px;">
        <div style="background-color: #cc1414; color: white; width: 38px; height: 38px; display: flex; align-items: center; justify-content: center; font-family: monospace; font-weight: 900; font-size: 20px; border-radius: 6px; box-shadow: 0 2px 5px rgba(204,20,20,0.4);">TT</div>
        <div>
            <h1 style="color:#ff2b2b; font-size:24px; font-weight:900; margin:0; letter-spacing:0.5px; line-height:1;">TELLER</h1>
            <p style="color:#8b949e; font-size:13px; margin:0;">Official Compiler</p>
        </div>
    </div>
    """, unsafe_allow_html=True)

with col_btn1:
    if st.button("Code", use_container_width=True):
        st.session_state.active_tab = "Code"
        st.rerun()

with col_btn2:
    if st.button("Output", use_container_width=True):
        st.session_state.active_tab = "Output"
        st.rerun()


default_script = """workspace.start

# 1. Define a Function
store.function InitPlayer(Name)
    store.var {
        var("player") = "Ghost"
        var("coins") = 100
    }
end

# 2. Call Function
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

# ----------------------------------------
# TAB 1: CODE EDITOR
# ----------------------------------------
if st.session_state.active_tab == "Code":
    # File Tab Header
    st.markdown("""
    <div class="file-tab-container">
        <div style="display:flex; align-items:center;">
            <span class="file-tt-icon">TT</span> main.tt
        </div>
        <span class="file-add-btn">+</span>
    </div>
    """, unsafe_allow_html=True)

    # Clean st_ace component (Not wrapped in custom HTML so you can type perfectly)
    user_code = st_ace(
        value=default_script,
        language="ruby", 
        theme="tomorrow_night_eighties",
        keybinding="vscode",
        font_size=14,
        tab_size=4,
        show_gutter=True, # Enables line numbers natively
        wrap=True,
        auto_update=True,
        min_lines=18,
        key="teller_editor"
    )

    # Console Input & Run Button
    col_run, col_in = st.columns([2, 5])
    with col_run:
        run_btn = st.button("▶ Run Code", type="primary", use_container_width=True)
    with col_in:
        user_stdin = st.text_input("Console Input", value="", label_visibility="collapsed", placeholder="Type terminal input here if script asks for it...")

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

            st.session_state.has_run = True
            if proc.returncode != 0 or raw_stderr:
                st.session_state.is_error = True
                st.session_state.terminal_out = raw_stderr if raw_stderr else raw_stdout
            else:
                st.session_state.is_error = False
                st.session_state.terminal_out = raw_stdout if raw_stdout else "[Program executed successfully]"
            
            # Switch to Output tab automatically
            st.session_state.active_tab = "Output"
            st.rerun()

        except subprocess.TimeoutExpired:
            st.session_state.has_run = True
            st.session_state.is_error = True
            st.session_state.terminal_out = "FatalError: Execution timed out."
            st.session_state.active_tab = "Output"
            st.rerun()
        finally:
            if os.path.exists(temp_source_path): os.remove(temp_source_path)
            if os.path.exists(temp_dir): os.rmdir(temp_dir)

# ----------------------------------------
# TAB 2: OUTPUT SCREEN
# ----------------------------------------
elif st.session_state.active_tab == "Output":
    
    # If the user hasn't clicked run yet, show the placeholder Live Console screen
    if not st.session_state.has_run:
        st.markdown("""
        <div style="display: flex; flex-direction: column; align-items: center; justify-content: center; height: 400px; color: #8b949e; background-color: #06090e; border: 1px solid #30363d; border-radius: 6px;">
            <div style="font-size: 56px; margin-bottom: 10px; font-family: monospace; font-weight: bold; color: #586069;">>_</div>
            <h3 style="margin: 0; color: #c9d1d9; font-weight: 500;">Live Console</h3>
            <p style="margin: 8px 0 0 0; font-size: 14px;">Click Run to start</p>
        </div>
        """, unsafe_allow_html=True)
    else:
        # Show actual output
        color_class = "stderr-text" if st.session_state.is_error else "stdout-text"
        st.markdown(f"""
        <div class="terminal-section {color_class}">
{st.session_state.terminal_out}
        </div>
        """, unsafe_allow_html=True)

# Hidden Guidebook included at the bottom for reference
with st.expander("📖 Teller Language Guidebook & Grammar", expanded=False):
    st.markdown("""
    **Variables:** `store.var { var("name") = value }`  
    **Input:** `input.console("...") { number.val = [var_name] }`  
    **Functions:** `store.function Name()`  
    **Loops:** `do text.print("...") [1,5]`  
    """)
