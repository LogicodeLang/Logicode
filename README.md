# Logicode
Welcome to Logicode!

Logicode is a minimalistic language that is mainly based on Logisim.

Because of that, the only built-in commands are AND, OR and NOT, and you make the rest.

The three logic gates are represented like so:

`a&b`: AND of `a` and `b`.
`a?b`: OR of `a` and `b`.
`!a`: NOT of `a`.

You can make extra things from these commands, like circuits and variables.

To create a circuit, you have to do this:

`circ circuit_name(arg1, arg2...)->{what the function does}`

`circ` is the circuit "declaration", and everything after the `->` is interpreted as code.

To create a variable:

`var var_name=value`

`var` is the variable declaration.

There is also output as well:

`out out_value`

`out` is the output declaration, and you can include the built-in commands, as well as self-made circuits, into the output to be processed.

Example code:

    circ xor(a,b)->(!(a&b))&(a?b)
    var test=xor(1,1)
    out !(test)

    Output: 1

The circuit `xor` calculates the XOR of two bits, and `test` is declared as the XOR of 1 and 1 (which is 0). Then, the `out` outputs the NOT of `test`, which is `1`.
