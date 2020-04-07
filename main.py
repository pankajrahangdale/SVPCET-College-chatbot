

from flask import Flask, render_template, request, Session, session

import aiml
from seminar2_progress import sntnce as s
import random
import re
from mappings import map_keys
import os

app = Flask(__name__)
app.secret_key = os.urandom(24)

botName = "Techbot"

@app.route("/")
def home():
    global botName
    session['sid'] = random.randint(1,10000) #uuid.uuid4()
    k.learn("std-startup.xml")
    k.respond("load aiml b", session.get('sid'))
   # botName = k.getBotPredicate("name")
    k.setPredicate('email', '', session.get('sid'))

    return render_template("index.html")

@app.route("/get")
def get_bot_response():
    userText = request.args.get('msg')
    return (start(userText))


sent_check = s.Sent_Similarity()

k = aiml.Kernel()

GREETING = ["Hello! My name is Techbot. I will try my best to provide you information related to our College! "]

DEFAULT_RESPONSES = ["I did not get you! Pardon please!","I couldn't understand what you just said! Kindly rephrase"
                     " what you said :-)", "What you are saying is out of my understanding! You can ask me"
                     " queries regrading SVPCET" ]

EMPTY_RESPONSES = ["Say something! I would love to help you!","Don't hesitate. I'll answer your queries to the best"
                   " of my knowledge!","Say my friend!"]

ONE_WORD_RESPONSES = ["Please elaborate your query for me to understand!", "I could not understand your context, please say more!",
                      "Sorry, I could not get you! Please say something more for me to understand!"]

def printBot(msg, lst=None):
    print(botName+": "+msg)
    if(lst!=None):
        print(botName+": ",lst)
    
def match(line, word):
    pattern = '\\b'+word+'\\b'
    if re.search(pattern, line, re.I)!=None:
        return True
    return False

def matchingSentence(inp):
    f = open('database\questions.txt')
    match = "";
    max_score=0;
    for line in f.readlines():
        score = sent_check.symmetric_sentence_similarity(inp, line)
        if score > max_score:
            max_score = score
            match = line
    f.close()
    return match, max_score

def preprocess(inp):
    if(inp!=""):
        if inp[-1]=='.':
            inp = inp[:-1]
    # to remove . symbol between alphabets. Eg. E.G.C becomes EGC
    inp = re.sub('(?<=\\W)(?<=\\w)\\.(?=\\w)(?=\\W)','',inp) 
    # to remove - symbol between alphabet. Eg. E-G-C becomes EGC
    inp = re.sub('(?<=\\w)-(?=\\w)',' ',inp) 
    # to remove . symbol at word boundaries. Eg. .E.G.C. becomes E.G.C
    inp = re.sub('((?<=\\w)\\.(?=\\B))|((?<=\\B)\\.(?=\\w))','',inp)
    # to remove ' ' symbol in acronyms. Eg. E B C becomes EBC
    inp = re.sub('(?<=\\b\\w) (?=\\w\\b)','',inp)
    inp = inp.upper()
#    print(inp)
    return inp

def isKeyword(word):
    f = open('database/questions.txt','r')
    keywords = f.read().split()
#    print(keywords)
    if(word in keywords):
        return True
    else:
        return False

def start(inp):
    global userName,UNAME_REQ,PWD_REQ
    print(session.get('sid'))
    # tasks: remove punctuation from input or make it get parsed, do something when no match is found; removed last period to end sentence
    p_inp = preprocess(inp)
    # function for transfer to authentication module
    
    
    inp = p_inp
    response = k.respond(inp, session.get('sid'))
    if(response=='No match'):
        # to invalidate wrong one-word input
        if(len(inp.split(" "))==1):
            if(isKeyword(inp)==False):
                if(UNAME_REQ==1):
                    k.setPredicate('email',inp, session.get('sid'))
                    UNAME_REQ = 0
                    PWD_REQ = 1
                    return "Please provide me your password too!"
                if(PWD_REQ==1):
                    k.setPredicate('pwd',inp, session.get('sid'))
                    PWD_REQ = 0
                    return "I'll now be able to answer your GEMS related queries if your credentials are valid! Otherwise you will have to provide your credentials again!"
                
                return(random.choice(ONE_WORD_RESPONSES))
                
        inp = matchingSentence(inp)
#        print(inp)
        response = k.respond(inp[0], session.get('sid'))
        confidence = inp[1]
        if(confidence < 0.5):
            log = open('database/invalidated_log.txt','a')
            log.write(p_inp+"\n")
            log.close()
            return(random.choice(DEFAULT_RESPONSES))
        else:
            response = re.sub('( )?(http:[%\-_/a-zA-z0-9\\.]*)','<a href="\\2">\\2</a>',response)
#            print(response)
            return(response)
    elif(response==""):
        return(random.choice(EMPTY_RESPONSES))
    else: 
        response = re.sub('( )?(http:[%\-_/a-zA-z0-9\\.]*)','<a href="\\2">\\2</a>',response)
        return (response)
    
    if(k.getPredicate('name', session.get('sid'))!=""):
        userName = k.getPredicate('name', session.get('sid'))
    else:
        k.setPredicate('name','Anonymous', session.get('sid'))
        userName = k.getPredicate('name', session.get('sid'))    





if __name__ == "__main__":
    app.run()
    