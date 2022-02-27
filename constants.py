ELF_HEADER_SIZE = 52
SECTION_SIZE = 40
SYMTAB_ENTRY_SIZE = 16
unknown = ("unknown_command", False, None)

binds = {
    0: "LOCAL",
    1: "GLOBAL",
    2: "WEAK",
    10: "LOOS",
    12: "HIOS",
    13: "LOPROC",
    15: "HIPROC"}
types = {
    0: "NOTYPE",
    1: "OBJECT",
    2: "FUNC",
    3: "SECTION",
    4: "FILE",
    5: "COMMON",
    6: "TLS",
    10: "LOOS",
    12: "HIOS",
    13: "LOPROC",
    15: "HIPROC"}
vises = {
    0: "DEFAULT",
    1: "INTERNAL",
    2: "HIDDEN",
    3: "PROTECTED"}
special = {
    0:     "UNDEF",
    65280: "LOPROC",
    65311: "HIPROC",
    65312: "LOOS",
    65343: "HIOS",
    65521: "ABS",
    65522: "COMMON",
    65535: "HIRESERVE"}
reg = {
    0: "zero",
    1: "ra",
    2: "sp",
    3: "gp",
    4: "tp",
    5: "t0",
    6: "t1",
    7: "t2",
    8: "s0",
    9: "s1",
    10: "a0",
    11: "a1",
    12: "a2",
    13: "a3",
    14: "a4",
    15: "a5",
    16: "a6",
    17: "a7",
    18: "s2",
    19: "s3",
    20: "s4",
    21: "s5",
    22: "s6",
    23: "s7",
    24: "s8",
    25: "s9",
    26: "s10",
    27: "s11",
    28: "t3",
    29: "t4",
    30: "t5",
    31: "t6"}
reg_rvc = {
    0: "s0",
    1: "s1",
    2: "a0",
    3: "a1",
    4: "a2",
    5: "a3",
    6: "a4",
    7: "a5"}
reg_csr = {
    0x000 : "ustatus",
    0x004 : "uie",
    0x005 : "utvec",
    0x040 : "uscratch",
    0x041 : "uepc",
    0x042 : "ucause",
    0x043 : "ubadaddr",
    0x044 : "uip",
    0x001 : "fflags",
    0x002 : "frm",
    0x003 : "fcsr",
    0xC00 : "cycle",
    0xC01 : "time",
    0xC02 : "instret",
    0xC03 : "hpmcounter3",
    0xC04 : "hpmcounter4",
    0xC1F : "hpmcounter31",
    0xC80 : "cycleh",
    0xC81 : "timeh",
    0xC82 : "instreth",
    0xC83 : "hpmcounter3h",
    0xC84 : "hpmcounter4h",
    0xC9F : "hpmcounter31h",
    0x100 : "sstatus",
    0x102 : "sedeleg",
    0x103 : "sideleg",
    0x104 : "sie",
    0x105 : "stvec",
    0x140 : "sscratch",
    0x141 : "sepc",
    0x142 : "scause",
    0x143 : "sbadaddr",
    0x144 : "sip",
    0x180 : "sptbr",
    0x200 : "hstatus",
    0x202 : "hedeleg",
    0x203 : "hideleg",
    0x204 : "hie",
    0x205 : "htvec",
    0x240 : "hscratch",
    0x241 : "hepc",
    0x242 : "hcause",
    0x243 : "hbadaddr",
    0x244 : "hip",
    0xF11 : "mvendorid",
    0xF12 : "marchid",
    0xF13 : "mimpid",
    0xF14 : "mhartid",
    0x300 : "mstatus",
    0x301 : "misa",
    0x302 : "medeleg",
    0x303 : "mideleg",
    0x304 : "mie",
    0x305 : "mtvec",
    0x340 : "mscratch",
    0x341 : "mepc",
    0x342 : "mcause",
    0x343 : "mbadaddr",
    0x344 : "mip",
    0x380 : "mbase",
    0x381 : "mbound",
    0x382 : "mibase",
    0x383 : "mibound",
    0x384 : "mdbase",
    0x385 : "mdbound",
    0xB00 : "mcycle",
    0xB02 : "minstret",
    0xB03 : "mhpmcounter3",
    0xB04 : "mhpmcounter4",
    0xB1F : "mhpmcounter31",
    0xB80 : "mcycleh",
    0xB82 : "minstreth",
    0xB83 : "mhpmcounter3h",
    0xB84 : "mhpmcounter4h",
    0xB9F : "mhpmcounter31h",
    0x320 : "mucounteren",
    0x321 : "mscounteren",
    0x322 : "mhcounteren",
    0x323 : "mhpmevent3",
    0x324 : "mhpmevent4",
    0x33F : "mhpmevent31",
    0x7A0 : "tselect",
    0x7A1 : "tdata1",
    0x7A2 : "tdata2",
    0x7A3 : "tdata3",
    0x7B0 : "dcsr",
    0x7B1 : "dpc",
    0x7B2 : "dscratch"}