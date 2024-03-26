import json
import urllib.request
import requests
import json
import re
from bs4 import BeautifulSoup
import edge_tts
import shutil
import uuid

url = "http://localhost:8765"
articles = ["der", "die", "das"]
pronouns = ["etwas/jemanden", "jemanden/etwas", "sich", "jemanden", "jemandem", "etwas", "jdm."]
prepositions = ["an", "auf", "hinter", "neben", "in", "über", "unter", "vor", "zwischen", "bei"]

def request(action, **params):
    return {'action': action, 'params': params, 'version': 6}

def invoke(action, **params):
    requestJson = json.dumps(request(action, **params)).encode('utf-8')
    response = json.load(urllib.request.urlopen(urllib.request.Request('http://127.0.0.1:8765', requestJson)))
    if len(response) != 2:
        raise Exception('response has an unexpected number of fields')
    if 'error' not in response:
        raise Exception('response is missing required error field')
    if 'result' not in response:
        raise Exception('response is missing required result field')
    if response['error'] is not None:
        raise Exception(response['error'])
    return response['result']

def extract_main_word(phrase):
    global articles, pronouns, prepositions
    word = ''
    phrase = re.sub(r'\[sound:.*?\]|,|\||\(.*?\)', '', phrase)
    pronouns_patter = re.compile(r'\b(?:' + '|'.join(re.escape(word) for word in pronouns) + r')\b')
    regex_pattern = '|'.join(re.escape(word) for word in pronouns)
    phrase = re.sub(r'\b(' + regex_pattern + r')\b', '', phrase)
    preposition_patter = re.compile(r'\b(?:' + '|'.join(prepositions) + r')\b')
    phrase = re.sub(preposition_patter, '', phrase)
    words = phrase.split()
    if len(words) == 1:
        word = words[0]
    elif words[0] in articles and len(words) > 1:
        word = words[1]
    return word

def add_note_frequency(note):
    if (note['fields']['Frequency']['value'] != ''):
        return
    phrase = note['fields']['Front']['value']
    word = extract_main_word(phrase)
    if word != '':
        freq = get_freuqency(word)
        print(phrase, word, freq)
        newnote = {'id': note["noteId"], 'fields': {"Frequency": str(freq)}}
        invoke('updateNoteFields', note=newnote)

def get_freuqency(word):
    freq = requests.get('https://www.dwds.de/api/frequency/?q=' + word).json()['frequency']
    return freq
    
def get_proved_ipa(word):
    res = requests.get('https://www.dwds.de/api/ipa/?q=' + word)
    if (res.status_code != 200):
        print("Error: ", word, res.status_code, res.text)
        return ' '
    
    res = res.json()[0]

    if res['status'] == 'proved':
        return res['ipa']
    else:
        return ' '

def add_note_ipa(note):
    if (note['fields']['IPA']['value'] != ''):
        return
    phrase = note['fields']['Front']['value']
    word = extract_main_word(phrase)
    if word != '':
        res = get_proved_ipa(word)
        print(word, res)
        newnote = {'id': note["noteId"], 'fields': {"IPA": res}}
        invoke('updateNoteFields', note=newnote)



media_path = invoke("getMediaDirPath")
DE_VOICE = "de-DE-ConradNeural"
EN_VOICE = ""
DEBUG = False

async def gen_audio(phrase, lang="de"):
    communicate = edge_tts.Communicate(phrase, DE_VOICE) if lang == "de" else edge_tts.Communicate(phrase)
    output = ("debug" if DEBUG else "edge")  + str(uuid.uuid1()) + ".mp3"
    await communicate.save(output)
    shutil.move("./" + output, media_path + "/" + output)
    return output

de_class = "sc-giDImq cdzKxF"
en_class = "sc-iwCbjw kqDtNB"

def add_note(phrase_item, deckname):
    # item: (de_phrase, en_phrase, freq, ipa)
    de_phrase, en_phrase, freq, ipa = phrase_item
    invoke('addNote', note={'deckName': deckname, 'modelName': 'Smart', 'fields': {'Front': de_phrase, 'Back': en_phrase, 'Frequency': freq, 'IPA': ipa}})

async def add_word_suger(de_phrase, en_phrase):
    de_word = extract_main_word(de_phrase)
    de_audio = await gen_audio(de_phrase, "de")
    en_audio = await gen_audio(en_phrase, "en")
    de_audio_label = "[sound:" + de_audio + "]"
    en_audio_label = "[sound:" + en_audio + "]"
    de_field = de_phrase + " " + de_audio_label
    en_field = en_phrase + " " + en_audio_label
    if (de_word == ''):
        return (de_field, en_field, '', '')
    else:
        freq = get_freuqency(de_word)
        ipa = get_proved_ipa(de_word)
    return (de_field, en_field, str(freq), ipa)

async def get_dw_words(dw_url):
    ### return items: [(de_phrase, en_phrase, freq, ipa)]
    response = requests.get(dw_url)
    html_content = response.text
    soup = BeautifulSoup(html_content, 'html.parser')
    de_phrases = [phrase.text for phrase in soup.find_all("a", class_=de_class)]
    en_phrases = [phrase.text for phrase in soup.find_all("span", class_=en_class)]

    if (len(de_phrases) != len(en_phrases)):
        raise ValueError("Error: The number of German and English")
        return
    elif (len(de_phrases) == 0 or len(en_phrases) == 0):
        raise ValueError("No phrases found.")

    items = []
    for i in range(len(de_phrases)):
        de_phrase = de_phrases[i]
        # de_audio_filename = await gen_audio(de_phrase)
        en_phrase = en_phrases[i]
        en_phrase = re.sub(r'\n', '', en_phrase)
        item = await add_word_suger(de_phrase, en_phrase)
        if (item[2] != '' and int(item[2]) <= 1):
            continue
        items.append(item)
    return items

async def add_dw_words(dw_url, deckname):
    items = await get_dw_words(dw_url)
    for item in items:
        add_note(item, deckname)