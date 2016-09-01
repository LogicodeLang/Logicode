import sys
from random import randint

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

replace_dict = {"&": " and ", "!": " not ", "?": " or ", "*": "randint(0,1)"}

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
                for b in range(len(out_args)):
                    out_args[b] = "(" + out_args[b] + ")"
                circ_co_ords = [circ_find_char, index]
                temp = circuits[a][2]
                for c in range(len(circuits[a][1])):
                    temp = temp.replace(circuits[a][1][c], out_args[c])
        out_code = out_code[:circ_co_ords[0]] + temp + out_code[circ_co_ords[1]:]
        for d in replace_dict:
            out_code = out_code.replace(d, replace_dict[d])
    return out_code


def lgc_process(index):
    # Output
    if code[index][:3] == "out":
        raw_code = code[index][4:]

        # Looking for variables
        while any(x in raw_code for x in variables):
            for d in variables:
                if d in raw_code:
                    var_co_ords = raw_code.find(d)
                    raw_code = raw_code[:var_co_ords] + str(variables[d]) + raw_code[var_co_ords + len(d):]

        # Looking for circuits
        raw_code = "(" + parse_circ(raw_code) + ")"
        output.append(str(int(eval(raw_code))))

    # Variables
    elif code[index][:3] == "var":
        var_info = code[index][4:].split("=")
        var_info[1] = parse_circ(var_info[1])
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
        
    elif code[index][:4] == "cond":
        cond_split_code = code[index].split("->")
        cond_split_code[0] = int(parse_circ(cond_split_code[0][5:]))
        conditions = cond_split_code[1].split("/")
        if cond_split_code[0] == 1:
            code[index] = conditions[0]
            lgc_process(index)
        else:
            code[index] = conditions[1]
            lgc_process(index)

for g in range(len(code)):
    lgc_process(g)

print("".join(output))
