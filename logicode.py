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

functions = []
function_names = []

replace_dict = {"&": " and ", "!": "not ", "?": " or "}

variables = {}

output = []

def parse_circ(string):
    out_code = string
    while any(x in out_code for x in function_names):
        temp = string
        for a in range(len(functions)):
            global func_co_ords
            if functions[a][0] in string:
                func_find_char = string.find(functions[a][0])
                out_args = string[func_find_char + len(functions[a][0]) + 1:].strip(")").split(",")
                func_co_ords = [func_find_char, string.find(")", func_find_char)]
                temp = functions[a][2]
                for b in range(len(functions[a][1])):
                    temp = temp.replace(functions[a][1][b], out_args[b])
        out_code = string[:func_co_ords[0]] + temp + string[func_co_ords[1] + 1:]
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

        # Looking for functions
        raw_code = parse_circ(raw_code)
        for d in replace_dict:
            raw_code = raw_code.replace(d, replace_dict[d])
        output.append(str(int(eval(raw_code))))

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
        function_name = split_code[0][0]
        args = split_code[0][1].split(",")
        functions.append([function_name, args, split_code[1]])
        function_names.append(function_name)

for f in range(len(code)):
    lgc_process(f)

print("".join(output))
