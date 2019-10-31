common_asserted = [
    ("0.5 * DXM1 * (source[delay][idx + Block0StrideX * Block0CELLSIZE + 0]"
     + " - source[delay][idx - Block0StrideX * Block0CELLSIZE + 0])"),
    ("0.5 * DYM1 * (source[delay][idx + Block0StrideY * Block0CELLSIZE + 0]"
     + " - source[delay][idx - Block0StrideY * Block0CELLSIZE + 0])"),
    ("(DXM2 * (source[delay][idx + 1 * Block0StrideX * Block0CELLSIZE + 0]"
     + " - 2.0 * source[delay][idx + 0 * Block0StrideX * Block0CELLSIZE + 0]"
     + " + source[delay][idx-1 * Block0StrideX * Block0CELLSIZE + 0]))"),
    ("(DYM2 * (source[delay][idx + 1 * Block0StrideY * Block0CELLSIZE + 0]"
     + " - 2.0 * source[delay][idx + 0 * Block0StrideY * Block0CELLSIZE + 0]"
     + " + source[delay][idx-1 * Block0StrideY * Block0CELLSIZE + 0]))"),
]

borders_asserted = [
    "sin(x)",
    "sin(x)",
    ("0.5 * DXM1 * (source[delay][idx + Block0StrideX * Block0CELLSIZE + 0]"
     + " - source[delay][idx - Block0StrideX * Block0CELLSIZE + 0])"),
    ("0.5 * DXM1 * (source[delay][idx + Block0StrideX * Block0CELLSIZE + 0]"
     + " - source[delay][idx - Block0StrideX * Block0CELLSIZE + 0])"),
    ("0.5 * DYM1 * (source[delay][idx + Block0StrideY * Block0CELLSIZE + 0]"
     + " - source[delay][idx - Block0StrideY * Block0CELLSIZE + 0])"),
    ("0.5 * DYM1 * (source[delay][idx + Block0StrideY * Block0CELLSIZE + 0]"
     + " - source[delay][idx - Block0StrideY * Block0CELLSIZE + 0])"),
    "sin(x)",
    "sin(x)",
    ("(2.0 * DXM2 * (source[delay][idx + Block0StrideX * Block0CELLSIZE + 0]"
     + " - source[delay][idx + 0] - (sin(x)) * DX))"),
    ("(2.0 * DXM2 * (source[delay][idx - Block0StrideX * Block0CELLSIZE + 0]"
     + " - source[delay][idx + 0] + (sin(x)) * DX))"),
    ("(DXM2 * (source[delay][idx + 1 * Block0StrideX * Block0CELLSIZE + 0]"
     + " - 2.0 * source[delay][idx + 0 * Block0StrideX * Block0CELLSIZE + 0]"
     + " + source[delay][idx-1 * Block0StrideX * Block0CELLSIZE + 0]))"),
    ("(DXM2 * (source[delay][idx + 1 * Block0StrideX * Block0CELLSIZE + 0]"
     + " - 2.0 * source[delay][idx + 0 * Block0StrideX * Block0CELLSIZE + 0]"
     + " + source[delay][idx-1 * Block0StrideX * Block0CELLSIZE + 0]))"),
    ("(DYM2 * (source[delay][idx + 1 * Block0StrideY * Block0CELLSIZE + 0]"
     + " - 2.0 * source[delay][idx + 0 * Block0StrideY * Block0CELLSIZE + 0]"
     + " + source[delay][idx-1 * Block0StrideY * Block0CELLSIZE + 0]))"),
    ("(DYM2 * (source[delay][idx + 1 * Block0StrideY * Block0CELLSIZE + 0]"
     + " - 2.0 * source[delay][idx + 0 * Block0StrideY * Block0CELLSIZE + 0]"
     + " + source[delay][idx-1 * Block0StrideY * Block0CELLSIZE + 0]))"),
    ("(2.0 * DYM2 * (source[delay][idx + Block0StrideY * Block0CELLSIZE + 0]"
     + " - source[delay][idx + 0] - (sin(x)) * DY))"),
    ("(2.0 * DYM2 * (source[delay][idx - Block0StrideY * Block0CELLSIZE + 0]"
     + " - source[delay][idx + 0] + (sin(x)) * DY))")
]

ics_asserted = [
    ("0.5 * DXM1 * (source[delay][idx + Block0StrideX * Block0CELLSIZE + 0]"
     + " - ic[firstIndex][secondIndexSTR + 0])"),
    ("0.5 * DXM1 * (ic[firstIndex][secondIndexSTR + 0]"
     + " - source[delay][idx - Block0StrideX * Block0CELLSIZE + 0])"),
    ("0.5 * DXM1 * (source[delay][idx + Block0StrideX * Block0CELLSIZE + 0]"
     + " - source[delay][idx - Block0StrideX * Block0CELLSIZE + 0])"),
    ("0.5 * DXM1 * (source[delay][idx + Block0StrideX * Block0CELLSIZE + 0]"
     + " - source[delay][idx - Block0StrideX * Block0CELLSIZE + 0])"),
    ("0.5 * DYM1 * (source[delay][idx + Block0StrideY * Block0CELLSIZE + 0]"
     + " - source[delay][idx - Block0StrideY * Block0CELLSIZE + 0])"),
    ("0.5 * DYM1 * (source[delay][idx + Block0StrideY * Block0CELLSIZE + 0]"
     + " - source[delay][idx - Block0StrideY * Block0CELLSIZE + 0])"),
    ("0.5 * DYM1 * (source[delay][idx + Block0StrideY * Block0CELLSIZE + 0]"
     + " - ic[firstIndex][secondIndexSTR + 0])"),
    ("0.5 * DYM1 * (ic[firstIndex][secondIndexSTR + 0]"
     + " - source[delay][idx - Block0StrideY * Block0CELLSIZE + 0])"),
    ("(DXM2 * (source[delay][idx + Block0StrideX * Block0CELLSIZE + 0]"
     + " - 2.0 * source[delay][idx + 0]"
     + " + ic[firstIndex][secondIndexSTR + 0]))"),
    ("(DXM2 * (ic[firstIndex][secondIndexSTR + 0]"
     + " - 2.0 * source[delay][idx + 0]"
     + " + source[delay][idx - Block0StrideX * Block0CELLSIZE + 0]))"),
    ("(DXM2 * (source[delay][idx + 1 * Block0StrideX * Block0CELLSIZE + 0]"
     + " - 2.0 * source[delay][idx + 0 * Block0StrideX * Block0CELLSIZE + 0]"
     + " + source[delay][idx-1 * Block0StrideX * Block0CELLSIZE + 0]))"),
    ("(DXM2 * (source[delay][idx + 1 * Block0StrideX * Block0CELLSIZE + 0]"
     + " - 2.0 * source[delay][idx + 0 * Block0StrideX * Block0CELLSIZE + 0]"
     + " + source[delay][idx-1 * Block0StrideX * Block0CELLSIZE + 0]))"),
    ("(DYM2 * (source[delay][idx + 1 * Block0StrideY * Block0CELLSIZE + 0]"
     + " - 2.0 * source[delay][idx + 0 * Block0StrideY * Block0CELLSIZE + 0]"
     + " + source[delay][idx-1 * Block0StrideY * Block0CELLSIZE + 0]))"),
    ("(DYM2 * (source[delay][idx + 1 * Block0StrideY * Block0CELLSIZE + 0]"
     + " - 2.0 * source[delay][idx + 0 * Block0StrideY * Block0CELLSIZE + 0]"
     + " + source[delay][idx-1 * Block0StrideY * Block0CELLSIZE + 0]))"),
    ("(DYM2 * (source[delay][idx + Block0StrideY * Block0CELLSIZE + 0]"
     + " - 2.0 * source[delay][idx + 0]"
     + " + ic[firstIndex][secondIndexSTR + 0]))"),
    ("(DYM2 * (ic[firstIndex][secondIndexSTR + 0]"
     + " - 2.0 * source[delay][idx + 0]"
     + " + source[delay][idx - Block0StrideY * Block0CELLSIZE + 0]))"),
]

vertexs_asserted = [
    ("sin(x)"),
    ("sin(x)"),
    ("sin(x)"),
    ("sin(x)"),
    ("sin(x)"),
    ("sin(x)"),
    ("sin(x)"),
    ("sin(x)"),
    ("(2.0 * DXM2 * (source[delay][idx + Block0StrideX * Block0CELLSIZE + 0]"
     + " - source[delay][idx + 0] - (sin(x)) * DX))"),
    ("(2.0 * DXM2 * (source[delay][idx - Block0StrideX * Block0CELLSIZE + 0]"
     + " - source[delay][idx + 0] + (sin(x)) * DX))"),
    ("(2.0 * DXM2 * (source[delay][idx - Block0StrideX * Block0CELLSIZE + 0]"
     + " - source[delay][idx + 0] + (sin(x)) * DX))"),
    ("(2.0 * DXM2 * (source[delay][idx + Block0StrideX * Block0CELLSIZE + 0]"
     + " - source[delay][idx + 0] - (sin(x)) * DX))"),
    ("(2.0 * DYM2 * (source[delay][idx + Block0StrideY * Block0CELLSIZE + 0]"
     + " - source[delay][idx + 0] - (sin(x)) * DY))"),
    ("(2.0 * DYM2 * (source[delay][idx + Block0StrideY * Block0CELLSIZE + 0]"
     + " - source[delay][idx + 0] - (sin(x)) * DY))"),
    ("(2.0 * DYM2 * (source[delay][idx - Block0StrideY * Block0CELLSIZE + 0]"
     + " - source[delay][idx + 0] + (sin(x)) * DY))"),
    ("(2.0 * DYM2 * (source[delay][idx - Block0StrideY * Block0CELLSIZE + 0]"
     + " - source[delay][idx + 0] + (sin(x)) * DY))"),
]
