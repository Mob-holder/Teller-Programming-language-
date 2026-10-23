import sys
import re

def run_teller(filename):
    with open(filename, "r") as f:
        lines = f.readlines()

    variables = {}
    active_condition = True  # Controls if/else execution

    for line in lines:
        line = line.strip()

        # 1. Ignore comments and empty lines
        if not line or line.startswith("#"):
            continue

        # 2. Check workspace start/end and memory blocks
        if line in ["workspace.start", "workspace.end", "end"] or line.startswith("block["):
            if line == "end":
                active_condition = True
            continue

        # 3. Store Variables: var("coins") = 100 or var("player") = "Ghost"
        var_match = re.search(r'var\("([^"]+)"\)\s*=\s*(.+)', line)
        if var_match:
            name, val = var_match.groups()
            val = val.strip().strip('"')
            # If it's a number, save as integer/float, otherwise text
            if val.isdigit():
                variables[name] = int(val)
            else:
                variables[name] = val
            continue

        # 4. Handle Conditions: if / or if
        if_match = re.search(r'(?:if|or if)\s+([A-Za-z0-9_]+)\s*(>=|<=|>|<|==|~=)\s*([A-Za-z0-9_]+)\s*then', line)
        if if_match:
            var_name, op, comp_val = if_match.groups()
            val = variables.get(var_name, 0)
            target = int(comp_val) if comp_val.isdigit() else comp_val.strip('"')

            if op == ">": active_condition = val > target
            elif op == "<": active_condition = val < target
            elif op == ">=": active_condition = val >= target
            elif op == "<=": active_condition = val <= target
            elif op == "==": active_condition = val == target
            elif op == "~=": active_condition = val != target
            continue

        # Skip execution if the current "if" check is False
        if not active_condition:
            continue

        # 5. Handle Link Operator: load(coins) : add(25)
        link_match = re.search(r'load\(([A-Za-z0-9_]+)\)\s*:\s*(add|sub|mult|div)\(([0-9]+)\)', line)
        if link_match:
            var_name, action, num = link_match.groups()
            num = int(num)
            if var_name in variables:
                if action == "add": variables[var_name] += num
                elif action == "sub": variables[var_name] -= num
                elif action == "mult": variables[var_name] *= num
                elif action == "div": variables[var_name] //= num
            continue

        # 6. Handle Printing: text.print("You have "__coins__" coins!")
        print_match = re.search(r'text\.print\((.+)\)', line)
        if print_match:
            raw_text = print_match.group(1).strip()
            
            # Replace Teller __variable__ interpolation
            for var_name, var_value in variables.items():
                pattern = f"__{var_name}__"
                raw_text = raw_text.replace(pattern, str(var_value))
            
            # Clean up outer quotes and extra string formatting
            clean_text = raw_text.replace('"', '').replace("'", "")
            print(clean_text)

if __name__ == "__main__":
    if len(sys.argv) > 1:
        run_teller(sys.argv[1])
    else:
        print("Usage: python teller.py <filename.tt>")
