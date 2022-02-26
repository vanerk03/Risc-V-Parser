# Elf Parser

## Elf-file parser that extracts `.text` and `.symtab` from the elf file.

### __Supports only__:
RV32I, RV32M and RVC commands which have equivalents in RV32I.
If Elf file contains a command which is not listed here, parser will output `unknown_command`.


#### Python 3.10.1


#### Sample of `.text` output
```
.text
00010074 register_fini: addi a5, zero, 0
00010078             beq a5, zero, LOC_00000
0001007c             lui a0, 65536
00010080             addi a0, a0, 1164
00010084             jal zero, atexit
00010088  LOC_00000: jalr zero, 0(ra)
0001008c     _start: auipc gp, 8192
00010090             addi gp, gp, -684
00010094             addi a0, gp, -972
00010098             addi a2, gp, -944
0001009c             sub a2, a2, a0
000100a0             addi a1, zero, 0
000100a4             jal ra, memset
000100a8             auipc a0, 0
...
```

#### Sample of `.symtab` output
```
.symtab
Symbol Value              Size Type     Bind     Vis       Index Name
[   0] 0x0                   0 NOTYPE   LOCAL    DEFAULT   UNDEF 
[   1] 0x10074               0 SECTION  LOCAL    DEFAULT       1 
[   2] 0x115cc               0 SECTION  LOCAL    DEFAULT       2 
[   3] 0x115d0               0 SECTION  LOCAL    DEFAULT       3 
[   4] 0x115d8               0 SECTION  LOCAL    DEFAULT       4 
[   5] 0x115e0               0 SECTION  LOCAL    DEFAULT       5 
[   6] 0x11a08               0 SECTION  LOCAL    DEFAULT       6 
[   7] 0x11a14               0 SECTION  LOCAL    DEFAULT       7 
[   8] 0x0                   0 SECTION  LOCAL    DEFAULT       8 
[   9] 0x0                   0 SECTION  LOCAL    DEFAULT       9 
[  10] 0x0                   0 FILE     LOCAL    DEFAULT     ABS 
[  11] 0x10074              24 FUNC     LOCAL    DEFAULT       1 register_fini
[  12] 0x0                   0 FILE     LOCAL    DEFAULT     ABS 
[  13] 0x115cc               0 OBJECT   LOCAL    DEFAULT       2 
[  14] 0x100d8               0 FUNC     LOCAL    DEFAULT       1 __do_global_dtors_aux
[  15] 0x11a14               1 OBJECT   LOCAL    DEFAULT       7 completed.1
[  16] 0x115d8               0 OBJECT   LOCAL    DEFAULT       4 __do_global_dtors
[  17] 0x10124               0 FUNC     LOCAL    DEFAULT       1 frame_dummy
...
```