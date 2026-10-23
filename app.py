import streamlit as st
import subprocess
import tempfile
import os

st.set_page_config(
    page_title="Teller Studio IDE",
    page_icon="⚡",
    layout="wide"
)

# Dark Studio Styling
st.markdown("""
<style>
    .main { background-color: #0e1117; color: #c9d1d9; }
    .brand-title {
        color: #ff2b2b !important;
        font-family: -apple-system, BlinkMacSystemFont, "Segoe UI", Roboto, sans-serif;
        font-size: 26px !important;
        font-weight: 800 !important;
        margin: 0 !important;
    }
    .brand-subtitle {
        color: #8b949e !important;
        font-size: 13px !important;
        margin: 0 !important;
    }
    .file-tab-custom {
        display: inline-flex;
        align-items: center;
        gap: 8px;
        background: #161b22;
        border-top: 3px solid #cc1414;
        border-left: 1px solid #30363d;
        border-right: 1px solid #30363d;
        padding: 7px 16px;
        font-family: 'Courier New', monospace;
        font-size: 15px;
        font-weight: bold;
        color: #ffffff;
        border-radius: 6px 6px 0 0;
        margin-bottom: 0px;
    }
    .tt-badge-icon {
        background-color: #cc1414;
        color: #ffffff;
        font-weight: 900;
        font-size: 11px;
        padding: 2px 6px;
        border-radius: 4px;
        letter-spacing: 0.5px;
    }
    .symbol-label {
        font-size: 12px;
        color: #8b949e;
        margin-top: 6px;
        margin-bottom: 2px;
    }
    .terminal-box {
        background-color: #06090e;
        border: 1px solid #30363d;
        border-radius: 6px;
        padding: 16px;
        font-family: 'SFMono-Regular', Consolas, 'Liberation Mono', Menlo, monospace;
        font-size: 13.5px;
        line-height: 1.45;
        min-height: 220px;
        white-space: pre-wrap;
    }
    .stdout-text { color: #5af78e; }
    .stderr-text { color: #ff5c57; }
</style>
""", unsafe_allow_html=True)

# Top Bar Header
st.markdown('<p class="brand-title">TELLER STUDIO</p><p class="brand-subtitle">Official compiler and interactive playground for Teller (.tt)</p>', unsafe_allow_html=True)

# Built-in Guidebook Expander
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
      - Booleans: `var("is_active") = true` or `false`
    - **Memory Block Checkpoints:** Every numbered step must finish with `block[1]`, `block[2]`, etc.
    - **Printing & String Interpolation:**
      - Access console with `system.console()` and `output(text.string) { ... }`
      - Use `text.print("Welcome "__player__", you have "__coins__" coins!")`
      - Or use raw connected variables: `text.print("You have "coins" coins!")`
    - **Pipelines / Linking:** Use `:` as "AND THEN". Example: `load(coins) : add(25)`
    - **Making Choices:**
      - `if coins >= 100 then ... end`
      - `or if coins < 50 then ... end`
      - Comparison operators: `>`, `<`, `>=`, `<=`, `==`, `~=` (Not equal).
    - **Strict Parameters:** `(*)` indicates a mandatory field; leaving it blank throws an error.
    """)

# Custom Tab with main.tt followed by TT Icon Badge
st.markdown('<div class="file-tab-custom">main.tt <span class="tt-badge-icon">TT</span></div>', unsafe_allow_html=True)

# Default Working Script
default_script = """workspace.start

    # Step 1: Save data
    store.var {
        var("coins") = 100
        var("player") = "Ghost"
        var("is_ready") = true
    }
    block[1]

    # Step 2: Add 25 coins using the link (:)
    load(coins) : add(25)
    block[2]

    # Step 3: Print result
    if is_ready == true then
        system.console()
        output(text.string) {
            text.print("Welcome back "__player__", you have "__coins__" coins!")
        }
    end
    block[3]

workspace.end"""

if "source_code" not in st.session_state:
    st.session_state["source_code"] = default_script

# Code Area (Clean text area bound to state)
user_code = st.text_area(
    "Source Editor",
    value=st.session_state["source_code"],
    height=340,
    label_visibility="collapsed",
    key="editor_area"
)
st.session_state["source_code"] = user_code

# Pydroid-style Quick Symbol Bar
st.markdown('<div class="symbol-label">QUICK SYMBOLS (PYDROID BAR):</div>', unsafe_allow_html=True)

symbols = ["Tab", ":", '"', "(", ")", "{", "}", "_", "*", "[", "]", "=", ">", "<", "~", "#"]
cols = st.columns(len(symbols))

for idx, sym in enumerate(symbols):
    with cols[idx]:
        if st.button(sym, key=f"sym_btn_{idx}", use_container_width=True):
            insert_text = "\t" if sym == "Tab" else sym
            st.session_state["source_code"] += insert_text
            st.rerun()

# Run Button
run_btn = st.button("▶ Run Code", type="primary")

st.markdown("#### Terminal Output")

if run_btn:
    temp_dir = tempfile.mkdtemp()
    temp_source_path = os.path.join(temp_dir, "main.tt")

    with open(temp_source_path, "w", encoding="utf-8") as f:
        f.write(st.session_state["source_code"])

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
