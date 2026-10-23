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

def substitute_vars(raw_msg, variables):
    for vn, vv in variables.items():
        raw_msg = raw_msg.replace(f"__{vn}__", str(vv))
        raw_msg = re.sub(rf'"{re.escape(vn)}"', str(vv), raw_msg)
        raw_msg = re.sub(rf'\b{re.escape(vn)}\b', str(vv), raw_msg)
    return raw_msg.replace('"', '').replace("'", "")

def execute_lines(lines, variables, functions, filename, start_line_idx=1, expected_block=1):
    condition_stack = []
    active_condition = True
    in_store_var = False
    in_output_block = False
    in_input_block = False
    in_function_def = False
    current_func = ""
    last_input_val = ""

    line_idx = start_line_idx - 1

    while line_idx < len(lines):
        raw_line = lines[line_idx]
        line_idx += 1
        stripped = raw_line.strip()

        if not stripped or stripped.startswith("#") or stripped in ["workspace.start", "workspace.end", "system.console()"]:
            continue

        if "(*)" in stripped:
            col = raw_line.find("(*)") + 1
            emit_diagnostic(filename, line_idx, raw_line, col, "SyntaxError", "unresolved parameter '(*)'")

        # Function Definition
        if stripped.startswith("store.function"):
            func_match = re.match(r'^store\.function\s+([A-Za-z0-9_]+)\((.*)\)$', stripped)
            if not func_match:
                emit_diagnostic(filename, line_idx, raw_line, 1, "SyntaxError", "malformed function", "syntax: store.function Name(args)")
            current_func = func_match.group(1)
            functions[current_func] = []
            in_function_def = True
            continue

        if in_function_def:
            if stripped == "end":
                in_function_def = False
                continue
            functions[current_func].append(raw_line)
            continue

        # Function Call
        call_match = re.match(r'^([A-Za-z0-9_]+)\((.*)\)$', stripped)
        if call_match and call_match.group(1) in functions and not stripped.startswith("input.console") and not stripped.startswith("output"):
            func_name = call_match.group(1)
            execute_lines(functions[func_name], variables, functions, filename, line_idx, expected_block)
            continue

        # Loops
        if stripped.startswith("do "):
            loop_match = re.match(r'^do\s+(text\.print\(".+"\))\s*\[(\d+),(\d+)\]$', stripped)
            if not loop_match:
                emit_diagnostic(filename, line_idx, raw_line, 1, "SyntaxError", "malformed loop", "syntax: do text.print(\"...\") [1,5]")
            
            cmd = loop_match.group(1)
            start_val, end_val = int(loop_match.group(2)), int(loop_match.group(3))
            
            print_match = re.match(r'^text\.print\((.+)\)$', cmd)
            if print_match:
                raw_msg = print_match.group(1).strip()
                final_msg = substitute_vars(raw_msg, variables)
                for _ in range(start_val, end_val + 1):
                    print(final_msg)
            continue

        # Input Console
        if stripped.startswith("input.console("):
            inp_match = re.match(r'^input\.console\("([^"]*)"\)(?:\s*\{)?$', stripped)
            if not inp_match:
                emit_diagnostic(filename, line_idx, raw_line, 1, "SyntaxError", "malformed input.console")
            print(inp_match.group(1), end=" ")
            try:
                last_input_val = input().strip()
                print(last_input_val)
            except EOFError:
                last_input_val = ""
            if stripped.endswith("{"):
                in_input_block = True
            continue

        if in_input_block:
            if stripped == "}":
                in_input_block = False
                continue
            num_match = re.match(r'^number\.val\s*=\s*\[([A-Za-z0-9_]+)\]$', stripped)
            if num_match:
                try:
                    variables[num_match.group(1)] = int(last_input_val)
                except ValueError:
                    emit_diagnostic(filename, line_idx, raw_line, 1, "TypeError", f"'{last_input_val}' is not a number")
                continue
            emit_diagnostic(filename, line_idx, raw_line, 1, "SyntaxError", "invalid input assignment")

        # Variables
        if stripped.startswith("store.var"):
            in_store_var = True
            continue

        if in_store_var:
            if stripped == "}":
                in_store_var = False
                continue
            var_match = re.match(r'^var\("([A-Za-z0-9_]+)"\)\s*=\s*(.+)$', stripped)
            if not var_match:
                emit_diagnostic(filename, line_idx, raw_line, 1, "SyntaxError", "invalid declaration")
            vname, raw_val = var_match.groups()
            raw_val = raw_val.strip()
            
            if raw_val in ["true", "false"]: variables[vname] = (raw_val == "true")
            elif raw_val.isdigit(): variables[vname] = int(raw_val)
            elif raw_val.startswith('"') and raw_val.endswith('"'): variables[vname] = raw_val[1:-1]
            else:
                math_match = re.match(r'^(\d+)\s*([\+\-\*\/])\s*(\d+)$', raw_val)
                if math_match:
                    n1, op, n2 = math_match.groups()
                    n1, n2 = int(n1), int(n2)
                    if op == "+": variables[vname] = n1 + n2
                    elif op == "-": variables[vname] = n1 - n2
                    elif op == "*": variables[vname] = n1 * n2
                    elif op == "/": variables[vname] = n1 // n2
            continue

        # Blocks
        if stripped.startswith("block["):
            block_match = re.fullmatch(r"block\[(\d+)\]", stripped)
            if not block_match:
                emit_diagnostic(filename, line_idx, raw_line, 1, "SyntaxError", "invalid block")
            step_num = int(block_match.group(1))
            if step_num != expected_block:
                emit_diagnostic(filename, line_idx, raw_line, 1, "SequenceError", f"expected block[{expected_block}], got {step_num}")
            expected_block += 1
            continue

        # Conditionals
        if stripped.startswith("if ") or stripped.startswith("or if "):
            cond_match = re.search(r'^(?:if|or if)\s+([A-Za-z0-9_]+)(?:\s*(>=|<=|>|<|==|~=)\s*([A-Za-z0-9_"]+))?\s+then$', stripped)
            if not cond_match:
                emit_diagnostic(filename, line_idx, raw_line, 1, "SyntaxError", "malformed condition")
            operand_a, op, operand_b = cond_match.groups()
            val_a = variables.get(operand_a, False)

            if op is None: outcome = bool(val_a)
            else:
                if operand_b == "true": comp = True
                elif operand_b == "false": comp = False
                elif operand_b.isdigit(): comp = int(operand_b)
                elif operand_b.startswith('"'): comp = operand_b[1:-1]
                else: comp = operand_b

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
            if condition_stack:
                condition_stack.pop()
                active_condition = condition_stack[-1] if condition_stack else True
            continue

        if not active_condition:
            continue

        # Pipelines
        if ":" in stripped:
            pipe_match = re.match(r'^load\(([A-Za-z0-9_]+)\)\s*:\s*(add|sub|mult|div)\(([0-9]+)\)$', stripped)
            if pipe_match:
                vname, act, val_str = pipe_match.groups()
                step_val = int(val_str)
                if act == "add": variables[vname] += step_val
                elif act == "sub": variables[vname] -= step_val
                elif act == "mult": variables[vname] *= step_val
                elif act == "div": variables[vname] //= step_val
            continue

        # Output
        if stripped.startswith("output(text.string)"):
            in_output_block = True
            continue

        if in_output_block:
            if stripped == "}":
                in_output_block = False
                continue
            if stripped.startswith("text.print"):
                print_match = re.match(r'^text\.print\((.+)\)$', stripped)
                if print_match:
                    print(substitute_vars(print_match.group(1).strip(), variables))
                continue

        emit_diagnostic(filename, line_idx, raw_line, 1, "SyntaxError", f"unexpected token '{stripped.split()[0]}'")

def run_teller(filename):
    try:
        with open(filename, "r", encoding="utf-8") as f:
            lines = f.readlines()
    except FileNotFoundError:
        print(f"FatalError: cannot open source file '{filename}'", file=sys.stderr)
        sys.exit(1)

    if not lines:
        sys.exit(1)

    execute_lines(lines, {}, {}, filename)

if __name__ == "__main__":
    if len(sys.argv) > 1:
        run_teller(sys.argv[1])
