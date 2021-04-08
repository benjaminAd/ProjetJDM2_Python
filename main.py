import requests


def requestToJDM(mot):
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
        if flag and j != '// END\n':
            code += j


if __name__ == '__main__':
    requestToJDM("jardinage")
