from email.parser import Parser
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


def output_command32(cmd: Command32):

    global offset_to_jump_command
    global has_offset

    rd = cmd.rd
    imm = int(cmd.imm, 2) - 2 * 2048 * int(cmd.get_bits(31, 31))
    rs1 = cmd.rs1
    has_offset = False

    try:
        match cmd.opcode:
            case "0110111":
                temp_imm = int(cmd.get_bits(12, 31), 2) * 4096
                return "lui {rd}, {imm}".format(rd=reg[rd], imm=temp_imm)

            case "0010111":
                temp_imm = int(cmd.get_bits(12, 30), 2) * 4096 - \
                    int(cmd.get_bits(31, 31)) * int(2 ** 31)
                return "auipc {rd}, {imm}".format(rd=reg[rd], imm=temp_imm)

            case "1101111":
                nm = ""
                temp_imm = int(cmd.get_bits(31, 31) + cmd.get_bits(12, 19) +
                               cmd.get_bits(20, 20) + cmd.get_bits(21, 30), 2) * 2 - (1 << 21) * int(cmd.get_bits(31, 31))
                has_offset = True
                offset_to_jump_command = temp_imm

                return "jal {rd}".format(rd=reg[rd])

            case "1100111":
                rs1 = cmd.rs1
                temp_imm = imm
                return "jalr {rd}, {imm}({rs1})".format(rs1=reg[rs1], rd=reg[rd], imm=temp_imm)

            case "1100011":
                nm = ""
                match cmd.funct3:
                    case "000": nm = "beq"
                    case "001": nm = "bne"
                    case "100": nm = "blt"
                    case "101": nm = "bge"
                    case "110": nm = "bltu"
                    case "111": nm = "bgeu"
                    case _: return "unknown_command"

                temp_imm = int(cmd.get_bits(31, 31) + cmd.get_bits(7, 7)
                               + cmd.get_bits(25, 30) + cmd.get_bits(8, 11), 2) * 2 - 4096 * 2 * int(cmd.get_bits(31, 31))

                has_offset = True
                offset_to_jump_command = temp_imm
                rs2 = int(cmd.get_bits(20, 24), 2)

                return "{nm} {rs1}, {rs2}".format(nm=nm, rs1=reg[rs1], rs2=reg[rs2])

            case "0000011":
                nm = ""
                match cmd.funct3:
                    case "000": nm = "lb"
                    case "001": nm = "lh"
                    case "010": nm = "lw"
                    case "100": nm = "lbu"
                    case "101": nm = "lhu"
                    case _: return "unknown_command"

                return "{name} {rd}, {imm}({rs1})".format(name=nm, rs1=reg[cmd.rs1], rd=reg[rd], imm=imm)
            case "0100011":
                nm = ""

                temp_imm_1 = -4096 * int(cmd.get_bits(31, 31)) \
                    + int(cmd.get_bits(25, 31) + cmd.get_bits(7, 11), 2)

                rs2 = int(cmd.get_bits(20, 24), 2)
                match cmd.funct3:
                    case "000": nm = "sb"
                    case "001": nm = "sh"
                    case "010": nm = "sw"
                return "{name} {rs2}, {imm1}({rs1})".format(
                    name=nm,
                    rs1=reg[rs1],
                    rs2=reg[rs2],
                    imm1=temp_imm_1)
            case "0010011":
                nm = ""
                match cmd.funct3:
                    case "000": nm = "addi"
                    case "010": nm = "slti"
                    case "011": nm = "sltiu"
                    case "100": nm = "xori"
                    case "110": nm = "ori"
                    case "111": nm = "andi"
                    case "001": nm = "slli"
                    case "101":
                        if cmd.get_bits(30, 30) == "0":
                            nm = "srli"
                            imm = int(cmd.get_bits(20, 25), 2)
                        else:
                            nm = "srai"
                            imm = int(cmd.get_bits(20, 25), 2)
                return "{nm} {rd}, {rs1}, {imm}".format(nm=nm, rs1=reg[rs1], rd=reg[rd], imm=imm)

            case "0110011":
                nm = ""
                rs2 = int(cmd.get_bits(20, 24), 2)
                if cmd.get_bits(25, 31) == "0000001":
                    match cmd.funct3:
                        case "000": nm = "mul"
                        case "001": nm = "mulh"
                        case "010": nm = "mulhsu"
                        case "011": nm = "mulhu"
                        case "100": nm = "div"
                        case "101": nm = "divu"
                        case "110": nm = "rem"
                        case "111": nm = "remu"
                else:
                    match cmd.funct3:
                        case "000":
                            if cmd.get_bits(30, 30) == "0":
                                nm = "add"
                            else:
                                nm = "sub"
                        case "001": nm = "sll"
                        case "010": nm = "slt"
                        case "011": nm = "sltu"
                        case "100": nm = "xor"
                        case "101":
                            if cmd.get_bits(30, 30) == "0":
                                nm = "srl"
                            else:
                                nm = "sra"
                        case "110": nm = "or"
                        case "111": nm = "and"
                return "{nm} {rd}, {rs1}, {rs2}".format(
                    nm=nm,
                    rs1=reg[rs1],
                    rs2=reg[rs2],
                    rd=reg[rd])
            case "1110011":
                nm = ""
                uimm = rs1
                csr = int(cmd.get_bits(20, 31), 2)
                match cmd.funct3:
                    case "000":
                        if cmd.get_bits(20, 20) == "0":
                            nm = "ecall"
                        else:
                            nm = "ebreak"
                        return "{nm}".format(nm=nm)
                    case "001":
                        return "csrrw {rd}, {csr}, {rs1}".format(rd=reg[rd], csr=reg_csr[csr], rs1=reg[uimm])
                    case "010":
                        return "csrrs {rd}, {csr}, {rs1}".format(rd=reg[rd], csr=reg_csr[csr], rs1=reg[uimm])
                    case "011":
                        return "csrrc {rd}, {csr}, {rs1}".format(rd=reg[rd], csr=reg_csr[csr], rs1=reg[uimm])
                    case "101":
                        return "csrrwi {rd}, {csr}, {uimm}".format(rd=reg[rd], csr=reg_csr[csr], uimm=uimm)
                    case "110":
                        return "csrrsi {rd}, {csr}, {uimm}".format(rd=reg[rd], csr=reg_csr[csr], uimm=uimm)
                    case "111":
                        return "csrrci {rd}, {csr}, {uimm}".format(rd=reg[rd], csr=reg_csr[csr], uimm=uimm)
                    case _:
                        return "unknown_command"

            case _:
                return "unknown_command"
    except KeyError as e:
        return "unknown_command"


def output_command16(cmd: Command16):

    global offset_to_jump_command, has_offset
    has_offset = False
    funct3 = cmd.funct3
    opcode = cmd.opcode
    nm = ""
    try:
        match opcode:
            case "00":
                rs2 = reg_rvc[int(cmd.get_bits(2, 4), 2)]
                rs1 = reg_rvc[int(cmd.get_bits(7, 9), 2)]
                uimm = int(cmd.get_bits(5, 5) + cmd.get_bits(10, 12) +
                           cmd.get_bits(6, 6), 2) * 4
                match funct3:
                    case "000":
                        imm = int(cmd.get_bits(7, 10) + cmd.get_bits(11, 12) +
                                  cmd.get_bits(5, 5) + cmd.get_bits(6, 6), 2) * 4
                        if imm == 0:
                            return "unknown_command"
                        nm = "c.addi4spn"
                        rd = reg_rvc[int(cmd.get_bits(2, 4), 2)]
                        return "{nm} {rd}, sp, {imm}".format(nm=nm, rd=rd, imm=imm)

                    case "010":
                        nm = "c.lw"

                    case "110":
                        nm = "c.sw"
                    case _:
                        return "unknown_command"

                return "{nm} {rs2}, {uimm}({rs1})".format(nm=nm, rs1=rs1, rs2=rs2, uimm=uimm)

            case "01":
                match funct3:
                    case "000":
                        if int(cmd.get_bits(7, 11), 2) == 0:

                            nm = "c.nop"
                            return nm
                        else:
                            nm = "c.addi"
                            rs1 = reg[int(cmd.get_bits(7, 11), 2)]
                            imm = int(cmd.get_bits(2, 6), 2) - \
                                int(cmd.get_bits(12, 12)) * 32
                            return "{nm} {rs1}, {imm}".format(nm=nm, rs1=rs1, imm=imm)
                    case "001":
                        nm = "c.jal"
                        has_offset = True
                        offset = int(cmd.get_bits(8, 8) + cmd.get_bits(10, 10) +
                                     cmd.get_bits(9, 9) + cmd.get_bits(6, 6) + cmd.get_bits(7, 7) +
                                     cmd.get_bits(2, 2) + cmd.get_bits(11, 11) + cmd.get_bits(3, 5), 2) * 2 - int(cmd.get_bits(12, 12)) * 2048
                        offset_to_jump_command = offset
                        return "{nm}".format(nm=nm, off=offset)

                    case "010":
                        nm = "c.li"
                        rd = reg[int(cmd.get_bits(7, 11), 2)]
                        imm = int(cmd.get_bits(2, 6), 2) - \
                            32 * int(cmd.get_bits(12, 12))
                        return "{nm} {rd}, {imm}".format(nm=nm, rd=rd, imm=imm)
                    case "011":
                        match int(cmd.get_bits(7, 11), 2):
                            case 2:
                                nm = "c.addi16sp"
                                nzimm = int(cmd.get_bits(3, 4) + cmd.get_bits(5, 5) + cmd.get_bits(
                                    2, 2) + cmd.get_bits(6, 6), 2) * 16 - 512 * int(cmd.get_bits(12, 12))
                                return "{nm} sp, {nzimm}".format(nm=nm, nzimm=nzimm)
                            case 0:
                                return "unknown_command"
                            case _:
                                nzimm = int(cmd.get_bits(12, 12) +
                                            cmd.get_bits(2, 6), 2) * 4096
                                rd = reg[int(cmd.get_bits(7, 11), 2)]
                                return "c.lui {rd}, {nzimm}".format(rd=rd, nzimm=nzimm)
                    case "100":
                        nzuimm = int(cmd.get_bits(12, 12) +
                                     cmd.get_bits(2, 6), 2)
                        rd = reg_rvc[int(cmd.get_bits(7, 9), 2)]
                        imm = int(cmd.get_bits(2, 6), 2) - \
                            int(cmd.get_bits(12, 12)) * 32

                        match cmd.get_bits(10, 11):
                            case "00":
                                return "c.srli {rd}, {nzuimm}".format(nzuimm=nzuimm, rd=rd)
                            case "01":
                                return "c.srai {rd}, {nzuimm}".format(nzuimm=nzuimm, rd=rd)
                            case "10":
                                return "c.andi {rd}, {imm}".format(imm=imm, rd=rd)
                            case "11":
                                match cmd.get_bits(5, 6):
                                    case "00": nm = "c.sub"
                                    case "01": nm = "c.xor"
                                    case "10": nm = "c.or"
                                    case "11": nm = "c.and"
                                rs2 = reg_rvc[int(cmd.get_bits(2, 4), 2)]
                                rs1 = reg_rvc[int(cmd.get_bits(7, 9), 2)]
                                # rs1 = rd
                                return "{nm} {rs1}, {rs2}".format(nm=nm, rs1=rs1, rs2=rs2)
                    case "101":
                        nm = "c.j"
                        has_offset = True
                        offset = int(cmd.get_bits(8, 8) + cmd.get_bits(10, 10) +
                                     cmd.get_bits(9, 9) + cmd.get_bits(6, 6) + cmd.get_bits(7, 7) +
                                     cmd.get_bits(2, 2) + cmd.get_bits(11, 11) + cmd.get_bits(3, 5), 2) * 2 - int(cmd.get_bits(12, 12)) * 2048

                        offset_to_jump_command = offset
                        return "{nm}".format(nm=nm, offset=offset)

                    case "110":
                        has_offset = True
                        offset = int(cmd.get_bits(12, 12) + cmd.get_bits(5, 6) +
                                     cmd.get_bits(2, 2) + cmd.get_bits(10, 11) + cmd.get_bits(3, 4), 2) * 2 - 2 * 256 * int(cmd.get_bits(12, 12))
                        offset_to_jump_command = offset
                        rs1 = reg_rvc[int(cmd.get_bits(7, 9), 2)]
                        return "c.beqz {rs1}".format(rs1=rs1, offset=offset)
                    case "111":

                        has_offset = True
                        offset = int(cmd.get_bits(12, 12) + cmd.get_bits(5, 6) +
                                     cmd.get_bits(2, 2) + cmd.get_bits(10, 11) + cmd.get_bits(3, 4), 2) * 2 - 2 * 256 * int(cmd.get_bits(12, 12))
                        offset_to_jump_command = offset
                        rs1 = reg_rvc[int(cmd.get_bits(7, 9), 2)]
                        return "c.bnez {rs1}".format(rs1=rs1, offset=offset)
                    case _:
                        return "unknown_command"
            case "10":
                match funct3:
                    case "000":
                        rs1 = reg[int(cmd.get_bits(7, 11), 2)]
                        nzuimm = int(cmd.get_bits(12, 12) +
                                     cmd.get_bits(2, 6), 2)
                        return "c.slli {rs1}, {nzuimm}".format(rs1=rs1, nzuimm=nzuimm)
                    case "010":
                        rd = reg[int(cmd.get_bits(7, 11), 2)]
                        uimm = int(cmd.get_bits(2, 3) + cmd.get_bits(12,
                                                                     12) + cmd.get_bits(4, 6), 2) * 4
                        return "c.lwsp {rd}, {uimm}(sp)".format(rd=rd, uimm=uimm)

                    case "100":
                        match int(cmd.get_bits(2, 6), 2):
                            case 0:
                                match int(cmd.get_bits(7, 11)):
                                    case 0:
                                        return "c.ebreak"
                                    case _:
                                        rs1 = reg[int(cmd.get_bits(7, 11), 2)]

                                        if cmd.get_bits(12, 12) == "0":
                                            return "c.jr {rs1}".format(rs1=rs1)
                                        else:
                                            return "c.jalr {rs1}".format(rs1=rs1)
                            case _:
                                rd = reg[int(cmd.get_bits(7, 11), 2)]
                                rs2 = reg[int(cmd.get_bits(2, 6), 2)]

                                if cmd.get_bits(12, 12) == "0":
                                    nm = "c.mv"

                                    return nm + " " + rd + ", " + rs2
                                else:
                                    nm = "c.add"
                                    return nm + " " + rd + ", " + rs2

                    case "110":
                        nm = "c.swsp"
                        uimm = int(cmd.get_bits(7, 8) +
                                   cmd.get_bits(9, 12), 2) * 4
                        rs2 = reg[int(cmd.get_bits(2, 6), 2)]
                        return "{nm} {rs2}, {uimm}(sp)".format(nm=nm, rs2=rs2, uimm=uimm)
                    case _:
                        "unknown_command"
            case _:
                return "unknown_command"
    except KeyError:
        return "unknown_command"


def parse_command(start: int, parser: Parser) -> str:
    first_byte = parser.get_bytes(start, 1)
    first_bits = (first_byte % 2) + (first_byte // 2) % 2

    if first_bits == 2:
        command = parser.get_command(parser.get_bytes(start, 4), 32)
        return output_command32(command), 4
        # it consists of 32 bits
    else:
        command = parser.get_command(parser.get_bytes(start, 4), 16)
        return output_command16(command), 2