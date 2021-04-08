import requests


class TypeRelation:
    def __init__(self, id, trname, trgpname, help):
        self.id = id
        self.trname = trname
        self.trgpname = trgpname
        self.help = help


class RelationSortante:
    def __init__(self, id, node1, node2, type, w):
        self.id = id
        self.node1 = node1
        self.node2 = node2
        self.type = type
        self.w = w


class Terms:

    def __init__(self, id, name, type, w):
        self.id = id
        self.name = name
        self.type = type
        self.w = w

    def getData(self):
        print(self.id, " ", self.name)


class JDM:

    def __init__(self):
        self.termsList = []
        self.relationsSortantesList = []
        self.typeRelationsList = []

    def separateData(self, Data):
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


    def requestToJDM(self, mot):
        url = "http://www.jeuxdemots.org/rezo-dump.php?gotermsubmit=Chercher&gotermrel=penser&rel=?gotermsubmit=Chercher" \
              "&gotermrel=" + mot + "&rel= "
        res = requests.get(url)
        code = ""
        flag = False
        for j in res.text.splitlines(True):
            if j == '<CODE>\n':
                flag = True
            if j == '</CODE>\n':
                print(code)
                return code
            if flag and j != '// END\n' and j != '\n':
                code += j


if __name__ == '__main__':
    jdm = JDM()
    jdm.separateData(jdm.requestToJDM("jardinage"))
