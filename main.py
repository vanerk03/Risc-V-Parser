from Constants import *
from Commands import *
import Parser



class SymtabEntry:
    def __init__(self,
                 st_name,
                 st_value,
                 st_size,
                 st_info,
                 st_other,
                 st_shndx, 
                 symtab_entry_offset, 
                 parser
                 ) -> None:

        self.st_name = st_name
        self.st_value = st_value
        self.st_size = st_size
        self.st_info = st_info
        self.st_other = st_other
        self.st_shndx = st_shndx

        # fields we get from st_info
        self.bind = binds[st_info >> 4]
        self.type = types[st_info & 0xf]

        # fields we get from st_other
        self.vis = vises[st_other & 0x3]

        # fields we get from index
        if self.st_shndx in special.keys():
            self.index = special[self.st_shndx]
        else:
            self.index = self.st_shndx
        global symtab_name_offset
        self.name = parser.get_name_start(self.st_name + symtab_name_offset)

    def get_res(self, num: int):

        return "{Symbol} {Value} {Size} {Type} {Bind} {Vis} {Index} {Name}".format(
            Symbol="[%s]" % str(num).rjust(4),
            Value=hex(self.st_value).ljust(17),
            Size=str(self.st_size).rjust(5),
            Type=self.type.ljust(8),
            Bind=self.bind.ljust(8),
            Vis=self.vis.ljust(8),
            Index=str(self.index).rjust(6),
            Name=self.name
        )


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


def parse_command(start: int) -> str:
    first_byte = parser.get_bytes(start, 1)
    first_bits = (first_byte % 2) + (first_byte // 2) % 2

    if first_bits == 2:
        command = parser.get_command(parser.get_bytes(start, 4), 32)
        return output_command32(command), 4
        # it consists of 32 bits
    else:
        command = parser.get_command(parser.get_bytes(start, 4), 16)
        return output_command16(command), 2
        # it consists of 16 bits
if __name__ == "__main__":
    try:
        input_file = open(input("input filename: "), "rb")
        stream = input_file.read()
        out = open(input("output filename: "), "w")
    except FileNotFoundError:
        print("file is not found")
        exit()

    parser = Parser.Parser(stream)

    hd = parser.get_elf_header()
    number_of_sections = hd.e_shnum
    number_of_symtab_entries = None

    sections = []
    symtab_entries = []
    code = []

    left_label_dict = dict()
    right_label_dict = dict()

    symtab_name_offset = None
    symtab_offset = None
    code_offset = None
    loc_counter = 0


    for i in range(hd.e_shnum):
        sections.append(parser.get_section(hd.e_shoff + i * SECTION_SIZE))

    name_table_sections = sections[hd.e_shstrndx]

    for sect in sections:
        name = parser.get_name_section(sect, name_table_sections.sh_offset)
        if name == ".symtab":
            symtab_offset = sect.sh_offset
            number_of_symtab_entries = sect.sh_size // 16

        if name == ".strtab":
            symtab_name_offset = sect.sh_offset

        if name == ".text":
            code_offset = sect.sh_offset
            code_size = sect.sh_size
            code_address = sect.sh_addr


    if symtab_name_offset is None or symtab_offset is None \
            or code_offset is None or number_of_symtab_entries is None:

        print("Elf file is incorrect")
        exit()

    for i in range(number_of_symtab_entries):
        symtab_entries.append(parser.get_symtab_entry(
            symtab_offset + i * SYMTAB_ENTRY_SIZE, symtab_name_offset))
        if symtab_entries[i].name != "":
            left_label_dict[symtab_entries[i].st_value] = symtab_entries[i].name


    i = code_offset
    end = code_offset + code_size
    print(".text", file=out)
    cnt = 0

    offset_to_jump_command = 0
    has_offset = False

    parsed_code = []


    while i < end:
        left_lbl, right_lbl = False, False
        offset = None
        num = cnt + code_address
        res, bits = parse_command(i)

        if left_label_dict.__contains__(num):
            left_lbl = left_label_dict[num]

        if has_offset and left_label_dict.__contains__(num + offset_to_jump_command):
            right_label_dict[num] = left_label_dict[num + offset_to_jump_command]

        if has_offset:
            offset = offset_to_jump_command

        parsed_code.append(ParsedCommand(num, res, offset))

        i += bits
        cnt += bits


    for i in range(len(parsed_code)):

        code = parsed_code[i]
        command = code.command
        offset = code.offset
        num = code.num
        right_label = False
        left_label = False

        if not offset is None:
            new_num = num + offset

            if left_label_dict.__contains__(new_num):
                right_label_dict[num] = left_label_dict[new_num]

            elif not left_label_dict.__contains__(new_num) and right_label_dict.__contains__(num):
                left_label_dict[new_num] = right_label_dict[num]

            else:
                right_label_dict[num] = "LOC_{0}".format(
                    hex(loc_counter)[2:].rjust(5, '0'))
                loc_counter += 1
                left_label_dict[new_num] = right_label_dict[num]


    for i in range(len(parsed_code)):
        code = parsed_code[i]
        num = code.num
        res = code.command

        left_lbl, right_lbl = False, False

        if left_label_dict.__contains__(code.num):
            left_lbl = left_label_dict[num]

        if right_label_dict.__contains__(code.num):
            right_lbl = right_label_dict[num]

        if not left_lbl:
            left_lbl = ""
        else:
            left_lbl = left_lbl + ":"

        if not right_lbl:
            right_lbl = ""
        else:
            right_lbl = ", " + right_lbl

        print("{0} {1} {2}{3}".format(
            hex(num)[2:].rjust(8, '0'), left_lbl.rjust(11, " "),
            res, right_lbl
        ), file=out)


    print(file=out)
    print(".symtab", file=out)
    print("Symbol Value              Size Type     Bind     Vis       Index Name", file=out)
    for i in range(len(symtab_entries)):
        print(symtab_entries[i].get_res(i), file=out)
    input_file.close()
    out.close()
