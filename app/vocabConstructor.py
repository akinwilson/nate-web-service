#!/usr/bin/env python3

from bs4 import BeautifulSoup
from bs4.element import Comment
from urllib.request import urlopen
import re
from collections import Counter
from typing import Dict

class Retriever:

    def __init__(self, url):
        self.url = url
        self.html = urlopen(self.url).read()

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


    def __call__(self) -> str:
        return self.text_from_html()


class TextProcessor:
    def __init__(self,text,sort_type=None):
        self.text = text 
        self.sort_type = sort_type

    def _keep_alphabetic(self,text:str) -> str:
        return re.sub(r"[0-9]+[a-z]*", "", " ".join( re.sub('\W+', '', ch) for ch in text.split() ))

    def _get_vocabulary(self, text:str) -> Dict:
        return dict(Counter([word.lower() for word in text.split()]))

    def sort_vocab(self, vocab:Dict)->Dict:
        if self.sort_type is None:
            return vocab
        elif self.sort_type=="alphabetically":
            return dict( sorted(vocab.items(), key=lambda x: x[0]) )
        elif self.sort_type=="frequency":
            return  dict( sorted(vocab.items(), key=lambda x: x[1], reverse=True) )
        else:
            raise ValueError(f"sort type: '{self.sort_type}' invalid type. Choose from 'frequency' or 'alphabetically' sorting vocabulary")

    def __call__(self,):
        return self.sort_vocab(self._get_vocabulary(self._keep_alphabetic(self.text)))

