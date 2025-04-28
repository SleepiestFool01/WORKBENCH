# workbench.py

import sys

stack = []

# Check for program file argument
if len(sys.argv) < 2:
    print("Usage: python workbench.py <program_file>")
    sys.exit(1)

filename = sys.argv[1]

# Read the program file
try:
    with open(filename, 'r') as file:
        lines = file.readlines()
except FileNotFoundError:
    print(f"Error: File '{filename}' not found.")
    sys.exit(1)

def safe_pop():
    if not stack:
        print("Error: Stack underflow")
        sys.exit(1)
    return stack.pop()

# Interpreter loop
line_number = 0
while line_number < len(lines):
    line = lines[line_number].strip()

    if line == "" or line.startswith("#"):
        line_number += 1
        continue

    parts = line.split()
    command = parts[0]

    if command == "CUT":
        number = int(parts[1])
        stack.append(number)

    elif command == "GLUE":
        string_value = " ".join(parts[1:]).strip('"')
        stack.append(string_value)

    elif command == "MEASURE":
        user_input = input()
        try:
            user_input = int(user_input)
        except ValueError:
            pass
        stack.append(user_input)

    elif command == "JOIN":
        b = safe_pop()
        a = safe_pop()
        if isinstance(a, int) and isinstance(b, int):
            stack.append(a + b)
        else:
            print("Error: JOIN expects two numbers")
            sys.exit(1)

    elif command == "MORTISE":
        b = safe_pop()
        a = safe_pop()
        if isinstance(a, int) and isinstance(b, int):
            stack.append(a * b)
        else:
            print("Error: MORTISE expects two numbers")
            sys.exit(1)

    elif command == "TRIM":
        amount = int(parts[1])
        top = safe_pop()
        if isinstance(top, int):
            stack.append(top - amount)
        else:
            print("Error: TRIM expects a number on the stack")
            sys.exit(1)

    elif command == "REPEAT":
        count = safe_pop()
        char = safe_pop()
        if isinstance(count, int) and isinstance(char, str):
            # stack.append(char * count) this would repeat the string on the same line i like it better with new lines 
            repeated = "\n".join([char for _ in range(count)])  # Each repetition on a new line
            stack.append(repeated)
        else:
            print("Error: REPEAT expects a string and a number")
            sys.exit(1)

    elif command == "REVERSE":
        value = safe_pop()
        if isinstance(value, str):
            stack.append(value[::-1])
        else:
            print("Error: REVERSE expects a string")
            sys.exit(1)

    elif command == "SAND":
        safe_pop()

    elif command == "INSPECT":
        print(safe_pop())

    elif command == "IFZERO":
        cond = safe_pop()
        if cond != 0:
            line_number += 1  # Skip next line

    elif command == "END":
        pass

    else:
        print(f"Unknown command: {command}")
        sys.exit(1)

    line_number += 1

