from enum import IntEnum

class mnemonic (IntEnum):

    LABEL = -1
    ENTRY = -2

    DUMMY = 0
    PUSH = 1
    POP = 2
    JUMP = 3
    JIF0 = 4
    FRAME = 5
    POPR = 6
    CALL = 7
    RET = 8
    PULP = 9
    PUAP = 10
    DUP  = 11
    PRINT = 15

    LOADG = 16
    LOADL = 17
    LOADA = 18
    LOADR = 19
    LOADP = 20
    STOREG = 24
    STOREL = 25
    STOREA = 26
    STORER = 27
    STOREP = 28

    SIN = 32
    COS = 33
    TAN = 34
    ASIN = 35
    ACOS = 36
    ATAN = 37
    ATAN2 = 38
    ROOT = 39
    POW = 40
    LOG = 41

    UTOI = 48
    UTOF = 49
    ITOF = 50
    ITOU = 51
    FTOU = 52
    FTOI = 53

    ADDU = 64
    SUBU = 65
    MULU = 66
    DIVU = 67
    MODU = 68
    LTU = 69
    LTEU = 70
    GTU = 71
    GTEU = 72
    EQU = 73
    NEQU = 74

    ADDI = 80
    SUBI = 81
    MULI = 82
    DIVI = 83
    MODI = 84
    LTI = 85
    LTEI = 86
    GTI = 87
    GTEI = 88
    EQI = 89
    NEQI = 90

    ADDF = 96
    SUBF = 97
    MULF = 98
    DIVF = 99
    MODF = 100
    LTF = 101
    LTEF = 102
    GTF = 103
    GTEF = 104
    EQF = 105
    NEQF = 106

    REDDU = 128
    REDDI = 129
    REDDF = 130
    REDDS = 131

    WRIDU = 136
    WRIDI = 137
    WRIDF = 138
    WRIDS = 139

    GSPO = 144
    GSRO = 145
    GSSC = 146
    SSPO = 148
    SSRO = 149
    SSSC = 150
    CSFT = 152
    SSPA = 153
    DS   = 154

