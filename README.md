CUT	    Push number to stack

GLUE	Push string to stack

MEASURE	Get input from user

JOIN	Add top two numbers

MORTISE	Multiply top two numbers

TRIM	Subtract a number from top of stack

REPEAT	Repeat a char N times

REVERSE	Reverse a string

SAND	Pop & discard top of stack

INSPECT	Print top of stack

IFZERO	Pops condition, if 0 executes next line

END	Marks end of block (placeholder for future flow control)

!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!TERMINAL COMMANDS!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!

HOW TO RUN TRANSPILER

python3 transpiler.py file.txt

gcc output.c -o output   

Ex.
python3 transpiler.py reverse_repeat.txt

gcc output.c -o output   

HOW TO RUN "WORKBENCH"

python3 workbench.py file.txt

Ex. 
python3 workbench.py multiply_input.txt


HOW TO RUN COMPILED LANGUAGE

python3 transpiler.py file.txt

clang -S -emit-llvm output.c -o anyname.ll

clang anyname.ll -o anyname

NOTE 

LLVM transpilers only work on some of the programs, only full proof way was to convert to C first.

