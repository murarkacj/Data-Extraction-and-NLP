# %%
from bs4 import BeautifulSoup
from urllib.request import urlopen
import trafilatura
import requests
import pandas as pd
import os
import chardet
from nltk.tokenize import word_tokenize,sent_tokenize
from nltk.corpus import cmudict
from nltk.corpus import stopwords
import re

# %%
def data_extraction(url_id,url):
    response = requests.get(url)
    html = response.text
    # Extract the text from the HTML
    soup = BeautifulSoup(html, 'html.parser')
    text = soup.get_text()
    downloaded = trafilatura.fetch_url(url)
    soup = BeautifulSoup(html, "html.parser")
    title = soup.find('meta', property='og:title').get('content')
    text = trafilatura.extract(downloaded)
    print(title,text)
    f = open(f"Data Extraction/{url_id}.txt", "a")
    f.write(title + "\n")
    if text is not None:
        f.write(text)
    else:
        f.write('Text not present')
    f.close()

# %%
input_links = pd.read_excel('Input.xlsx',engine='openpyxl', dtype=str)
for index, row in input_links.iterrows():
    data_extraction(row["URL_ID"],row['URL'])

# %%
# Define an empty list to store stopwords
stopwords_cust = []

# Specify the folder containing text files with stopwords
stopwords_folder_path = "StopWords"

# Iterate through text files in the stopwords folder
for filename in os.listdir(stopwords_folder_path):
    if filename.endswith(".txt"):
        file_path = os.path.join(stopwords_folder_path, filename)
        
        # Detect the file's encoding
        with open(file_path, 'rb') as file:
            result = chardet.detect(file.read())

        # Use the detected encoding to read the file
        encoding = result['encoding']
        with open(file_path, 'r', encoding=encoding) as file:
            file_contents = file.read()
            stopwords_cust += file_contents.splitlines()

# %%
postive_words = []
postive_words_with_stopwords = []
with open('MasterDictionary//positive-words.txt', 'r') as file:
    file_contents = file.read()
    postive_words_with_stopwords += file_contents.splitlines()
    for i in range(len(postive_words_with_stopwords)):
        if postive_words_with_stopwords[i] not in stopwords_cust:
            postive_words.append(postive_words_with_stopwords[i])

# %%
negative_words = []
negative_words_with_stopwords = []
with open('MasterDictionary//negative-words.txt', 'r') as file:
    file_contents = file.read()
    negative_words_with_stopwords += file_contents.splitlines()
    for i in range(len(negative_words_with_stopwords)):
        if negative_words_with_stopwords[i] not in stopwords_cust:
            negative_words.append(negative_words_with_stopwords[i])

# %%
def count_syllables(word):
    # Convert the word to lowercase for consistent comparison
    word = word.lower()
    
    # Define a list of vowels
    vowels = "aeiou"
    
    # Initialize a count for syllables
    syllable_count = 0
    
    # Check if the word ends with "es" or "ed" and adjust syllable count accordingly
    if word.endswith("es"):
        syllable_count -= 1
    elif word.endswith("ed"):
        syllable_count -= 1
    
    # Count the syllables by iterating through the characters in the word
    for i in range(len(word)):
        # Check if the character is a vowel and the next character is not a vowel to avoid double-counting
        if word[i] in vowels and (i == len(word) - 1 or word[i + 1] not in vowels):
            syllable_count += 1

    # Adjust the count for single-letter words
    if len(word) == 1 and word != "a" and word != "i":
        syllable_count = 0

    return syllable_count

# %%
# Specify the folder containing text files with stopwords
data_folder_path = "Data Extraction"

# Iterate through text files in the stopwords folder
for filename in os.listdir(data_folder_path):
    if filename.endswith(".txt"):
        # Define an empty list to store words
        words = []
        positive_score = 0
        negative_score = 0
        file_path = os.path.join(data_folder_path, filename)
        
        # Detect the file's encoding
        with open(file_path, 'rb') as file:
            result = chardet.detect(file.read())

        # Use the detected encoding to read the file
        encoding = result['encoding']
        with open(file_path, 'r', encoding=encoding) as file:
            file_contents = file.read()
            article_words = word_tokenize(file_contents)
            article_sentences = sent_tokenize(file_contents)
            for i in range(len(article_words)):
                if article_words[i] not in stopwords_cust:
                    words.append(article_words[i])
        for i in words:
            if i in postive_words:
                positive_score += 1
            elif i in negative_words:
                negative_score -= 1
        polarity_score = (positive_score + negative_score) / ((positive_score - negative_score) + 0.000001)
        subjectivity_score = (positive_score - negative_score) / ((len(words) + 0.000001))
        avg_wrd_sen = len(article_words) / len(article_sentences)
        num_cmplx = 0
        for i in words:
            if count_syllables(i) >= 2:
                   num_cmplx += 1
        syll = 0
        for i in words:
            syll += count_syllables(i)
        syll_per_word = syll / len(words)
        per_cmplx_words = num_cmplx / len(words) 
        fog_indx = 0.4 * ( avg_wrd_sen + per_cmplx_words )
        stop_words_nltk = set(stopwords.words('english'))
        filtered_words = [w for w in article_words if not w.lower() in stop_words_nltk]
        # initializing punctuations string
        punc = '''!()-[]{};:'"\,<>./?@#$%^&*_~'''
        # Removing punctuations in string
        # Using loop + punctuation string 
        for i in range(len(filtered_words)):
            for ele in filtered_words[i]:
                if ele in punc:
                    filtered_words[i] = ele.replace(ele, "")
        filtered_words = [w for w in filtered_words if w != ""]
        word_count = len(filtered_words)
        total_characters = sum(len(word) for word in filtered_words)
        avg_wrd_len = total_characters /  word_count
        # Define the personal pronouns you want to count
        personal_pronouns = ["I", "we", "my", "ours", "us"]
        # Create a regex pattern to match the personal pronouns, but exclude "US"
        pattern = r'\b(?:' + '|'.join(personal_pronouns) + r')\b(?!S\b)'
        # Use re.findall to find all matches of the pattern in the text
        matches = re.findall(pattern, file_contents, flags=re.IGNORECASE)
        # Count the number of matches
        personal_pronoun_count = len(matches)
        dataframe = pd.read_excel('Output Data Structure.xlsx',engine='openpyxl', dtype=str)
        for index, row in dataframe.iterrows():
            row_url_id = str(row['URL_ID']+'.txt')
            if row_url_id == filename:
                dataframe.loc[index, 'POSITIVE SCORE'] = positive_score
                dataframe.loc[index, 'NEGATIVE SCORE'] = negative_score
                dataframe.loc[index, 'POLARITY SCORE'] = polarity_score
                dataframe.loc[index, 'SUBJECTIVITY SCORE'] = subjectivity_score
                dataframe.loc[index, 'AVG SENTENCE LENGTH'] = avg_wrd_sen
                dataframe.loc[index, 'PERCENTAGE OF COMPLEX WORDS'] = per_cmplx_words
                dataframe.loc[index, 'FOG INDEX'] = fog_indx
                dataframe.loc[index, 'AVG NUMBER OF WORDS PER SENTENCE'] = avg_wrd_sen
                dataframe.loc[index, 'COMPLEX WORD COUNT'] = num_cmplx
                dataframe.loc[index, 'WORD COUNT'] = word_count
                dataframe.loc[index, 'SYLLABLE PER WORD'] = syll_per_word
                dataframe.loc[index, 'PERSONAL PRONOUNS'] = personal_pronoun_count
                dataframe.loc[index, 'AVG WORD LENGTH'] = avg_wrd_len
        dataframe.to_excel('Output Data Structure.xlsx', engine='openpyxl', index=False)


# %%



