#!/usr/bin/env python

from topic import TopicPred

tp = TopicPred("data/word_dict.pikle", "data/train_model.m")
text = open("tests/data/31519313.txt").read()
class_a = tp.classify(text)
print(class_a)

