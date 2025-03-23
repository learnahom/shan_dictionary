from bs4 import BeautifulSoup
import requests
from PySide6.QtWidgets import *
from PySide6.QtGui import QIcon,QTextCursor
import qdarkstyle
import threading
import re

dictionary={}

def shanSpaces(x):
    x = x.replace(" ", "")
    consonants = "ၵၶငၸသၺတထၼပၽၾမယရလဝႁဢ"
    vowels = ["ၢ","ႃ","e","E","o","r","v","w","ိ","ီ","ု","ူ","ဵ","ႅ","ေ","ႄ","ွ","ႆ"]  # Includes diphthongs, glides
    tones = ["ႇ","ႈ","း","ႉ","ႊ"]
    
    x = x.replace(" ", "")  # Remove all spaces
    x = x.replace("ံ", "မ်")  # Replace ံ with မ်

    # Replace special vowel combinations
    x = x.replace("ို", "e")
    x = x.replace("ိူ", "E")
    x = x.replace("ေႃ", "o")

    # Handle glides
    x = x.replace("ြႃ", "r")
    x = x.replace("ႂ်", "v")
    x = x.replace("ႂႃ", "w")
    
    words = []
    w = ""
    
    for i, char in enumerate(x):
        w += char
        
        # CV: Not CVT or CVCq
        if len(w) == 2 and w[1] in vowels and (
            i == len(x)-1 or (i < len(x)-1 and x[i+1] not in tones and (i < len(x)-2 and x[i+2] != "်"))
        ):
            words.append(w)
            w = ""
        # CCq: Not CCqT
        elif len(w) == 3 and w[1] in consonants and w[2] == "်" and (
            i == len(x)-1 or (i < len(x)-1 and x[i+1] not in tones)
        ):
            words.append(w)
            w = ""
        # CVT: Not CVCq
        elif len(w) == 3 and w[1] in vowels and w[2] in tones:
            words.append(w)
            w = ""
        # CCqT
        elif len(w) == 4 and w[1] in consonants and w[2] == "်" and w[3] in tones:
            words.append(w)
            w = ""
        # CVCq: Not CVCTq
        elif len(w) == 4 and w[1] in vowels and w[2] in consonants and w[3] == "်" and (
            i == len(x)-1 or (i < len(x)-1 and x[i+1] not in tones)
        ):
            words.append(w)
            w = ""
        # CVCTq
        elif len(w) == 5 and w[1] in vowels and w[2] in consonants and w[3] == "်" and (
            i == len(x)-1 or (i < len(x)-1 and x[i+1] not in tones)
        ):
            words.append(w)
            w = ""

        # CCV, CCVT, CCVCq, CCVCqT, etc
        elif x[i] == "်" and (i == len(x)-1 or (i < len(x)-1 and x[i+1] not in tones)):
            words.append(w)
            w = ""
        elif i != 0 and x[i-1] == "်" and x[i] in tones:
            words.append(w)
            w = ""
    
    # Restore original characters
    for i in range(len(words)):
        words[i] = words[i].replace("e", "ို").replace("E", "ိူ").replace("o", "ေႃ")
        words[i] = words[i].replace("r", "ြႃ").replace("v", "ႂ်").replace("w", "ႂႃ")

    return words

class MainWindow(QMainWindow):
    def __init__(self) -> None:
        super().__init__()
        self.setWindowTitle('Shan Translator')
        self.setWindowIcon(QIcon('icon.png'))
        
        self.rows =[] # to store result
        self.entry = QLineEdit(self)
        self.entry.setPlaceholderText("Type any sentence here")
        btn = QPushButton('Translate',self)
        btn.setStyleSheet('color:rgb(55,54,59);background-color: rgb(68,138,255);')
        self.entry.setMinimumHeight(35)
        btn.setMinimumHeight(35)
        
        self.textArea = QTextEdit(self)
        self.textArea.setMinimumWidth(600)
        self.textArea.setMinimumHeight(400)

        layout = QGridLayout()
        layout.addWidget(self.entry,0,0,1,3)
        layout.addWidget(btn,0,3)
        layout.addWidget(self.textArea,1,0,1,4)
        self.frame=QFrame()
        self.frame.setLayout(layout)
        self.setCentralWidget(self.frame)
        self.entry.returnPressed.connect(self.fetchAPI)
        btn.clicked.connect(self.fetchAPI)

    def fetchAPI(self):
        url = "http://sealang.net/shan/search.pl"
        self.textArea.setText("Please Wait...\n")
        words = shanSpaces(self.entry.text())
        output = ""
        for word in words:
            if word in dictionary:
                output += dictionary[word]
            else:
                dictionary[word] = '• '+word+'\n'
                r = requests.post(url, data={"dict":'shan',"language": 'shan',"orth":word})
                soup = BeautifulSoup(r.text, "html.parser")
                if r.status_code==200:
                    for sense in soup.find_all("sense"):
                        print(sense)
                        dictionary[word] +='\t'+sense.find('pos').getText()+'. '+sense.find('def').getText()+'\n'
                    output += dictionary[word]
                else:
                    output+='\tWORD NOT FOUND\n'
            QApplication.processEvents()
            self.textArea.setText(output+"Please Wait...\n")
        self.textArea.setText(output)
        
if __name__=='__main__':
    app=QApplication([])
    app.setStyleSheet(qdarkstyle.load_stylesheet('pyside6'))
    win=MainWindow()
    win.show()
    app.exec()