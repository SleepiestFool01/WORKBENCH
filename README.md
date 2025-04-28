# WoodLang

A stack-based programming language for simple numeric and string operations.

## Reserved Words

| Keyword   | Description                                     |
|-----------|-------------------------------------------------|
| `CUT`     | Push number to stack                            |
| `GLUE`    | Push string to stack                            |
| `MEASURE` | Get input from user                             |
| `JOIN`    | Add top two numbers                             |
| `MORTISE` | Multiply top two numbers                        |
| `TRIM`    | Subtract a number from top of stack             |
| `REPEAT`  | Repeat a character N times                      |
| `REVERSE` | Reverse a string                                |
| `SAND`    | Pop and discard top of stack                    |
| `INSPECT` | Print top of stack                              |
| `IFZERO`  | Pops condition; if 0, executes next line        |
| `END`     | Marks end of block (placeholder for future flow control) |

---

## Terminal Commands

### How to Run the Transpiler (to C code)

```bash
python3 transpiler.py file.txt
gcc output.c -o output
```

**Example:**

```bash
python3 transpiler.py reverse_repeat.txt
gcc output.c -o output
```

---

### How to Run the "Workbench" Interpreter

```bash
python3 workbench.py file.txt
```

**Example:**

```bash
python3 workbench.py multiply_input.txt
```

---

### How to Run Compiled LLVM Code

```bash
python3 transpiler.py file.txt
clang -S -emit-llvm output.c -o anyname.ll
clang anyname.ll -o anyname
```

