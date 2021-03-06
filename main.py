import os.path

import requests
import time


class Regle:
    def __init__(self, baseType, endWord, transformType, transformation, exception):
        self.baseType = baseType
        self.endWord = endWord.replace('"', '')
        self.transformType = transformType
        self.transformation = transformation.replace('"', '')
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
        self.nettoyerPath = "Nettoyes/" + self.mot + ".txt"
        self.termsList = []
        self.relationsSortantesList = []
        self.typeRelationsList = []
        self.regles = Regles()
        self.termsListImp = []
        self.relations = []
        self.AfficherNom = []
        self.AfficherAdj = []
        self.AfficherAdv = []
        self.AfficherVer = []

    '''
    M??thode qui va v??rifier si un mot d??riv?? existe
    en utilisant une nouvelle instance de la classe JDM 
    cette m??thode va v??rifier s'il existe un fichier nettoy?? correspondant au mot d??riv?? si c'est le 
    nous allons nettoy?? les donn??es puis v??rifier la s??mantique ?? l'aide de la m??thode checkSemantique
    Si le fichier n'existe pas nous allons v??rifier que le mot d??riv?? n'est pas un n??ologisme puis v??rifier la s??mantique 
    du mot
    :return boolean 
    '''
    def checkIfWordExist(self, mot, typeMot):
        jdm2 = JDM(mot)
        if os.path.isfile(jdm2.nettoyerPath):
            jdm2.nettoyage()
            return jdm2.checkSemantique(typeMot)
        else:
            if jdm2.checkIfNeology(jdm2.requestToJDM()):
                return jdm2.checkSemantique(typeMot)
            else:
                return False


    '''
    M??thode qui va v??rifier qu'un mot d??riv?? correspond bien ?? la s??mantique donn??e dans la r??gle
    :return boolean
    '''
    def checkSemantique(self, typeMot):
        for relation in self.relations:
            if relation.mot2.name.split("'")[1] == typeMot:
                return True
        return False

    '''
        Cette m??thode va parcourir l'ensemble des r??gles pr??sent dans le fichier regles.txt
        La r??gle est d??compos??e sour le format suivant :
         Type de mot;terminaison;Type de transformation; terminaison tranform??e; exeption
         On va d'abord regarde le type de base du mot et s'il correspond au type de base de la r??gle on va pouvoir
         v??rifier la terminaison de la r??gle et du mot
         Si la terminaison est = $ alors on regarde la r??gle peut s'appliquer ?? n'importe quel mot peu importe la terminaison
         sinon on v??rifie que les terminaisons correspondent
         Si elles sorrespondent alors on va d??river le mot et utiliser la m??thode checkIfWordExist et si cette m??thode renvoie vrai
         alors nous ajoutons le mot d??riv?? ?? la liste correspondante afin de pouvoir l'afficher plus tard
    '''
    def checkRule(self):
        for rule in self.regles.regles:
            if self.mot[-len(rule.exception):] != rule.exception:
                for relation in self.relations:
                    if rule.baseType == relation.mot2.name.split("'")[1]:
                        if rule.endWord == "$":
                            newWord = self.mot + rule.transformation
                            if self.checkIfWordExist(newWord, rule.transformType):
                                self.addToDisplayTab(newWord, rule.transformType)
                        else:
                            length = len(rule.endWord)
                            endword = self.mot[-length:]
                            newWord = self.mot[:(len(self.mot) - length)] + rule.transformation
                            if endword == rule.endWord and self.checkIfWordExist(
                                    newWord, rule.transformType):
                                self.addToDisplayTab(newWord, rule.transformType)

    '''
        m??thode qui va s??parer les donn??es selon les relation
        Term1;Relation;Term2
        Dans le cas de ce projet on va garder uniquement les relations r_pos et r_isa
        Ce nettoyage aura pour but de conserver uniquement les relations qui vont relier le mot courant
        aux terms contenant Nom:, Adj:, Adv:, Ver:
        Exemple : 27354,'accompli',1,128;2247340,27354,161702,4,26;161702,'Ver:PPas',4,50
        Si le fichier nettoy?? n'existe pas on va faire le tri, affecter les valeurs ?? une variable et sauvegarder dnas un fichier
        Si le fichier existe nous allons juste parcourir ce fichier et attribuer les donn??es dans une liste
    '''
    def nettoyage(self):
        if os.path.isfile(self.nettoyerPath):
            file = open(self.nettoyerPath, "r")
            try:
                with file as reader:
                    line = reader.readline()
                    while line != '':
                        dataSplit = line.split(";")
                        term = dataSplit[0].split(",")
                        relation = dataSplit[1].split(",")
                        term2 = dataSplit[2].split(",")
                        self.relations.append(Relation(Terms(term[0], term[1], term[2], term[3]),
                                                       RelationSortante(relation[0], relation[1], relation[2],
                                                                        relation[3], relation[4]),
                                                       Terms(term2[0], term2[1], term2[2], term2[3].replace("\n", ""))))
                        line = reader.readline()
            finally:
                file.close()
        else:
            BaseTerm = None
            for term in self.termsList:
                if len(term.name.split("'")) > 1:
                    if self.mot == term.name.split("'")[1]:
                        BaseTerm = term
                else:
                    if self.mot == term.name:
                        BaseTerm = term
                if "Nom:" in term.name or "Adj:" in term.name or "Ver:" in term.name or "Adv:" in term.name:
                    self.termsListImp.append(term)
            if BaseTerm is not None and len(self.termsListImp) != 0:
                file = open(self.nettoyerPath, "w")
                for termImp in self.termsListImp:
                    for relation in self.relationsSortantesList:
                        if relation.node1 == BaseTerm.id and relation.node2 == termImp.id and (
                                relation.type == "4" or relation.type == "6"):
                            file.write(BaseTerm.id + "," + BaseTerm.name + "," + BaseTerm.type + "," + BaseTerm.w + ";")
                            file.write(
                                relation.id + "," + relation.node1 + "," + relation.node2 + "," + relation.type + "," + relation.w + ";")
                            file.write(termImp.id + "," + termImp.name + "," + termImp.type + "," + termImp.w + "\n")
                            self.relations.append(Relation(BaseTerm, relation, termImp))
                file.close()

    '''
        M??thode qui va s??parer en 3 cat??gories les donn??es re??ues :
            - Listes de termes
            - Listes de relations sortantes
            - Listes de type de relations
        puis on va faire appel ?? l'algorithme de nettoyage de donn??es
        :param Donn??es re??ues du r??zo dump
    '''
    def separateData(self, Data):
        if Data == None:
            print("Vous avez cr???? un n??ologisme!")
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


    '''
    V??rifie si les donn??es re??ues sont des n??ologies et si ??a ne l'est pas la m??thode va faire appel ?? la m??thode SeparateData
    :param Data --> Donn??es extraites du r??zo dump
    :return boolean
    '''
    def checkIfNeology(self, Data):
        if Data == None:
            return False
        else:
            self.separateData(Data)
            return True

    '''
    V??rifie qu'un fichier mot.txt existe:
        S'il existe on va r??cup??rer les lignes de ce fichier
        Sinon fais une requ??te au r??zo dump afin de r??cup??rer les informations concernant un mot puis sauvegarde ces infos dans un fichier.txt
        :return cha??ne de caract??re contenant l'ensemble des informations renvoy??es par la requ??te
    '''
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

    def addToDisplayTab(self, newWord, transformType):
        if "Ver:" in transformType:
            self.AfficherVer.append(newWord)
        if "Nom:" in transformType:
            self.AfficherNom.append(newWord)
        if "Adv:" in transformType:
            self.AfficherAdv.append(newWord)
        if "Adj:" in transformType:
            self.AfficherAdj.append(newWord)

    def display(self):
        if len(self.AfficherNom) > 0 or len(self.AfficherVer) > 0 or len(self.AfficherAdj) > 0 or len(
                self.AfficherAdv) > 0:
            print("Voici les mots que vous avez produit ?? partir de " + self.mot + ":")
            if len(self.AfficherNom) > 0:
                print("Voici les noms g??n??r??s:")
                for nom in self.AfficherNom:
                    print(nom)
                print("\n")
            if len(self.AfficherVer) > 0:
                print("Voici les verbes g??n??r??s:")
                for nom in self.AfficherVer:
                    print(nom)
                print("\n")
            if len(self.AfficherAdj) > 0:
                print("Voici les adjectifs g??n??r??s:")
                for nom in self.AfficherAdj:
                    print(nom)
                print("\n")
            if len(self.AfficherAdv) > 0:
                print("Voici les adverbes g??n??r??s:")
                for nom in self.AfficherAdv:
                    print(nom)
                print("\n")
        else:
            print("Votre mot n'est pas d??rivable avec l'ensemble des r??gles actuelles")

    '''
    On v??rifie si le fichier nettoy?? existe, s'il existe on va pouvoir sauver beaucoup de temps en ??vitant la 
    requ??te au r??zo dump et l'utilisation de l'algo de nettoyage ce qui peut diviser le temps d'ex??cution par 5 voir 10
    '''
    def start(self):
        self.regles = Regles()
        if os.path.isfile(self.nettoyerPath):
            self.nettoyage()
            self.checkRule()
        else:
            self.separateData(self.requestToJDM())
            self.checkRule()
        self.display()


if __name__ == '__main__':
    while True:
        mot = input("Entre un mot, ajout. ou exit.\n")
        if mot == "exit.":
            break
        elif mot == "ajout.":
            print("Indiquer la r??gle que vous souhaitez ajouter?")
            print("Le format est le suivant --> Type de mot;terminaison;type du mot une fois transform??e;terminaison "
                  "transform??e;exception")
            print("Dans le cas o?? aucune exception ne vous vient ?? l'esprit ??crivez juste le symbole $")
            print("Faites de m??me dans le cas o?? souhaitez que votre r??gle soit utilisable peu importe la terminaison")
            regle = input()
            split = regle.split(";")
            if len(split) == 5:
                file = open("Regles.txt", "a")
                file.write("\n" + regle)
                file.close()
                print("Votre r??gle -->", regle, "a bien ??t?? ajouter")
        else:
            starttime = time.time()
            jdm = JDM(mot)
            jdm.start()
            print("vous avez obtenus ces r??sultats en", (time.time() - starttime), "secondes.\n")
