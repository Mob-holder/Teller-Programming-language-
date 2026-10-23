import sys
import re

def emit_diagnostic(filename, line_no, raw_line, col_start, error_type, message, note=None):
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
        print(f"FatalError: cannot open source file '{filename}'", file=sys.stderr)
        sys.exit(1)

    variables = {}
    condition_stack = []
    active_condition = True
    workspace_begun = False
    workspace_ended = False
    in_store_var = False
    in_output_block = False
    expected_block = 1

    for line_idx, raw_line in enumerate(lines, start=1):
        stripped = raw_line.strip()

        # Ignore comments and empty lines
        if not stripped or stripped.startswith("#"):
            continue

        # Check for mandatory field symbol (*)
        if "(*)" in stripped:
            col = raw_line.find("(*)") + 1
            emit_diagnostic(
                filename, line_idx, raw_line, col,
                "SyntaxError", "mandatory parameter '(*)' was left blank",
                "note: you must fill this field."
            )

        # -------------------------------------------------------------
        # 1. START AND END
        # -------------------------------------------------------------
        if stripped == "workspace.start":
            workspace_begun = True
            continue

        if not workspace_begun:
            emit_diagnostic(filename, line_idx, raw_line, 1, "ScopeError", "code outside workspace", "note: line 1 must be 'workspace.start'")

        if workspace_ended:
            emit_diagnostic(filename, line_idx, raw_line, 1, "ScopeError", "code after workspace ended", "note: nothing can go after 'workspace.end'")

        if stripped == "workspace.end":
            workspace_ended = True
            continue

        # -------------------------------------------------------------
        # 2. SAVE INFORMATION
        # -------------------------------------------------------------
        if stripped.startswith("store.var"):
            if stripped != "store.var {":
                col = raw_line.find("store.var") + 1
                emit_diagnostic(filename, line_idx, raw_line, col, "SyntaxError", "missing '{'", "syntax: store.var {")
            in_store_var = True
            continue

        if in_store_var:
            if stripped == "}":
                in_store_var = False
                continue

            var_match = re.match(r'^var\("([A-Za-z0-9_]+)"\)\s*=\s*(.+)$', stripped)
            if not var_match:
                emit_diagnostic(filename, line_idx, raw_line, 1, "SyntaxError", "invalid variable syntax", "syntax: var(\"name\") = value")
            
            vname, raw_val = var_match.groups()
            raw_val = raw_val.strip()

            if raw_val.isdigit():
                variables[vname] = int(raw_val)
            elif raw_val.startswith('"') and raw_val.endswith('"'):
                variables[vname] = raw_val[1:-1]
            elif raw_val.lower() in ["true", "false"]:
                variables[vname] = (raw_val.lower() == "true")
            else:
                # Math support (10 + 5)
                math_match = re.match(r'^(\d+)\s*([\+\-\*\/])\s*(\d+)$', raw_val)
                if math_match:
                    n1, op, n2 = math_match.groups()
                    n1, n2 = int(n1), int(n2)
                    if op == "+": variables[vname] = n1 + n2
                    elif op == "-": variables[vname] = n1 - n2
                    elif op == "*": variables[vname] = n1 * n2
                    elif op == "/": variables[vname] = n1 // n2
                else:
                    emit_diagnostic(filename, line_idx, raw_line, 1, "SyntaxError", f"invalid value '{raw_val}'")
            continue

        # -------------------------------------------------------------
        # 3. MEMORY BLOCK INDEXING
        # -------------------------------------------------------------
        if stripped.startswith("block["):
            block_match = re.fullmatch(r"block\[(\d+)\]", stripped)
            if not block_match:
                emit_diagnostic(filename, line_idx, raw_line, 1, "SyntaxError", "invalid block syntax")
            
            step_num = int(block_match.group(1))
            if step_num != expected_block:
                emit_diagnostic(filename, line_idx, raw_line, 1, "SequenceError", f"expected block[{expected_block}], got block[{step_num}]")
            expected_block += 1
            continue

        # -------------------------------------------------------------
        # 4. CHOICES
        # -------------------------------------------------------------
        if stripped.startswith("if ") or stripped.startswith("or if "):
            if not stripped.endswith(" then"):
                emit_diagnostic(filename, line_idx, raw_line, len(stripped)-3, "SyntaxError", "missing 'then'")

            cond_match = re.search(r'^(?:if|or if)\s+([A-Za-z0-9_]+)\s*(>=|<=|>|<|==|~=)\s*([A-Za-z0-9_"]+)\s+then$', stripped)
            if not cond_match:
                emit_diagnostic(filename, line_idx, raw_line, 1, "SyntaxError", "malformed condition")

            v_a, op, v_b = cond_match.groups()
            if v_a not in variables:
                emit_diagnostic(filename, line_idx, raw_line, 1, "NameError", f"'{v_a}' is not defined")

            val_a = variables[v_a]
            
            if v_b.isdigit(): comp = int(v_b)
            elif v_b.startswith('"') and v_b.endswith('"'): comp = v_b[1:-1]
            elif v_b.lower() in ["true", "false"]: comp = (v_b.lower() == "true")
            else: comp = v_b

            if op == ">": outcome = (val_a > comp)
            elif op == "<": outcome = (val_a < comp)
            elif op == ">=": outcome = (val_a >= comp)
            elif op == "<=": outcome = (val_a <= comp)
            elif op == "==": outcome = (val_a == comp)
            elif op == "~=": outcome = (val_a != comp)
            else: outcome = False

            condition_stack.append(outcome)
            active_condition = outcome
            continue

        if stripped == "end":
            if not condition_stack:
                emit_diagnostic(filename, line_idx, raw_line, 1, "SyntaxError", "'end' without 'if'")
            condition_stack.pop()
            active_condition = condition_stack[-1] if condition_stack else True
            continue

        if not active_condition:
            continue

        # -------------------------------------------------------------
        # 5. LINKING ACTIONS
        # -------------------------------------------------------------
        if ":" in stripped:
            pipe_match = re.match(r'^load\(([A-Za-z0-9_]+)\)\s*:\s*(add|sub|mult|div)\(([0-9]+)\)$', stripped)
            if not pipe_match:
                emit_diagnostic(filename, line_idx, raw_line, 1, "SyntaxError", "malformed link operator", "syntax: load(var) : add(num)")

            vname, act, val_str = pipe_match.groups()
            if vname not in variables:
                emit_diagnostic(filename, line_idx, raw_line, 1, "NameError", f"'{vname}' not defined")
            
            step_val = int(val_str)
            if act == "add": variables[vname] += step_val
            elif act == "sub": variables[vname] -= step_val
            elif act == "mult": variables[vname] *= step_val
            elif act == "div": variables[vname] //= step_val
            continue

        # -------------------------------------------------------------
        # 6. SCREEN OUTPUT
        # -------------------------------------------------------------
        if stripped == "system.console()":
            continue

        if stripped.startswith("output(text.string)"):
            if stripped != "output(text.string) {":
                emit_diagnostic(filename, line_idx, raw_line, 1, "SyntaxError", "missing '{'")
            in_output_block = True
            continue

        if in_output_block:
            if stripped == "}":
                in_output_block = False
                continue

            if stripped.startswith("text.print"):
                print_match = re.match(r'^text\.print\((.+)\)$', stripped)
                if not print_match:
                    emit_diagnostic(filename, line_idx, raw_line, 1, "SyntaxError", "malformed text.print")

                raw_msg = print_match.group(1).strip()

                # Supports both __var__ AND "var" string connections
                for vn, vv in variables.items():
                    raw_msg = raw_msg.replace(f"__{vn}__", str(vv))
                    raw_msg = re.sub(rf'"{re.escape(vn)}"', str(vv), raw_msg)
                    raw_msg = re.sub(rf'\b{re.escape(vn)}\b', str(vv), raw_msg)

                print(raw_msg.replace('"', '').replace("'", ""))
                continue

        emit_diagnostic(filename, line_idx, raw_line, 1, "SyntaxError", f"unexpected command '{stripped.split()[0]}'")

if __name__ == "__main__":
    if len(sys.argv) > 1:
        run_teller(sys.argv[1])
    else:
        print("Usage: python teller.py <filename.tt>")
