import sys
import re
import alkana
import os

userdict = {}
if os.path.isfile("userdict.json"):
    import json
    with open("userdict.json","r") as f:
        userdict = json.load(f)

romantable = {
    "ka": "か",
    "ki": "き",
    "ku": "く",
    "ke": "け",
    "ko": "こ",

    "ga": "が",
    "gi": "ぎ",
    "gu": "ぐ",
    "ge": "げ",
    "go": "ご",


    "sa": "さ",
    "si": "し",
    "su": "す",
    "se": "せ",
    "so": "そ",

    "za": "ざ",
    "zi": "じ",
    "zu": "ず",
    "ze": "ぜ",
    "zo": "ぞ",

    "ji": "じ",


    "ta": "た",
    "ti": "ち",
    "tu": "つ",
    "te": "て",
    "to": "と",

    "da": "だ",
    "di": "ぢ",
    "du": "づ",
    "de": "で",
    "do": "ど",


    "na": "な",
    "ni": "に",
    "nu": "ぬ",
    "ne": "ね",
    "no": "の",


    "ha": "は",
    "hi": "ひ",
    "hu": "ふ",
    "he": "へ",
    "ho": "ほ",

    "ba": "ば",
    "bi": "び",
    "bu": "ぶ",
    "be": "べ",
    "bo": "ぼ",

    "pa": "ぱ",
    "pi": "ぴ",
    "pu": "ぷ",
    "pe": "ぷ",
    "po": "ぽ",


    "ma": "ま",
    "mi": "み",
    "mu": "む",
    "me": "め",
    "mo": "も",

    "ya": "や",
    "yu": "ゆ",
    "yo": "よ",

    "ra": "ら",
    "ri": "り",
    "ru": "る",
    "re": "れ",
    "ro": "ろ",

    "wa": "わ",
    "wo": "を",

    "nn": "ん",
}

lowercase = {
    "a": "あ",
    "b": "ぶ",
    "c": "く",
    "d": "で",
    "e": "え",
    "f": "ふ",
    "g": "ぐ",
    "h": "ふ",
    "i": "い",
    "j": "じ",
    "k": "く",
    "l": "れ",
    "m": "む",
    "n": "ぬ",
    "o": "お",
    "p": "ぷ",
    "q": "く",
    "r": "る",
    "s": "す",
    "t": "つ",
    "u": "う",
    "x": "くす",
    "y": "い",
    "z": "ず",
}

uppercase = {
    "A": "エー",
    "B": "ビー",
    "C": "シー",
    "D": "ディー",
    "E": "イー",
    "F": "エフ",
    "G": "ジー",
    "H": "エイチ",
    "I": "アイ",
    "J": "ジェイ",
    "K": "ケー",
    "L": "エル",
    "M": "エム",
    "N": "エヌ",
    "O": "オー",
    "P": "ピー",
    "Q": "キュー",
    "R": "アール",
    "S": "エス",
    "T": "ティー",
    "U": "ユー",
    "V": "ブイ",
    "W": "ダブリュ",
    "X": "エックス",
    "Y": "ワイ",
    "Z": "ゼット",
}


replacements = {**userdict, **romantable, **lowercase, **uppercase}

UppperPattern = re.compile(r'[A-Z]{2,}')
def upperkana(text):
    while True:
        r = UppperPattern.search(text)
        if r == None:
            break
        text= text[:r.start()]+romankana(r.group(),True)+text[r.end():]
    return text

AlphabetPattern = re.compile(r'[a-zA-Z]*')
def englishkana(text):
    i = 0
    result = ""
    for w in AlphabetPattern.findall(text):
        if w == "":
            result += text[i]
            i+=1
        else:
            kana = alkana.get_kana(w)
            if(kana !=None):
                result += kana
            else:
                result += romankana(w,ignore_upper=True)
            i+=len(w)
        if i >= len(text):
            break
    return result

def romankana(text,ignore_upper=False):
    if ignore_upper != True:
        text=text.lower()
    text = re.sub('({})'.format('|'.join(map(re.escape, replacements.keys()))), lambda m: replacements[m.group()], text)
    return text

if __name__=="__main__":
    print(romankana(sys.argv[1]))
