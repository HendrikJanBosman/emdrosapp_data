import sys
import re
sys.path.append('../../../emdrosapp_src')
from emdros_application.mql_engine import *

verse_label_pattern = "^[0-9]+:[0-9]+"
stripped_label_pattern = "^[0-9]+"


class SentenceDelimiter:

    def __init__(self, database):
	import importlib
	self.spin = Spinner()
	kernel = importlib.import_module('emdros_application.syscfg.esperanto')

	self.mql = MQLEngine(database = database, kernel = kernel)
	self.mql.doQuery("USE DATABASE %s GO" % database) 
	self.mql.createObjectType('sentence')
	self.mql.createObjectType('clause_atom')

	self.mql.doQuery("SELECT ALL OBJECTS WHERE [word get surface, graphical_labels] GO")
	initial_words = self.mql.getPySheaf().flatten()

	self.clause_atoms     = []
	self.clause_atom_txt  = ""
	self.sentences   = []
	self.sentence_txt  = ""
	self.doSentences()


    def doSentences(self):
	q = "SELECT ALL OBJECTS WHERE [word get surface] GO"
	self.mql.doQuery(q)
	curr_sentence = PyObject(otype = "sentence")
	curr_clause_atom = PyObject(otype = "clause_atom", monads=SetOfMonads())
	for straw in self.mql.getPySheaf():
	    for word in straw:
		curr_clause_atom.appendPyObject(word)	
		self.clause_atom_txt   += "%s " % word["surface"]
		self.sentence_txt += "%s " % word["surface"]
		if word['surface'][-1] in ".,;:!?":
		    self.mql.storeObject(curr_clause_atom)
		    self.clause_atom_txt = ""
		    curr_sentence.appendPyObject(curr_clause_atom)
		    curr_clause_atom = PyObject(otype = "clause_atom", monads=SetOfMonads())
		if word['surface'][-1] in ".;:!?":
		    self.mql.storeObject(curr_sentence)
		    curr_sentence = PyObject(otype = "sentence", monads = SetOfMonads())
		    self.sentence_txt = ""
	curr_clause_atom.appendPyObject(word)	
	curr_sentence.appendPyObject(curr_clause_atom)
	


	

if __name__ == '__main__':
    if len(sys.argv) < 2:
	sys.stderr.write("usage: python dosentence.py <database>\n")
	quit()
    pp = SentenceDelimiter(sys.argv[1])
