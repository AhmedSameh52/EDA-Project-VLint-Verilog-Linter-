-------------
config file
-------------
to use the linter you have to write one or more of the following checks:
->Arithmetic Overflow
->Non Full/Parallel Case
->Multi-Driven Bus/Register
->Un-initialized Register
->Unreachable FSM State
**you have to use the exact syntax and if you are going to choose one or more checks please enter each check in a new line

for example:

Non Full/Parallel Case
Multi-Driven Bus/Register

--------------------
verilog code Notes 
--------------------
**please do not enter more than one space after each word, for correct parsing.
**you can add spaces normally at the beginning or end of each line in the code.

for example this is one of the correct ways to write the code: 

 module mmf (
   output wire [0:2] sum
       );
  wire [0:2] a ;
wire [0:2] b ; 
 assign a = 3'b111 ;
   assign b = 3'b001 ;
 assign sum = a * b + a - b  ;
endmodule
