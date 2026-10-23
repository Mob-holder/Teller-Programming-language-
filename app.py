import streamlit as st
import subprocess
import tempfile
import os
from streamlit_ace import st_ace

st.set_page_config(page_title="Teller", page_icon="⚡", layout="wide")

st.markdown("""
<style>
    .main { background-color: #0e1117; color: #c9d1d9; }
    .header-box { display: flex; align-items: center; gap: 14px; margin-bottom: 8px; }
    .tt-top-logo {
        background: #cc1414; color: #ffffff; font-family: -apple-system, BlinkMacSystemFont, sans-serif;
        font-weight: 900; font-size: 26px; letter-spacing: -1px; width: 50px; height: 50px;
        border-radius: 10px; display: flex; align-items: center; justify-content: center;
        box-shadow: 0 4px 12px rgba(204, 20, 20, 0.4);
    }
    .brand-title { color: #ff2b2b !important; font-size: 32px !important; font-weight: 900 !important; margin: 0 !important; letter-spacing: 0.5px; }
    .brand-subtitle { color: #8b949e !important; font-size: 13px !important; margin: 0 !important; }
    .file-tab-custom {
        display: inline-flex; align-items: center; gap: 8px; background: #161b22;
        border-top: 3px solid #cc1414; border-left: 1px solid #30363d; border-right: 1px solid #30363d;
        padding: 7px 16px; font-family: 'Courier New', monospace; font-size: 14px; font-weight: bold; color: #ffffff;
        border-radius: 6px 6px 0 0; margin-bottom: 0px;
    }
    .tab-badge { background-color: #cc1414; color: #ffffff; font-weight: 900; font-size: 10px; padding: 2px 6px; border-radius: 3px; letter-spacing: 0.5px; }
    .terminal-box {
        background-color: #06090e; border: 1px solid #30363d; border-radius: 6px;
        padding: 16px; font-family: 'SFMono-Regular', Consolas, monospace;
        font-size: 13.5px; line-height: 1.45; min-height: 220px; white-space: pre-wrap;
    }
    .stdout-text { color: #5af78e; }
    .stderr-text { color: #ff5c57; }
</style>
""", unsafe_allow_html=True)

st.markdown("""
<div class="header-box">
    <div class="tt-top-logo">TT</div>
    <div>
        <p class="brand-title">TELLER</p>
        <p class="brand-subtitle">Official compiler and interactive playground for Teller (.tt)</p>
    </div>
</div>
""", unsafe_allow_html=True)

with st.expander("📖 Teller Language Guidebook & Grammar Rules", expanded=False):
    st.markdown("""
    ### **Teller's Rules and Grammars**
    - **Extension:** `.tt` (Example: `main.tt`)
    - **Start and End:** Always type `workspace.start` on line 1 and finish with `workspace.end`.
    - **Variables & Scopes:** 
      - Enclose in `store.var { ... }`
      - Text: `var("player") = "Ghost"`
      - Numbers: `var("coins") = 50`
      - Direct Math: `var("calc") = 10 + 5`
      - Booleans: Strictly lowercase `true` or `false`
    - **Memory Block Checkpoints:** Every numbered step must finish with `block[1]`, `block[2]`, etc.
    - **Printing & String Interpolation:**
      - Access console with `system.console()` and `output(text.string) { ... }`
      - Use `text.print("Welcome "__player__", you have "__coins__" coins!")`
    - **Pipelines / Linking:** Use `:` as "AND THEN". Example: `load(coins) : add(25)`
    - **Making Choices:**
      - `if coins >= 100 then ... end`
      - `or if coins < 50 then ... end`
      - Comparison operators: `>`, `<`, `>=`, `<=`, `==`, `~=` (Not equal).
    - **Strict Parameters:** `(*)` indicates a mandatory field.
    """)

st.markdown('<div class="file-tab-custom">main.tt <span class="tab-badge">TT</span></div>', unsafe_allow_html=True)

default_script = """workspace.start

# Step 1: Save data
store.var {
    var("coins") = 100
    var("player") = "Ghost"
}
block[1]

# Step 2: Add 25 coins using the link (:)
load(coins) : add(25)
block[2]

# Step 3: Print result
system.console()
output(text.string) {
    text.print("Welcome back "__player__", you have "__coins__" coins!")
}
block[3]

workspace.end"""

# Reliable Ace Editor (Native Streamlit Component)
user_code = st_ace(
    value=default_script,
    language="ruby", 
    theme="tomorrow_night_eighties",
    keybinding="vscode",
    font_size=15,
    tab_size=4,
    show_gutter=True,
    wrap=True,
    auto_update=True,  # Ensures every keystroke is saved immediately
    min_lines=18,
    key="teller_editor"
)

# Native Run Button ensuring proper backend execution
run_btn = st.button("▶ Run Code", type="primary")

st.markdown("#### Terminal Output")

if run_btn:
    temp_dir = tempfile.mkdtemp()
    temp_source_path = os.path.join(temp_dir, "main.tt")

    with open(temp_source_path, "w", encoding="utf-8") as f:
        f.write(user_code)

    try:
        proc = subprocess.run(
            ["python", "teller.py", temp_source_path],
            capture_output=True,
            text=True,
            timeout=5
        )

        raw_stdout = proc.stdout.replace(temp_source_path, "main.tt")
        raw_stderr = proc.stderr.replace(temp_source_path, "main.tt")

        if proc.returncode != 0 or raw_stderr:
            err_msg = raw_stderr if raw_stderr else raw_stdout
            st.markdown(f'<div class="terminal-box stderr-text">{err_msg}</div>', unsafe_allow_html=True)
        else:
            out_msg = raw_stdout if raw_stdout else "[Program executed successfully with no output]"
            st.markdown(f'<div class="terminal-box stdout-text">{out_msg}</div>', unsafe_allow_html=True)

    except subprocess.TimeoutExpired:
        st.markdown('<div class="terminal-box stderr-text">FatalError: Execution timed out.</div>', unsafe_allow_html=True)
    except Exception as exc:
        st.markdown(f'<div class="terminal-box stderr-text">InternalError: {exc}</div>', unsafe_allow_html=True)
    finally:
        if os.path.exists(temp_source_path):
            os.remove(temp_source_path)
        if os.path.exists(temp_dir):
            os.rmdir(temp_dir)
else:
    st.markdown('<div class="terminal-box" style="color:#545d68;">Click "▶ Run Code" to compile and run...</div>', unsafe_allow_html=True)
