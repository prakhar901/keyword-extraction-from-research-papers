import pandas as pd
import PyPDF2
import re
import math
import nltk
from nltk.tokenize import word_tokenize
from ordered_set import OrderedSet

def clean(text):
    text = text.lower()  # convert all words to lower case,
    text = re.sub(r'\s+', ' ', text)  # replace or substitute all spaces, tabs, indents (\s) with ' ' (space)
    text = re.sub(r'\d', ' ', text)  # replace all digits by ' '
    text = re.sub(r'[^a-zA-Z. ]+', '',text)  # replace all non words (\W) with ' '.
    text = text.replace("keyword","[")
    text = text.replace("introduction","]")
    text = "".join(re.split("[\[\]]", text)[::2])
    text = text.replace("reference", "-")
    split_string = text.split("-", 1)
    text = split_string[0]
    #print(text)
    filtered_list = []
    stop_words = nltk.corpus.stopwords.words('english')
    # Tokenize the sentence
    words = word_tokenize(text)
    for w in words:
        if w.lower() not in stop_words:
            filtered_list.append(w)

    text = " ".join(filtered_list)
    #print(text)
    return text
# list of all words
def get_sentence_of_words(text):
    sentence = list()  # list of sentences
    words = list()  # list of words in each sentence.
    sentence_list = list()
    temp = text.strip().split(". ")  # temporary list of sentences.

    for sent in temp:

        words = sent.strip().split(" ")  # getting the words in sentences.

        words = [i for i in words if len(i) > 1]

        if (len(words) > 1):
            sentence.append(words)  # sentence is a list of lists.contains a list of sentences in which each sentence
            # is a list of words

        sentence_list.append(sent)

    #print(sentence,print(len(sentence))
    return sentence, sentence_list
def vectorize(sentence):
    # set of unique words in the whole document.
    unique_words = OrderedSet()
    for sent in sentence:
        for word in sent:
            unique_words.add(word)
    unique_words = list(unique_words)  # converting the set to a list to make it easier to work with it.

    #print(unique_words, len(unique_words))
    # a list of lists that contains the vectorized form of each sentence in the document.
    vector = list()
    for sent in sentence:  # iterate for every sentence in the document
        temp_vector = [0] * len(
            unique_words)  # create a temporary vector to calculate the occurence of each word in that sentence.
        for word in sent:  # iterate for every word in the sentence.
            temp_vector[unique_words.index(word)] += 1
        vector.append(temp_vector)  # add the temporary vector to the list of vectors for each sentence (list of lists)
    #print(vector)
    return vector, unique_words


# function to calculate the tf scores
def tf(vector, sentence, unique_words):
    tf = list()

    no_of_unique_words = len(unique_words)

    for i in range(len(sentence)):

        tflist = list()
        sent = sentence[i]
        count = vector[i]

        for word in sent:
            score = count[sent.index(word)] / float(len(sent))  # tf = no. of occurence of a word/ total no. of words in the sentence.

            if (score == 0):
                score = 1 / float(len(sentence))

            tflist.append(score)

        tf.append(tflist)

    #print(tf)

    return tf


# function to calculate idf.
def idf(vector, sentence, unique_words):
    # idf = log(no. of sentences / no. of sentences in which the word appears).

    no_of_sentences = len(sentence)

    idf = list()

    for sent in sentence:

        idflist = list()

        for word in sent:

            count = 0  # no. of times the word occurs in the entire text.

            for k in sentence:
                if (word in k):
                    count += 1

            score = math.log(no_of_sentences / float(count))  # caclulating idf scores

            idflist.append(score)

        idf.append(idflist)

    #print(idf)

    return idf


# function to calculate the tf-idf scores.
def tf_idf(tf, idf):
    # tf-idf = tf(w) * idf(w)

    tfidf = [[0 for j in range(len(tf[i]))] for i in range(len(tf))]

    for i in range(len(tf)):
        for j in range(len(tf[i])):
            tfidf[i][j] = tf[i][j] * float(idf[i][j])

    # print(tfidf)

    return tfidf


def extract_keywords(tfidf, processed_text):
    mapping = {}
    for i in range(len(tfidf)):
        for j in range(len(tfidf[i])):
            mapping[processed_text[i][j]] = tfidf[i][j]
    mapping = dict(sorted(mapping.items(), key=lambda value: value[1]))
    #print(mapping)
    word_scores = sorted(mapping.values(), reverse=True)
    words = []
    scores_to_word = {}
    for i in range(len(tfidf)):
        for j in range(len(tfidf[i])):
            scores_to_word[tfidf[i][j]] = processed_text[i][j]

    for i in range(len(word_scores)):
        if (word_scores[i] != 0):
            words.append(scores_to_word[word_scores[i]])
        else:
            words.append(scores_to_word[word_scores[i]])
            break
    #print(words)
    words = OrderedSet(words)
    for i in mapping:
        if (mapping[i] == 0):
            words.append(i)
    #print(words, mapping)
    return words, mapping
def save_keywords(words, mapping):
    scores = []
    for word in words:
        scores.append(mapping[word])
    # print(words, scores)
    d = {'Words': words, 'Scores': scores}
    data = pd.DataFrame(d)
    data.to_csv('keywords.csv', sep='\t')
    print(data)


if __name__ == '__main__':
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

        #file1 = open(outputfilen, 'a', errors='ignore')
        #file1.writelines(text)
        #file1.close()
    pdfFileObj.close()
    #data = open(outputfilen).read()
    # print(data)

    t_clean = clean(text)

    processed_text, sentence_list = get_sentence_of_words(t_clean)

    sentence_to_index = {i: k for k, i in enumerate(sentence_list)}

    vector, unique_words = vectorize(processed_text)

    tf = tf(vector, processed_text, unique_words)

    idf = idf(vector, processed_text, unique_words)

    tfidf = tf_idf(tf, idf)

    keywords, mapping = extract_keywords(tfidf, processed_text)

    save_keywords(keywords, mapping)
