from enum import IntEnum

class mnemonic (IntEnum):

    # dummy operation used in while compiling
    # these operation will not appear in output
    LABEL = -1
    ENTRY = -2

    DUMMY = 0 # we don't use 0 for detect compile error easily
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
    LOADD = 21
    STOREG = 24
    STOREL = 25
    STOREA = 26
    STORER = 27
    STOREP = 28
    STORED = 29

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
    RAND = 42

    INV = 48
    INC = 49
    DEC = 50
    ITOF = 56
    FTOI = 57

    ADDI = 64
    SUBI = 65
    MULI = 66
    DIVI = 67
    MODI = 68

    ADDF = 69
    SUBF = 70
    MULF = 71
    DIVF = 72
    MODF = 73

    AND = 74
    OR = 75
    XOR = 76
    LSHI = 77
    RSHI = 78

    EQI = 80
    NEQI = 81
    LTI = 82
    LTEI = 83
    GTI = 84
    GTEI = 85

    EQF = 88
    NEQF = 89
    LTF = 90
    LTEF = 91
    GTF = 92
    GTEF = 93

    SLEN = 96
    STOI = 97
    STOF = 98
    SSN = 99
    SST = 100
    SCMP = 103
    ITOS = 104
    FTOS = 105
    GSN = 106
    GST = 107
    SCPY = 109
    MCMP = 110
    MCPY = 111

    GSPO = 112
    GSRO = 113
    GSSC = 114
    SSPO = 116
    SSRO = 117
    SSSC = 118
    CSFT = 120
    FCFS = 121
    FCFT = 122
    SSPA = 123
    GSPA = 124
    DUPS = 125
    CHIC = 126
    DESS = 127

