import sys

if len(sys.argv) < 2:
    print("Usage: python llvm_transpiler.py <source_file>")
    sys.exit(1)

filename = sys.argv[1]

with open(filename, 'r') as file:
    lines = [line.strip() for line in file.readlines()]

ir_code = []

# LLVM IR Header
ir_code.append("; ModuleID = 'woodlang'")
ir_code.append("declare i32 @printf(i8*, ...)")
ir_code.append("declare i32 @scanf(i8*, ...)")
ir_code.append("declare i32 @puts(i8*)")
ir_code.append("@print.int = constant [4 x i8] c\"%d\\0A\\00\"")
ir_code.append("@input.int = constant [3 x i8] c\"%d\\00\"")
ir_code.append("@input.buf = global [256 x i8] zeroinitializer")
ir_code.append("define i32 @main() {")
ir_code.append("entry:")

num_stack_index = 0
str_stack_index = 0
globals_section = []
string_table = {}  # Deduplication table
stack_trace = []  # Track type of stack entries ('num' or string content)

for idx, line in enumerate(lines):
    if line == "" or line.startswith("#"):
        continue

    parts = line.split()
    command = parts[0]

    if command == "CUT":
        ir_code.append(f"  %n{num_stack_index} = alloca i32")
        ir_code.append(f"  store i32 {parts[1]}, i32* %n{num_stack_index}")
        stack_trace.append('num')
        num_stack_index += 1

    elif command == "GLUE":
        content = line[line.index('"')+1:line.rindex('"')]
        if content not in string_table:
            string_table[content] = str_stack_index
            globals_section.append(f"@str{str_stack_index} = constant [{len(content)+1} x i8] c\"{content}\\00\"")
            str_stack_index += 1
        stack_trace.append(content)

    elif command == "MEASURE":
        ir_code.append(f"  %n{num_stack_index} = alloca i32")
        ir_code.append(f"  %input.ptr{num_stack_index} = getelementptr [256 x i8], [256 x i8]* @input.buf, i32 0, i32 0")
        ir_code.append(f"  call i32 (i8*, ...) @scanf(i8* getelementptr ([3 x i8], [3 x i8]* @input.int, i32 0, i32 0), i32* %n{num_stack_index})")
        stack_trace.append('num')
        num_stack_index += 1

    elif command == "JOIN":
        ir_code.append(f"  %a{num_stack_index} = load i32, i32* %n{num_stack_index - 2}")
        ir_code.append(f"  %b{num_stack_index} = load i32, i32* %n{num_stack_index - 1}")
        ir_code.append(f"  %sum{num_stack_index} = add i32 %a{num_stack_index}, %b{num_stack_index}")
        ir_code.append(f"  store i32 %sum{num_stack_index}, i32* %n{num_stack_index - 2}")
        num_stack_index -= 1
        stack_trace.pop()

    elif command == "MORTISE":
        ir_code.append(f"  %a{num_stack_index} = load i32, i32* %n{num_stack_index - 2}")
        ir_code.append(f"  %b{num_stack_index} = load i32, i32* %n{num_stack_index - 1}")
        ir_code.append(f"  %mul{num_stack_index} = mul i32 %a{num_stack_index}, %b{num_stack_index}")
        ir_code.append(f"  store i32 %mul{num_stack_index}, i32* %n{num_stack_index - 2}")
        num_stack_index -= 1
        stack_trace.pop()

    elif command == "TRIM":
        ir_code.append(f"  %top{num_stack_index} = load i32, i32* %n{num_stack_index - 1}")
        ir_code.append(f"  %sub{num_stack_index} = sub i32 %top{num_stack_index}, {parts[1]}")
        ir_code.append(f"  store i32 %sub{num_stack_index}, i32* %n{num_stack_index - 1}")

    elif command == "INSPECT":
        if not stack_trace:
            print(f"Error: Stack underflow at line {idx + 1}")
            sys.exit(1)
        top_item = stack_trace.pop()
        if top_item == 'num':
            ir_code.append(f"  %val{num_stack_index} = load i32, i32* %n{num_stack_index - 1}")
            ir_code.append(f"  call i32 (i8*, ...) @printf(i8* getelementptr ([4 x i8], [4 x i8]* @print.int, i32 0, i32 0), i32 %val{num_stack_index})")
            num_stack_index -= 1
        else:
            str_idx = string_table[top_item]
            length = len(top_item) + 1
            ir_code.append(f"  %str{str_idx} = getelementptr [{length} x i8], [{length} x i8]* @str{str_idx}, i32 0, i32 0")
            ir_code.append(f"  call i32 @puts(i8* %str{str_idx})")

    elif command == "SAND":
        if not stack_trace:
            print(f"Error: Stack underflow at line {idx + 1}")
            sys.exit(1)
        top_item = stack_trace.pop()
        if top_item == 'num':
            num_stack_index -= 1

    elif command == "REVERSE":
        ir_code.append(f"  ; REVERSE not implemented directly in LLVM IR, requires runtime logic")

    elif command == "REPEAT":
        ir_code.append(f"  ; REPEAT not implemented directly in LLVM IR, requires runtime loop")

    elif command == "IFZERO":
        ir_code.append(f"  %cond{num_stack_index} = load i32, i32* %n{num_stack_index - 1}")
        ir_code.append(f"  %iszero{num_stack_index} = icmp eq i32 %cond{num_stack_index}, 0")
        ir_code.append(f"  br i1 %iszero{num_stack_index}, label %ifzero_block{idx}, label %continue_block{idx}")
        ir_code.append(f"ifzero_block{idx}:")
        ir_code.append(f"  ; Execute next line")
        ir_code.append(f"  br label %continue_block{idx}")
        ir_code.append(f"continue_block{idx}:")
        num_stack_index -= 1
        stack_trace.pop()

    elif command == "END":
        ir_code.append(f"  ; END marker, no operation")

ir_code.append("  ret i32 0")
ir_code.append("}")

# Add global declarations at the top (for GLUE)
ir_code = ir_code[:7] + globals_section + ir_code[7:]

with open("output.ll", "w") as f:
    f.write("\n".join(ir_code))

print("Transpilation complete! Output written to output.ll")
