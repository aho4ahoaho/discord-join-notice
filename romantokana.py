import sys
import re

worddict={
    "intel":"いんてる",
    "amd":"えーえむでぃー",
    "cpu":"しーぴーゆー",
    "message":"めっせーじ",
    "log":"ろぐ",
    }

romantable = {
    "ka":"か",
    "ki":"き",
    "ku":"く",
    "ke":"け",
    "ko":"こ",

    "ga":"が",
    "gi":"ぎ",
    "gu":"ぐ",
    "ge":"げ",
    "go":"ご",


    "sa":"さ",
    "si":"し",
    "su":"す",
    "se":"せ",
    "so":"そ",

    "za":"ざ",
    "zi":"じ",
    "zu":"ず",
    "ze":"ぜ",
    "zo":"ぞ",

    "ji":"じ",


    "ta":"た",
    "ti":"ち",
    "tu":"つ",
    "te":"て",
    "to":"と",

    "da":"だ",
    "di":"ぢ",
    "du":"づ",
    "de":"で",
    "do":"ど",


    "na":"な",
    "ni":"に",
    "nu":"ぬ",
    "ne":"ね",
    "no":"の",


    "ha":"は",
    "hi":"ひ",
    "hu":"ふ",
    "he":"へ",
    "ho":"ほ",

    "ba":"ば",
    "bi":"び",
    "bu":"ぶ",
    "be":"べ",
    "bo":"ぼ",

    "pa":"ぱ",
    "pi":"ぴ",
    "pu":"ぷ",
    "pe":"ぷ",
    "po":"ぽ",


    "ma":"ま",
    "mi":"み",
    "mu":"む",
    "me":"め",
    "mo":"も",

    "ya":"や",
    "yu":"ゆ",
    "yo":"よ",

    "ra":"ら",
    "ri":"り",
    "ru":"る",
    "re":"れ",
    "ro":"ろ",

    "wa":"わ",
    "wo":"を",

    "nn":"ん",
}

lowercase={
    "a":"あ",
    "b":"ぶ",
    "c":"く",
    "d":"で",
    "e":"え",
    "f":"ふ",
    "g":"ぐ",
    "h":"ふ",
    "i":"い",
    "j":"じ",
    "k":"く",
    "l":"れ",
    "m":"む",
    "n":"ぬ",
    "o":"お",
    "p":"ぷ",
    "q":"く",
    "r":"る",
    "s":"す",
    "t":"つ",
    "u":"う",
    "x":"くす",
    "y":"い",
    "z":"ず",
}

replacements={**worddict ,**romantable,**lowercase}

def romankana(text):
    text=text.lower()

    text = re.sub('({})'.format('|'.join(map(re.escape, replacements.keys()))), lambda m: replacements[m.group()], text)

    return text

if __name__=="__main__":
    print(romankana(sys.argv[1]))
