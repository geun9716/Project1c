'''
 * literal과 관련된 데이터와 연산을 소유한다.
 * section 별로 하나씩 인스턴스를 할당한다.
'''
class LiteralTable():

    def __init__(self):
        self.literalList = []
        self.locationList = []
    '''
     * 새로운 Literal을 table에 추가한다.
	 * @param literal : 새로 추가되는 literal의 label
	 * @param location : 해당 literal이 가지는 주소값
	 * 주의 : 만약 중복된 literal이 putLiteral을 통해서 입력된다면 이는 프로그램 코드에 문제가 있음을 나타낸다. 
	 * 매칭되는 주소값의 변경은 modifyLiteral()을 통해서 이루어져야 한다.
    '''
    def putLiteral(self, literal, location):
        self.literalList.append(literal)
        self.locationList.append(location)
    '''
     * 기존에 존재하는 literal 값에 대해서 가리키는 주소값을 변경한다.
	 * @param literal : 변경을 원하는 literal의 label
	 * @param newLocation : 새로 바꾸고자 하는 주소값
    '''
    def modifyLiteral(self, literal, newLocation):
        self.locationList.insert(self.literalList.index(literal),newLocation)
        del self.locationList[self.literalList.index(literal)+1]
    '''
     * 인자로 전달된 literal이 어떤 주소를 지칭하는지 알려준다. 
	 * @param literal : 검색을 원하는 literal의 label
	 * @return literal이 가지고 있는 주소값. 해당 literal이 없을 경우 -1 리턴
    '''
    def search(self, literal):
        if(literal in self.literalList):
            return self.locationList[self.literalList.index(literal)]
        else:
            return -1


