import streamlit as st
import subprocess
import tempfile
import os
import html
from streamlit_ace import st_ace

st.set_page_config(page_title="Teller", page_icon="⚡", layout="wide", initial_sidebar_state="collapsed")

# Initialize Session State
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
    .main { background-color: #0e1117; color: #c9d1d9; }
    [data-testid="stHeader"] { display: none; }
    footer { display: none !important; }
    .block-container { padding-top: 2rem !important; padding-bottom: 2rem !important; max-width: 1000px !important; }
    
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
    
    .terminal-section {
        background-color: #06090e; border: 1px solid #30363d; border-radius: 6px;
        padding: 15px 20px; margin-top: 15px; min-height: 350px;
        font-family: 'SFMono-Regular', Consolas, monospace; white-space: pre-wrap;
    }
    .stdout-text { color: #5af78e; }
    .stderr-text { color: #ff5c57; }
</style>
""", unsafe_allow_html=True)

# Top Navbar
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

# ----------------------------------------
# TAB 1: CODE EDITOR
# ----------------------------------------
if st.session_state.active_tab == "Code":
    st.markdown("""
    <div class="file-tab-container">
        <div style="display:flex; align-items:center;">
            <span class="file-tt-icon">TT</span> main.tt
        </div>
        <span class="file-add-btn">+</span>
    </div>
    """, unsafe_allow_html=True)

    # Changed language to "text" to kill Ruby autocompletes like "chomp"
    user_code = st_ace(
        value=default_script,
        language="text", 
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
    
    if not st.session_state.has_run:
        st.markdown("""
        <div style="display: flex; flex-direction: column; align-items: center; justify-content: center; height: 400px; color: #8b949e; background-color: #06090e; border: 1px solid #30363d; border-radius: 6px;">
            <div style="font-size: 56px; margin-bottom: 10px; font-family: monospace; font-weight: bold; color: #586069;">>_</div>
            <h3 style="margin: 0; color: #c9d1d9; font-weight: 500;">Live Console</h3>
            <p style="margin: 8px 0 0 0; font-size: 14px;">Click Run to start</p>
        </div>
        """, unsafe_allow_html=True)
    else:
        color_class = "stderr-text" if st.session_state.is_error else "stdout-text"
        # html.escape forces browsers to treat <module> as plain text, preventing layout breaks
        safe_output = html.escape(st.session_state.terminal_out)
        
        st.markdown(f"""
        <div class="terminal-section {color_class}">
{safe_output}
        </div>
        """, unsafe_allow_html=True)

# ----------------------------------------
# GUIDEBOOK
# ----------------------------------------
with st.expander("📖 Teller Language Guidebook & Grammar", expanded=False):
    st.markdown("""
# Teller's Rules and Grammar

Teller File extension - `.tt`  
Example - `main.tt`  
Our Compiler - [https://y4n85txldtzxkojiy5zexb.streamlit.app/](https://y4n85txldtzxkojiy5zexb.streamlit.app/)

## Grammars
- **Start and End:** Always type `workspace.start` at the beginning and end it with `workspace.end`.
- **Strings and variables:** You must use variables as `var` inside the scripts. To print a variable, just type the variable name inside the print text. To connect the variable and the text inside print, check this example: `text.print("You currently have "__coins__" coins!")`. In this situation, `__` is used to connect the words with each other and `"coins"` is a variable.
- **Linking or connecting words outside of print:** Use `:` instead of `and` to link words. Think of this word as `and`.
- **Memory block indexing:** If you do every step (like at the first step you made the variables and stored their info), then after this you'll have to type `block[1]` or `block[2]` according to the count of the blocks or the steps.
- **Strict parameters and parentheses:** Use `(*)` when the word is required to be filled.

---

## Teller Rules and Cheat Sheet

### 1. HOW TO START AND END
- `workspace.start` = Turns the code ON (must be on line 1)
- `workspace.end` = Turns the code OFF (goes at the very end)

### 2. HOW TO SAVE INFORMATION
- `store.var` = Opens your memory box
- `var("coins")` = Saves a number (like: `var("coins") = 50`)
- `var("name")` = Saves a word (like: `var("name") = "Ghost"`)

### 3. SPECIAL TELLER SYMBOLS
- `:` = Means "AND THEN". Chains 2 actions together on one line.
  - *Example:* `load(coins) : add(20)`
- `(*)` = Means "REQUIRED". If left blank, it causes an error.
  - *Example:* `string1(*)`
- `__word__` = Shows a saved variable inside your text.
  - *Example:* `text.print("You have "__coins__" coins!")`
- `block[1]` = Marks Step 1 as finished in memory.
- `block[2]` = Marks Step 2 as finished in memory.

### 4. MAKING CHOICES
- `if ... then` = Runs only if the condition is true.
- `or if ... then` = Runs if the first check failed.
- `end` = Per block steps require an `end` at the close. Each `end` should be under its first `end` letter.

### 5. SHOWING TEXT ON SCREEN
- `system.console()` = Turns on the screen output.
- `output(text.string)` = Sends your text to be printed.
- `text.print(...)` = The actual words you want to show.

### 6. LOOPING 
- `do text.print("Hello, World!") [1,3]` = Will print the text 3 times in the output.

### 7. FUNCTIONS
Functions are like a magical spell.
```teller
store.function Player(Health, Age)
    store.var {
        var("Health") = 100
        var("Age") = 18
    }
end
block[1]

Player(Health) 
block[2]

workspace.end

### 8. INPUT TEXTS
To make any user able to answer the questions in the output console, we use input.console.
input.console("Enter your age")
Now, to make the number an actual mathematical value, we use number.val. For example, if the system gives an interactive question asking for your age and you enter 17, Teller wouldn't initially know if it is a mathematical value. If we just type 17+10, it'll print 1710 only. By typing number.val, we are able to add 17 with 10 with the result being 27.
Example:

input.console("Enter your age:") {
    number.val = [age] 
}
load(age) : add(3)
system.console()
output(text.string) {
    text.print("You'll turn "__age__" in 3 years!")
}

SYMBOLS
### 1. Calculation Symbols
+ (Plus) = Adds numbers together. Example: 10 + 5 (equals 15)
- (Minus) = Takes away numbers. Example: 10 - 5 (equals 5)
* (Multiply) = Multiplies numbers (Times). Example: 5 * 2 (equals 10)
/ (Divide) = Divides numbers into parts. Example: 10 / 2 (equals 5)
= (Set / Equals) = Saves a value into a variable. Example: var("Coins") = 50
### 2. Comparison Symbols
> (Greater Than) = Left side is bigger than right. Example: if Level > 10 then
< (Less Than) = Left side is smaller than right. Example: if Level < 5 then
>= (Greater / Equal) = Bigger than or exact match. Example: if Coins >= 100 then
<= (Less / Equal) = Smaller than or exact match. Example: if Health <= 0 then
== (Exact Match) = Checks if both sides are strictly identical. Example: if Name == "Ghost" then
~= (Not Equal) = Checks if both sides are different. Example: if Rank ~= "Admin" then
### 3. TELLER GRAMMAR SYMBOLS
: (Link / And) = Chains two actions on one line. Example: load(Coins) : add(25)
(*) (Mandatory) = Field must be filled; cannot be blank. Example: string1(*)
__ (Double Under) = Wraps a saved variable to display in text. Example: text.print("Level: "__Level__"!")
# (Comment) = Notes for human eyes; the computer ignores it. Example: # This adds gold reward
. (Dot Accessor) = Opens a tool inside a system. Example: system.console() or workspace.start
"" (Speech Marks) = Wraps plain words/text so it is not read as math. Example: "Hello player"
() (Pouch) = Holds target names or inputs. Example: load(Coins)
[] (Memory Slot) = Labels memory step checkpoints. Example: block[1]
{} (Room / Scope) = Boxes grouped code together. Example: store.var { ... }

# Sample working script -
workspace.start

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

workspace.end
Still in BETA. More features coming soon!
""")