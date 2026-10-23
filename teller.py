import sys
import re

def emit_diagnostic(filename, line_no, raw_line, col_start, error_type, message, note=None):
    """Formats professional Clang/Python-style error diagnostics with line previews and carets."""
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
    active_condition = True
    condition_stack = []
    workspace_begun = False
    workspace_ended = False

    for line_idx, raw_line in enumerate(lines, start=1):
        stripped = raw_line.strip()

        # Discard whitespace-only lines and full comment lines
        if not stripped or stripped.startswith("#"):
            continue

        # ---------------------------------------------------------
        # 1. SCOPE VALIDATION (workspace.start / workspace.end)
        # ---------------------------------------------------------
        if stripped == "workspace.start":
            if workspace_begun:
                emit_diagnostic(
                    filename, line_idx, raw_line, raw_line.find("workspace.start") + 1,
                    "ScopeError", "redefinition of active workspace session",
                    "note: 'workspace.start' was already initialized."
                )
            workspace_begun = True
            continue

        if not workspace_begun:
            first_token = stripped.split()[0]
            col = raw_line.find(first_token) + 1
            emit_diagnostic(
                filename, line_idx, raw_line, col,
                "SyntaxError", f"unexpected token '{first_token}' outside workspace scope",
                "note: source entry requires 'workspace.start' before declaring statements."
            )

        if workspace_ended:
            first_token = stripped.split()[0]
            col = raw_line.find(first_token) + 1
            emit_diagnostic(
                filename, line_idx, raw_line, col,
                "ScopeError", f"code declared after workspace termination",
                "note: all expressions must reside prior to 'workspace.end'."
            )

        if stripped == "workspace.end":
            workspace_ended = True
            continue

        # ---------------------------------------------------------
        # 2. VARIABLE STORAGE SCOPES (store.var { ... })
        # ---------------------------------------------------------
        if stripped.startswith("store.var"):
            if "{" not in stripped:
                col = raw_line.find("store.var") + len("store.var") + 1
                emit_diagnostic(
                    filename, line_idx, raw_line, col,
                    "SyntaxError", "expected '{' following block scope declaration",
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
                    "SyntaxError", "expected assignment operator '=' in variable declaration"
                )

            var_match = re.search(r'var\("([^"]+)"\)\s*=\s*(.+)', stripped)
            if not var_match:
                col = raw_line.find("var(") + 1
                emit_diagnostic(
                    filename, line_idx, raw_line, col,
                    "SyntaxError", "invalid variable definition syntax",
                    "syntax: var(\"identifier\") = <literal>"
                )

            ident, raw_val = var_match.groups()
            raw_val = raw_val.strip().strip('"').strip("'")
            if raw_val.isdigit():
                variables[ident] = int(raw_val)
            else:
                variables[ident] = raw_val
            continue

        # ---------------------------------------------------------
        # 3. CONTROL FLOW BRANCHING (if ... then / or if ... then / end)
        # ---------------------------------------------------------
        if stripped.startswith("if ") or stripped.startswith("or if "):
            if not stripped.endswith("then"):
                col = len(raw_line.rstrip()) + 1
                emit_diagnostic(
                    filename, line_idx, raw_line, col,
                    "SyntaxError", "expected keyword 'then' at end of condition clause"
                )

            cond_match = re.search(r'(?:if|or if)\s+([A-Za-z0-9_]+)\s*(>=|<=|>|<|==|~=)\s*([A-Za-z0-9_]+)\s*then', stripped)
            if not cond_match:
                col = raw_line.find("if") + 1
                emit_diagnostic(
                    filename, line_idx, raw_line, col,
                    "SyntaxError", "malformed conditional test expression",
                    "valid operators: >, <, >=, <=, ==, ~="
                )

            operand_a, op, operand_b = cond_match.groups()
            val_a = variables.get(operand_a, 0)
            target = int(operand_b) if operand_b.isdigit() else operand_b.strip('"').strip("'")

            if op == ">": outcome = (val_a > target)
            elif op == "<": outcome = (val_a < target)
            elif op == ">=": outcome = (val_a >= target)
            elif op == "<=": outcome = (val_a <= target)
            elif op == "==": outcome = (val_a == target)
            elif op == "~=": outcome = (val_a != target)

            condition_stack.append(outcome)
            active_condition = outcome
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

        # Skip execution branches when evaluating a false condition
        if not active_condition:
            continue

        # ---------------------------------------------------------
        # 4. PIPELINE OPERATOR (load(...) : action(...))
        # ---------------------------------------------------------
        if ":" in stripped:
            link_match = re.search(r'load\(([A-Za-z0-9_]+)\)\s*:\s*(add|sub|mult|div)\(([0-9]+)\)', stripped)
            if not link_match:
                col = raw_line.find(":") + 1
                emit_diagnostic(
                    filename, line_idx, raw_line, col,
                    "SyntaxError", "invalid pipeline link invocation",
                    "expected: load(<ident>) : <action>(<value>)"
                )

            target_var, action, step_str = link_match.groups()
            step = int(step_str)

            if target_var not in variables:
                col = raw_line.find(target_var) + 1
                emit_diagnostic(
                    filename, line_idx, raw_line, col,
                    "NameError", f"name '{target_var}' is not defined in active scope"
                )

            if action == "add": variables[target_var] += step
            elif action == "sub": variables[target_var] -= step
            elif action == "mult": variables[target_var] *= step
            elif action == "div": variables[target_var] //= step
            continue

        # ---------------------------------------------------------
        # 5. STREAM OUTPUT & SYSTEM DIRECTIVES
        # ---------------------------------------------------------
        if stripped in ["system.console()"] or stripped.startswith("output(") or stripped.startswith("block["):
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
            for v_name, v_val in variables.items():
                raw_str = raw_str.replace(f"__{v_name}__", str(v_val))

            clean = raw_str.replace('"', '').replace("'", "")
            print(clean)
            continue

        # ---------------------------------------------------------
        # 6. UNRECOGNIZED INSTRUCTION / UNEXPECTED TOKEN
        # ---------------------------------------------------------
        first_token = stripped.split()[0]
        col = raw_line.find(first_token) + 1
        emit_diagnostic(
            filename, line_idx, raw_line, col,
            "SyntaxError", f"unexpected token '{first_token}'",
            "note: command not recognized by the Teller grammar engine."
        )

    # File-level scope termination checks
    if workspace_begun and not workspace_ended:
        emit_diagnostic(
            filename, len(lines), lines[-1] if lines else "", 1,
            "ScopeError", "unexpected end-of-file: missing 'workspace.end'"
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
