from nltk.corpus import stopwords
from nltk.tokenize import word_tokenize
from nltk.stem import PorterStemmer
from nltk.stem import LancasterStemmer,WordNetLemmatizer,SnowballStemmer
import string
NO_OF_CHARS = 2220000
from os.path import dirname, join

 
def badCharHeuristic(string, size):
    
    # Initialize all occurrence as -1
    badChar = [-1]*NO_OF_CHARS
    # Fill the actual value of last occurrence
    for i in range(size):
        badChar[ord(string[i])] = i
 
    # retun initialized list
    return badChar
 
def search(txt, pat):
    '''
    A pattern searching function that uses Bad Character
    Heuristic of Boyer Moore Algorithm
    '''
    m = len(pat)
    n = len(txt)
    
    # create the bad character list by calling
    # the preprocessing function badCharHeuristic()
    # for given pattern
    badChar = badCharHeuristic(pat, m)
 
    # s is shift of the pattern with respect to text
    s = 0
    while(s <= n-m):
        j = m-1
 
        # Keep reducing index j of pattern while
        # characters of pattern and text are matching
        # at this shift s
        while j>=0 and pat[j] == txt[s+j]:
            j -= 1
 
        # If the pattern is present at current shift,
        # then index j will become -1 after the above loop
        if j<0:
            #print("Pattern occur at shift = {}".format(s))
 
            '''   
                Shift the pattern so that the next character in text
                      aligns with the last occurrence of it in pattern.
                The condition s+m < n is necessary for the case when
                   pattern occurs at the end of text
               '''
            s += (m-badChar[ord(txt[s+m])] if s+m<n else 1)
            return True
        else:
            '''
            Shift the pattern so that the bad character in text
               aligns with the last occurrence of it in pattern. The
               max function is used to make sure that we get a positive
               shift. We may get a negative shift if the last occurrence
               of bad character in pattern is on the right side of the
               current character.
            '''
            s += max(1, j-badChar[ord(txt[s+j])])
            
def prepare_content(content):
    puncList = string.punctuation + "«" + "»" + "'"
    # STOP WORDS
    stop_words = set(stopwords.words('french'))
    # TOKENIZE
    word_tokens = word_tokenize(content)
    filtered_content = []
    # STEMMING | LEMMATIZATION
    porter = WordNetLemmatizer()
    for w in word_tokens:
        if w not in stop_words:
            w = w.lower()
            if w not in puncList:
                word = porter.lemmatize(w)
                filtered_content.append(word)
    
    return filtered_content           

def plagiarism(txt, pat):
    txt = txt.lower()
    pat = pat.lower()
    th_a = len (txt.split(" "))
    th_b = len(pat.split(" "))
    sh = 0
    print(th_a,th_b)
    prepareTxt = ' '.join(map(str,prepare_content(txt)))
    tableau = []
    for text in prepare_content(pat):  
        if search(prepareTxt, text) == True :
            sh= sh+1
            tableau.append(text)
    p = (float(2 * sh)/(th_a + th_b)) * 100
    return p
            