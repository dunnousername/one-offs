#!/usr/bin/python3
import nltk
from nltk.parse.generate import generate
from random import choice

grammar = nltk.CFG.fromstring("""
S -> SS | SZ
SZ -> "when" PREDICATE "," SS | "Alex Jones told me that" SS | "I read that" SS | "I read that when" PREDICATE "," SS | SS
SS -> EFFECT "because" CAUSE | CAUSENOUN "causes" EFFECTNOUN | SS CONJUCTION SS | CAUSE THEREFORE CONCLUSION | ASSUMPTION THEREFORE CONCLUSION | PERSON "created" PROBLEM "to sell more" PRODUCTS
CONJUNCTION -> "," "and" | "," "so"
THEREFORE -> "," "so it must be the case that" | "," "therefore" | "," "which means"
CAUSE -> "they put" CAUSENOUN "in" OBJECTNOUN | OBJECTNOUN "has" CAUSENOUN | GROUP "kills people" | GROUP "is run by reptillians" | PERSON "eats dead children" | "gravity doesn't exist" | "you can't feel gravity" | ASSUMPTION
EFFECT -> "they steal your soul" | "your soul gets uploaded to" JARGON "machines" | "you get" EFFECTVERB | OBJECTNOUN "creates" EFFECTNOUN | CONCLUSION
CAUSENOUN -> "radiation" | "radioisotopes" | "dihydrogen monoxide" | "microwaves" | JARGON "bots" | "antimatter" | JARGON "waves" | "dead babies" | "alien semen" | "coronavirus"
EFFECTNOUN -> "autism" | "5G" | "cancer" | "acid" | "mind control"
EFFECTVERB -> "killed" | "executed" | "brainwashed" | "mutated"
OBJECTNOUN -> "a vaccine" | "a cell phone" | "the water supply" | "a 5G tower"
JARGON -> JARGONA JARGONS | "5G" JARGONA JARGONS | "genetically modified" "5G" JARGONA JARGONS
JARGONA -> "nuclear" | "quantum" | "bio-" | "radioactive"
JARGONS -> "nano-" | "micro-"
PREDICATE -> "you get a vaccine" | "you use your phone" | "you use a computer" | "you drink tap water"
PERSON -> "the president" | "the pope"
PEOPLE -> PERSON | GROUP
GROUP -> "the NSA" | "Monsanto" | "the government" | "the CIA"
CONCLUSION -> "Epstein didn't kill himself" | "the periodic table is a lie" | "the Earth is flat" | "coronavirus is not actually contagious"
ASSUMPTION -> "birds are government drones" | "the government puts cognitohazards in Facebook" | "masks don't stop coronavirus" | "jet fuel can't melt steel beams" | PERSON "caused 9/11"
PRODUCTS -> "globes" | "vaccines" | "drugs" | "cell phones"
PROBLEM -> CAUSENOUN | "5G" | "autism" | GROUP
""")

def _rewrite(sentence):
    space = False
    for word in sentence:
        if space and word not in ',':
            yield from ' '
        space = True
        if word[-1] in '-':
            space = False
            yield from word[:-1]
        else:
            yield from word

def rewrite(sentence):
    return ''.join(_rewrite(sentence))

sentences = list(generate(grammar, depth=8))
for i in range(0, 25):
    print(rewrite(choice(sentences)))