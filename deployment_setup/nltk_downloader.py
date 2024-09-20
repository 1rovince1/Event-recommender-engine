# !python3.9 -m pip install nltk











# use this code (if SSL error or cerificate error arises, use other code)

# import nltk

# nltk.download('stopwords')  
# nltk.download('wordnet')  # For lemmatizer
# nltk.download('omw-1.4')  # For lemmatizer if needed











# use this code incase SSL or certificate error arises

import nltk
import ssl

try:
    _create_unverified_https_context = ssl._create_unverified_context
except AttributeError:
    pass
else:
    ssl._create_default_https_context = _create_unverified_https_context

nltk.download('stopwords')  
nltk.download('wordnet')  # For lemmatizer
nltk.download('omw-1.4')  # For lemmatizer if needed
