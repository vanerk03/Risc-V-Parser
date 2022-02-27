from Commands import *
from MatchFunction import *


def main():
    try:
        input_file = open(input("input filename: "), "rb")
        stream = input_file.read()
        out = open(input("output filename: "), "w")
    except FileNotFoundError:
        print("file is not found")
        exit()

    parser = Parser(stream)

    hd = parser.get_elf_header()
    number_of_sections = hd.e_shnum
    number_of_symtab_entries = None

    sections, symtab_entries, code, parsed_code = [], [], [], []

    left_lbl_dict, right_lbl_dict = {}, {}

    symtab_name_offset, symtab_offset, code_offset = None, None, None

    loc_counter = 0

    for i in range(number_of_sections):
        sections.append(parser.get_section(hd.e_shoff + i * SECTION_SIZE))

    name_table_sections = sections[hd.e_shstrndx]

    for sect in sections:
        name = parser.get_name_section(sect, name_table_sections.sh_offset)
        if name == ".symtab":
            symtab_offset = sect.sh_offset
            number_of_symtab_entries = sect.sh_size // 16
        elif name == ".strtab":
            symtab_name_offset = sect.sh_offset
        elif name == ".text":
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
            left_lbl_dict[symtab_entries[i].st_value] = symtab_entries[i].name

    i = code_offset
    end = code_offset + code_size
    print(".text", file=out)
    cnt = 0

    offset_to_jump = 0
    has_offset = False

    while i < end:
        left_lbl, right_lbl = False, False
        offset = None
        num = cnt + code_address
        res, has_offset, offset_to_jump, bits = parse_command(
            i, parser)

        if left_lbl_dict.__contains__(num):
            left_lbl = left_lbl_dict[num]

        if has_offset and left_lbl_dict.__contains__(num + offset_to_jump):
            right_lbl_dict[num] = left_lbl_dict[num + offset_to_jump]
        if has_offset:
            offset = offset_to_jump

        parsed_code.append(ParsedCommand(num, res, offset))

        i += bits
        cnt += bits

    for code in parsed_code:
        offset = code.offset
        num = code.num
        left_lbl, right_lbl = False, False

        if not offset is None:
            new_num = num + offset

            if left_lbl_dict.__contains__(new_num):
                right_lbl_dict[num] = left_lbl_dict[new_num]
            elif not left_lbl_dict.__contains__(new_num) and right_lbl_dict.__contains__(num):
                left_lbl_dict[new_num] = right_lbl_dict[num]
            else:
                right_lbl_dict[num] = "LOC_{0}".format(
                    hex(loc_counter)[2:].rjust(5, '0'))
                loc_counter += 1
                left_lbl_dict[new_num] = right_lbl_dict[num]

    for code in parsed_code:
        num = code.num
        res = code.command

        left_lbl, right_lbl = False, False

        if left_lbl_dict.__contains__(code.num):
            left_lbl = left_lbl_dict[num]

        if right_lbl_dict.__contains__(code.num):
            right_lbl = right_lbl_dict[num]

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


if __name__ == "__main__":
    main()
