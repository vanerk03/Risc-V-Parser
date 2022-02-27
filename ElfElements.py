from Constants import *
import Parser

class Section:
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
        return f"({self.sh_name}, {self.sh_type}, {self.sh_flags}, {self.sh_addr}, {self.sh_offset},\
                  {self.sh_size}, {self.sh_link}, {self.sh_info}, {self.sh_addralign}, {self.sh_entsize})"


class ElfHeader:
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


class SymtabEntry:
    def __init__(self,
                 st_name,
                 st_value,
                 st_size,
                 st_info,
                 st_other,
                 st_shndx,
                 symtab_name_offset,
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