import sys

# File access and creation
code_name = raw_input("File: ")

try:
    logicode_file = open(code_name + ".lgc", "r")
except IOError:
    logicode_file = open(code_name + ".lgc", "w")
    sys.exit()


# Initialising variables
code = (logicode_file.read()).split("\n")

circuits = []
circuit_names = []

replace_dict = {"&": " and ", "!": " not ", "?": " or "}

variables = {}

output = []

def parse_circ(string):
    out_code = string
    while any(x in out_code for x in circuit_names):
        temp = out_code
        for a in range(len(circuits)):
            if circuits[a][0] in out_code:
                circ_find_char = out_code.find(circuits[a][0])

                # Bracket matching checker
                index = circ_find_char + len(circuits[a][0]) + 1
                brace_check = 1
                while brace_check != 0:
                    if out_code[index] == "(":
                        brace_check += 1
                    elif out_code[index] == ")":
                        brace_check -= 1
                    index += 1

                out_args = out_code[circ_find_char + len(circuits[a][0]) + 1:index - 1].split(",")
                circ_co_ords = [circ_find_char, index]
                temp = circuits[a][2]
                for b in range(len(circuits[a][1])):
                    temp = temp.replace(circuits[a][1][b], out_args[b])
        out_code = out_code[:circ_co_ords[0]] + temp + out_code[circ_co_ords[1]:]
    return out_code

def lgc_process(index):
    # Output
    if code[index][:3] == "out":
        raw_code = code[index][4:]

        # Looking for variables
        while any(x in raw_code for x in variables):
            for c in variables:
                if c in raw_code:
                    var_co_ords = raw_code.find(c)
                    raw_code = raw_code[:var_co_ords] + str(variables[c]) + raw_code[var_co_ords + len(c):]

        # Looking for circuits
        raw_code = parse_circ(raw_code)
        for d in replace_dict:
            raw_code = raw_code.replace(d, replace_dict[d])
        output.append(str(int(eval(raw_code))))

    # Variables
    elif code[index][:3] == "var":
        var_info = code[index][4:].split("=")
        var_info[1] = parse_circ(var_info[1])
        for e in replace_dict:
            var_info[1] = var_info[1].replace(e, replace_dict[e])
        variables[var_info[0]] = int(eval(var_info[1]))

    # Circuits
    elif code[index][:4] == "circ":
        split_code = code[index].split("->")
        split_code[0] = split_code[0][5:-1].split("(")
        split_code[1] = parse_circ(split_code[1])
        circuit_name = split_code[0][0]
        args = split_code[0][1].split(",")
        circuits.append([circuit_name, args, split_code[1]])
        circuit_names.append(circuit_name)

for f in range(len(code)):
    lgc_process(f)

print("".join(output))
