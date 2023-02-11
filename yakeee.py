import yake
import PyPDF2
import re
import nltk
from nltk.tokenize import word_tokenize

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
text = text.replace("keyword","[")
text = text.replace("introduction","]")
text = "".join(re.split("[\[\]]", text)[::2])
text = text.replace("reference", "-")
split_string = text.split("-", 1)
text = split_string[0]
filtered_list = []
stop_words = nltk.corpus.stopwords.words('english')

    # Tokenize the sentence
words = word_tokenize(text)
for w in words:
    if w.lower() not in stop_words:
        filtered_list.append(w)

    text = " ".join(filtered_list)
language = "en"
max_ngram_size = 2
numOfKeywords = 20

kw_extractor = yake.KeywordExtractor(lan=language,
                                     n=max_ngram_size,
                                     top=numOfKeywords)

keywords = kw_extractor.extract_keywords(text)

for kw in keywords:
    print(kw)