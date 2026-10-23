import sys
import re

def emit_diagnostic(filename, line_no, raw_line, col_start, error_type, message, note=None):
    """Outputs Clang/Python-style diagnostics with line excerpts, column tracking, and carets."""
    col = max(1, col_start)
    caret_indent = " " * (col - 1)
    
    diagnostic = [
        f"\nFile \"{filename}\", line {line_no}:{col}",
        f"  {raw_line.rstrip()}",
        f"  {caret_indent}^",
        f"{error_type}: {message}"
    ]
    if note:
        diagnostic.append(f"  note: {note}")
    
    print("\n".join(diagnostic), file=sys.stderr)
    sys.exit(1)

def run_teller(filename):
    try:
        with open(filename, "r", encoding="utf-8") as f:
            lines = f.readlines()
    except FileNotFoundError:
        print(f"FatalError: cannot open source file '{filename}': No such file or directory", file=sys.stderr)
        sys.exit(1)

    variables = {}
    condition_stack = []
    active_condition = True
    workspace_begun = False
    workspace_ended = False
    expected_block = 1

    for line_idx, raw_line in enumerate(lines, start=1):
        stripped = raw_line.strip()

        # Skip blank lines and comments
        if not stripped or stripped.startswith("#"):
            continue

        # Check for unresolved mandatory placeholder symbol (*)
        if "(*)" in stripped:
            col = raw_line.find("(*)") + 1
            emit_diagnostic(
                filename, line_idx, raw_line, col,
                "SyntaxError", "mandatory parameter '(*)' was left unfilled",
                "note: replace '(*)' with a valid identifier, literal, or expression."
            )

        # -------------------------------------------------------------
        # 1. SCOPE VALIDATION (workspace.start & workspace.end)
        # -------------------------------------------------------------
        if stripped == "workspace.start":
            if workspace_begun:
                col = raw_line.find("workspace.start") + 1
                emit_diagnostic(
                    filename, line_idx, raw_line, col,
                    "ScopeError", "redefinition of active workspace session",
                    "note: 'workspace.start' is already declared and running."
                )
            workspace_begun = True
            continue

        if not workspace_begun:
            first_tok = stripped.split()[0]
            col = raw_line.find(first_tok) + 1
            emit_diagnostic(
                filename, line_idx, raw_line, col,
                "SyntaxError", f"unexpected token '{first_tok}' before workspace entry",
                "note: line 1 must begin with 'workspace.start' to turn the code ON."
            )

        if workspace_ended:
            first_tok = stripped.split()[0]
            col = raw_line.find(first_tok) + 1
            emit_diagnostic(
                filename, line_idx, raw_line, col,
                "ScopeError", f"code statement found after workspace termination",
                "note: no statements are permitted after 'workspace.end'."
            )

        if stripped == "workspace.end":
            workspace_ended = True
            continue

        # -------------------------------------------------------------
        # 2. MEMORY BLOCK CHECKPOINTS (block[1], block[2], ...)
        # -------------------------------------------------------------
        block_match = re.fullmatch(r"block\[(\d+)\]", stripped)
        if block_match:
            step_num = int(block_match.group(1))
            if step_num != expected_block:
                col = raw_line.find("block[") + 1
                emit_diagnostic(
                    filename, line_idx, raw_line, col,
                    "SequenceError", f"expected checkpoint 'block[{expected_block}]', but found 'block[{step_num}]'",
                    "note: memory slots must increment sequentially according to step count."
                )
            expected_block += 1
            continue

        # -------------------------------------------------------------
        # 3. VARIABLE STORAGE ROOM (store.var { ... })
        # -------------------------------------------------------------
        if stripped.startswith("store.var"):
            if "{" not in stripped:
                col = raw_line.find("store.var") + len("store.var") + 1
                emit_diagnostic(
                    filename, line_idx, raw_line, col,
                    "SyntaxError", "expected scope room '{' following 'store.var'",
                    "syntax: store.var { ... }"
                )
            continue

        if stripped == "}":
            continue

        if "var(" in stripped:
            if "=" not in stripped:
                col = raw_line.find("var(") + 1
                emit_diagnostic(
                    filename, line_idx, raw_line, col,
                    "SyntaxError", "expected assignment '=' in variable definition"
                )

            var_match = re.search(r'var\("([^"]+)"\)\s*=\s*(.+)', stripped)
            if not var_match:
                col = raw_line.find("var(") + 1
                emit_diagnostic(
                    filename, line_idx, raw_line, col,
                    "SyntaxError", "malformed variable declaration syntax",
                    "syntax: var(\"identifier\") = <value>"
                )

            vname, raw_expr = var_match.groups()
            raw_expr = raw_expr.strip()

            # Direct math evaluation in definition (e.g., 10 + 5, 10 - 5, 5 * 2, 10 / 2)
            math_calc = re.match(r"^(\d+)\s*([\+\-\*\/])\s*(\d+)$", raw_expr)
            if math_calc:
                n1, op, n2 = math_calc.groups()
                n1, n2 = int(n1), int(n2)
                if op == "+": val = n1 + n2
                elif op == "-": val = n1 - n2
                elif op == "*": val = n1 * n2
                elif op == "/": val = n1 // n2
                variables[vname] = val
            elif raw_expr.lower() == "true":
                variables[vname] = True
            elif raw_expr.lower() == "false":
                variables[vname] = False
            elif raw_expr.isdigit():
                variables[vname] = int(raw_expr)
            else:
                variables[vname] = raw_expr.strip('"').strip("'")
            continue

        # -------------------------------------------------------------
        # 4. CONDITIONAL BRANCHING (if ... then / or if ... then / end)
        # -------------------------------------------------------------
        if stripped.startswith("if ") or stripped.startswith("or if "):
            if not stripped.endswith("then"):
                col = len(raw_line.rstrip()) + 1
                emit_diagnostic(
                    filename, line_idx, raw_line, col,
                    "SyntaxError", "expected keyword 'then' at end of condition clause"
                )

            cond_match = re.search(r'(?:if|or if)\s+([A-Za-z0-9_]+)(?:\s*(>=|<=|>|<|==|~=)\s*([A-Za-z0-9_"]+))?\s+then', stripped)
            if not cond_match:
                col = raw_line.find("if") + 1
                emit_diagnostic(
                    filename, line_idx, raw_line, col,
                    "SyntaxError", "malformed conditional test expression",
                    "valid operators: >, <, >=, <=, ==, ~="
                )

            target_var, op, target_val = cond_match.groups()
            val_a = variables.get(target_var, None)

            if val_a is None:
                col = raw_line.find(target_var) + 1
                emit_diagnostic(
                    filename, line_idx, raw_line, col,
                    "NameError", f"name '{target_var}' is not defined in active scope"
                )

            # Bare boolean flag check (e.g., if is_alive then)
            if op is None and target_val is None:
                branch_result = bool(val_a)
            else:
                if target_val.lower() == "true": comp = True
                elif target_val.lower() == "false": comp = False
                elif target_val.isdigit(): comp = int(target_val)
                else: comp = target_val.strip('"').strip("'")

                if op == ">": branch_result = (val_a > comp)
                elif op == "<": branch_result = (val_a < comp)
                elif op == ">=": branch_result = (val_a >= comp)
                elif op == "<=": branch_result = (val_a <= comp)
                elif op == "==": branch_result = (val_a == comp)
                elif op == "~=": branch_result = (val_a != comp)
                else: branch_result = False

            condition_stack.append(branch_result)
            active_condition = branch_result
            continue

        if stripped == "end":
            if not condition_stack:
                col = raw_line.find("end") + 1
                emit_diagnostic(
                    filename, line_idx, raw_line, col,
                    "SyntaxError", "unmatched 'end' statement without corresponding 'if' block"
                )
            condition_stack.pop()
            active_condition = condition_stack[-1] if condition_stack else True
            continue

        if not active_condition:
            continue

        # -------------------------------------------------------------
        # 5. PIPELINE OPERATOR (load(...) : add/sub/mult/div(...))
        # -------------------------------------------------------------
        if ":" in stripped:
            pipe_match = re.search(r'load\(([A-Za-z0-9_]+)\)\s*:\s*(add|sub|mult|div)\(([0-9]+)\)', stripped)
            if not pipe_match:
                col = raw_line.find(":") + 1
                emit_diagnostic(
                    filename, line_idx, raw_line, col,
                    "SyntaxError", "malformed pipeline link invocation",
                    "expected: load(<var>) : <action>(<value>)"
                )

            vname, act, val_str = pipe_match.groups()
            step_val = int(val_str)

            if vname not in variables:
                col = raw_line.find(vname) + 1
                emit_diagnostic(
                    filename, line_idx, raw_line, col,
                    "NameError", f"name '{vname}' is not defined in active scope"
                )

            if act == "add": variables[vname] += step_val
            elif act == "sub": variables[vname] -= step_val
            elif act == "mult": variables[vname] *= step_val
            elif act == "div": variables[vname] //= step_val
            continue

        # -------------------------------------------------------------
        # 6. SYSTEM DIRECTIVES & SCREEN PRINTING
        # -------------------------------------------------------------
        if stripped in ["system.console()"] or stripped.startswith("output("):
            continue

        if "text.print" in stripped:
            print_match = re.search(r'text\.print\((.+)\)', stripped)
            if not print_match:
                col = raw_line.find("text.print") + len("text.print") + 1
                emit_diagnostic(
                    filename, line_idx, raw_line, col,
                    "SyntaxError", "expected balanced '(' ... ')' enclosing string expression"
                )

            raw_str = print_match.group(1).strip()

            # Substitute __var__ variables
            for v_name, v_val in variables.items():
                raw_str = raw_str.replace(f"__{v_name}__", str(v_val))

            # Substitute raw connected variables: "text"var"text" or "text" var "text"
            for v_name, v_val in variables.items():
                raw_str = re.sub(rf'"{re.escape(v_name)}"', str(v_val), raw_str)
                raw_str = re.sub(rf'\b{re.escape(v_name)}\b', str(v_val), raw_str)

            # Strip remaining presentation speech marks
            clean_output = raw_str.replace('"', '').replace("'", "")
            print(clean_output)
            continue

        # Catch-all unexpected token diagnostic
        first_token = stripped.split()[0]
        col = raw_line.find(first_token) + 1
        emit_diagnostic(
            filename, line_idx, raw_line, col,
            "SyntaxError", f"unexpected token '{first_token}'",
            "note: command not recognized by the Teller grammar engine."
        )

    # -------------------------------------------------------------
    # FILE TERMINATION SCOPE INTEGRITY
    # -------------------------------------------------------------
    if workspace_begun and not workspace_ended:
        emit_diagnostic(
            filename, len(lines), lines[-1] if lines else "", 1,
            "ScopeError", "unexpected end-of-file: missing 'workspace.end'",
            "note: every program must be turned OFF with 'workspace.end' at the very end."
        )

    if condition_stack:
        emit_diagnostic(
            filename, len(lines), lines[-1] if lines else "", 1,
            "SyntaxError", f"expected 'end' to close {len(condition_stack)} unclosed conditional block(s)"
        )

if __name__ == "__main__":
    if len(sys.argv) > 1:
        run_teller(sys.argv[1])
    else:
        print("Usage: python teller.py <source_file.tt>", file=sys.stderr)
        sys.exit(1)
