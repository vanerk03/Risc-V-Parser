import sys
from constants import *

try:
    input_file = open(sys.argv[1], "rb")
    stream = input_file.read()
    out = open(sys.argv[2], "w")
except FileNotFoundError:
    print("file: {0} is not found".format(sys.argv[1]))
    exit()


class elf_header:
    def __init__(self, e_ident, e_type, e_machine,
                 e_version, e_entry, e_phoff, e_shoff, e_flags,
                 e_ehsize, e_phentsize, e_phnum,
                 e_shentsize, e_shnum, e_shstrndx):

        self.e_ident = e_ident
        self.e_type = e_type
        self.e_machine = e_machine
        self.e_version = e_version
        self.e_entry = e_entry
        self.e_phoff = e_phoff
        self.e_shoff = e_shoff
        self.e_flags = e_flags
        self.e_ehsize = e_ehsize
        self.e_phentsize = e_phentsize
        self.e_phnum = e_phnum
        self.e_shentsize = e_shentsize
        self.e_shnum = e_shnum
        self.e_shstrndx = e_shstrndx


class section:
    def __init__(self, sh_name, sh_type, sh_flags, sh_addr,
                 sh_offset, sh_size,
                 sh_link, sh_info, sh_addralign, sh_entsize):

        self.sh_name = sh_name
        self.sh_type = sh_type
        self.sh_flags = sh_flags
        self.sh_addr = sh_addr
        self.sh_offset = sh_offset
        self.sh_size = sh_size
        self.sh_link = sh_link
        self.sh_info = sh_info
        self.sh_addralign = sh_addralign
        self.sh_entsize = sh_entsize

    def __repr__(self) -> str:
        return "{0} {1} {2} {3} {4} {5} {6} {7} {8} {9}".format(self.sh_name, self.sh_type, self.sh_flags, self.sh_addr, self.sh_offset,
                                                                self.sh_size, self.sh_link, self.sh_info, self.sh_addralign, self.sh_entsize)


class symtab_entry:
    def __init__(self,
                 st_name,
                 st_value,
                 st_size,
                 st_info,
                 st_other,
                 st_shndx) -> None:

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
        self.name = get_name_start(self.st_name + symtab_name_offset)

    def get_res(self, num: int):

        ans = "{Symbol} {Value} {Size} {Type} {Bind} {Vis} {Index} {Name}".format(
            Symbol="[%s]" % str(num).rjust(4),
            Value=hex(self.st_value).ljust(17),
            Size=str(self.st_size).rjust(5),
            Type=self.type.ljust(8),
            Bind=self.bind.ljust(8),
            Vis=self.vis.ljust(8),
            Index=str(self.index).rjust(6),
            Name=self.name
        )

        return ans


class command32:
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


class command16:
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


class parsed_commands:
    def __init__(self, num, command, offset) -> None:
        self.num = num
        self.command = command
        self.offset = offset


def get_param(start, sz: list[int]):
    try:

        s = []
        for i in range(len(sz)):
            s.append(get_bytes(start, sz[i]))
            start += sz[i]
        return s
    except IndexError:
        print("Incorrect elf file")
        exit()


def get_elf_header() -> elf_header:
    sz = [16, 2, 2, 4, 4, 4, 4, 4, 2, 2, 2, 2, 2, 2]
    return elf_header(*get_param(0, sz))


def get_section(start) -> section:
    return section(*get_param(start, [4] * 10))


def get_symtab_entry(start) -> symtab_entry:
    sz = [4, 4, 4, 1, 1, 2]
    return symtab_entry(*get_param(start, sz))


def get_byte(i: int) -> str:
    return stream[i]


def get_bytes(start, length):
    res = 0
    for i in range(start + length - 1, start - 1, -1):
        res <<= 8
        res += get_byte(i)
    return res


def print_bytes(start, length, cc=16, show_nums: bool = False):
    for i in range(start, start + length):
        if cc == 16:
            ans = hex(stream[i])
        elif cc == 10:
            ans = stream[i]
        else:
            raise ValueError
        if not show_nums:
            print(ans, end=" ")
        else:
            print("{0}:".format(i - start + 1), ans, end=" ")
    print()


def get_name_section(sect: section, offset: int) -> str:
    i = sect.sh_name + offset
    return get_name_start(i)


def get_name_start(start: int) -> str:
    nm = ""
    i = start

    while True:
        if get_byte(i) == 0:
            return nm
        else:
            nm += chr(get_byte(i))
        i += 1


def get_command(number: int, command_length: int):

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
        return command16(*s)

    elif command_length == 32:

        bits.extend([0] * (32 - len(bits)))
        sz = [[0, 6], [7, 11], [12, 14], [15, 19], [20, 31]]

        for elem in sz:
            a, b = elem[0], elem[1]
            s.append("".join(map(str, reversed(bits[a:b + 1]))))
        s.append("".join(map(str, bits[0:32])))
        return command32(*s)

    else:
        raise ValueError("only 16-bit or 32-bit instructions are allowed")


def output_command16(cmd: command16):

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


def output_command32(cmd: command32):

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
    first_byte = get_bytes(start, 1)
    first_bits = (first_byte % 2) + (first_byte // 2) % 2

    if first_bits == 2:
        command = get_command(get_bytes(start, 4), 32)
        return output_command32(command), 4
        # it consists of 32 bits
    else:
        command = get_command(get_bytes(start, 4), 16)
        return output_command16(command), 2
        # it consists of 16 bits


hd = get_elf_header()
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
    sections.append(get_section(hd.e_shoff + i * SECTION_SIZE))

name_table_sections = sections[hd.e_shstrndx]

for sect in sections:
    name = get_name_section(sect, name_table_sections.sh_offset)
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
    symtab_entries.append(get_symtab_entry(
        symtab_offset + i * SYMTAB_ENTRY_SIZE))
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

    parsed_code.append(parsed_commands(num, res, offset))

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
