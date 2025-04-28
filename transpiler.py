import sys

if len(sys.argv) < 2:
    print("Usage: python transpiler.py <source_file>")
    sys.exit(1)

filename = sys.argv[1]

with open(filename, 'r') as file:
    lines = [line.strip() for line in file.readlines()]

c_code = [
    '#include <stdio.h>',
    '#include <stdlib.h>',
    '#include <string.h>',
    '',
    '#define STACK_SIZE 100',
    '#define STR_SIZE 256',
    '',
    'int num_stack[STACK_SIZE];',
    'int num_top = -1;',
    '',
    'char str_stack[STACK_SIZE][STR_SIZE];',
    'int str_top = -1;',
    '',
    'void push_num(int n) { num_stack[++num_top] = n; }',
    'int pop_num() { return num_stack[num_top--]; }',
    '',
    'void push_str(const char* s) { strcpy(str_stack[++str_top], s); }',
    'void pop_str(char* dest) { strcpy(dest, str_stack[str_top--]); }',
    '',
    'void reverse_str(char* s) {',
    '    int len = strlen(s);',
    '    for (int i = 0; i < len / 2; ++i) {',
    '        char tmp = s[i];',
    '        s[i] = s[len - i - 1];',
    '        s[len - i - 1] = tmp;',
    '    }',
    '}',
    '',
    'int main() {',
]

label_counter = 0
label_map = {}

# First pass: collect IFZERO labels
for idx, line in enumerate(lines):
    if line.startswith("IFZERO"):
        label_map[idx + 1] = f"label_{label_counter}"
        label_counter += 1

# Second pass: transpile
for idx, line in enumerate(lines):
    if idx in label_map:
        c_code.append(f'{label_map[idx]}: ;')

    if line == "" or line.startswith("#"):
        continue

    parts = line.split()
    command = parts[0]

    if command == "CUT":
        c_code.append(f'    push_num({parts[1]});')

    elif command == "GLUE":
        content = line[line.index('"')+1:line.rindex('"')]
        c_code.append(f'    push_str("{content}");')

    elif command == "MEASURE":
        c_code.append('    {')
        c_code.append('        char buffer[STR_SIZE];')
        c_code.append('        fgets(buffer, STR_SIZE, stdin);')
        c_code.append('        buffer[strcspn(buffer, "\\n")] = 0;')
        c_code.append('        char* endptr;')
        c_code.append('        int num = strtol(buffer, &endptr, 10);')
        c_code.append('        if (*endptr == \'\\0\') push_num(num);')
        c_code.append('        else push_str(buffer);')
        c_code.append('    }')

    elif command == "JOIN":
        c_code.append('    {')
        c_code.append('        int b = pop_num();')
        c_code.append('        int a = pop_num();')
        c_code.append('        push_num(a + b);')
        c_code.append('    }')

    elif command == "MORTISE":
        c_code.append('    {')
        c_code.append('        int b = pop_num();')
        c_code.append('        int a = pop_num();')
        c_code.append('        push_num(a * b);')
        c_code.append('    }')

    elif command == "TRIM":
        c_code.append('    {')
        c_code.append(f'        int amount = {parts[1]};')
        c_code.append('        int top = pop_num();')
        c_code.append('        push_num(top - amount);')
        c_code.append('    }')

    elif command == "REPEAT":
        c_code.append('    {')
        c_code.append('        int count = pop_num();')
        c_code.append('        char s[STR_SIZE]; pop_str(s);')
        c_code.append('        for (int i = 0; i < count; ++i) printf("%s\\n", s);')
        c_code.append('    }')

    elif command == "REVERSE":
        c_code.append('    {')
        c_code.append('        char s[STR_SIZE]; pop_str(s);')
        c_code.append('        reverse_str(s);')
        c_code.append('        push_str(s);')
        c_code.append('    }')

    elif command == "SAND":
        c_code.append('    if (num_top >= 0) pop_num(); else pop_str((char[STR_SIZE]){0});')

    elif command == "INSPECT":
        c_code.append('    {')
        c_code.append('        if (num_top >= 0) printf("%d\\n", pop_num());')
        c_code.append('        else { char s[STR_SIZE]; pop_str(s); printf("%s\\n", s); }')
        c_code.append('    }')

    elif command == "IFZERO":
        label = label_map[idx + 1]
        c_code.append('    {')
        c_code.append('        int cond = pop_num();')
        c_code.append(f'        if (cond != 0) goto {label};')
        c_code.append('    }')

    elif command == "END":
        c_code.append('    // END')

c_code.append('    return 0;')
c_code.append('}')

with open("output.c", "w") as out_file:
    out_file.write("\n".join(c_code))

print("Transpilation complete! Output written to output.c")
