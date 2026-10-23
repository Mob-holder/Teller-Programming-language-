import streamlit as st
import subprocess
import tempfile
import os

st.set_page_config(page_title="Teller Online Compiler", layout="wide")

st.title("⚡ Teller (.tt) Online Playground")
st.caption("Write your Teller code below and click Run!")

default_code = '''workspace.start
    store.var {
        var("player") = "Champion"
        var("coins") = 100
    }
    load(coins) : add(50)
    system.console()
    output(text.string) {
        text.print("Welcome __player__! Total Gold: __coins__")
    }
workspace.end'''

col1, col2 = st.columns(2)

with col1:
    user_code = st.text_area("Your Teller Code (.tt)", default_code, height=350)
    run_btn = st.button("▶ Run Code", type="primary")

with col2:
    st.subheader("Console Output")
    if run_btn:
        # Save user code to a temporary .tt file
        with tempfile.NamedTemporaryFile(delete=False, suffix=".tt", mode="w") as f:
            f.write(user_code)
            temp_path = f.name
        
        # Run it through your teller.py
        try:
            result = subprocess.run(
                ["python", "teller.py", temp_path],
                capture_output=True,
                text=True,
                timeout=5
            )
            if result.stdout:
                st.code(result.stdout, language="text")
            if result.stderr:
                st.error(result.stderr)
        except Exception as e:
            st.error(str(e))
        finally:
            if os.path.exists(temp_path):
                os.remove(temp_path)
