import requests


class Regle:
    def __init__(self, baseType, endWord, transformType, transformation, exception):
        self.baseType = baseType
        self.endWord = endWord
        self.transformType = transformType
        self.transformation = transformation
        self.exception = exception

    def toString(self):
        print(self.baseType, ' & ', self.endWord, ' => ', self.transformType, ' & ', self.transformation)


class Regles:
    def __init__(self):
        self.regles = []
        file = open('Regles.txt')
        try:
            with file as reader:
                line = reader.readline()
                while line != '':
                    separateLine = line.split(';')
                    self.regles.append(
                        Regle(separateLine[0], separateLine[1], separateLine[2], separateLine[3],
                              separateLine[4].replace("\n", "")))
                    line = reader.readline()
        finally:
            file.close()


class TypeRelation:
    def __init__(self, id, trname, trgpname, help):
        self.id = id
        self.trname = trname
        self.trgpname = trgpname
        self.help = help

    def getData(self):
        print(self.id, self.trname, self.trgpname)


class RelationSortante:
    def __init__(self, id, node1, node2, type, w):
        self.id = id
        self.node1 = node1
        self.node2 = node2
        self.type = type
        self.w = w

    def getData(self):
        print(self.node1, ">", self.node2, "==>", self.type)


class Terms:

    def __init__(self, id, name, type, w):
        self.id = id
        self.name = name
        self.type = type
        self.w = w

    def getData(self):
        print(self.id, " ", self.name)


class JDM:

    def __init__(self, mot):
        self.mot = mot
        self.termsList = []
        self.relationsSortantesList = []
        self.typeRelationsList = []
        self.regles = Regles()

    def checkRule(self):
        for rule in self.regles.regles:
            if self.mot[-len(rule.exception):] != rule.exception:
                if rule.baseType == 'Ver:Inf':
                    length = len(rule.endWord)
                    endword = self.mot[-length:]
                    if endword == rule.endWord:
                        print(self.mot.replace(endword, rule.transformation))

    def separateData(self, Data):
        if Data == None:
            print("le mot", self.mot, "n'existe pas")
        else:
            for line in Data.split("\n"):
                lineSeparator = line.split(";")
                if lineSeparator[0] == 'e':
                    self.termsList.append(
                        Terms(lineSeparator[1], lineSeparator[2], lineSeparator[3], lineSeparator[4]))
                if lineSeparator[0] == 'r':
                    self.relationsSortantesList.append(
                        RelationSortante(lineSeparator[1], lineSeparator[2], lineSeparator[3], lineSeparator[4],
                                         lineSeparator[5]))
                if lineSeparator[0] == 'rt':
                    self.typeRelationsList.append(
                        TypeRelation(lineSeparator[1], lineSeparator[2], lineSeparator[3], lineSeparator[4]))

    def requestToJDM(self):
        url = "http://www.jeuxdemots.org/rezo-dump.php?gotermsubmit=Chercher&gotermrel=penser&rel=?gotermsubmit=Chercher&gotermrel=" + self.mot + "&rel= "
        res = requests.get(url)
        code = ""
        flag = False
        for j in res.text.splitlines(True):
            if j == '<CODE>\n':
                flag = True
            if j == '</CODE>\n':
                return code
            if flag and j != '// END\n' and j != '\n':
                code += j


if __name__ == '__main__':
    jdm = JDM("manger")
    jdm.separateData(jdm.requestToJDM())
    jdm.checkRule()
