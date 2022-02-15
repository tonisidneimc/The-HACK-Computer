__all__ = ["SymbolTable"]

class SymbolTable(object) :

    symbols = {
      "SCREEN" : 16384,
         "KBD" : 24576,
          "SP" :     0,
         "LCL" :     1,
         "ARG" :     2,
        "THIS" :     3,
        "THAT" :     4
    }

    def __init__(self) :
        self.symbols.update({f"R{value}" : value for value in range(16)})

    def add_entry(self, symbol : str, address : int) :
        self.symbols[symbol] = address

    def contains(self, symbol : str) -> bool:
        return symbol in self.symbols

    def get_address(self, symbol : str) -> int:
        return self.symbols[symbol]
        