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
ir_code.append("declare i8* @fgets(i8*, i32, %struct.FILE*)")
ir_code.append("%struct.FILE = type opaque")
ir_code.append("@stdin = external global %struct.FILE*")
ir_code.append("@print.int = constant [4 x i8] c\"%d\\0A\\00\"")
ir_code.append("@input.int = constant [3 x i8] c\"%d\\00\"")
ir_code.append("@input.buf = global [256 x i8] zeroinitializer")
ir_code.append("define i32 @main() {")
ir_code.append("entry:")

num_stack_index = 0
str_stack_index = 0
dyn_string_count = 0
globals_section = []
string_table = {}  # Deduplication table
stack_trace = []  # Track type and ID (e.g., 'num', 'Hello', 'dynstr1')

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
        ir_code.append(f"  %result{num_stack_index} = call i32 (i8*, ...) @scanf(i8* getelementptr ([3 x i8], [3 x i8]* @input.int, i32 0, i32 0), i32* %n{num_stack_index})")
        ir_code.append(f"  %scan_fail{num_stack_index} = icmp eq i32 %result{num_stack_index}, 0")
        ir_code.append(f"  br i1 %scan_fail{num_stack_index}, label %fallback{num_stack_index}, label %continue{num_stack_index}")
        ir_code.append(f"fallback{num_stack_index}:")
        ir_code.append(f"  %fptr{num_stack_index} = getelementptr [256 x i8], [256 x i8]* @input.buf, i32 0, i32 0")
        ir_code.append(f"  %stdinptr{num_stack_index} = load %struct.FILE*, %struct.FILE** @stdin")
        ir_code.append(f"  call i8* @fgets(i8* %fptr{num_stack_index}, i32 256, %struct.FILE* %stdinptr{num_stack_index})")
        ir_code.append(f"  %char{num_stack_index} = load i8, i8* %fptr{num_stack_index}")
        ir_code.append(f"  %ascii{num_stack_index} = sext i8 %char{num_stack_index} to i32")
        ir_code.append(f"  store i32 %ascii{num_stack_index}, i32* %n{num_stack_index}")
        ir_code.append(f"  br label %continue{num_stack_index}")
        ir_code.append(f"continue{num_stack_index}:")
        stack_trace.append('num')
        num_stack_index += 1

# (rest of your transpiler code stays the same)

ir_code.append("  ret i32 0")
ir_code.append("}")

# Add global declarations at the top
ir_code = ir_code[:7] + globals_section + ir_code[7:]

with open("output.ll", "w") as f:
    f.write("\n".join(ir_code))

print("Transpilation complete! Output written to output.ll")
