#coding=utf-8

import sys
import re
import copy
import math
import string

from emdros_path import *
from emdros_application import *

alphabet = 'abcdefghijklmnopqrstuvwxyzðþæƿABCDEFGHIJKLMNOPQRSTUVWXYZÐÞÆ'


class TextImporter(EmdrosApplication):

    def __init__(self, options):
        EmdrosApplication.__init__(self, options, title="Old English Importer", DO_REF=False, DO_OUT=False, DO_LBL=False)
	self.documents = []
	self.chapters = []
	self.verses = []
	self.half_verses = []
	self.words = []
	self.monadSets = []
	self.curr_versenr        = 0
	self.curr_monad          = 0

	self.spin = Spinner()
	self.DBX = self.cfg.get('debug_mode')

	for self.document in self.cfg.get_multi('document'):
	    self.processDocument(self.document, self.cfg)


    def processDocument(self, document, cfg):
	writeln('importing document: %s' % document, outstream=sys.stderr)
	input = open(cfg.get('txt_file', document), 'r')
	abbr = cfg.get('abbr', document)
	if abbr is None:
	    abbr = document
	encoding = cfg.get('encoding', document)
	if encoding is None: encoding = 'utf-8'
	volume = cfg.get('volume', document)

	self.currDocument       = {'abbr' : abbr}
	self.currChapter            = {}
	self.currVerse          = {}
	self.currWord           = {}
	self.TEXTMODE           = False
	self.curr_versenr       = 0

	self.currDocName        = None
	self.currChapterName        = None

	# every document starts on the next round 1000 plus 1
	if cfg.get('start_docs_at_round_1000') and self.curr_monad > 1:
	    self.curr_monad =  int(math.ceil(self.curr_monad / 1000.0)) * 1000

	self.curr_monad += 1
	self.currDocument['first_monad'] = self.curr_monad
	self.TEXTMODE = False
	self.currChapter = {}

	for line in input:
	    line = re.sub("\n$", "", line).decode(encoding).encode('utf-8')
	    self.processLine(line, cfg)
	if self.currChapter:
	    self.storeChapter(self.currChapter, self.curr_monad)
	self.currDocument['last_monad'] = self.curr_monad  - 1
	self.documents.append(self.currDocument)
	self.monadSets.append((self.currDocument['abbr'],
	                       self.currDocument['first_monad'],
	                       self.currDocument['last_monad']))
	input.close()

    def storeChapter(self, chapter, curr_monad):
	    chapter['last_monad'] = curr_monad - 1
	    chapter['label'] = "%s %s" % (self.currDocument['abbr'], chapter['name'])
	    self.monadSets.append(("%s_%s" % (self.currDocument['abbr'],
	                                      chapter['name']), 
					      chapter['first_monad'],
					      chapter['last_monad']))
	    self.chapters.append(copy.deepcopy(chapter))

    def processLine(self, line, cfg):

	def initVerse(cfg):
	    self.TEXTMODE = True
	    if cfg.get('restart_verse_at_chapter', self.document):
		self.curr_versenr = 0

	DEBUG(line, dbx=self.DBX)

	if re.search("^[ \t]*$", line):
	    return

	# START OF DOCUMENT
	if re.search("^#[^#]", line):
	    initVerse(cfg)
	    self.currDocument['name'] = self.document #re.sub("^[ \t#]*", "", line)
	    self.currDocument ['first_monad'] = self.curr_monad

	elif re.search("^##[^#]", line): # START OF CHAPTER
	    self.currChapterName = re.sub("^[ \t#]*", "", line)
	    if self.currChapter.has_key('first_monad'):
		self.storeChapter(self.currChapter, self.curr_monad)
	    initVerse(cfg)
	    self.currChapter['document'] = self.currDocument['name']
	    self.currChapter['name'] = self.currChapterName
	    self.currChapter['first_monad'] = self.curr_monad

	elif self.TEXTMODE:
		self.processVerse(line, cfg)

	elif not self.TEXTMODE:               # COMMENT, not in TEXTMODE
	    if 'comment' not in self.currDocument.keys():
		self.currDocument['comment'] = [line]
	    else:
		self.currDocument['comment'].append(line)



    def processVerse(self, line, cfg):
	self.curr_versenr += 1
	currVerse = {'verse'      : self.curr_versenr,
	             'first_monad': self.curr_monad,
		    'document'    : self.currDocument['name'] }
	currVerse['label'] = self.currDocument['abbr']
	if self.currChapterName is not None:
	    currVerse['chapter'] = self.currChapterName
	    currVerse['label'] += ' ' + self.currChapterName
	currVerse['label'] += ' ' + str(self.curr_versenr)
	half_verses = re.split("[ ]*\/[ ]*", line)

	self.curr_half_verse = 0
	for hv in half_verses:
	    self.processHalfVerse(hv, cfg)

	currVerse['last_monad'] = self.curr_monad - 1
	self.verses.append(currVerse)


    def processHalfVerse(self, half_verse, cfg):
	self.curr_half_verse += 1
	currHalfVerse = {'half_verse': self.curr_half_verse,
	                 'verse'      : self.curr_versenr,
			 'first_monad': self.curr_monad,
			'document'    : self.currDocument['name'] }
	words = re.split(" ", half_verse)
	for w in words:
	    self.processWord(w, cfg)
	currHalfVerse['last_monad'] = self.curr_monad - 1 
	self.half_verses.append(currHalfVerse)

    def processWord(self, w, cfg):
	if self.DBX:
	    DEBUG('%s %s' %(w, self.curr_monad), outstream=sys.stderr)
	else:
	    self.spin.next()
	w = re.sub("^(?P<xxx>[^%s]*)'" % alphabet, "\g<xxx>‘", w)
	w = re.sub("'(?P<xxx>[^%s]*)$" % alphabet, "’\g<xxx>", w)
	#re.sub("^'", u'\N{LEFT SINGLE QUOTATION MARK}'.encode('utf-8'), w)
	#re.sub("'$", u'\N{RIGHT SINGLE QUOTATION MARK}'.encode('utf-8'), w)

	currWord = {}
	currWord['first_monad'] = self.curr_monad
	currWord['last_monad']  = self.curr_monad
	currWord['surface'] = w
	currWord['graphemes'] = self.toGraphemes(w)
	currWord['ascii_txt'] = self.toASCII(w)
	currWord['latex_txt'] = self.toLaTeX(w)
	DEBUG(currWord, dbx=self.DBX)
	if currWord['surface']:
	    self.words.append(currWord)
	self.curr_monad += 1


    def toGraphemes(self, w):
	if self.cfg.get('uppercase_graphemes'):
	    return self.toupper(self.stripped(w))
	else:
	    return self.tolower(self.stripped(w))

    def toASCII(self, w):
	r = self.stripped(w)
        r = re.sub(u'\N{LATIN CAPITAL LETTER AE}'.encode('utf-8'), 'AE', r)
        r = re.sub(u'\N{LATIN SMALL LETTER AE}'.encode('utf-8'), 'ae', r)
	r = re.sub(u'\N{LATIN CAPITAL LETTER ETH}'.encode('utf-8'), 'DH', r)
	r = re.sub(u'\N{LATIN SMALL LETTER ETH}'.encode('utf-8'), 'dh', r)
	r = re.sub(u'\N{LATIN CAPITAL LETTER THORN}'.encode('utf-8'), 'TH', r)
	r = re.sub(u'\N{LATIN SMALL LETTER THORN}'.encode('utf-8'), 'th', r)
	return r

    def toLaTeX(self, w):
	r = self.stripped(w)
        r = re.sub(u'\N{LATIN CAPITAL LETTER AE}'.encode('utf-8'), '{\\\\AE}', r)
        r = re.sub(u'\N{LATIN SMALL LETTER AE}'.encode('utf-8'), '{\\\\ae}', r)
	r = re.sub(u'\N{LATIN CAPITAL LETTER ETH}'.encode('utf-8'), '{\\DH}', r)
	r = re.sub(u'\N{LATIN SMALL LETTER ETH}'.encode('utf-8'), '{\\dh}', r)
	r = re.sub(u'\N{LATIN CAPITAL LETTER THORN}'.encode('utf-8'), '{\\\\TH}', r)
	r = re.sub(u'\N{LATIN SMALL LETTER THORN}'.encode('utf-8'), '{\\\\th}', r)
	return r

    def stripped(self, w):
	r = re.sub('Ā', 'A', w)
	r = re.sub('ā|â', 'a', w)
	r = re.sub('ċ', 'c', r)
	r = re.sub('Ē', 'E', r)
	r = re.sub('ē|ê|ĺ', 'e', r)
	r = re.sub('Ġ', 'G', r)
	r = re.sub('ġ', 'g', r)
	r = re.sub('ī|Ľ', 'i', r)
	r = re.sub('Ō|Ő', 'O', r)
	r = re.sub('ō|ô|ő|ľ', 'o', r)
	r = re.sub('Ū', 'U', r)
	r = re.sub('ū', 'u', r)
	r = re.sub('ȳ|ŷ', 'y', r)

	r = re.sub('Ǣ', u'\N{LATIN CAPITAL LETTER AE}'.encode('utf-8'), r)
	r = re.sub('ǣ', 'æ', r)

	r = re.sub('[^%s]' % alphabet, '', r)

	return r

    def toupper(self, r):
	r = re.sub('æ', u'\N{LATIN CAPITAL LETTER AE}'.encode('utf-8'), r)
	r = re.sub('ð', u'\N{LATIN CAPITAL LETTER ETH}'.encode('utf-8'), r)
	r = re.sub('þ', u'\N{LATIN CAPITAL LETTER THORN}'.encode('utf-8'), r)
	return r.upper()

    def tolower(self, r):
	r = re.sub(u'\N{LATIN CAPITAL LETTER AE}'.encode('utf-8'), 'æ', r)
	r = re.sub(u'\N{LATIN CAPITAL LETTER ETH}'.encode('utf-8'), 'ð', r)
	r = re.sub(u'\N{LATIN CAPITAL LETTER THORN}'.encode('utf-8'), 'þ', r)
	return r.lower()

    def dump(self):
	print("documents")
	for obj in self.documents:
	    print(obj)
	print

	print("chapters")
	for obj in self.chapters:
	    print(obj)
	print

	print("verses")
	for obj in self.verses:
	    print(obj)
	print

	print("half_verses")
	for obj in self.half_verses:
	    print(obj)
	print

	print("words")
	for obj in self.words:
	    print(obj)
	print

    
    def createObjects(self, objList, objType, featName = None):
	def fVal(obj, val):
	    try: 
		if type(obj[val]) == str:
		    return '"%s"' % obj[val]
		else:
		    return repr(obj[val])
	    except:
		return None

	if not objList:
	    return
	q = "CREATE OBJECTS WITH OBJECT TYPE [%s]\n" % objType
	for obj in objList:
	    if obj['first_monad'] == obj['last_monad']:
		monad_string = "{%d}" % obj['first_monad']
	    else:
		monad_string = "{%d-%d}" % \
		(obj['first_monad'], obj['last_monad'])
	    q +=  "CREATE OBJECT FROM MONADS = %s [\n" % monad_string
	    if type(featName) in (list, tuple):
		for f in featName:
		    val = fVal(obj,f)
		    if val is not None:
			q += "    %s:=%s;\n" % (f, val)
		else:
		    val = fVal(obj,featName)
		    if val is not None:
			q +=  "    %s:=%s;\n" % (featName, val)
	    q +=  "]\n"
	q += "GO\n"
	print q
	DEBUG(q, dbx=self.DBX)


    def outputMQL(self):
	for line in open(self.cfg.get("schema_file"), "r"):
	    print re.sub("\n$", "", line)
	print
	print

	self.createObjects(self.documents, 'Document', ('name', 'abbr'))
	self.createObjects(self.chapters, 'Chapter', ('name', 'document', 'label'))
	self.createObjects(self.verses, 'Verse', ('document', 'chapter', 'verse', 'label'))
	self.createObjects(self.half_verses, 'Half_verse', ('document', 'chapter', 'verse', 'half_verse'))
	self.createObjects(self.words, 'Word', ('surface', 'graphemes', 'ascii_txt', 'latex_txt'))

	print
	DEBUG("", dbx=self.DBX)
	for ms in self.monadSets:
	    print "CREATE MONAD SET %s WITH MONADS = {%d-%d} GO" % \
		    (ms[0], ms[1], ms[2])
	    DEBUG("CREATE MONAD SET %s WITH MONADS = {%d-%d} GO" % \
		    (ms[0], ms[1], ms[2]), dbx=self.DBX)



if __name__ == '__main__':

    options = Options()
    options.set('kernel', 'oldenglish')
    tImp = TextImporter(options=options)
    tImp.outputMQL()
