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

    def checkSemantique(self, typeMot):
        for relation in self.relations:
            if relation.mot2.name.split("'")[1] == typeMot:
                return True
        return False

    '''
        Cette méthode va parcourir l'ensemble des règles présent dans le fichier regles.txt
        La règle est décomposée sour le format suivant :
         Type de mot;terminaison;Type de transformation; terminaison tranformée; exeption
         On va d'abord regarde le type de base du mot et s'il correspond au type de base de la règle on va pouvoir
         vérifier la terminaison de la règle et du mot
         Si la terminaison est = $ alors on regarde la règle peut s'appliquer à n'importe quel mot peu importe la terminaison
         sinon on vérifie que les terminaisons correspondent
         Si elles sorrespondent alors on va dériver le mot et utiliser la méthode checkIfWordExist et si cette méthode renvoie vrai
         alors nous ajoutons le mot dérivé à la liste correspondante afin de pouvoir l'afficher plus tard
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
        méthode qui va séparer les données selon les relation
        Term1;Relation;Term2
        Dans le cas de ce projet on va garder uniquement les relations r_pos et r_isa
        Ce nettoyage aura pour but de conserver uniquement les relations qui vont relier le mot courant
        aux terms contenant Nom:, Adj:, Adv:, Ver:
        Exemple : 27354,'accompli',1,128;2247340,27354,161702,4,26;161702,'Ver:PPas',4,50
        Si le fichier nettoyé n'existe pas on va faire le tri, affecter les valeurs à une variable et sauvegarder dnas un fichier
        Si le fichier existe nous allons juste parcourir ce fichier et attribuer les données dans une liste
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
        Méthode qui va séparer en 3 catégories les données reçues :
            - Listes de termes
            - Listes de relations sortantes
            - Listes de type de relations
        puis on va faire appel à l'algorithme de nettoyage de données
        :param Données reçues du rézo dump
    '''
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


    '''
    Vérifie si les données reçues sont des néologies et si ça ne l'est pas la méthode va faire appel à la méthode SeparateData
    :param Data --> Données extraites du rézo dump
    :return boolean
    '''
    def checkIfNeology(self, Data):
        if Data == None:
            return False
        else:
            self.separateData(Data)
            return True

    '''
    Vérifie qu'un fichier mot.txt existe:
        S'il existe on va récupérer les lignes de ce fichier
        Sinon fais une requête au rézo dump afin de récupérer les informations concernant un mot puis sauvegarde ces infos dans un fichier.txt
        :return chaîne de caractère contenant l'ensemble des informations renvoyées par la requête
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
            print("Voici les mots que vous avez produit à partir de " + self.mot + ":")
            if len(self.AfficherNom) > 0:
                print("Voici les noms générés:")
                for nom in self.AfficherNom:
                    print(nom)
                print("\n")
            if len(self.AfficherVer) > 0:
                print("Voici les verbes générés:")
                for nom in self.AfficherVer:
                    print(nom)
                print("\n")
            if len(self.AfficherAdj) > 0:
                print("Voici les adjectifs générés:")
                for nom in self.AfficherAdj:
                    print(nom)
                print("\n")
            if len(self.AfficherAdv) > 0:
                print("Voici les adverbes générés:")
                for nom in self.AfficherAdv:
                    print(nom)
                print("\n")
        else:
            print("Votre mot n'est pas dérivable avec l'ensemble des règles actuelles")

    '''
    On vérifie si le fichier nettoyé existe, s'il existe on va pouvoir sauver beaucoup de temps en évitant la 
    requête au rézo dump et l'utilisation de l'algo de nettoyage ce qui peut diviser le temps d'exécution par 5 voir 10
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
            print("Indiquer la règle que vous souhaitez ajouter?")
            print("Le format est le suivant --> Type de mot;terminaison;type du mot une fois transformée;terminaison "
                  "transformée;exception")
            print("Dans le cas où aucune exception ne vous vient à l'esprit écrivez juste le symbole $")
            print("Faites de même dans le cas où souhaitez que votre règle soit utilisable peu importe la terminaison")
            regle = input()
            split = regle.split(";")
            if len(split) == 5:
                file = open("Regles.txt", "a")
                file.write("\n" + regle)
                file.close()
                print("Votre règle -->", regle, "a bien été ajouter")
        else:
            starttime = time.time()
            jdm = JDM(mot)
            jdm.start()
            print("vous avez obtenus ces résultats en", (time.time() - starttime), "secondes.\n")
