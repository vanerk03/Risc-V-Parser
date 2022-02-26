from Commands import *
from ElfElements import *

class Parser:
    def __init__(self, stream: str) -> None:
        self.stream = stream

    def get_param(self, start, sz: list[int]):
        try:
            s = []
            for i in range(len(sz)):
                s.append(self.get_bytes(start, sz[i]))
                start += sz[i]
            return s
        except IndexError:
            print("Incorrect elf file")
            exit()

    def get_elf_header(self) -> ElfHeader:
        sz = [16, 2, 2, 4, 4, 4, 4, 4, 2, 2, 2, 2, 2, 2]
        return ElfHeader(*self.get_param(0, sz))

    def get_section(self, start) -> Section:
        return Section(*self.get_param(start, [4] * 10))

    def get_symtab_entry(self, start, symtab_entry_offset) -> SymtabEntry:
        sz = [4, 4, 4, 1, 1, 2]
        return SymtabEntry(*self.get_param(start, sz), symtab_entry_offset, self)

    def get_byte(self, i: int) -> str:
        return self.stream[i]

    def get_bytes(self, start, length):
        res = 0
        for i in range(start + length - 1, start - 1, -1):
            res <<= 8
            res += self.get_byte(i)
        return res

    def print_bytes(self, start, length, cc=16, show_nums: bool = False):
        for i in range(start, start + length):
            if cc == 16:
                ans = hex(self.stream[i])
            elif cc == 10:
                ans = self.stream[i]
            else:
                raise ValueError
            if not show_nums:
                print(ans, end=" ")
            else:
                print("{0}:".format(i - start + 1), ans, end=" ")
        print()

    def get_name_section(self, sect: Section, offset: int) -> str:
        i = sect.sh_name + offset
        return self.get_name_start(i)

    def get_name_start(self, start: int) -> str:
        nm = ""
        i = start

        while True:
            if self.get_byte(i) == 0:
                return nm
            else:
                nm += chr(self.get_byte(i))
            i += 1

    def get_command(self, number: int, command_length: int):

        bits = []
        s = []
        while number:
            bits.append(number % 2)
            number //= 2

        if command_length == 16:
            bits.extend([0] * (16 - len(bits)))
            sz = [[0, 1], [2, 6], [7, 11], [12, 12], [13, 15]]

            for elem in sz:
                a, b = elem[0], elem[1]
                s.append("".join(map(str, reversed(bits[a:b + 1]))))
            s.append("".join(map(str, bits[0:16])))
            return Command16(*s)

        elif command_length == 32:

            bits.extend([0] * (32 - len(bits)))
            sz = [[0, 6], [7, 11], [12, 14], [15, 19], [20, 31]]

            for elem in sz:
                a, b = elem[0], elem[1]
                s.append("".join(map(str, reversed(bits[a:b + 1]))))
            s.append("".join(map(str, bits[0:32])))
            return Command32(*s)

        else:
            raise ValueError("only 16-bit or 32-bit instructions are allowed")
