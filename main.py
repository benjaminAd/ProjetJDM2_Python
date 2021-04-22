import os.path

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


class Relation:
    def __init__(self, mot, typeRel, mot2):
        self.mot = mot
        self.typeRel = typeRel
        self.mot2 = mot2

    def getData(self):
        print(self.mot.name, self.typeRel, self.mot2)


class JDM:

    def __init__(self, mot):
        self.mot = mot
        self.path = "Requests/" + self.mot + ".txt"
        self.termsList = []
        self.relationsSortantesList = []
        self.typeRelationsList = []
        self.regles = Regles()
        self.termsListImp = []
        self.relations = []

    def checkIfWordExist(self, mot, typeMot):
        jdm = JDM(mot)
        if jdm.checkIfNeology(jdm.requestToJDM()):
            return jdm.checkSemantique(typeMot)
        else:
            return False

    def checkSemantique(self, typeMot):
        for relation in self.relations:
            if relation.mot2.name.split("'")[1] == typeMot:
                return True
        return False

    def checkRule(self):
        createdWord = []
        for rule in self.regles.regles:
            if self.mot[-len(rule.exception):] != rule.exception:
                for relation in self.relations:
                    if rule.baseType == relation.mot2.name.split("'")[1] or rule.baseType == "$":
                        length = len(rule.endWord)
                        endword = self.mot[-length:]
                        if endword == rule.endWord and self.checkIfWordExist(
                                self.mot.replace(endword, rule.transformation), rule.transformType):
                            createdWord.append(self.mot.replace(endword, rule.transformation))
        return createdWord

    def nettoyage(self):
        BaseTerm = None
        for term in self.termsList:
            if self.mot == term.name.split("'")[1]:
                BaseTerm = term
            if "Nom:" in term.name or "Adj:" in term.name or "Ver:" in term.name or "Adv:" in term.name:
                self.termsListImp.append(term)

        for termImp in self.termsListImp:
            for relation in self.relationsSortantesList:
                if relation.node1 == BaseTerm.id and relation.node2 == termImp.id and (
                        relation.type == "4" or relation.type == "6"):
                    self.relations.append(Relation(BaseTerm, relation, termImp))

    def separateData(self, Data):
        if Data == None:
            print("Vous avez créé un néologisme!")
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
            self.nettoyage()

    def checkIfNeology(self, Data):
        if Data == None:
            return False
        else:
            self.separateData(Data)
            return True

    def requestToJDM(self):
        code = ""
        flag = False
        if os.path.isfile(self.path):
            file = open(self.path, "r")
            try:
                with file as reader:
                    line = reader.readline()
                    while line != '':
                        code += line
                        line = reader.readline()
            finally:
                file.close()
            return code
        else:
            url = "http://www.jeuxdemots.org/rezo-dump.php?gotermsubmit=Chercher&gotermrel=penser&rel=?gotermsubmit=Chercher&gotermrel=" + self.mot + "&rel= "
            res = requests.get(url)
            for j in res.text.splitlines(True):
                if j == '<CODE>\n':
                    flag = True
                if j == '</CODE>\n':
                    fichier = open("Requests/" + self.mot + ".txt", "w")
                    fichier.write(code)
                    fichier.close()
                    return code
                if flag and j != '// END\n' and j != '\n':
                    code += j


if __name__ == '__main__':
    jdm = JDM("assister")
    jdm.separateData(jdm.requestToJDM())
    derivation = jdm.checkRule()

    for mot in derivation:
        print(mot)