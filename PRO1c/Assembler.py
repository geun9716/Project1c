from InstTable import *
from TokenTable import *
from SymbolTable import *
from LiteralTable import *
import copy
'''
 * Assembler : 
 * 이 프로그램은 SIC/XE 머신을 위한 Assembler 프로그램의 메인 루틴이다.
 * 프로그램의 수행 작업은 다음과 같다. 
 * 1) 처음 시작하면 Instruction 명세를 읽어들여서 assembler를 세팅한다. 
 * 2) 사용자가 작성한 input 파일을 읽어들인 후 저장한다. 
 * 3) input 파일의 문장들을 단어별로 분할하고 의미를 파악해서 정리한다. (pass1) 
 * 4) 분석된 내용을 바탕으로 컴퓨터가 사용할 수 있는 object code를 생성한다. (pass2) 
'''
class Assembler():
    # 읽어들인 input 파일의 내용을 한 줄 씩 저장하는 공간.
    lineList = []
    # 프로그램의 section별로 symbol table을 저장하는 공간
    symtabList = []
    # 프로그램의 section별로 literal table을 저장하는 공간
    literaltabList = []
    # 프로그램의 section별로 프로그램을 저장하는 공간
    TokenList = []
    '''
     * Token, 또는 지시어에 따라 만들어진 오브젝트 코드들을 출력 형태로 저장하는 공간.   
	 * 필요한 경우 String 대신 별도의 클래스를 선언하여 ArrayList를 교체해도 무방함.
    '''
    codeList = []
    '''
     * 클래스 초기화. instruction Table을 초기화와 동시에 세팅한다.
	 * @param instFile : instruction 명세를 작성한 파일 이름. 
    '''
    def __init__(self,instFile):
        # instruction 명세를 저장한 공간
        self.instTable = InstTable(instFile)
    '''
     * inputFile을 읽어들여서 lineList에 저장한다.
	 * @param inputFile : input 파일 이름.
    '''
    def loadInputFile(self,inputFile):
        f = open(inputFile, "r")
        for line in f:
            self.lineList.append(line)
        f.close()
    '''
     * pass1 과정을 수행한다.
	 *   1) 프로그램 소스를 스캔하여 토큰단위로 분리한 뒤 토큰테이블 생성
	 *   2) label을 symbolTable에 정리
	 *   
	 *    주의사항 : SymbolTable과 TokenTable은 프로그램의 section별로 하나씩 선언되어야 한다.
    '''
    def pass1(self):
        # Parsing
        tkt = TokenTable(SymbolTable, LiteralTable, self.instTable)
        for i in self.lineList:
            tkt.putToken(i)
        # 프로그램별 TokenTable을 TokenList에 저장, location값 저장 
        symtmp = SymbolTable()
        littmp = LiteralTable()
        tmp = TokenTable(symtmp, littmp, self.instTable)
        locctr = 0
        for i in range(len(tkt.tokenList)):
            tkt.getToken(i).location = locctr
            if(tkt.getToken(i).label != "" and tkt.getToken(i).label[0] != "."):
                if(tkt.getToken(i).operator == "CSECT"):                            #CSECT
                    tmp.length = locctr;
                    locctr = 0
                    tkt.getToken(i).location = 0

                    tmp.symTab = copy.deepcopy(symtmp)
                    tmp.literalTab = copy.deepcopy(littmp)

                    self.TokenList.append(tmp)
                    self.symtabList.append(symtmp)
                    self.literaltabList.append(littmp)

                    symtmp = SymbolTable()
                    littmp = LiteralTable()
                    tmp = TokenTable(symtmp, littmp, self.instTable)

                symtmp.putSymbol(tkt.getToken(i).label, tkt.getToken(i).location)   #PUT SYMTAB
            if(tkt.getToken(i).operator != ""):
                if(tkt.getToken(i).operator == "RESW"):                             #RESW
                    locctr += 3*int(tkt.getToken(i).operand[0])
                    tkt.getToken(i).byteSize = 3*int(tkt.getToken(i).operand[0])
                elif(tkt.getToken(i).operator == "RESB"):                           #RESB
                    locctr += int(tkt.getToken(i).operand[0])
                    tkt.getToken(i).byteSize = int(tkt.getToken(i).operand[0])
                elif(tkt.getToken(i).operator == "WORD"):                           #WORD
                    tkt.getToken(i).byteSize = 3
                    locctr += 3
                elif(tkt.getToken(i).operator == "BYTE"):                           #BYTE
                    if(tkt.getToken(i).operand[0] == "X"):
                        tkt.getToken(i).byteSize = 1
                        locctr += 1
                    else:
                        tkt.getToken(i).byteSize = 1
                        locctr += 1
                elif(tkt.getToken(i).operator == "EQU"):                            #EQU
                    if(tkt.getToken(i).operand[0].rfind("-")>0):
                        arr = tkt.getToken(i).operand[0].split("-")
                        tkt.getToken(i).location = symtmp.search(arr[0])-symtmp.search(arr[1])
                        symtmp.modifySymbol(tkt.getToken(i).label, tkt.getToken(i).location)
                elif(tkt.getToken(i).operator == "LTORG" 
                     or tkt.getToken(i).operator == "END"):                         #LTORG & END
                    for j in range(len(littmp.literalList)):
                        littmp.modifyLiteral(littmp.literalList[j],tkt.getToken(i).location)                        
                        if(littmp.literalList[j][1] == "C"):                        #CHAR TYPE
                            locctr += len(littmp.literalList[j][3:-1])
                            tkt.getToken(i).byteSize = len(littmp.literalList[j][3:-1])
                        elif(littmp.literalList[j][1] == "X"):                      #HEX TYPE
                            length = int(len(littmp.literalList[j][3:-1]))
                            if((length % 2) > 0):
                                locctr += length/2 + 1
                                tkt.getToken(i).byteSize = length/2 + 1
                            else:
                                locctr += length/2
                                tkt.getToken(i).byteSize = length/2
                elif(int(self.instTable.search_format(tkt.getToken(i).operator)) > 0): #NORMAL INST
                    format2 = self.instTable.search_format(tkt.getToken(i).operator)
                    if(tkt.getToken(i).operator[0] == "+"):                         #EXTENDED
                        locctr += 4
                        tkt.getToken(i).byteSize = 4
                    else:                                                           #OTHER INST
                        locctr += int(format2)
                        tkt.getToken(i).byteSize += int(format2)
            if(tkt.getToken(i).operand[0] != "" and tkt.getToken(i).operand[0][0] == "="): #PUT LITERAL TABLE
                index = littmp.search(tkt.getToken(i).operand[0])
                if(index < 0):
                    littmp.putLiteral(tkt.getToken(i).operand[0], tkt.getToken(i).location)
            tmp.tokenList.append(tkt.getToken(i))                                   #ADD_Token_in_tmp
            print(tkt.getToken(i).toString())

        #Last Tables ADD
        tmp.length = int(locctr)
        tmp.symTab = symtmp
        tmp.literalTab = littmp

        self.TokenList.append(tmp)
        self.symtabList.append(symtmp)
        self.literaltabList.append(littmp)
    '''
     * 작성된 SymbolTable들을 출력형태에 맞게 출력한다.
	 * @param fileName : 저장되는 파일 이름
    '''
    def printSymbolTable(self,fileName):
        f = open(fileName,"w")
        for i in range(len(self.symtabList)):
            for j in range(len(self.symtabList[i].symbolList)):
                f.write(self.symtabList[i].symbolList[j] 
                        + "\t" + '{0:4X}'.format(self.symtabList[i].locationList[j])+"\n")
            f.write("\n")
        f.close()
    '''
     * 작성된 LiteralTable들을 출력형태에 맞게 출력한다.
	 * @param fileName : 저장되는 파일 이름
    '''
    def printLiteralTable(self,fileName):
        f = open(fileName,"w")
        for i in range(len(self.literaltabList)):
            for j in range(len(self.literaltabList[i].literalList)):
                f.write(self.literaltabList[i].literalList[j][3:-1] 
                        + "\t" + '{0:4X}'.format(self.literaltabList[i].locationList[j])+"\n")
        f.close()
    '''
     * pass2 과정을 수행한다.
	 *   1) 분석된 내용을 바탕으로 object code를 생성하여 codeList에 저장.
    '''
    def pass2(self):
        size = 0
        tmp = ""
        temp = ""
        T = ""
        for n in range(len(self.TokenList)):										#프로그램 별 TokenTable
            for m in range(len(self.TokenList[n].tokenList)):                       #TokenTable별 TokenList

                self.TokenList[n].makeObjectCode(m)                                 #Make OJBECT CODE

                if(self.TokenList[n].getToken(m).operator != ""):
                    if(self.TokenList[n].getToken(m).operator == "START" 
                       or self.TokenList[n].getToken(m).operator == "CSECT"):       #H RECORD
                        tmp = "H"+self.symtabList[n].symbolList[0]+"\t" +'{0:06X}'.format(self.symtabList[n].locationList[0]) + '{0:06X}'.format(self.TokenList[n].length)
                        self.codeList.append(tmp)
                    elif(self.TokenList[n].getToken(m).operator == "EXTDEF"):       #D RECORD
                        tmp = "D"
                        for i in range(len(self.TokenList[n].getToken(m).operand)):
                            if(self.TokenList[n].getToken(m).operand[i] != ""):
                                tmp += self.TokenList[n].getToken(m).operand[i] + '{0:06X}'.format(self.symtabList[n].search(self.TokenList[n].getToken(m).operand[i]))
                        self.codeList.append(tmp)
                    elif(self.TokenList[n].getToken(m).operator == "EXTREF"):       #R RECORD
                        tmp = "R"
                        for i in range(len(self.TokenList[n].getToken(m).operand)):
                            if(self.TokenList[n].getToken(m).operand[i] != ""):
                                tmp += self.TokenList[n].getToken(m).operand[i]
                        self.codeList.append(tmp)
                #T RECORD
                if(m == 0):
                    T = "T" + '{0:06X}'.format(self.TokenList[n].getToken(m).location)

                if(self.TokenList[n].getToken(m).objectCode != "NO"):
                    if((size + int(self.TokenList[n].getToken(m).byteSize)) > 0x1e):#T LIMIT 0x1E
                        T += '{0:02X}'.format(int(len(temp)/2))+temp
                        self.codeList.append(T)
                        T = "T" + '{0:06X}'.format(self.TokenList[n].getToken(m).location)
                        size = 0
                        temp = ""
                    if(self.TokenList[n].getToken(m-1).objectCode == "NO"):
                        T = "T" + '{0:06X}'.format(self.TokenList[n].getToken(m).location)
                    temp += self.TokenList[n].getObjectCode(m)
                    size += self.TokenList[n].getToken(m).byteSize
                else:
                    if(self.TokenList[n].getToken(m).operator != "" 
                       and self.TokenList[n].getToken(m).operator == "CSECT"):      #CSECT
                         T = "T" + '{0:06X}'.format(self.TokenList[n].getToken(m).location)
                         size = 0
                         temp = ""
                    elif( m > 1 and self.TokenList[n].getToken(m-1).objectCode != "NO"):
                        T += '{0:02X}'.format(int(len(temp)/2))+temp
                        self.codeList.append(T)
                        size = 0
                        temp = ""
                print(self.TokenList[n].getToken(m).toString() + "\t" 
                      + self.TokenList[n].getObjectCode(m))
            if(temp != ""):                                                         #Last Buffer ADD
                T += '{0:02X}'.format(int(len(temp)/2))+temp
                self.codeList.append(T)
                size = 0
                temp = ""
            #M RECORD
            for i in range(len(self.TokenList[n].M)):
                self.codeList.append("M"+'{0:06X}'.format(self.TokenList[n].M[i].location) + '{0:02X}'.format(self.TokenList[n].M[i].length) + self.TokenList[n].M[i].Flag + self.TokenList[n].M[i].operand)
            #E RECORD
            if(n == 0):
                self.codeList.append("E"+ '{0:06X}'.format(self.symtabList[n].locationList[0]))
            else:
                self.codeList.append("E")

            self.codeList.append(" ")
    '''
     * 작성된 codeList를 출력형태에 맞게 출력한다.
	 * @param fileName : 저장되는 파일 이름
    '''
    def printObjectCode(self, fileName):
        f = open(fileName,"w")
        for i in range(len(self.codeList)):
           f.write(self.codeList[i]+"\n")
           print(self.codeList[i])
        f.close()

# 어셈블러의 메인 루틴
assembler = Assembler(".\inst.data")
assembler.loadInputFile(".\input.txt")
assembler.pass1()
assembler.printSymbolTable(".\symtab_20160262.txt")
assembler.printLiteralTable(".\literaltab_20160262.txt")
assembler.pass2()
assembler.printObjectCode(".\output_20160262.txt")