import streamlit as st
import subprocess
import tempfile
import os
import streamlit.components.v1 as components

st.set_page_config(
    page_title="Teller",
    page_icon="⚡",
    layout="wide"
)

# Custom Dark Styling
st.markdown("""
<style>
    .main { background-color: #0e1117; color: #c9d1d9; }
    .header-box {
        display: flex;
        align-items: center;
        gap: 14px;
        margin-bottom: 8px;
    }
    .tt-top-logo {
        background: #cc1414;
        color: #ffffff;
        font-family: -apple-system, BlinkMacSystemFont, "Segoe UI", Roboto, sans-serif;
        font-weight: 900;
        font-size: 26px;
        letter-spacing: -1px;
        width: 52px;
        height: 52px;
        border-radius: 10px;
        display: flex;
        align-items: center;
        justify-content: center;
        box-shadow: 0 4px 12px rgba(204, 20, 20, 0.4);
    }
    .brand-title {
        color: #ff2b2b !important;
        font-family: -apple-system, BlinkMacSystemFont, "Segoe UI", Roboto, sans-serif;
        font-size: 32px !important;
        font-weight: 900 !important;
        margin: 0 !important;
        letter-spacing: 0.5px;
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
        font-size: 14px;
        font-weight: bold;
        color: #ffffff;
        border-radius: 6px 6px 0 0;
        margin-bottom: 0px;
    }
    .tab-badge {
        background-color: #cc1414;
        color: #ffffff;
        font-weight: 900;
        font-size: 10px;
        padding: 2px 6px;
        border-radius: 3px;
        letter-spacing: 0.5px;
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

# Top Bar: Red TT Logo on top + Pure "TELLER"
st.markdown("""
<div class="header-box">
    <div class="tt-top-logo">TT</div>
    <div>
        <p class="brand-title">TELLER</p>
        <p class="brand-subtitle">Official compiler and interactive playground for Teller (.tt)</p>
    </div>
</div>
""", unsafe_allow_html=True)

# Guidebook Expander
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

# Clean File Tab with TT Badge (No broken raw SVG leakage)
st.markdown('<div class="file-tab-custom">main.tt <span class="tab-badge">TT</span></div>', unsafe_allow_html=True)

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

# Interactive OneCompiler IDE with Native Fast Symbol Bar & Teller Keywords
ide_component = f"""
<!DOCTYPE html>
<html>
<head>
    <script src="https://cdnjs.cloudflare.com/ajax/libs/ace/1.32.7/ace.js"></script>
    <script src="https://cdnjs.cloudflare.com/ajax/libs/ace/1.32.7/ext-language_tools.js"></script>
    <style>
        body {{ margin: 0; background: #0e1117; font-family: sans-serif; }}
        #editor {{
            width: 100%;
            height: 330px;
            font-size: 15px;
            border: 1px solid #30363d;
            border-radius: 0 6px 0 0;
        }}
        .symbol-bar {{
            display: flex;
            background: #161b22;
            border: 1px solid #30363d;
            border-top: none;
            padding: 6px;
            gap: 4px;
            overflow-x: auto;
            border-radius: 0 0 6px 6px;
        }}
        .sym-btn {{
            background: #21262d;
            border: 1px solid #30363d;
            color: #c9d1d9;
            padding: 6px 11px;
            font-family: monospace;
            font-size: 14px;
            border-radius: 4px;
            cursor: pointer;
            white-space: nowrap;
        }}
        .sym-btn:hover {{
            background: #30363d;
            color: #ffffff;
            border-color: #ff2b2b;
        }}
    </style>
</head>
<body>
    <div id="editor">{default_script}</div>
    <div class="symbol-bar">
        <button class="sym-btn" onclick="insertSym('\\t')">Tab</button>
        <button class="sym-btn" onclick="insertSym(':')">:</button>
        <button class="sym-btn" onclick="insertSym('\\"')">"</button>
        <button class="sym-btn" onclick="insertSym('(')">(</button>
        <button class="sym-btn" onclick="insertSym(')')">)</button>
        <button class="sym-btn" onclick="insertSym('{{')">{{</button>
        <button class="sym-btn" onclick="insertSym('}}')">}}</button>
        <button class="sym-btn" onclick="insertSym('_')">_</button>
        <button class="sym-btn" onclick="insertSym('*')">*</button>
        <button class="sym-btn" onclick="insertSym('[')">[</button>
        <button class="sym-btn" onclick="insertSym(']')">]</button>
        <button class="sym-btn" onclick="insertSym('=')">=</button>
        <button class="sym-btn" onclick="insertSym('>')">&gt;</button>
        <button class="sym-btn" onclick="insertSym('<')">&lt;</button>
        <button class="sym-btn" onclick="insertSym('~=')">~=</button>
        <button class="sym-btn" onclick="insertSym('#')">#</button>
    </div>

    <script>
        var editor = ace.edit("editor");
        editor.setTheme("ace/theme/tomorrow_night_eighties");
        editor.session.setMode("ace/mode/text");
        editor.setOptions({{
            enableBasicAutocompletion: true,
            enableSnippets: true,
            enableLiveAutocompletion: true,
            showLineNumbers: true,
            tabSize: 4,
            useSoftTabs: true,
            behavioursEnabled: true,
            wrap: true
        }});

        // Only Teller Keywords
        var tellerCompleter = {{
            getCompletions: function(editor, session, pos, prefix, callback) {{
                var keywords = [
                    {{ caption: "workspace.start", value: "workspace.start\\n\\t", meta: "scope" }},
                    {{ caption: "workspace.end", value: "workspace.end", meta: "scope" }},
                    {{ caption: "store.var", value: "store.var {{\\n\\tvar(\\"coins\\") = 50\\n}}", meta: "storage" }},
                    {{ caption: "var", value: "var(\\"name\\") = ", meta: "var" }},
                    {{ caption: "true", value: "true", meta: "bool" }},
                    {{ caption: "false", value: "false", meta: "bool" }},
                    {{ caption: "load", value: "load(coins) : add(25)", meta: "pipeline" }},
                    {{ caption: "add", value: "add()", meta: "math" }},
                    {{ caption: "sub", value: "sub()", meta: "math" }},
                    {{ caption: "mult", value: "mult()", meta: "math" }},
                    {{ caption: "div", value: "div()", meta: "math" }},
                    {{ caption: "block[1]", value: "block[1]", meta: "step" }},
                    {{ caption: "block[2]", value: "block[2]", meta: "step" }},
                    {{ caption: "block[3]", value: "block[3]", meta: "step" }},
                    {{ caption: "if ... then", value: "if coins >= 100 then\\n\\t\\nend", meta: "control" }},
                    {{ caption: "or if ... then", value: "or if coins < 50 then\\n\\t\\nend", meta: "control" }},
                    {{ caption: "end", value: "end", meta: "control" }},
                    {{ caption: "system.console()", value: "system.console()", meta: "system" }},
                    {{ caption: "output(text.string)", value: "output(text.string) {{\\n\\ttext.print(\\"\\")\\n}}", meta: "output" }},
                    {{ caption: "text.print", value: "text.print(\\"\\")", meta: "print" }}
                ];
                callback(null, keywords);
            }}
        }};

        var langTools = ace.require("ace/ext/language_tools");
        langTools.setCompleters([tellerCompleter]);

        function insertSym(sym) {{
            editor.insert(sym);
            editor.focus();
            updateParent();
        }}

        function updateParent() {{
            var content = editor.getValue();
            var target = window.parent.document.querySelector('textarea[aria-label="hidden_source_bridge"]');
            if (target) {{
                target.value = content;
                target.dispatchEvent(new Event('input', {{ bubbles: true }}));
            }}
        }}

        editor.session.on('change', updateParent);
        setTimeout(updateParent, 400);
    </script>
</body>
</html>
"""

components.html(ide_component, height=410)

# Hidden Bridge Area for Execution Sync
source_code = st.text_area("hidden_source_bridge", value=default_script, label_visibility="collapsed")
st.markdown("<style>textarea[aria-label='hidden_source_bridge'] { display: none !important; }</style>", unsafe_allow_html=True)

# Run Button Bar
run_btn = st.button("▶ Run Code", type="primary")

st.markdown("#### Terminal Output")

if run_btn:
    temp_dir = tempfile.mkdtemp()
    temp_source_path = os.path.join(temp_dir, "main.tt")

    with open(temp_source_path, "w", encoding="utf-8") as f:
        f.write(source_code)

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
