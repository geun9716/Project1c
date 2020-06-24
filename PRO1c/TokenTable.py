import math
from SymbolTable import *
from LiteralTable import *
from InstTable import *
'''
 * 사용자가 작성한 프로그램 코드를 단어별로 분할 한 후, 의미를 분석하고, 최종 코드로 변환하는 과정을 총괄하는 클래스이다. <br>
 * pass2에서 object code로 변환하는 과정은 혼자 해결할 수 없고 symbolTable과 instTable의 정보가 필요하므로 이를 링크시킨다.<br>
 * section 마다 인스턴스가 하나씩 할당된다.
'''
class TokenTable():
    MAX_OPERAND = 3
    # bit 조작의 가독성을 위한 선언
    nFlag = 32
    iFlag = 16
    xFlag = 8
    bFlag = 4
    pFlag = 2
    eFlag = 1
        
    # REGISTER의 값을 저장하는 Dictionary
    registMap={"A" : 0, "X" : 1, "L" : 2, "B" : 3, "S" : 4, "T" : 5, "F" : 6 ,"PC" : 8, "SW" : 9 }
    
    '''
     * 초기화하면서 symTable, literalTable 그리고 instTable을 링크시킨다.
	 * @param symTab : 해당 section과 연결되어있는 symbol table
	 * @param literalTab : 해당 section과 연결되어있는 literal table
	 * @param instTab : instruction 명세가 정의된 instTable
    '''
    def __init__(self, SymbolTab, LiteralTab, instT):
        # Token을 다룰 때 필요한 테이블들을 링크시킨다.
        self.symTab = SymbolTab
        self.literalTab = LiteralTab
        self.instTab = instT
        # 각 line을 의미별로 분할하고 분석하는 공간.
        self.tokenList = []
        # 프로그램의 section별 길이를 저장하는 공간
        self.length = 0
        # 프로그램의 Modify 정보를 저장하는 공간
        self.M=[]
    '''
    * 일반 문자열을 받아서 Token단위로 분리시켜 tokenList에 추가한다.
	 * @param line : 분리되지 않은 일반 문자열
    '''
    def putToken(self,line):
        tk = Token(line,self.instTab)
        self.tokenList.append(tk)
    '''
     * tokenList에서 index에 해당하는 Token을 리턴한다.
	 * @param index
	 * @return : index번호에 해당하는 코드를 분석한 Token 클래스
    '''
    def getToken(self, index):
        return self.tokenList[index]
    '''
     * Pass2 과정에서 사용한다.
	 * instruction table, symbol table literal table 등을 참조하여 objectcode를 생성하고, 이를 저장한다.
	 * @param index
    '''
    def makeObjectCode(self, index):
        tmp = ""
        object = 0;targetAddr = 0
        
        if(self.getToken(index).operator != ""):
            format = self.instTab.search_format(self.getToken(index).operator)
            if(self.getToken(index).operator == "START" or self.getToken(index).operator == "CSECT"):   #H RECORD
                self.getToken(index).objectCode = "NO"
            elif(self.getToken(index).operator == "EXTDEF"):                                            #D RECORD
                self.getToken(index).objectCode = "NO"
            elif(self.getToken(index).operator == "EXTREF"):                                            #R RECORD
                self.getToken(index).objectCode = "NO"
            elif(self.getToken(index).operator == "LTORG" or self.getToken(index).operator == "END"):   #LTORT & END
                for i in range(len(self.literalTab.literalList)):
                    if(self.literalTab.literalList[i][1] == "C"):                                       #CHAR TYPE
                        tmp = self.literalTab.literalList[i][3:-1]
                        for j in range(len(tmp)):
                            object |= ord(tmp[j]) << (len(tmp)-j-1) * 8
                    elif(self.literalTab.literalList[i][1] == "X"):                                     #HEX TYPE
                        tmp = self.literalTab.literalList[i][3:-1]
                        object |= int(tmp,16)
                        self.getToken(index).objectCode = '{0:02X}'.format(object)
            elif(self.getToken(index).operator == "WORD"):                                              #WORD
                if('0'<=self.getToken(index).operand[0][0] and self.getToken(index).operand[0][0] <= '9'):
                    object |= int(self.getToken(index).operand[0])
                else:
                    self.getToken(index).objectCode = '{0:06X}'.format(0)
                    if(self.getToken(index).operand[0].find('-')>=0):                                   #MODIFY
                        arr = self.getToken(index).operand[0].split('-')
                        self.M.append(Modify(self.getToken(index).location, 6, '+', arr[0]))
                        self.M.append(Modify(self.getToken(index).location, 6, '-', arr[1]))
            elif(self.getToken(index).operator == "BYTE"):                                              #BYTE
                if(self.getToken(index).operand[0][0] == "X"):
                    tmp = self.getToken(index).operand[0][2:-1]
                    object |= int(tmp,16)
                    self.getToken(index).objectCode = '{0:02X}'.format(object)
            elif(int(format)>0):                                                                        #NORMAL INST
                if(self.getToken(index).operator[0] == "+"):                                            #EXTENDED
                    object |= self.instTab.search_opcode(self.getToken(index).operator) << 24
                    object |= self.getToken(index).nixbpe << 20
                    self.M.append(Modify(self.getToken(index).location+1, 5,
                                        '+', self.getToken(index).operand[0]))
                elif(int(format) == 2):
                    object |= self.instTab.search_opcode(self.getToken(index).operator) << 8
                    object |= self.registMap[self.getToken(index).operand[0]] << 4
                    if(len(self.getToken(index).operand) > 1):                                          #REGISTER
                        object |= self.registMap[self.getToken(index).operand[1]]
                    self.getToken(index).objectCode = '{0:04X}'.format(object)
                elif(int(format) == 3):
                    object |= self.instTab.search_opcode(self.getToken(index).operator) << 16
                    object |= self.getToken(index).nixbpe << 12

                    if(self.getToken(index).getFlag(self.nFlag) > 0 
                       and self.getToken(index).getFlag(self.iFlag) > 0):                               #SIC/XE NORMAL
                        if(self.getToken(index).operand[0] != ""):
                            targetAddr = self.symTab.search(self.getToken(index).operand[0]) - self.getToken(index + 1).location
                    elif(self.getToken(index).getFlag(self.nFlag) > 0):                                 #INDIRECT
                        targetAddr = self.symTab.search(self.getToken(index).operand[0][1:]) 
                        - self.getToken(index + 1).location
                    elif(self.getToken(index).getFlag(self.iFlag) > 0):                                 #IMMEDIATE
                        targetAddr = int(self.getToken(index).operand[0][1:])
            else:
                self.getToken(index).objectCode = "NO"
        else:
            self.getToken(index).objectCode = "NO"

        if(self.getToken(index).operand[0] != "" and self.getToken(index).operand[0][0] == "="):        #LITERAL VALUE
            value = self.literalTab.search(self.getToken(index).operand[0])
            if(value > 0):
                targetAddr = value - self.tokenList[index + 1].location
        if(targetAddr < 0):                                                                             #NAGATIVE TARGET_ADDRESS
            targetAddr &= 4095

        object |= targetAddr                                                                            #MAKE OBJECT CODE
        
        print(object);
        
        if(self.getToken(index).objectCode == ""):
            self.getToken(index).objectCode = '{0:06X}'.format(object)
    '''
     * index번호에 해당하는 object code를 리턴한다.
	 * @param index
	 * @return : object code
    '''
    def getObjectCode(self, index):
        return self.tokenList[index].objectCode


'''
* 각 라인별로 저장된 코드를 단어 단위로 분할한 후  의미를 해석하는 데에 사용되는 변수와 연산을 정의한다. 
* 의미 해석이 끝나면 pass2에서 object code로 변형되었을 때의 바이트 코드 역시 저장한다.
'''
class Token():
    # 의미 분석 단계에서 사용되는 변수들
    location = 0
    label = ""
    operator = ""
    operand = [""]
    comment = ""
    nixbpe = 0
    # object code 생성 단계에서 사용되는 변수들 
    objectCode =""
    byteSize = 0
    '''
     * 클래스를 초기화 하면서 바로 line의 의미 분석을 수행한다. 
	 * @param line : 문장단위로 저장된 프로그램 코드, instTab : parsing을 하기위한 InstTable 링크
    '''
    def __init__(self, line, instTab):
        self.instTab = instTab
        self.parsing(line)
    '''
    * n,i,x,b,p,e flag를 설정한다. 
	 * 
	 * 사용 예 : setFlag(nFlag, 1); 
	 *   또는     setFlag(TokenTable.nFlag, 1);
	 * 
	 * @param flag : 원하는 비트 위치
	 * @param value : 집어넣고자 하는 값. 1또는 0으로 선언한다.
    '''
    def setFlag(self,flag,value):
        temp = math.log2(flag)
        if(value == 1):
            self.nixbpe |= value << int(temp)
        elif(value == 0):
            self.nixbpe &= value << int(temp)
    '''
     * 원하는 flag들의 값을 얻어올 수 있다. flag의 조합을 통해 동시에 여러개의 플래그를 얻는 것 역시 가능하다 
	 * 
	 * 사용 예 : getFlag(nFlag)
	 *   또는     getFlag(nFlag|iFlag)
	 * 
	 * @param flags : 값을 확인하고자 하는 비트 위치
	 * @return : 비트위치에 들어가 있는 값. 플래그별로 각각 32, 16, 8, 4, 2, 1의 값을 리턴할 것임.
    '''
    def getFlag(self, flags):
        return self.nixbpe & flags
    '''
     * line의 실질적인 분석을 수행하는 함수. Token의 각 변수에 분석한 결과를 저장한다.
	 * @param line 문장단위로 저장된 프로그램 코드.
    '''
    def parsing(self,line):
        arr = line.split("\t")
        for i in arr:
            i = i.rstrip('\n')

        if(arr[0]==""):                                         #haven't label
            self.operator = arr[1].rstrip('\n')
            if(len(arr) > 2):                                   #have operand
                self.operand = arr[2].split(",")
                self.operand[-1] = self.operand[-1].rstrip('\n')
            if(len(arr) > 3):                                   #have comment
                self.comment = arr[3]
        elif(arr[0].strip() == "."):                            #remark Token
            self.label = arr[0].rstrip('\n')
        else:                                                   #have label
            self.label = arr[0]
            self.operator = arr[1].rstrip('\n')
            if(len(arr) > 2):                                   #have operand
                self.operand = arr[2].split(",")
                self.operand[-1] = self.operand[-1].rstrip('\n')
            if(len(arr) > 3):                                   #have comment
                self.comment = arr[3]

        format = self.instTab.search_format(self.operator)
        if(self.operator != ""):
            if(self.operator[0] == "+"):                        #EXTENDED
                self.setFlag(TokenTable.eFlag,1)
            elif (int(format)==3):
                self.setFlag(TokenTable.pFlag,1)

            if(self.operand[0] != ""):
                if(self.operand[0][0] == "#"):                  #IMMEDIATE
                    self.setFlag(TokenTable.pFlag,0)
                    self.setFlag(TokenTable.iFlag,1)
                elif(self.operand[0][0] == "@"):                #INDIRECT
                    self.setFlag(TokenTable.nFlag,1)
                elif(int(format)==3):                           #NORMAL TYPE
                    self.setFlag(TokenTable.nFlag,1)
                    self.setFlag(TokenTable.iFlag,1)

                if(len(self.operand) > 1):
                    if(self.operand[1][0] == "X"):
                        self.setFlag(TokenTable.xFlag,1)
            elif(self.operator == "RSUB"):                      #RSUB
                self.setFlag(TokenTable.pFlag,0)
                self.setFlag(TokenTable.iFlag,1)
                self.setFlag(TokenTable.nFlag,1)
    '''
     * Token을 볼 수 있는 toString 함수.
	 * @return:Token을 이루고 있는 변수들의 String값
    '''
    def toString(self):
        return str('{0:4X}'.format(self.location)+"\t"+self.label+"\t"
                   +self.operator+"\t"+self.operand[0]+"\t"+'{0:6b}'.format(self.nixbpe))
'''
* Modified CODE 생성을 위한 CLASS
* location, length, Flag, operand의 값을 가진다.
'''
class Modify():
    def __init__(self, loc, len, Flag, operand):
        self.location = int(loc)
        self.length = int(len)
        self.Flag = Flag
        self.operand = operand
