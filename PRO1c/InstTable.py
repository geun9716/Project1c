'''
 * 모든 instruction의 정보를 관리하는 클래스. instruction data들을 저장한다
 * 또한 instruction 관련 연산, 예를 들면 목록을 구축하는 함수, 관련 정보를 제공하는 함수 등을 제공 한다.
'''

class InstTable():
    '''
     * inst.data 파일을 불러와 저장하는 공간.
	 *  명령어의 이름을 집어넣으면 해당하는 Instruction의 정보들을 리턴할 수 있다.
    '''
    instMap = {}
    '''
    * 입력받은 이름의 파일을 열고 해당 내용을 파싱하여 instMap에 저장한다.
    '''
    def openFile(self, fileName):
        f = open(fileName, "r")
        for buffer in f:
            instarr = buffer.split(' ',1)
            self.instMap[instarr[0]] = Instruction(buffer)
        f.close()
    '''
	 * 클래스 초기화. 파싱을 동시에 처리한다.
	 * @param instFile : instuction에 대한 명세가 저장된 파일 이름
    '''
    def __init__(self, instFile):
        self.openFile(instFile)
    '''
     * 입력받은 str값을 가진 Inst를 찾아서 format을 return
	 * 정상 : (int)format , 오류 : -1
    '''
    def search_format(self,str):
        if(str == ""):
            return -1
        if(str[0] == "+"):
            str = str[1:]
        if(str in self.instMap):
            return self.instMap[str].format
        else:
            return -1
    '''
    * 입력받은 str값을 가진 Inst를 찾아서 opcode를 return
	 * 정상 : (int)opcode , 오류 : -1
    '''
    def search_opcode(self, str):
        if(str == ""):
            return -1
        if(str[0] == "+"):
            str = str[1:]
        if(str in self.instMap):
            return self.instMap[str].opcode
        else:
            return -1

class Instruction():
    '''instruction이 몇 바이트 명령어인지 저장. 이후 편의성을 위함'''
    name = ""
    format = 0
    opcode = 0
    numberOfOperand = 0
    '''
     * 클래스를 선언하면서 일반문자열을 즉시 구조에 맞게 파싱한다.
	 * @param line : instruction 명세파일로부터 한줄씩 가져온 문자열
    '''
    def __init__(self, line):
        self.parsing(line)
    '''
     * 일반 문자열을 파싱하여 instruction 정보를 파악하고 저장한다.
	 * @param line : instruction 명세파일로부터 한줄씩 가져온 문자열
    '''
    def parsing(self, line):
        arr = line.split(' ')
        self.name = arr[0]
        self.format = int(arr[1])
        self.opcode = int(arr[2], 16)
        self.numberOfOperand = int(arr[3].strip())

