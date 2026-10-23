import streamlit as st
import subprocess
import tempfile
import os
import streamlit.components.v1 as components

st.set_page_config(page_title="Teller", page_icon="⚡", layout="wide")

st.markdown("""
<style>
    .main { background-color: #0e1117; color: #c9d1d9; }
    .header-box { display: flex; align-items: center; gap: 14px; margin-bottom: 8px; }
    .tt-top-logo {
        background: #cc1414; color: #ffffff; font-family: sans-serif;
        font-weight: 900; font-size: 26px; letter-spacing: -1px;
        width: 50px; height: 50px; border-radius: 10px;
        display: flex; align-items: center; justify-content: center;
    }
    .brand-title { color: #ff2b2b !important; font-size: 32px !important; font-weight: 900 !important; margin: 0 !important; }
    .brand-subtitle { color: #8b949e !important; font-size: 13px !important; margin: 0 !important; }
    .file-tab-custom {
        display: inline-flex; align-items: center; gap: 8px; background: #161b22;
        border-top: 3px solid #cc1414; border-left: 1px solid #30363d; border-right: 1px solid #30363d;
        padding: 7px 16px; font-family: monospace; font-size: 14px; font-weight: bold; color: #ffffff;
        border-radius: 6px 6px 0 0; margin-bottom: 0px;
    }
    .tab-badge { background-color: #cc1414; color: #ffffff; font-weight: 900; font-size: 10px; padding: 2px 6px; border-radius: 3px; }
    .terminal-box {
        background-color: #06090e; border: 1px solid #30363d; border-radius: 6px;
        padding: 16px; font-family: monospace; font-size: 13.5px; min-height: 220px; white-space: pre-wrap;
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

with st.expander("📖 Teller Rules and Cheat Sheet", expanded=False):
    st.markdown("""
    1. **HOW TO START AND END**
       `workspace.start` / `workspace.end`
    2. **HOW TO SAVE INFORMATION**
       `store.var { var("coins") = 50 }`
    3. **SPECIAL TELLER SYMBOLS**
       `:` Chains actions (e.g. `load(coins) : add(20)`)
       `(*)` Mandatory field
       `block[1]` Memory step checkpoint
    4. **MAKING CHOICES**
       `if coins >= 100 then ... end`
    5. **SHOWING TEXT**
       `system.console()`
       `output(text.string) { text.print("You have "coins" coins!") }`
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

ide_component = f"""
<!DOCTYPE html>
<html>
<head>
    <script src="https://cdnjs.cloudflare.com/ajax/libs/ace/1.32.7/ace.js"></script>
    <script src="https://cdnjs.cloudflare.com/ajax/libs/ace/1.32.7/ext-language_tools.js"></script>
    <style>
        body {{ margin: 0; background: #0e1117; font-family: sans-serif; }}
        #editor {{ width: 100%; height: 330px; font-size: 15px; border: 1px solid #30363d; border-radius: 0 6px 0 0; }}
        .symbol-bar {{ display: flex; background: #161b22; border: 1px solid #30363d; border-top: none; padding: 6px; gap: 4px; overflow-x: auto; border-radius: 0 0 6px 6px; }}
        .sym-btn {{ background: #21262d; border: 1px solid #30363d; color: #c9d1d9; padding: 6px 11px; font-family: monospace; font-size: 14px; border-radius: 4px; cursor: pointer; white-space: nowrap; }}
        .sym-btn:hover {{ background: #30363d; color: #ffffff; border-color: #ff2b2b; }}
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
        // Ruby mode enables colorful # comments, strings, and standard keywords
        editor.session.setMode("ace/mode/ruby"); 
        
        editor.setOptions({{ 
            enableBasicAutocompletion: true, 
            enableSnippets: true, 
            enableLiveAutocompletion: true, 
            showLineNumbers: true, 
            tabSize: 4, 
            useSoftTabs: true, 
            behavioursEnabled: true 
        }});

        var tellerCompleter = {{
            getCompletions: function(editor, session, pos, prefix, callback) {{
                var keywords = [
                    {{ caption: "if", value: "if ", meta: "keyword" }}, {{ caption: "or", value: "or ", meta: "keyword" }},
                    {{ caption: "then", value: "then", meta: "keyword" }}, {{ caption: "end", value: "end", meta: "keyword" }},
                    {{ caption: "workspace.start", value: "workspace.start\\n\\t", meta: "keyword" }},
                    {{ caption: "workspace.end", value: "workspace.end", meta: "keyword" }},
                    {{ caption: "store.var", value: "store.var {{\\n\\tvar(\\"*\\") = \\n}}", meta: "keyword" }},
                    {{ caption: "var", value: "var(\\"*\\") = ", meta: "keyword" }},
                    {{ caption: "block", value: "block[*]", meta: "keyword" }},
                    {{ caption: "load", value: "load(*)", meta: "keyword" }},
                    {{ caption: "add", value: "add(*)", meta: "math" }}, {{ caption: "sub", value: "sub(*)", meta: "math" }},
                    {{ caption: "mult", value: "mult(*)", meta: "math" }}, {{ caption: "div", value: "div(*)", meta: "math" }},
                    {{ caption: "system.console()", value: "system.console()", meta: "keyword" }},
                    {{ caption: "output(text.string)", value: "output(text.string) {{\\n\\ttext.print(\\"*\\")\\n}}", meta: "keyword" }},
                    {{ caption: "text.print", value: "text.print(\\"*\\")", meta: "keyword" }}
                ];
                callback(null, keywords);
            }}
        }};
        
        // This strictly replaces default completers so you only see Teller words
        var langTools = ace.require("ace/ext/language_tools");
        langTools.setCompleters([tellerCompleter]);

        function insertSym(sym) {{
            editor.insert(sym); editor.focus(); updateParent();
        }}
        function updateParent() {{
            var content = editor.getValue();
            var target = window.parent.document.querySelector('.stTextArea textarea');
            if (target) {{
                var nativeSetter = Object.getOwnPropertyDescriptor(window.HTMLTextAreaElement.prototype, "value").set;
                nativeSetter.call(target, content);
                target.dispatchEvent(new Event('input', {{ bubbles: true }}));
            }}
        }}
        editor.session.on('change', updateParent);
        setTimeout(updateParent, 500);
    </script>
</body>
</html>
"""
components.html(ide_component, height=410)

source_code = st.text_area("hidden_bridge", value=default_script, label_visibility="collapsed")
st.markdown("<style>.stTextArea { display: none !important; }</style>", unsafe_allow_html=True)

run_btn = st.button("▶ Run Code", type="primary")
st.markdown("#### Terminal Output")

if run_btn:
    temp_dir = tempfile.mkdtemp()
    temp_source_path = os.path.join(temp_dir, "main.tt")

    with open(temp_source_path, "w", encoding="utf-8") as f:
        f.write(source_code)

    try:
        proc = subprocess.run(["python", "teller.py", temp_source_path], capture_output=True, text=True, timeout=5)
        raw_stdout = proc.stdout.replace(temp_source_path, "main.tt")
        raw_stderr = proc.stderr.replace(temp_source_path, "main.tt")

        if proc.returncode != 0 or raw_stderr:
            err_msg = raw_stderr if raw_stderr else raw_stdout
            st.markdown(f'<div class="terminal-box stderr-text">{err_msg}</div>', unsafe_allow_html=True)
        else:
            out_msg = raw_stdout if raw_stdout else "[Program executed successfully with no output]"
            st.markdown(f'<div class="terminal-box stdout-text">{out_msg}</div>', unsafe_allow_html=True)
    except Exception as exc:
        st.markdown(f'<div class="terminal-box stderr-text">InternalError: {exc}</div>', unsafe_allow_html=True)
