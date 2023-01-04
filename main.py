import re
import itertools
import operator
errors = []
multiDrivenArrayCheck = []
multiDrivenArrayCheckAssign = []
checkArithmeticDictSize = {}
checkArithmeticDict = {}

ops = {
    '+' : operator.add,
    '-' : operator.sub,
    '*' : operator.mul
}

def toBinary(a):
  size = a.__len__()
  count = 0
  for i,num in enumerate(a):
    count += int(a[i]) * (2 ** (size-i-1))
  return count

def ArithmeticOverflowCheck(verilog_lines, module_lines):

    for i, line in enumerate(module_lines):
      if module_lines[i].split(" ")[1] == "output" or module_lines[i].split(" ")[1] == "input":
        checkArithmeticDictSize.update({module_lines[i].split(" ")[4]: int(module_lines[i].split(" ")[3].split(":")[1].split("]")[0]) + 1})
    for i, line in enumerate(verilog_lines):
      if verilog_lines[i].split(" ")[1] == "wire" or verilog_lines[i].split(" ")[1] == "reg":
        checkArithmeticDictSize.update({verilog_lines[i].split(" ")[3]: int(verilog_lines[i].split(" ")[2].split(":")[1].split("]")[0]) + 1})

    for i, line in enumerate(verilog_lines):
      if verilog_lines[i].split(" ").__len__() >= 5:
        if verilog_lines[i].split(" ")[1] == "assign" and verilog_lines[i].split(" ")[4][0] >= "0" and verilog_lines[i].split(" ")[4][0] <= "9":
          sizeOfBits = verilog_lines[i].split(" ")[4].__len__() - 3
          tempString = verilog_lines[i].split(" ")[4].replace(str(sizeOfBits), '')
          checkArithmeticDict.update({verilog_lines[i].split(" ")[2]: toBinary(tempString.replace("\'b", '')) })

    for i, line in enumerate(verilog_lines):
      if verilog_lines[i].split(" ")[1] == "assign" and not(verilog_lines[i].split(" ")[4][0] >= "0" and verilog_lines[i].split(" ")[4][0] <= "9"):
        value = checkArithmeticDictSize[verilog_lines[i].split(" ")[2]]
        tempString = verilog_lines[i].split(" ")
        tempString.pop(1)
        answer = 0
        for i,temp in enumerate(tempString):
          if tempString[i] == '*':
            answer = (ops['*'](checkArithmeticDict[tempString[i-1]],checkArithmeticDict[tempString[i+1]]))
          elif tempString[i] == '+' and i == 4:
            answer = ops['+'](checkArithmeticDict[tempString[i-1]],checkArithmeticDict[tempString[i+1]])
          elif tempString[i] == '+':
            answer = ops['+'](answer, checkArithmeticDict[tempString[i + 1]])
          elif tempString[i] == '-' and i == 4:
            answer = ops['-'](checkArithmeticDict[tempString[i - 1]], checkArithmeticDict[tempString[i + 1]])
          elif tempString[i] == '-':
            answer = ops['-'](answer, checkArithmeticDict[tempString[i + 1]])

        if  answer >= (2**checkArithmeticDictSize[tempString[1]]):
          errors.append(f'Line {tempString[0]}: Arithmetic Overflow, Variable: ' + str(tempString[1]))

def checkNotFullandNotParallel(lines):
  states = []
  sizeOfBits = 0
  isThereDefault = False
  for i, line in enumerate(lines):
    if lines[i].split(" ").__len__() >= 3:
      if lines[i].split(" ")[2] == ":" and lines[i].split(" ")[1] != "default":
        sizeOfBits = lines[i].split(" ")[1].__len__() - 3
        tempString = lines[i].split(" ")[1].replace(str(sizeOfBits), '')
        states.append(tempString.replace("\'b", ''))
      if lines[i].split(" ")[1] == "default":
        isThereDefault = True
  #For generating all values of binary to be tested
  lst = list(itertools.product([0, 1], repeat = sizeOfBits))
  lstString = []
  #Put the binary values in array of strings
  for tup in lst:
    tempString2 = ''
    counter2 = 0
    for j in tup:
      tempString2 = tempString2 + str(tup[counter2])
      counter2 += 1
    lstString.append(tempString2)

  for temp in (lstString):
    if temp in states:
      continue
    if(not isThereDefault):
      errors.append('line ' + str(lines[0]) + ' is NOT a Full Case')
      break

  if len(states) != len(set(states)):
    errors.append('line ' + str(lines[0]) + ' is NOT a Parallel Case')

def checkFSMState(lines):
  states = []
  for i, line in enumerate(lines):
    if lines[i].split(" ").__len__() >= 3:
      if lines[i].split(" ")[2] == ":" and lines[i].split(" ")[1] != "default":
        states.append(lines[i].split(" ")[1])

  for i, line in enumerate(lines):
    for j, state in enumerate(states):
      if lines[i].split(" ").__len__() >= 6:
        if lines[i].split(" ")[4] == "<=":
          if lines[i].split(" ")[5] == states[j]:
            states.pop(j)
  if states.__len__() != 0:
    errors.append(f'Line {lines[0].split(" ")[0]}: Unreachable FSM State(s): ' + str(states))

def checkMultiDrivenAssign(lines):
  for i, line in enumerate(lines):
    isDuplicate = False
    if  lines[i].split(" ").__len__() >= 4:
      if lines[i].split(" ")[3] == "=":
        if multiDrivenArrayCheckAssign.__len__() == 0:
          multiDrivenArrayCheckAssign.append(lines[i].split(" ")[2])
          continue
        for  j, tempString in enumerate(multiDrivenArrayCheckAssign):
          if lines[i].split(" ")[2] == multiDrivenArrayCheckAssign[j]:
            errors.append(f'Line {lines[i].split(" ")[0]}: MultiDriven Bus/Register Found, Bus/Register: ' + str(multiDrivenArrayCheckAssign[j]))

def checkMultiDriven(lines):
  tempDict = {}
  for i, line in enumerate(lines):
    for j, tempString in enumerate(multiDrivenArrayCheck):
      if lines[i].split(" ")[1] == multiDrivenArrayCheck[j]:
        errors.append(f'Line {lines[i].split(" ")[0]}: MultiDriven Bus/Register Found, Bus/Register: ' + str(multiDrivenArrayCheck[j]))

  for i, line in enumerate(lines):
    isDuplicate = False
    if  lines[i].split(" ").__len__() >= 3:
      if lines[i].split(" ")[2] == "=":
        if multiDrivenArrayCheck.__len__() == 0:
          multiDrivenArrayCheck.append(lines[i].split(" ")[1])
        for  j, tempString in enumerate(multiDrivenArrayCheck):
          if lines[i].split(" ")[1] == multiDrivenArrayCheck[j]:
            isDuplicate = True
        if(not isDuplicate):
          multiDrivenArrayCheck.append(lines[i].split(" ")[1])

def checkUnintializedRegisters(lines):
  register = []
  for i, line in enumerate(lines):
    if lines[i].split(" ").__len__() > 2:
      if lines[i].split(" ")[2] == "reg":
        register.append(lines[i].split(" ")[3])
    if lines[i].split(" ").__len__() >= 3 and register.__len__() >= 1:
      if register[0] in lines[i].split(" ") and "=" in lines[i].split(" "):
        if lines[i].split(" ").index(register[0]) < lines[i].split(" ").index("="):
          register.pop(0)
        elif lines[i].split(" ").index(register[0]) > lines[i].split(" ").index("="):
          errors.append(f'Line {i + 1}: Uninitialized register found, register: ' + str(register[0]))

def verilogChecker(lines, configArray):

  lines = lines.split("\n")
  for i,line in enumerate(lines):
    lines[i] = lines[i].strip()

  for i, tempString in enumerate(lines):
    tempString = str (i+1)+ " " + tempString
    lines[i] = tempString
  ModuleArray = []
  tempLines = []
  tempLines = lines.copy()

  for i, tempString in enumerate(lines):
    if(lines[i].removeprefix(str(i+1)).split(" ")[1] == "module"):
      counter = i
      while(True):
        if(lines[counter].removeprefix(str(counter+1)).split(" ")[1] == ");"):
          ModuleArray.append(lines[counter])
          break
        ModuleArray.append(lines[counter])
        counter += 1
  for i, tempString in enumerate(tempLines):
    for j, tempString1 in enumerate(ModuleArray):
      if tempLines[i] == ModuleArray[j]:
        tempLines.pop(i)

  if "Multi-Driven Bus/Register" in configArray:
    for i, tempString in enumerate(lines):
      if (lines[i].removeprefix(str(i + 1)).split(" ")[1] == "always"):
        alwaysArray = []
        counter = i
        while (True):
          if (lines[counter].removeprefix(str(counter + 1)).split(" ")[1] == "end"):
            alwaysArray.append(lines[counter])
            break
          alwaysArray.append(lines[counter])
          counter += 1
        checkMultiDriven(alwaysArray)
        for z, tempString2 in enumerate(tempLines):
          for j, tempString1 in enumerate(alwaysArray):
            if tempLines[z] == alwaysArray[j]:
              tempLines.pop(z)
    checkMultiDrivenAssign(tempLines)

  if "Non Full/Parallel Case" in configArray or "Unreachable FSM State" in configArray:
    for i, tempString in enumerate(lines):
      if (lines[i].removeprefix(str(i + 1)).split(" ")[1] == "case"):
        caseArray = []
        counter = i
        while (True):
          if (lines[counter].removeprefix(str(counter + 1)).split(" ")[1] == "endcase"):
            caseArray.append(lines[counter])
            break
          caseArray.append(lines[counter])
          counter += 1
        if "Non Full/Parallel Case" in configArray:
          checkNotFullandNotParallel(caseArray)
        if "Unreachable FSM State" in configArray:
          checkFSMState(caseArray)

  if "Arithmetic Overflow" in configArray:
    ArithmeticOverflowCheck(lines, ModuleArray)

  if "Un-initialized Register" in configArray:
    checkUnintializedRegisters(lines)


verilogFile = open("verilogCode.txt", "r")
lines = verilogFile.read()

ErrorsFile = open("ErrorsReport.txt", "w")

configFile = open("configFile.txt", "r")
config = configFile.read()
configArray = config.split('\n')
for i,line in enumerate(configArray):
  configArray[i] = configArray[i].strip()

verilogChecker(lines, configArray)


if errors.__len__() == 0:
  ErrorsFile.write("No Errors in Verilog Code")
else:
  for i,error in enumerate(errors):
    ErrorsFile.write(errors[i])
    ErrorsFile.write("\n")


