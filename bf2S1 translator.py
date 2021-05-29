#this program will first translate the given bf to IR code
#then optimize the IR code
#and after that translate the IR code to S1monsAssembly

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

#also this does not used S1monsAssembly stdio:
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
        #taken the raw text and makes it into a nice list stream form
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
            
            xOutput += (xIndentLevel * "    ") + str(xIrLine) + "\n"
    
            if xIrLine.xCommand == "loop":
                xIndentLevel += 1
                
    
        return xOutput
        
    
    def Translate(self, xRawInput):
        xCommandStream = self.Structuring(xRawInput)
        self.xIrLines = []
        self.xOutputCode = []
    
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
        
        
        #Final translating
        
        #core routines
        #mem $0 -> cell pointer
        #mem $1 -> internal argument storage for subroutines
        
        #mem $9 -> start of user memory

        self.xOutputCode += [
                ['"setup system stuff:'],
                ['"set cell pointer'],
                
                ["set", "9"],
                ["sRD", "0"],
                
                ["got", "skip"],
                
                ["lab", "movr"],
                ["lDA", "0"],
                ["add", ""],
                ["set", "0"],
                ["jmA", "ptrOverflow"],
                ["sAD", "0"],            
                ["ret", ""],
                ["lab", "ptrOverflow"],
                ["set", "9"],
                ["sRD", "0"],
                ["ret", ""],

                ["lab", "movl"],
                ["lDA", "0"],
                ["sub", ""],
                ["set", "8"],
                ["jmA", "ptrOverflow"],
                ["sAD", "0"],               
                ["ret", ""],
                ["lab", "ptrOverflow"],
                ["clr", ""],
                ["set", "1"],
                ["sub", ""],
                ["sAD", "0"],
                ["ret", ""],

                ["lab", "add"],
                ["lPA", "0"],
                ["add", ""],
                ["and", "255"],
                ["sAP", "0"],
                ["ret"],

                ["lab", "sub"],
                ["lPA", "0"],
                ["sub", ""],
                ["and", "255"],
                ["sAP", "0"],
                ["ret"],
                
                ["lab", "output"],
                ["lPA", "0"],
                ["putstr", ""],
                ["ret", ""],
            
                ["lab", "input"],
                ["getstr", ""],
                ["sAP", "0"],
                ["ret", ""],
                
                ["lab", "clear"],
                ["set", "0"],
                ["sRP", "0"],
                ["ret", ""],
                
                ["lab", "skip"],
                ["", ""],
                ["", ""],
                ['"start of main program:', ""],
            ]
        
        
        
        
        xTranslateLoopIndentLevel = 0
        #this will map an indent level to a iterator number do that if there are two loops on the same indent level, they get different iterator numbers
        xTranslateLoopIndentLevelMapper = {}
        xTranslateLoopIndentLevelIndex = 0
        
        for xTranslateIterator in self.xIrLines:
            xCommand    = xTranslateIterator.xCommand
            xAttribute = xTranslateIterator.xAttribute


            #check for command that don't have direct subroutines and treat them in a special way            
            if xCommand == "loop":
                xTranslateLoopIndentLevelMapper[xTranslateLoopIndentLevel] = xTranslateLoopIndentLevelIndex
                xTranslateLoopIndentLevelIndex += 1
                
                
                xIndex = xTranslateLoopIndentLevelMapper[xTranslateLoopIndentLevel]        
                self.xOutputCode += [["lPA", "0"], ["jm0", "end" + str(xIndex)], ["lab", "loop" + str(xIndex)]]
                xTranslateLoopIndentLevel += 1

            elif xCommand == "end":
                xTranslateLoopIndentLevel -= 1
                xIndex = xTranslateLoopIndentLevelMapper[xTranslateLoopIndentLevel]        
                self.xOutputCode += [["lPA", "0"], ["jm0", "end" + str(xIndex)], ["got", "loop" + str(xIndex)], ["lab", "end" + str(xIndex)]]
                        
            else:
                if xAttribute: self.xOutputCode += [["set", str(xAttribute)]]
                        
                self.xOutputCode += [["jmS", str(xCommand)]]
                
                                
                
        return "\n".join([" ".join(x) for x in self.xOutputCode])
    
    
    
if __name__ == '__main__':
    cM = cMain()
    
    try:
        xInputPath  = sys.argv[sys.argv.index("--input")  + 1]
        xOutputPath = sys.argv[sys.argv.index("--output") + 1]
    
    except Exception:
        print("Error while loading file")
        exit()
    
    
    xInputFile = open(xInputPath, "r").read()

    xOutput = cM.Translate(xInputFile)
    print(xOutput)
    
    xOutputFile = open(xOutputPath, "w")
    xOutputFile.write(xOutput)
    xOutputFile.close()
    
    