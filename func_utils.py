from bs4 import BeautifulSoup
import re
from nltk.corpus import stopwords
import itertools
import emoji
import string
from nltk.stem.wordnet import WordNetLemmatizer
from nltk.tokenize import word_tokenize
from nltk.stem import PorterStemmer


def tweet_cleaning(tweet):    
    stopwords_set = set(stopwords.words('english'))
    not_stopwords = ['not', 'what'] 
    stopwords_set = set([word for word in stopwords_set if word not in not_stopwords])

    punctuation_set = set(string.punctuation) 
    punctuation_set = punctuation_set.union(['—','“', '”', '•', '（＾∇＾）','이민호 김고은 더킹영원의군주 이곤'])

    lemmatizer = WordNetLemmatizer()
    stemmer = PorterStemmer()
    
    #Escaping HTML characters
    tweet = BeautifulSoup(tweet).get_text()

    # general 
    tweet = ''.join(re.sub('(\d+)(st|nd|rd|th)', 'digits', tweet))
    tweet = tweet.replace('[\\t\\n\\r\\f\\v]', ' ')
    tweet = tweet.replace('-', ' ')
    tweet = tweet.replace('’', "'")
    tweet = ''.join(re.sub('US', 'United States of America', tweet))
    tweet = ''.join(re.sub('UK', 'United Kingdom', tweet))

    #tweet = ''.join(re.sub('[\$]?[0-9.?,?]+', 'hasprice', tweet))
    
    tweet = ' '.join(re.sub('(\w+:\/\/\S+)', '', tweet).split())
    tweet = ' '.join(re.sub('(@\w+)', '', tweet).split())
    
    # Removal of hashtags
    #tweet = ' '.join(re.sub('(#\w+).*?', '', tweet).split())
    tweet = ' '.join([a for a in re.split('(#\w+).*?', tweet) if a]).replace('#','').strip() # keep words of hashtag
    
    # Split at upper case 
    #tweet = ' '.join(splitAtUpperCase(tweet))
    tweet = ' '.join(re.findall('\d+|[A-Z]?[a-z\'?]+|[A-Z]{2,}', tweet))
   
    #Lower case
    tweet = tweet.lower()
    
    #CONTRACTIONS source: https://en.wikipedia.org/wiki/Contraction_%28grammar%29
    CONTRACTIONS = load_dict_contractions()
    words = tweet.split()
    reformed = [CONTRACTIONS[word] if word in CONTRACTIONS else word for word in words]
    tweet = " ".join(reformed)
    
    #Removal of Punctuation
    tweet = tweet.replace(":"," ")
    tweet = ''.join([i for i in tweet if i not in punctuation_set]) # on characters
    
    # Standardizing words
    tweet = ' '.join(word_tokenize(tweet)) 
    
    #Deal with emoticons source: https://en.wikipedia.org/wiki/List_of_emoticons
    SMILEY = load_dict_smileys()  
    words = tweet.split()
    reformed = [SMILEY[word] if word in SMILEY else word for word in words]
    tweet = " ".join(reformed)
    
    #Deal with emojis
    tweet = emoji.demojize(tweet)

    # remove numbers 
    tweet = ' '.join(re.sub('\d+', 'digits', tweet).split())
    
    # remove stopwords
    tweet = ' '.join([i for i in tweet.split() if i not in stopwords_set]) 
    
    # convert months to month_of_year
    months_list = ['january', 'february', 'march', 'april', 
                   'may', 'june', 'july', 'august', 'september',
                   'october', 'november', 'december']
    big_regex = re.compile('|'.join(map(re.escape, months_list)))
    tweet = big_regex.sub('month_of_year ', tweet)
    

    # remove non english
    #tweet = " ".join(w for w in word_tokenize(tweet) if w.lower() in words_set or not w.isalpha())

    
    # lemmatize
    #tweet = ' '.join([lemmatizer.lemmatize(word) for word in tweet.split()]) # on words
    tweet = ' '.join([stemmer.stem(word) for word in tweet.split()]) # on words
    #tweet = ' '.join([lemmatizer.lemmatize(tweet)]) # on words
   
    return tweet



# self defined contractions
def load_dict_contractions():
    
    return {
        "ain't":"is not",
        "amn't":"am not",
        "aren't":"are not",
        "can't":"cannot",
        "'cause":"because",
        "couldn't":"could not",
        "couldn't've":"could not have",
        "could've":"could have",
        "daren't":"dare not",
        "daresn't":"dare not",
        "dasn't":"dare not",
        "didn't":"did not",
        "doesn't":"does not",
        "don't":"do not",
        "e'er":"ever",
        "em":"them",
        "everyone's":"everyone is",
        "finna":"fixing to",
        "gimme":"give me",
        "gonna":"going to",
        "gon't":"go not",
        "gotta":"got to",
        "hadn't":"had not",
        "hasn't":"has not",
        "haven't":"have not",
        "he'd":"he would",
        "he'll":"he will",
        "he's":"he is",
        "he've":"he have",
        "how'd":"how would",
        "how'll":"how will",
        "how're":"how are",
        "how's":"how is",
        "i'd":"i would",
        "i'll":"i will",
        "i'm":"i am",
        "i'm'a":"i am about to",
        "i'm'o":"i am going to",
        "isn't":"is not",
        "it'd":"it would",
        "it'll":"it will",
        "it's":"it is",
        "I've":"i have",
        "i've":"i have",
        "ive":"i have",
        "kinda":"kind of",
        "let's":"let us",
        "mayn't":"may not",
        "may've":"may have",
        "mightn't":"might not",
        "might've":"might have",
        "mustn't":"must not",
        "mustn't've":"must not have",
        "must've":"must have",
        "needn't":"need not",
        "ne'er":"never",
        "o'":"of",
        "o'er":"over",
        "ol'":"old",
        "oughtn't":"ought not",
        "shalln't":"shall not",
        "shan't":"shall not",
        "she'd":"she would",
        "she'll":"she will",
        "she's":"she is",
        "shouldn't":"should not",
        "shouldn't've":"should not have",
        "should've":"should have",
        "somebody's":"somebody is",
        "someone's":"someone is",
        "something's":"something is",
        "that'd":"that would",
        "that'll":"that will",
        "that're":"that are",
        "that's":"that is",
        "there'd":"there would",
        "there'll":"there will",
        "there're":"there are",
        "there's":"there is",
        "these're":"these are",
        "they'd":"they would",
        "they'll":"they will",
        "they're":"they are",
        "they've":"they have",
        "this's":"this is",
        "those're":"those are",
        "'tis":"it is",
        "'twas":"it was",
        "wanna":"want to",
        "wasn't":"was not",
        "we'd":"we would",
        "we'd've":"we would have",
        "we'll":"we will",
        "we're":"we are",
        "weren't":"were not",
        "we've":"we have",
        "what'd":"what did",
        "what'll":"what will",
        "what're":"what are",
        "what's":"what is",
        "what've":"what have",
        "when's":"when is",
        "where'd":"where did",
        "where're":"where are",
        "where's":"where is",
        "where've":"where have",
        "which's":"which is",
        "who'd":"who would",
        "who'd've":"who would have",
        "who'll":"who will",
        "who're":"who are",
        "who's":"who is",
        "who've":"who have",
        "why'd":"why did",
        "why're":"why are",
        "why's":"why is",
        "won't":"will not",
        "wouldn't":"would not",
        "would've":"would have",
        "y'all":"you all",
        "you'd":"you would",
        "you'll":"you will",
        "you're":"you are",
        "you've":"you have",
        "whatcha":"what are you",
        "coal":"cool",
        "fab":"fabulous",
        "fav":"favourite",
        "luv":"love",
        "sux":"sucks",
        "yass":"yes",
        "def": "definitely"
        }


# emoticons
def load_dict_smileys():
    
    return {
        ":‑)":"smiley",
        ":-]":"smiley",
        ":-3":"smiley",
        ":->":"smiley",
        "8-)":"smiley",
        ":-}":"smiley",
        ":)":"smiley",
        ":]":"smiley",
        ":3":"smiley",
        ":>":"smiley",
        "8)":"smiley",
        ":}":"smiley",
        ":o)":"smiley",
        ":c)":"smiley",
        ":^)":"smiley",
        "=]":"smiley",
        "=)":"smiley",
        ":-))":"smiley",
        ":‑D":"smiley",
        "8‑D":"smiley",
        "x‑D":"smiley",
        "X‑D":"smiley",
        ":D":"smiley",
        "8D":"smiley",
        "xD":"smiley",
        "XD":"smiley",
        ":‑(":"sad",
        ":‑c":"sad",
        ":‑<":"sad",
        ":‑[":"sad",
        ":(":"sad",
        ":c":"sad",
        ":<":"sad",
        ":[":"sad",
        ":-||":"sad",
        ">:[":"sad",
        ":{":"sad",
        ":@":"sad",
        ">:(":"sad",
        ":'‑(":"sad",
        ":'(":"sad",
        ":‑P":"playful",
        "X‑P":"playful",
        "x‑p":"playful",
        ":‑p":"playful",
        ":‑Þ":"playful",
        ":‑þ":"playful",
        ":‑b":"playful",
        ":P":"playful",
        "XP":"playful",
        "xp":"playful",
        ":p":"playful",
        ":Þ":"playful",
        ":þ":"playful",
        ":b":"playful",
        "<3":"love"
        }


