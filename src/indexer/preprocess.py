import string
import nltk
from nltk.corpus import stopwords
from nltk.stem import PorterStemmer
from nltk.tokenize import word_tokenize

# NLTK resources might need to be downloaded, handled in setup
try:
    stop_words = set(stopwords.words('english'))
except LookupError:
    nltk.download('stopwords')
    nltk.download('punkt')
    nltk.download('punkt_tab')
    stop_words = set(stopwords.words('english'))

stemmer = PorterStemmer()

def preprocess_text(text):
    """
    Tokenizes, removes stopwords and punctuation, and stems the text.
    Returns a list of processed tokens.
    """
    if not isinstance(text, str):
        return []
        
    # Lowercase
    text = text.lower()
    
    # Tokenize
    tokens = word_tokenize(text)
    
    # Remove punctuation and stopwords, then stem
    processed_tokens = []
    for token in tokens:
        if token not in string.punctuation and token not in stop_words:
            # removing standalone punctuations that might be missed
            token = token.strip(string.punctuation)
            if token:
                processed_tokens.append(stemmer.stem(token))
                
    return processed_tokens
