
__all__ = ["A_Instruction", "C_Instruction"]

COMP_TABLE = {
      "0": "0101010",   
      "1": "0111111",  "-1": "0111010",
      "D": "0001100",   "A": "0110000",
     "!D": "0001101",  "!A": "0110001",
     "-D": "0001111",  "-M": "1110011",
    "D+1": "0011111", "A+1": "0110111",
    "D-1": "0001110", "A-1": "0110010",
    "D+A": "0000010", "D-A": "0010011", 
    "A-D": "0000111", "M-D": "1000111",
    "D&A": "0000000", "D&M": "1000000",
    "D|A": "0010101", "D|M": "1010101",
      "M": "1110000",  "!M": "1110001",
    "M+1": "1110111", "M-1": "1110010",
    "D+M": "1000010", "D-M": "1010011"
}

DEST_TABLE = {
       "": "000",
      "M": "001",
      "D": "010",
     "MD": "011",
      "A": "100",
     "AM": "101",
     "AD": "110",
    "AMD": "111"
}

JUMP_TABLE = {
       "": "000",
    "JGT": "001",
    "JEQ": "010",
    "JGE": "011",
    "JLT": "100",
    "JNE": "101",
    "JLE": "110",
    "JMP": "111"
}

class Instruction :
    def __init__(self) : pass

    def is_c_instr(self) -> bool:
        return isinstance(self, C_Instruction)

    def is_a_instr(self) -> bool:
        return isinstance(self, A_Instruction)

class A_Instruction(Instruction) :
    def __init__(self, token, value, unresolved=False) :
        self.token = token
        self.value = value
        self.unresolved = unresolved

    def gencode(self) -> str:
        if self.unresolved :
            raise RuntimeError(f'Unknown instruction on line {self.token.lineno}')

        return "0" + f"{self.value:015b}"[-15:]

    def __str__(self) :
        return "@" + str(self.value)

class C_Instruction(Instruction) :
    def __init__(self, token, dest, comp, jmp) :
        self.token = token
        self.dest = dest
        self.comp = comp
        self.jmp = jmp

    def gencode(self) -> str:
        if self.dest not in DEST_TABLE or  \
            self.comp not in COMP_TABLE or \
            self.jmp not in JUMP_TABLE :
            raise RuntimeError(f'Unknown instruction on line {self.token.lineno}')

        dest, comp, jmp = DEST_TABLE[self.dest], COMP_TABLE[self.comp], JUMP_TABLE[self.jmp]
        
        return "111" + comp + dest + jmp

    def __str__(self) :
        return (self.dest + '=' if self.dest else '') + self.comp + (';' + self.jmp if self.jmp else '')
