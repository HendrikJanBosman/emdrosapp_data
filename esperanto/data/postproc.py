#encoding=utf-8
import sys
import re
sys.path.append('../../../emdrosapp_src')
from emdros_application.mql_engine import *

verse_label_pattern = "^[0-9]+:[0-9]+"
stripped_label_pattern = "^[0-9]+"


class PostProcessor:

    def __init__(self, database, book_name, book_abbr):
	import importlib
	self.spin = Spinner()
	self.book = book_name
	self.abbr = book_abbr
	kernel = importlib.import_module('emdros_application.syscfg.esperanto')

	self.mql = MQLEngine(database = database, kernel = kernel)
	self.mql.doQuery("USE DATABASE %s GO" % database) 
	self.createObjects()

	self.mql.doQuery("SELECT ALL OBJECTS WHERE [word get surface,stripped_surface] GO")
	initial_words = self.mql.getPySheaf().flatten()

	self.words    = []
	self.chapters = []
	self.verses   = []

	self.last_label = None
	self.start_of_verse = None

	for word in initial_words:
	    self.spin.next()
	    self.mql.updateObject(self.doWord(word))
	self.doVerse(word, forced=True)
	self.doChapters()


    def doWord(self, word):

	def asc2utf8(str):
	    ret = copy.deepcopy(str)
	    ret = re.sub("cx", "ĉ", ret)
	    ret = re.sub("gx", "ĝ", ret)
	    ret = re.sub("hx", "ĥ", ret)
	    ret = re.sub("jx", "ĵ", ret)
	    ret = re.sub("sx", "ŝ", ret)
	    ret = re.sub("ux", "ŭ", ret)

	    ret = re.sub("CX", "Ĉ", ret)
	    ret = re.sub("GX", "Ĝ", ret)
	    ret = re.sub("HX", "Ĥ", ret)
	    ret = re.sub("JX", "Ĵ", ret)
	    ret = re.sub("SX", "Ŝ", ret)
	    ret = re.sub("UX", "Ŭ", ret)

	    return ret

	def asc2latex(str):
	    ret = copy.deepcopy(str)
	    ret = re.sub("cx", "\\^{c}", ret)
	    ret = re.sub("gx", "\\^{g}", ret)
	    ret = re.sub("hx", "\\^{h}", ret)
	    ret = re.sub("jx", "\\^{\\j}", ret)
	    ret = re.sub("sx", "\\^{s}", ret)
	    ret = re.sub("ux", "\\u{u}", ret)

	    ret = re.sub("CX", "\\^{C}", ret)
	    ret = re.sub("GX", "\\^{G}", ret)
	    ret = re.sub("HX", "\\^{H}", ret)
	    ret = re.sub("JX", "\\^{J}", ret)
	    ret = re.sub("SX", "\\^{S}", ret)
	    ret = re.sub("UX", "\\u{U}", ret)

	    return ret

	def utf82asc(str): # NB: BUG, DOES NOTHING, USED WORKAROUND
	    ret = copy.deepcopy(str)
	    ret = re.sub(u"ĉ", "cx", ret)
	    ret = re.sub(u"ĝ", "gx", ret)
	    ret = re.sub(u"ĥ", "hx", ret)
	    ret = re.sub(u"ĵ", "jx", ret)
	    ret = re.sub(u"ŝ", "sx", ret)
	    ret = re.sub(u"ŭ", "ux", ret)

	    ret = re.sub(u"Ĉ", "CX", str)
	    ret = re.sub(u"Ĝ", "GX", ret)
	    ret = re.sub(u"Ĥ", "HX", ret)
	    ret = re.sub(u"Ĵ", "JX", ret)
	    ret = re.sub(u"Ŝ", "SX", ret)
	    ret = re.sub(u"Ŭ", "UX", ret)

	    return ret

	surface = copy.deepcopy(word['surface'])
	stripped_surface = copy.deepcopy(word['stripped_surface'])

	if re.match(verse_label_pattern, surface):
	    self.doVerse(word)
	    surface = re.sub(verse_label_pattern, "", surface)
	    stripped_surface = re.sub(stripped_label_pattern, "", stripped_surface)
	surface_asc          = utf82asc(surface)
	surface              = asc2utf8(surface)
	graphemes            = stripped_surface.lower()
	graphemes_asc        =  utf82asc(graphemes)
	graphemes            =  asc2utf8(graphemes)
	stripped_surface_asc = utf82asc(stripped_surface)
	stripped_surface     = asc2utf8(stripped_surface)

	surface_ltx          = asc2latex(surface_asc)
	stripped_surface_ltx = asc2latex(stripped_surface_asc)
	graphemes_ltx        = asc2latex(graphemes_asc)

	word['surface']              = '"%s"' % surface
	word['surface_ascii']        = '"%s"' % surface_asc
	word['surface_latex']        = '"%s"' % surface_ltx
	word['graphemes']            = '"%s"' % graphemes
	word['graphemes_ascii']      = '"%s"' % graphemes_asc
	word['graphemes_latex']      = '"%s"' % graphemes_ltx
	word['stripped_surface']     = '"%s"' % stripped_surface
	word['stripped_surface_ascii'] = '"%s"' % stripped_surface_asc
	word['stripped_surface_latex'] = '"%s"' % stripped_surface_ltx

	return word	



    def doVerse(self, word, forced=False):
	label = re.sub("(?P<lbl>%s).*" % verse_label_pattern,
	                "\g<lbl>", word['surface'])
	if forced or (self.start_of_verse is not None):
	    end_of_last_verse = word.monads.last() - 1
	    new_mon = SetOfMonads(self.start_of_verse, end_of_last_verse)
	    verse = PyObject(otype="verse", monads=new_mon)
	    verse['book']   = '"%s"' % self.book
	    verse['abbr']   = '"%s"' % self.abbr
	    verse['label']   = '"%s"' % self.last_label
	    verse['chapter'] = int(re.sub(":.*$", "", self.last_label))
	    verse['verse']   = int(re.sub("^[0-9]+:", "", self.last_label))
	    self.mql.storeObject(verse)
	self.last_label = label
	self.start_of_verse = word.monads.first()


    def doChapters(self):
	def makeChapter(curr_mon, curr_chapter):
	    chapter = PyObject(otype="chapter", monads=curr_mon)
	    chapter['book']   = '"%s"' % self.book
	    chapter['abbr']   = '"%s"' % self.abbr
	    chapter['chapter'] = curr_chapter
	    self.mql.storeObject(chapter)
	    self.mql.createNamedMonadSet("%s_%d" % (self.abbr, curr_chapter),
	                                 curr_mon)
	     

	q = "SELECT ALL OBJECTS WHERE [verse get chapter] GO"
	self.mql.doQuery(q)
	curr_chapter = None
	curr_mon = SetOfMonads()
	for straw in self.mql.getPySheaf():
	    for verse in straw:
		if (curr_chapter is not None and verse['chapter'] != curr_chapter):
		    makeChapter(curr_mon, curr_chapter)
		    curr_mon = SetOfMonads()
		curr_mon.unionWith(verse.monads)
		curr_chapter = verse['chapter']
	makeChapter(curr_mon, curr_chapter)
		
    def doSentences(self):
	q = "SELECT ALL OBJECTS WHERE [word get surface] GO"
	self.mql.doQuery(q)
	curr_sentence = PyObject(otype = "sentence", monads = SetOfMonads())
	curr_clause = PyObject(otype = "clause, monads = SetOfMonads()")
	for straw in self.mql.getPySheaf():
	    for word in straw:
		curr_clause.monads.unionWith(word.monads)
		if word['surface'][-1] in ".,;:!?":
		    DEBUG(curr_clause)
		    curr_sentence.appendPyObject(curr_clause)
		    curr_clause = PyObject(otype = "clause, monads = SetOfMonads()")
		if word['surface'][-1] in ".!?":
		    DEBUG(curr_sentence)


	

    def createObjects(self):
	self.mql.createObjectType('chapter')
	self.mql.createObjectFeature('chapter', 'book', 'string')
	self.mql.createObjectFeature('chapter', 'abbr', 'string')
	self.mql.createObjectFeature('chapter', 'chapter', 'integer')

	self.mql.createObjectType('verse')
	self.mql.createObjectFeature('verse', 'book', 'string')
	self.mql.createObjectFeature('verse', 'abbr', 'string')
	self.mql.createObjectFeature('verse', 'chapter', 'integer')
	self.mql.createObjectFeature('verse', 'verse', 'integer')
	self.mql.createObjectFeature('verse', 'label', 'string')

	self.mql.createObjectFeature("word","graphemes", "string")
	self.mql.createObjectFeature("word","graphemes_ascii", "string")
	self.mql.createObjectFeature("word","graphemes_latex", "string")
	self.mql.createObjectFeature("word","surface_ascii", "string")
	self.mql.createObjectFeature("word","surface_latex", "string")
	self.mql.createObjectFeature("word","stripped_surface_ascii", "string")
	self.mql.createObjectFeature("word","stripped_surface_latex", "string")

if __name__ == '__main__':
    if len(sys.argv) < 4:
	sys.stderr.write("usage: python postproc.py <database> <bookname> <abbr>\n")
	quit()
    pp = PostProcessor(sys.argv[1], sys.argv[2], sys.argv[3])
