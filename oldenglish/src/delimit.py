#!/bin/python
#coding=utf-8

import sys
from emdros_path import *
from emdros_application import *
from copy import *

alphabet = 'abcdefghijklmnopqrstuvwxyzðþæABCDEFGHIJKLMNOPQRSTUVWXYZÐÞÆ'
capitals = 'ABCDEFGHIJKLMNOPQRSTUVWXYZÐÞÆ' 

def PySheaf2List(sheaf, spin):
    l = []
    for straw in sheaf:
	for obj in straw:
	    l.append(obj)
    return l

class Delimiter(EmdrosApplication):

    def __init__(self, options):
        EmdrosApplication.__init__(self, options=options,
                                   DO_REF=False, DO_OUT=False, DO_LBL=False)
	self.DBX = self.cfg.get('debug_mode')
	self.SENT_ATOM_ON = False
	self.SENTENCE_ON = False
	self.ASIDE_ON = False
	self.QUOTE_ON = False
	self.spin = Spinner()

	self.sentence_atoms = []
	self.sentences = []
	self.asides = []
	self.quotes = []

	self.curr_sentence_atom = PyObject(otype = "sentence_atom")
	self.curr_sentence      = PyObject(otype = "sentence")
	self.curr_aside         = PyObject(otype = "aside")
	self.curr_quotes        = [PyObject(otype = "quote")]

	self.mql.createObjectType('sentence')
	self.mql.createObjectType('sentence_atom')
	self.mql.createObjectType('quote')
	self.mql.createObjectType('aside')
	
	self.SENTENCE_ATOM_ON  = False
	self.SENTENCE_ON       = False
	self.QUOTE_ON          = False
	self.SUBQUOTE_ON       = False
	self.ASIDE_ON          = False

    def mainLoop(self):

	q = "SELECT ALL OBJECTS WHERE [word get surface] GO"
	if self.mql.doQuery(q):
	    for straw in self.mql.getPySheaf():
		for w in straw:
		    self.spin.next()
		    self.doWord(w)
	else:
	    exitOnError('query failed:\n%s' % q)

    def doWord(self, w):

##### SENTENCE ATOMS AND SENTENCES

	self.curr_sentence.appendPyObject(w)
	self.curr_sentence_atom.appendPyObject(w)

	if self.endOfSentenceAtom(w):
	    self.sentence_atoms.append(self.curr_sentence_atom)
	    self.curr_sentence_atom = PyObject(otype ='sentence_atom')

	if self.endOfSentence(w):
	    self.sentences.append(self.curr_sentence)
	    self.curr_sentence = PyObject(otype ='sentence')

##### ASIDES: --START AND END WITH DOUBLE HYPHENS LIKE THIS--

	if self.startOfAside(w):
	    if self.ASIDE_ON:
		warning("new aside starts while another aside is active:\n%s" %\
		             self.PyObjectSurface(self.curr_sentence))
		self.sub = PyObject(otype = "quote")
		self.sub.appendPyObject(w)
		self.curr_subquotes.append
	    self.curr_aside = PyObject(otype = 'aside')
	    self.curr_aside.appendPyObject(w)
	    self.ASIDE_ON = True

	elif self.ASIDE_ON:
	    self.curr_aside.appendPyObject(w)

	if self.endOfAside(w):
	    if self.ASIDE_ON: 
		self.asides.append(self.curr_aside)
		self.curr_aside = PyObject(otype = "aside")
		self.ASIDE_ON = False

##### QUOTES / DIRECT SPEECHES

	if self.startOfQuote(w):
	    quote = PyObject(otype = "quote")
	    self.curr_quotes.append(quote)
	for i in range(0, len(self.curr_quotes)):
	    self.curr_quotes[i].appendPyObject(w)

	if self.endOfQuote(w):
	    if len(self.curr_quotes) > 1:
		self.quotes.append(self.curr_quotes[-1])
		self.curr_quotes = self.curr_quotes[:-1]


    def endOfSentence(self, w):
	return re.search('[?!\.]', w['surface'])

    def endOfSentenceAtom(self, w):
	return self.endOfSentence(w) \
	   or re.search('[,;:]', w['surface']) \
	   or re.search('--$', w['surface'])

    def startOfQuote(self, w):
	return re.search("^[^%s]*‘" % alphabet, w['surface'])

    def endOfQuote(self, w):
	return re.search("’[^%s]*$" % alphabet, w['surface'])

    def startOfAside(self,w):
	return re.search("^--", w['surface'])

    def endOfAside(self, w):
	return re.search("--$", w['surface'])

    def PyObjectSurface(self, obj):
	surface = obj.sheaf[0][0]['surface']
	for straw in obj.sheaf[1:]:
	    surface += " %s" % straw[0]['surface']
	return surface


    def writeObjects(self, otype, obj_list):
	if obj_list == []:
	    return
	writeln('CREATE OBJECTS WITH OBJECT type [%s]\n' % otype, outstream=sys.stdout)
	for obj in obj_list:
	    #DEBUG(self.PyObjectSurface(obj))
	    writeln('CREATE OBJECT FROM MONADS = %s []\n' % \
	             obj.monads.toString(), outstream=sys.stdout)
	writeln('GO', outstream=sys.stdout)
	#DEBUG("<Enter>", pause=True)

    def output(self):
	self.writeObjects('sentence_atom', self.sentence_atoms)
	self.writeObjects('sentence', self.sentences)
	self.writeObjects('aside', self.asides)
	self.writeObjects('quote', self.quotes)

if __name__ == '__main__':
    options = Options()
    d = Delimiter(options)
    d.mainLoop()
    d.output()
