from Constants import *
from Commands import *
from Parser import Parser

def output_command16(cmd: Command16):
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
                            return unknown
                        nm = "c.addi4spn"
                        rd = reg_rvc[int(cmd.get_bits(2, 4), 2)]
                        return f"{nm} {rd}, sp, {imm}", False, None

                    case "010":
                        nm = "c.lw"

                    case "110":
                        nm = "c.sw"
                    case _:
                        return unknown

                return f"{nm} {rs2}, {uimm}({rs1})", False, None

            case "01":
                match funct3:
                    case "000":
                        if int(cmd.get_bits(7, 11), 2) == 0:

                            nm = "c.nop"
                            return nm, False, None
                        else:
                            nm = "c.addi"
                            rs1 = reg[int(cmd.get_bits(7, 11), 2)]
                            imm = int(cmd.get_bits(2, 6), 2) - \
                                int(cmd.get_bits(12, 12)) * 32
                            return f"{nm} {rs1}, {imm}", False, None
                    case "001":
                        nm = "c.jal"
                        offset = int(cmd.get_bits(8, 8) + cmd.get_bits(10, 10) +
                                     cmd.get_bits(9, 9) + cmd.get_bits(6, 6) + cmd.get_bits(7, 7) +
                                     cmd.get_bits(2, 2) + cmd.get_bits(11, 11) + cmd.get_bits(3, 5), 2) * 2 - int(cmd.get_bits(12, 12)) * 2048
                        return f"{nm}", True, offset

                    case "010":
                        nm = "c.li"
                        rd = reg[int(cmd.get_bits(7, 11), 2)]
                        imm = int(cmd.get_bits(2, 6), 2) - \
                            32 * int(cmd.get_bits(12, 12))
                        return f"{nm} {rd}, {imm}", False, None
                    case "011":
                        match int(cmd.get_bits(7, 11), 2):
                            case 2:
                                nm = "c.addi16sp"
                                nzimm = int(cmd.get_bits(3, 4) + cmd.get_bits(5, 5) + cmd.get_bits(
                                    2, 2) + cmd.get_bits(6, 6), 2) * 16 - 512 * int(cmd.get_bits(12, 12))
                                return f"{nm} sp, {nzimm}", False, None
                            case 0:
                                return unknown
                            case _:
                                nzimm = int(cmd.get_bits(12, 12) +
                                            cmd.get_bits(2, 6), 2) * 4096
                                rd = reg[int(cmd.get_bits(7, 11), 2)]
                                return f"c.lui {rd}, {nzimm}", False, None
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
                                return f"{nm} {rs1}, {rs2}", False, None
                    case "101":
                        nm = "c.j"
                        offset = int(cmd.get_bits(8, 8) + cmd.get_bits(10, 10) +
                                     cmd.get_bits(9, 9) + cmd.get_bits(6, 6) + cmd.get_bits(7, 7) +
                                     cmd.get_bits(2, 2) + cmd.get_bits(11, 11) + cmd.get_bits(3, 5), 2) * 2 - int(cmd.get_bits(12, 12)) * 2048

                        return f"{nm}", True, offset

                    case "110":
                        offset = int(cmd.get_bits(12, 12) + cmd.get_bits(5, 6) +
                                     cmd.get_bits(2, 2) + cmd.get_bits(10, 11) + cmd.get_bits(3, 4), 2) * 2 - 2 * 256 * int(cmd.get_bits(12, 12))
                        rs1 = reg_rvc[int(cmd.get_bits(7, 9), 2)]
                        return f"c.beqz {rs1}", True, offset
                    case "111":
                        offset = int(cmd.get_bits(12, 12) + cmd.get_bits(5, 6) +
                                     cmd.get_bits(2, 2) + cmd.get_bits(10, 11) + cmd.get_bits(3, 4), 2) * 2 - 2 * 256 * int(cmd.get_bits(12, 12))
                        rs1 = reg_rvc[int(cmd.get_bits(7, 9), 2)]
                        return f"c.bnez {rs1}", True, offset
                    case _:
                        return unknown
            case "10":
                match funct3:
                    case "000":
                        rs1 = reg[int(cmd.get_bits(7, 11), 2)]
                        nzuimm = int(cmd.get_bits(12, 12) +
                                     cmd.get_bits(2, 6), 2)
                        return f"c.slli {rs1}, {nzuimm}", False, None
                    case "010":
                        rd = reg[int(cmd.get_bits(7, 11), 2)]
                        uimm = int(cmd.get_bits(2, 3) + cmd.get_bits(12,
                                                                     12) + cmd.get_bits(4, 6), 2) * 4
                        return f"c.lwsp {rd}, {uimm}(sp)", False, None

                    case "100":
                        match int(cmd.get_bits(2, 6), 2):
                            case 0:
                                match int(cmd.get_bits(7, 11)):
                                    case 0:
                                        return "c.ebreak", False, None
                                    case _:
                                        rs1 = reg[int(cmd.get_bits(7, 11), 2)]

                                        if cmd.get_bits(12, 12) == "0":
                                            return f"c.jr {rs1}", False, None
                                        else:
                                            return f"c.jalr {rs1}", False, None
                            case _:
                                rd = reg[int(cmd.get_bits(7, 11), 2)]
                                rs2 = reg[int(cmd.get_bits(2, 6), 2)]

                                if cmd.get_bits(12, 12) == "0":
                                    nm = "c.mv"
                                else:
                                    nm = "c.add"
                                return f"{nm} {rd}, {rs2}", False, None
                                 
                    case "110":
                        nm = "c.swsp"
                        uimm = int(cmd.get_bits(7, 8) +
                                   cmd.get_bits(9, 12), 2) * 4
                        rs2 = reg[int(cmd.get_bits(2, 6), 2)]
                        return f"{nm} {rs2}, {uimm}(sp)", False, None
                    case _:
                        unknown
            case _:
                return unknown
    except KeyError:
        return unknown


def output_command32(cmd: Command32):

    rd = cmd.rd
    imm = int(cmd.imm, 2) - 2 * 2048 * int(cmd.get_bits(31, 31))
    rs1 = cmd.rs1

    try:
        match cmd.opcode:
            case "0110111":
                temp_imm = int(cmd.get_bits(12, 31), 2) * 4096
                return "lui {rd}, {imm}".format(rd=reg[rd], imm=temp_imm), False, None

            case "0010111":
                temp_imm = int(cmd.get_bits(12, 30), 2) * 4096 - \
                    int(cmd.get_bits(31, 31)) * int(2 ** 31)
                return "auipc {rd}, {imm}".format(rd=reg[rd], imm=temp_imm), False, None

            case "1101111":
                nm = ""
                temp_imm = int(cmd.get_bits(31, 31) + cmd.get_bits(12, 19) +
                               cmd.get_bits(20, 20) + cmd.get_bits(21, 30), 2) * 2 - (1 << 21) * int(cmd.get_bits(31, 31))
                return "jal {rd}".format(rd=reg[rd]), True, temp_imm

            case "1100111":
                rs1 = cmd.rs1
                temp_imm = imm
                return "jalr {rd}, {imm}({rs1})".format(rs1=reg[rs1], rd=reg[rd], imm=temp_imm), False, None

            case "1100011":
                nm = ""
                match cmd.funct3:
                    case "000": nm = "beq"
                    case "001": nm = "bne"
                    case "100": nm = "blt"
                    case "101": nm = "bge"
                    case "110": nm = "bltu"
                    case "111": nm = "bgeu"
                    case _: return unknown

                temp_imm = int(cmd.get_bits(31, 31) + cmd.get_bits(7, 7)
                               + cmd.get_bits(25, 30) + cmd.get_bits(8, 11), 2) * 2 - 4096 * 2 * int(cmd.get_bits(31, 31))

                rs2 = int(cmd.get_bits(20, 24), 2)

                return "{nm} {rs1}, {rs2}".format(nm=nm, rs1=reg[rs1], rs2=reg[rs2]), True, temp_imm

            case "0000011":
                nm = ""
                match cmd.funct3:
                    case "000": nm = "lb"
                    case "001": nm = "lh"
                    case "010": nm = "lw"
                    case "100": nm = "lbu"
                    case "101": nm = "lhu"
                    case _: return unknown

                return "{name} {rd}, {imm}({rs1})".format(name=nm, rs1=reg[cmd.rs1], rd=reg[rd], imm=imm), False, None
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
                    imm1=temp_imm_1), False, None
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
                return "{nm} {rd}, {rs1}, {imm}".format(nm=nm, rs1=reg[rs1], rd=reg[rd], imm=imm), False, None

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
                    rd=reg[rd]), False, None
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
                        return f"{nm}", False, None
                    case "001":
                        return "csrrw {rd}, {csr}, {rs1}".format(rd=reg[rd], csr=reg_csr[csr], rs1=reg[uimm]), False, None
                    case "010":
                        return "csrrs {rd}, {csr}, {rs1}".format(rd=reg[rd], csr=reg_csr[csr], rs1=reg[uimm]), False, None
                    case "011":
                        return "csrrc {rd}, {csr}, {rs1}".format(rd=reg[rd], csr=reg_csr[csr], rs1=reg[uimm]), False, None
                    case "101":
                        return "csrrwi {rd}, {csr}, {uimm}".format(rd=reg[rd], csr=reg_csr[csr], uimm=uimm), False, None
                    case "110":
                        return "csrrsi {rd}, {csr}, {uimm}".format(rd=reg[rd], csr=reg_csr[csr], uimm=uimm), False, None
                    case "111":
                        return "csrrci {rd}, {csr}, {uimm}".format(rd=reg[rd], csr=reg_csr[csr], uimm=uimm), False, None
                    case _:
                        return unknown

            case _:
                return unknown
    except KeyError as e:
        return unknown


def parse_command(start: int, parser: Parser) -> str:
    first_byte = parser.get_bytes(start, 1)
    first_bits = (first_byte % 2) + (first_byte // 2) % 2

    if first_bits == 2:
        command = parser.get_command(parser.get_bytes(start, 4), 32)
        return *output_command32(command), 4
    else:
        command = parser.get_command(parser.get_bytes(start, 4), 16)
        return *output_command16(command), 2
