import sys

if len(sys.argv) < 2:
    print("Usage: python transpiler.py <source_file>")
    sys.exit(1)

filename = sys.argv[1]

with open(filename, 'r') as file:
    lines = [line.strip() for line in file.readlines()]

cpp_code = [
    #makes the header of the C++ program
    '#include <iostream>',
    '#include <stack>',
    '#include <string>',
    '#include <algorithm>',
    '',
    'using namespace std;',
    '',
    'int main() {',
    '    stack<int> num_stack;',
    '    stack<string> str_stack;',
    ''
]

label_counter = 0
line_counter = 0
label_map = {}

# First pass: Identify IFZERO targets
for idx, line in enumerate(lines):
    if line.startswith("IFZERO"):
        label_map[idx + 1] = f"label_{label_counter}"
        label_counter += 1

# Second pass: Generate code
for idx, line in enumerate(lines):
    if idx in label_map:
        cpp_code.append(f'{label_map[idx]}: ;')

    if line == "" or line.startswith("#"):
        continue

    parts = line.split()
    command = parts[0]

    if command == "CUT":
        cpp_code.append(f'    num_stack.push({parts[1]});')

    elif command == "GLUE":
        content = line[line.index('"')+1:line.rindex('"')]
        cpp_code.append(f'    str_stack.push("{content}");')

    elif command == "MEASURE":
        cpp_code.append('    {')
        cpp_code.append('        if (cin.peek() >= \'0\' && cin.peek() <= \'9\') {')
        cpp_code.append('            int input; cin >> input; num_stack.push(input);')
        cpp_code.append('            cin.ignore();')
        cpp_code.append('        } else {')
        cpp_code.append('            string input; getline(cin, input); str_stack.push(input);')
        cpp_code.append('        }')
        cpp_code.append('    }')

    elif command == "JOIN":
        cpp_code.append('    {')
        cpp_code.append('        int b = num_stack.top(); num_stack.pop();')
        cpp_code.append('        int a = num_stack.top(); num_stack.pop();')
        cpp_code.append('        num_stack.push(a + b);')
        cpp_code.append('    }')

    elif command == "MORTISE":
        cpp_code.append('    {')
        cpp_code.append('        int b = num_stack.top(); num_stack.pop();')
        cpp_code.append('        int a = num_stack.top(); num_stack.pop();')
        cpp_code.append('        num_stack.push(a * b);')
        cpp_code.append('    }')

    elif command == "TRIM":
        cpp_code.append('    {')
        cpp_code.append(f'        int amount = {parts[1]};')
        cpp_code.append('        int top = num_stack.top(); num_stack.pop();')
        cpp_code.append('        num_stack.push(top - amount);')
        cpp_code.append('    }')

    elif command == "REPEAT":
        cpp_code.append('    {')
        cpp_code.append('        int count = num_stack.top(); num_stack.pop();')
        cpp_code.append('        string s = str_stack.top(); str_stack.pop();')
        cpp_code.append('        for (int i = 0; i < count; ++i) cout << s << endl;')
        cpp_code.append('    }')

    elif command == "REVERSE":
        cpp_code.append('    {')
        cpp_code.append('        string s = str_stack.top(); str_stack.pop();')
        cpp_code.append('        reverse(s.begin(), s.end());')
        cpp_code.append('        str_stack.push(s);')
        cpp_code.append('    }')

    elif command == "SAND":
        cpp_code.append('    if (!num_stack.empty()) num_stack.pop(); else str_stack.pop();')

    elif command == "INSPECT":
        cpp_code.append('    {')
        cpp_code.append('        if (!num_stack.empty()) { cout << num_stack.top() << endl; num_stack.pop(); }')
        cpp_code.append('        else { cout << str_stack.top() << endl; str_stack.pop(); }')
        cpp_code.append('    }')

    elif command == "IFZERO":
        label = label_map[idx + 1]
        cpp_code.append('    {')
        cpp_code.append('        int cond = num_stack.top(); num_stack.pop();')
        cpp_code.append(f'        if (cond != 0) goto {label};')
        cpp_code.append('    }')

    elif command == "END":
        cpp_code.append('    // END')

cpp_code.append('    return 0;')
cpp_code.append('}')

with open("output.cpp", "w") as out_file:
    out_file.write("\n".join(cpp_code))

print("Transpilation complete! Output written to output.cpp")
