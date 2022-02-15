import re
import sys

from symbol_table import *
from token_type import *
from instr_type import *

table = SymbolTable() # initialize symbol table

def tokenize(code):
    keywords = {'JGT','JEQ','JGE','JLT','JNE','JLE', 'JMP'}

    token_specification = [
        ('SKIP',     r'(\/\/[^\n]+)|[ \f\t]+'),          # Skip over comments, spaces and tabs
        ('NUMBER',   r'\d+'),                            # Integer number
        ('AT', r'\@'),                                   # Labels or A-instruction
        ('ASSIGN',   r'\='),                             # Assignment operator
        ('SEP',      r'\;'),                             # Separator
        ('LPAREN', r'\('), ('RPAREN', r'\)'),            # Parenthesis
        ('IDENTIFIER', r'([A-Z_a-z][A-Z_a-z\d\.\$]*)'),  # Identifiers
        ('OP',       r'[+\-&\|!]'),                      # Arithmetic operators
        ('NEWLINE',  r'\n'),                             # Line endings
        ('EOF', r'$(?![\r\n])'),                         # End of File signaling
        ('MISMATCH', r'.'),                              # Any other character
    ]
    tok_regex = '|'.join('(?P<%s>%s)' % pair for pair in token_specification)
    line_num = 1
    line_start = 0
    
    for match in re.finditer(tok_regex, code):
        kind = match.lastgroup
        value = match.group()
        column = match.start() - line_start
        
        if kind == 'SKIP':
            continue
        elif kind == 'NEWLINE':
            line_start = match.end()
            line_num += 1

        elif kind == 'IDENTIFIER' and value in keywords:
            kind = value
        
        elif kind == 'MISMATCH':
            raise RuntimeError(f'{value!r} unexpected on line {line_num}')
            
        yield Token(kind, value, line_num, column)

def parse(generator : object) -> list:

    instructions = []
    instr_addr = 0

    while True :
        try :
            token = next(generator)

            if token.type == 'NEWLINE': continue

            elif token.type == 'EOF' : break

            elif token.type == 'LPAREN' :
                # label declaration instruction
                token = next(generator)

                if token.type != 'IDENTIFIER' :
                    raise RuntimeError(f'Expected identifier on line {token.lineno}')
                
                elif next(generator).type != 'RPAREN' : # consume ')'
                    raise RuntimeError(f'Expected \')\' on line {token.lineno}')   

                elif table.contains(token.value) :
                    raise RuntimeError(f'Label redeclaration on line {token.lineno}')
                else :
                    table.add_entry(token.value, instr_addr)

                continue # labels don't increments instruction address

            elif token.type == 'AT' :
                # A-instruction -> @value
                token_next = next(generator)
                
                if token_next.type == 'NUMBER' :
                    instructions.append(A_Instruction(token, int(token_next.value)))

                elif token_next.type == 'IDENTIFIER' :
                    if table.contains(token_next.value) :
                        instructions.append(A_Instruction(token, table.get_address(token_next.value)))
                    else :
                        instructions.append(A_Instruction(token, token_next.value, unresolved=True))
                else :
                    raise RuntimeError(f'Unexpected {token.value!r} on line {token.lineno}')

            else :
                # C-instruction -> (dest =)? comp (; jmp)?

                dest = '' # 000 no store
                comp = ''
                jmp  = '' # 000 no jmp

                c_instr = [token.value]

                for tk in generator :
                    if tk.type == 'NEWLINE' : break

                    c_instr.append(tk.value)

                c_instr = ''.join(c_instr).split(';') # split dest, comp from jmp

                if len(c_instr) > 2 :
                    raise RuntimeError(f'Malformed expression on line {token.lineno}')
                
                elif len(c_instr) == 2 : 
                    jmp = c_instr[1]

                c_instr = c_instr[0].split('=')

                if len(c_instr) > 2 :
                    raise RuntimeError(f'Malformed expression on line {token.lineno}')
                elif len(c_instr) == 2 : 
                    dest, comp = c_instr[0], c_instr[1]
                else :
                    comp = c_instr[0]

                instructions.append(C_Instruction(token, dest, comp, jmp))

            instr_addr += 1

        except StopIteration:
            break

        except RuntimeError as err:
            print(err, file=sys.stderr)
            sys.exit(64)

    return instructions

def assemble(source : str) :

    tokenizer = tokenize(source) # create a token generator object

    instructions = parse(generator=tokenizer)

    binary = []; var_addr = 16

    for instruction in instructions:

        if instruction.is_a_instr() and instruction.unresolved :
            # second pass
            if table.contains(instruction.value) :
                instruction.value = table.get_address(instruction.value)
            else :
                table.add_entry(instruction.value, var_addr)
                instruction.value = var_addr
                var_addr += 1

            instruction.unresolved = False
        try:
            code = instruction.gencode()
            print(instruction, code, sep='  ')

        except Exception as err:
            print(err, file=sys.stderr)
            sys.exit(64)
        else:
            binary.append(code)

    return binary

if __name__ == "__main__" :

    if len(sys.argv) != 2 :
        print("Expected file name", file=sys.stderr)
        sys.exit(1)

    filename = sys.argv[1]

    if not filename.endswith(".asm") :
        print("Not an assembly file", file=sys.stderr)
        sys.exit(1)

    try :
        with open(sys.argv[1], "r") as asm_program :
            binary_code = assemble(asm_program.read())

            with open(filename[:-4] + ".hack", "w") as hack_program :
                hack_program.write('\n'.join(binary_code))

    except IOError as error:
        print(error, file=sys.stderr)
