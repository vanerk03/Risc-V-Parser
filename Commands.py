from Constants import *

class Command32:
    def __init__(self, opcode, rd, funct3, rs1, imm, full):
        self.opcode = opcode
        self.rd = int(rd, 2)
        self.funct3 = funct3
        self.rs1 = int(rs1, 2)
        self.imm = imm
        self.full = full

    def get_bits(self, start, end):
        return "".join(reversed(self.full[start:end + 1]))

    def __repr__(self) -> str:
        return reversed(self.full)


class Command16:
    def __init__(self, opcode, nzimm_1, rs, nzimm_2, funct3, full):
        self.opcode = opcode
        self.nzimm_1 = nzimm_1
        self.rs = rs
        self.nzimm_2 = nzimm_2
        self.funct3 = funct3
        self.full = full

    def get_bits(self, start, end):
        return "".join(reversed(self.full[start:end + 1]))

    def get_bits(self, start, end):
        return "".join(reversed(self.full[start:end + 1]))

    def __repr__(self) -> str:
        return reversed(self.full)


class ParsedCommand:
    def __init__(self, num, command, offset) -> None:
        self.num = num
        self.command = command
        self.offset = offset