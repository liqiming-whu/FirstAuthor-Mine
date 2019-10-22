#!/usr/bin/env python3
import os
import re
import pickle
import joblib
from nltk.tokenize import word_tokenize
import nltk.data
FAMINE_DIR = os.path.dirname(os.path.abspath(__file__))
NLTK_DATA = os.path.join(os.path.join(FAMINE_DIR, 'data'), 'nltk_data')
nltk.data.path.append(NLTK_DATA)


def clean_str(text):
    text = re.sub(r"[^A-Za-z0-9(),!?\'\`\"]", " ", text)
    text = re.sub(r"\s{2,}", " ", text)
    text = text.strip().lower()
    return text


def addwhitespace(text):
    """For using CountVectorizer().fit_transform()"""
    return [" ".join(map(str, i)) for i in text]


class TopicPred:
    def __init__(self, fvoc="word_dict.pickle", fmodel="train_model.m"):
        self.fvoc = fvoc
        self.fmodel = fmodel
        assert os.path.exists(self.fvoc)
        assert os.path.exists(self.fmodel)
        self.voc = pickle.load(open(self.fvoc, "rb"))
        self.model = joblib.load(self.fmodel)

    @property
    def model2label(self):
        d = dict()
        d[0] = "Biology"
        d[1] = "Chemistry"
        d[2] = "Physics"
        d[3] = "Computer Science"
        d[4] = "Others"
        return d

    def build_data(self, x):
        x = list(map(lambda d: word_tokenize(clean_str(d)), x))
        x = list(map(lambda d: list(
            map(lambda w: self.voc.get(w, self.voc["<unk>"]), d)), x))
        x = list(map(lambda d: d + [self.voc["<eos>"]], x))
        return x

    def classify(self, txt):
        """
        Classify article topic
        """
        text = self.build_data([txt])
        text = addwhitespace(text)
        preds = self.model.predict(text)
        return "".join(self.model2label[i] for i in preds)
