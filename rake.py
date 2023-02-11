import operator
import os
import PyPDF2
import re
# Utility function to load stop words from a file and return as a list of words
def loadStopWords(stopWordFile):
    stopWords = []
    for line in open(stopWordFile):
        if (line.strip()[0:1] != "#"):
            for word in line.split():  # in case more than one per line
                stopWords.append(word)
    return stopWords
# Utility function to return a list of all words that are have a length greater than a specified number of characters.
def separatewords(text, minWordReturnSize):
    splitter = re.compile('[^a-zA-Z0-9_\\+\\-/]')
    words = []
    for singleWord in splitter.split(text):
        currWord = singleWord.strip().lower()
        # leave numbers in phrase, but don't count as words, since they tend to invlate scores of their phrases
        if len(currWord) > minWordReturnSize:
            words.append(currWord)
    return words
# Utility function to return a list of sentences.
def splitSentences(text):
    sentenceDelimiters = re.compile(u'[.!?,;:\t\\-\\"\\(\\)\\\'\u2019\u2013]')
    sentenceList = sentenceDelimiters.split(text)
    return sentenceList
def buildStopwordRegExPattern(pathtostopwordsfile):
    stopwordlist = loadStopWords(pathtostopwordsfile)
    stopwordregexlist = []
    for wrd in stopwordlist:
        wrdregex = '\\b' + wrd + '\\b'
        stopwordregexlist.append(wrdregex)
    stopwordpattern = re.compile('|'.join(stopwordregexlist), re.IGNORECASE)
    return stopwordpattern
def generateCandidateKeywords(sentenceList, stopwordpattern):
    phraseList = []
    for s in sentenceList:
        tmp = re.sub(stopwordpattern, '|', s.strip())
        phrases = tmp.split("|")
        for phrase in phrases:
            phrase = phrase.strip().lower()
            if (phrase != ""):
                phraseList.append(phrase)
    return phraseList
def calculateWordScores(phraseList):
    wordfreq = {}
    worddegree = {}
    for phrase in phraseList:
        wordlist = separatewords(phrase, 0)
        wordlistlength = len(wordlist)
        wordlistdegree = wordlistlength - 1
        # if wordlistdegree > 3: wordlistdegree = 3 #exp.
        for word in wordlist:
            wordfreq.setdefault(word, 0)
            wordfreq[word] += 1
            worddegree.setdefault(word, 0)
            worddegree[word] += wordlistdegree
    for item in wordfreq:
        worddegree[item] = worddegree[item] + wordfreq[item]
    wordscore = {}
    for item in wordfreq:
        wordscore.setdefault(item, 0)
        wordscore[item] = worddegree[item] / (wordfreq[item] * 1.0)
    return wordscore
def generateCandidateKeywordScores(phraseList, wordscore):
    keywordcandidates = {}
    for phrase in phraseList:
        keywordcandidates.setdefault(phrase, 0)
        wordlist = separatewords(phrase, 0)
        candidatescore = 0
        for word in wordlist:
            candidatescore += wordscore[word]
        keywordcandidates[phrase] = candidatescore
    return keywordcandidates
def rake(text):
    sentenceList = splitSentences(text)
    stoppath = os.path.join(os.path.dirname(__file__), "SmartStoplist.txt")
    stopwordpattern = buildStopwordRegExPattern(stoppath)
    # generate candidate keywords
    phraseList = generateCandidateKeywords(sentenceList, stopwordpattern)
    # calculate individual word scores
    wordscores = calculateWordScores(phraseList)
    # generate candidate keyword scores
    keywordcandidates = generateCandidateKeywordScores(phraseList, wordscores)
    sortedKeywords = sorted(keywordcandidates.items(), key=operator.itemgetter(1), reverse=True)
    noofkeywords=len(sortedKeywords)
    print(sortedKeywords[0:((noofkeywords)//3)])
    return sortedKeywords
if True:
    filename = input("enter name of input pdf file: ")
    # opening pdf file
    pdfFileObj = open(filename, 'rb')
    # creating a pdf reader object
    pdfReader = PyPDF2.PdfFileReader(pdfFileObj)
    # printing number of pages in pdf file
    n = pdfReader.numPages
    for i in range(n):
        page = pdfReader.getPage(i)
        text = page.extractText()
    pdfFileObj.close()
    text = text.lower()  # convert all words to lower case,

    text = re.sub(r'\s+', ' ', text)  # replace or substitute all spaces, tabs, indents (\s) with ' ' (space)

    text = re.sub(r'\d', ' ', text)  # replace all digits by ' '

    text = re.sub(r'[^a-zA-Z. ]+', '',text)  # replace all non words (\W) with ' '. (note: small w is for all words. capital W is for all non-words)
    text = text.replace("keyword", "[")
    text = text.replace("introduction", "]")
    text = "".join(re.split("[\[\]]", text)[::2])
    text = text.replace("reference", "-")
    split_string = text.split("-", 1)
    text = split_string[0]
    rake(text)
