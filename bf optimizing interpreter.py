#this program will first translate the given bf to IR code
#then optimize the IR code
#and after that interpret that IR

#the IR is basically a more efficient version of bf:
#    add     <attr> -> increment the current cell by <attr>
#    sub     <attr> -> decrement the current cell by <attr> 
#    movl    <attr> -> move the cell pointer left (down) by <attr>
#    movr    <attr> -> move the cell pointer right  (up) by <attr>
#    loop           -> loop while the current cell is 0
#    end            -> end the while loop
#    output         -> output the current cell as ascii
#    input          -> input into the current cell as ascii
#    clear          -> set the current cell to 0

#also this does not used stdio:
#getstr

import sys


class cIrLine:
    #this class will contain one IR code command and it's attribute if it has one
    
    def __init__(self, xCommand, xAttribute):
        self.xCommand   = str(xCommand)
        self.xAttribute = xAttribute


    def __str__(self):
        return self.xCommand + " " + str(self.xAttribute if self.xAttribute != None else "")


class cMain:
    def __init__(self):
        self.xCommands = "+-<>[].,"
    
    
    def Structuring(self, xRawInput):
        #this takes the raw text and makes it into a nice list stream form
        #(it's not really tokens though, because a command is only one character long)
        
        xCommandStream = []
        
        for xRawInputIterator in xRawInput:
            if xRawInputIterator in self.xCommands:
                xCommandStream.append(xRawInputIterator)
        
        return xCommandStream
    
    
    def CommandRepetitionOptimization(self, xIrLines):
        xIrLinesIndex = 0
        
        while xIrLinesIndex < len(xIrLines) - 1:
            #check if the current and next command are the same and check if then just found command repetition can be optimized,
            #if yes optimize by updating the current lines attribute and removing the next line
            #also if the optimization took place don#t increment the index, because that would skip a line
            
            xIrCurrentLine = xIrLines[xIrLinesIndex]
            xIrNextLine    = xIrLines[xIrLinesIndex + 1]
            
            if xIrCurrentLine.xCommand == xIrNextLine.xCommand and xIrCurrentLine.xCommand in ["add", "sub", "movl", "movr"]:
                xIrCurrentLine.xAttribute += 1
                xIrLines.pop(xIrLinesIndex + 1)
            
            else:           
                xIrLinesIndex += 1
        

        return xIrLines
    
    
    
    def CommandCancelEffectOptimization(self, xIrLines):
        #this will optimize a cases like this:
        #+++-- -> +
        #<<>>> -> >

        xIrLinesIndex = 0
        
        while xIrLinesIndex < len(xIrLines) - 1:
            xIrCurrentLine = xIrLines[xIrLinesIndex]
            xIrNextLine    = xIrLines[xIrLinesIndex + 1]
            
            #check for cancel cases (i know the list stuff is bad, but it's the first day of holiday and i'm lazy)
            if [xIrCurrentLine.xCommand, xIrNextLine.xCommand] in [["movr", "movl"], ["movl", "movr"], ["sub", "add"], ["add", "sub"]]:
                xIrLines.pop(xIrLinesIndex)
                xIrLines.pop(xIrLinesIndex)
                
                #we need to decrement the index because we also remove the current line with optimizing
                xIrLinesIndex -= 1
                
            else:           
                xIrLinesIndex += 1
        
        return xIrLines
    
    
    def MiscOptimization(self, xIrLines):
        #here are some other optimizations like:
        
        #loop \n sub 1 \n end -> clear
        #loop \n add 1 \n end -> clear        
        
        #add <some number, doesn't matter> \n clear -> clear
        #sub <some number, doesn't matter> \n clear -> clear
        
        xIrLinesIndex = 0
        
        while xIrLinesIndex < len(xIrLines) - 2:
            #check the clear case
            #also the add / sub attribute need to be a multiple of 2, because if it is one it will get stuck in an infinite loop and thus can not be optimized into a clear
        
            if xIrLines[xIrLinesIndex + 0].xCommand == "loop"         and \
               xIrLines[xIrLinesIndex + 1].xCommand in ["add", "sub"] and \
               xIrLines[xIrLinesIndex + 1].xAttribute % 2 != 0        and \
               xIrLines[xIrLinesIndex + 2].xCommand == "end":
                
                #replace the lines with the "clear" statement
                xIrLines.pop(xIrLinesIndex + 2)
                xIrLines.pop(xIrLinesIndex + 1)
                xIrLines.pop(xIrLinesIndex + 0)
                xIrLines.insert(xIrLinesIndex + 0, cIrLine(xCommand = "clear", xAttribute = None))
            
            
                #check if there was a "add" or "sub" command behind the now set clear, then of coarse remove it, because it would be removed be the clear anyways so we can just remove it
                while xIrLinesIndex != 0 and xIrLines[xIrLinesIndex - 1].xCommand in ["add", "sub"]:
                    xIrLines.pop(xIrLinesIndex - 1)
                    
            #here we can always increment the index, because we are inserting a now command at the base index
            xIrLinesIndex += 1
        
        return xIrLines

        
        
    
    def RenderIr(self, xIrLines):
        xIndentLevel = 0
        xOutput = ""
        
        for xIndex in range(len(xIrLines)):
            xIrLine = xIrLines[xIndex]
            if xIrLine.xCommand == "end" and xIndentLevel > 0:
                xIndentLevel -= 1
            
            xOutput += str(xIndex) + " " + (xIndentLevel * "    ") + str(xIrLine) + "\n"
    
            if xIrLine.xCommand == "loop":
                xIndentLevel += 1
                
    
        return xOutput
        
    
    def ScanIr(self):
        #map the start and the end of a loop recursively
        
        xEnd   = 0
        xStart = self.xScanPointer - 1


        while True:
            if len(self.xIrLines) == self.xScanPointer:
                return
            
            
            xLine = self.xIrLines[self.xScanPointer].xCommand
            
            if xLine == "loop":
                self.xScanPointer += 1                
                self.ScanIr()
                
            elif xLine == "end":
                xEnd = self.xScanPointer
                self.xScanPointer += 1
                
                self.xEnd2StartMapper[xEnd]   = xStart
                self.xStart2EndMapper[xStart] = xEnd
                
                return
                            
            else:
                self.xScanPointer += 1
    
    
    def Interpreter(self, xRawInput):
        xCommandStream = self.Structuring(xRawInput)
        self.xIrLines = []
        self.xOutputCode = []
    
        self.xInputBuffer = []
    
        #IR translating
        for xCommandIterator in xCommandStream:
            if xCommandIterator == "+":
                xIrCommand = "add"
                xIrAttribute = 1
                
            elif xCommandIterator == "-":
                xIrCommand = "sub"
                xIrAttribute = 1

            elif xCommandIterator == ">":
                xIrCommand = "movr"
                xIrAttribute = 1

            elif xCommandIterator == "<":
                xIrCommand = "movl"
                xIrAttribute = 1
                
            elif xCommandIterator == "[":
                xIrCommand = "loop"
                xIrAttribute = None
            
            elif xCommandIterator == "]":
                xIrCommand = "end"
                xIrAttribute = None

            elif xCommandIterator == ".":
                xIrCommand = "output"
                xIrAttribute = None

            elif xCommandIterator == ",":
                xIrCommand = "input"
                xIrAttribute = None

            self.xIrLines.append(cIrLine(xCommand = xIrCommand, xAttribute = xIrAttribute))


        #run all the optimization functions
        xOptimizationFunctions = [self.CommandCancelEffectOptimization, self.CommandRepetitionOptimization, self.MiscOptimization]
        for xFunctionIterator in xOptimizationFunctions:
            self.xIrLines = xFunctionIterator(self.xIrLines)
        
        print(self.RenderIr(self.xIrLines))
        print("\n" * 10)
        
        
        #map the loops
        self.xScanPointer = 0
        self.xEnd2StartMapper = {}
        self.xStart2EndMapper = {}
        self.ScanIr()
        

        #interpretation        
        xExePtr = 0
        xMemPtr = 0
        xMem = [0 for _ in range(65535)]
        
        while len(self.xIrLines) > xExePtr:
            xLine = self.xIrLines[xExePtr]
            xCommand   = xLine.xCommand
            xAttribute = int(xLine.xAttribute) if xLine.xAttribute else None
            
            if xCommand == "add":
                xMem[xMemPtr] = (xMem[xMemPtr] + xAttribute) % 256
                
            elif xCommand == "sub":
                xMem[xMemPtr] = (xMem[xMemPtr] - xAttribute) % 256
            
            elif xCommand == "movl":
                xMemPtr -= xAttribute
                    
            elif xCommand == "movr":
                xMemPtr += xAttribute
                
            elif xCommand == "output":
                print(chr(xMem[xMemPtr]), end = "", flush = True)
                
            elif xCommand == "input":
                if len(self.xInputBuffer) == 0:
                    self.xInputBuffer += list(input(">>>"))
                                
                xInput = ord(self.xInputBuffer.pop(0)) if len(self.xInputBuffer) != 0 else 0
                xMem[xMemPtr] = xInput
            
            elif xCommand == "loop":
                if xMem[xMemPtr] == 0:
                    xExePtr = self.xStart2EndMapper[xExePtr]
                    continue
            
            elif xCommand == "end":
                if xMem[xMemPtr] != 0:
                    xExePtr = self.xEnd2StartMapper[xExePtr]
                    continue

            elif xCommand == "clear":
                xMem[xMemPtr] = 0
            
            xExePtr += 1
            
            
        if "--dump" in sys.argv:
            print(xMem)
            
if __name__ == '__main__':
    cM = cMain()
    
    
    xInputFile = open(sys.argv[1], "r").read()
    cM.Interpreter(xInputFile)
    
    
    