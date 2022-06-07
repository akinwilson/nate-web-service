from bs4 import BeautifulSoup
from bs4.element import Comment
from urllib.request import urlopen
import re
from collections import Counter




class Retriever:

    def __init__(self, url):
        self.html = urlopen(url).read()

    def _tag_visible(self, element) -> bool:
        if element.parent.name in ['style', 'script', 'head', 'title', 'meta', '[document]']:
            return False
        if isinstance(element, Comment):
            return False
        return True

    def text_from_html(self):
        soup = BeautifulSoup(self.html, 'html.parser')
        texts = soup.findAll(text=True)
        visible_texts = filter(self._tag_visible, texts)  
        return " ".join(visible_texts)


    def __call__(self):
        return self.text_from_html()


def keep_alphabetic(text):
    return re.sub(r"[0-9]+[a-z]*", "", " ".join( re.sub('\W+', '', ch) for ch in text.split() ))

def get_vocabulary(text):
    return dict(Counter([word.lower() for word in text.split()]))


def sort_vocab(vocab, sort_type=['frequency', 'alphabetically']):
    if sort_type=="frequency":
        return  dict( sorted(vocab.items(), key=lambda x: x[1], reverse=True) )
    elif sort_type=="alphabetically":
        return dict( sorted(vocab.items(), key=lambda x: x[0]) )
    else:
        raise ValueError(f"sort type: '{sort_type}' invalid type. Choose from 'frequency' or 'alphabetically' sorting vocabulary")



