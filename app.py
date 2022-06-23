from transformers import pipeline
from youtube_transcript_api import YouTubeTranscriptApi
from flask import Flask, request
from flask_cors import CORS,cross_origin
from googletrans import Translator, constants
import re # regular expression
import nltk # natural language toolkit
import string
import heapq

app = Flask(__name__)
cors = CORS(app)
app.config['CORS_HEADERS'] = 'Content-Type'
#To activate venv: env\Scripts\activate.bat

def changeLanguage(result):
    translator = Translator()
    translation = translator.translate(result)
    return (translation.text)

def getytTranscript(video_id):
    YouTubeTranscriptApi.get_transcript(video_id,languages=['en','af','sq','am','ar','hy','az','bn','eu','be','bs','bg','my',
    'ca','ceb','zh-Hans','zh-Hant','co','hr','cs','da','nl','eo','et','fil','fi','fr','gl','ka','de','el','gu','ht','ha','haw',
    'iw','hi','hmn','hu','is','ig','id','ga','it','ja','jv','kn','kk','km','rw','ko','ku','ky','lo','la','lv','lt','lb','mk',
    'mg','ms','ml','mt','mi','mr','mn','ne','no','ny','or','ps','fa','pl','pt','pa','ro','ru','sm','gd','sr','sn','sd','si',
    'sk','sl','so','st','es','su','sw','sv','tg','ta','tt','te','th','tr','tk','uk','ur','ug','uz','vi','cy','fy','xh','yi',
    'yo','zu'])
    
    transcript = YouTubeTranscriptApi.get_transcript(video_id,languages=['en','af','sq','am','ar','hy','az','bn','eu','be','bs','bg','my',
    'ca','ceb','zh-Hans','zh-Hant','co','hr','cs','da','nl','eo','et','fil','fi','fr','gl','ka','de','el','gu','ht','ha','haw',
    'iw','hi','hmn','hu','is','ig','id','ga','it','ja','jv','kn','kk','km','rw','ko','ku','ky','lo','la','lv','lt','lb','mk',
    'mg','ms','ml','mt','mi','mr','mn','ne','no','ny','or','ps','fa','pl','pt','pa','ro','ru','sm','gd','sr','sn','sd','si',
    'sk','sl','so','st','es','su','sw','sv','tg','ta','tt','te','th','tr','tk','uk','ur','ug','uz','vi','cy','fy','xh','yi',
    'yo','zu'])

    print(transcript)

    result = ""
    for i in transcript:
        result += ' ' + i['text']
    return str(result)

@app.route('/')
def hello_world():

  return "Hello, World!"

@app.route('/api/summarize/', methods=['GET'])
def get_summarizedtext():

  youtube_video = request.args.get('youtube_url')

  video_id = youtube_video.split("=")[1]

  percent = request.args.get('percent')  # percentage of the summary
  choice = request.args.get('choice') # summarization choice

  translator = Translator()
  
  result=getytTranscript(video_id)
  detection = translator.detect(result)
  
  language=constants.LANGUAGES[detection.lang]
  print(language)

  print(len(result))
  print(result)
  
  if language!="english":
      result=changeLanguage(result)
      print('Transcript in English')
      print(result)  
 
  def frequency_based_summarization():
    summary = ""
    formatted_text = extractive_preprocess(result)
    #print(formatted_text)

    word_frequency = nltk.FreqDist(nltk.word_tokenize(formatted_text))
    #print(word_frequency)

    highest_frequency = max(word_frequency.values())
    #print(highest_frequency)

    for word in word_frequency.keys():
      #print(word)
      word_frequency[word] = (word_frequency[word] / highest_frequency)

    #print(word_frequency)

    sentence_list = nltk.sent_tokenize(result)
    #sentence_list

    score_sentences = {}
    for sentence in sentence_list:
      #print(sentence)
      for word in nltk.word_tokenize(sentence.lower()):
        #print(word)
        if sentence not in score_sentences.keys():
          score_sentences[sentence] = word_frequency[word]
        else:
          score_sentences[sentence] += word_frequency[word]

    print(score_sentences)
    n = len(sentence_list)
    per = n*(int(percent)/100)
    
    if int(per) == 0:
      per=1
    
    print(per)
    best_sentences = heapq.nlargest(int(per), score_sentences, key = score_sentences.get)

    print(best_sentences)

    summary = ' '.join(best_sentences)
    return summary
  #============================================================================
  def extractive_preprocess(text):

    text = re.sub(r'\s+', ' ', text)

    nltk.download('punkt')
    nltk.download('stopwords')
    stopwords = nltk.corpus.stopwords.words('english')

    formatted_text = text.lower()
    tokens = []
    for token in nltk.word_tokenize(formatted_text):
      tokens.append(token)
    #print(tokens)
    tokens = [word for word in tokens if word not in stopwords and word not in string.punctuation]
    formatted_text = ' '.join(element for element in tokens)

    return formatted_text

  #====================== Luhn Algo =================================
  def luhn_algo_based_summarization(text, top_n_words, distance, number_of_sentences, percentage):
    summary = ""
    original_sentences = [sentence for sentence in nltk.sent_tokenize(text)]
    #print(original_sentences)
    formatted_sentences = [extractive_preprocess(original_sentence) for original_sentence in original_sentences]
    #print(formatted_sentences)
    words = [word for sentence in formatted_sentences for word in nltk.word_tokenize(sentence)]
    #print(words)
    frequency = nltk.FreqDist(words)
    #print(frequency)
    #return frequency
    top_n_words = [word[0] for word in frequency.most_common(top_n_words)]
    #print(top_n_words)
    sentences_score = calculate_sentences_score(formatted_sentences, top_n_words, distance)
    #print(sentences_score)
    print(percentage)
    if percentage > 0:
      best_sentences = heapq.nlargest(int(len(formatted_sentences) * percentage), sentences_score)
    else:  
      best_sentences = heapq.nlargest(number_of_sentences, sentences_score)
    #print(best_sentences)
    best_sentences = [original_sentences[i] for (score, i) in best_sentences]
    #print(best_sentences)
    summary = ' '.join(best_sentences)
    return summary


  def calculate_sentences_score(sentences, important_words, distance):
    scores = []
    sentence_index = 0

    for sentence in [nltk.word_tokenize(sentence) for sentence in sentences]:
      #print('------------')
      #print(sentence)

      word_index = []
      for word in important_words:
        #print(word)
        try:
          word_index.append(sentence.index(word))
        except ValueError:
          pass

      word_index.sort()
      #print(word_index)

      if len(word_index) == 0:
        continue

      # [0, 1, 5]
      groups_list = []
      group = [word_index[0]]
      i = 1 # 3
      while i < len(word_index): # 3
        # first execution: 1 - 0 = 1
        # second execution: 2 - 1 = 1
        if word_index[i] - word_index[i - 1] < distance:
          group.append(word_index[i])
          #print('group', group)
        else:
          groups_list.append(group[:])
          group = [word_index[i]]
          #print('group', group)
        i += 1
      groups_list.append(group)
      #print('all groups', groups_list)

      max_group_score = 0
      for g in groups_list:
        #print(g)
        important_words_in_group = len(g)
        total_words_in_group = g[-1] - g[0] + 1
        score = 1.0 * important_words_in_group**2 / total_words_in_group
        #print('group score', score)

        if score > max_group_score:
          max_group_score = score

      scores.append((max_group_score, sentence_index))
      sentence_index += 1

    #print('final scores', scores)
    return scores

  #==============================================================

  def abstractive_summarization():
    summary = ""
    chunks = create_chunks(result)
    summarized_text = []
    summarizer = pipeline('summarization')
    summarized_text = summarizer(chunks)
    summary  = ' '.join([summ['summary_text'] for summ in summarized_text])
    return summary

  def create_chunks(result):
    max_chunk = 500
    result = re.sub(r'\s+', ' ', result)
    result = result.replace('.', '.<eos>')
    result = result.replace('?', '?<eos>')
    result = result.replace('!', '!<eos>')
    sentences = result.split('<eos>')
    current_chunk = 0 
    chunks = []
    for sentence in sentences:
        if len(chunks) == current_chunk + 1: 
            if len(chunks[current_chunk]) + len(sentence.split(' ')) <= max_chunk:
                chunks[current_chunk].extend(sentence.split(' '))
            else:
                current_chunk += 1
                chunks.append(sentence.split(' '))
        else:
            print(current_chunk)
            chunks.append(sentence.split(' '))

    for chunk_id in range(len(chunks)):
        chunks[chunk_id] = ' '.join(chunks[chunk_id])
    print(len(chunks))
    return chunks

  if choice=="freq-based":
    summary = frequency_based_summarization()
    print(summary)
    return summary

  elif choice=="luhn-algo":
    summary = luhn_algo_based_summarization(result, 5, 2, 3,int(percent)/100)
    print(summary)
    return summary

  elif choice=="abstractive":
    summary = abstractive_summarization()
    print(summary)
    return summary

if __name__ == '__main__':
    app.run(debug=True)


