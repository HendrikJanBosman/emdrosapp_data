#data files for Old English

## creating the database from the MQL dump
Run **mql -b 3 oldenglish.mql** to create the database.
this creates the database file *oldenglish* in this directory.

## creating the database from scratch
Run **make**
to produce the database from scratch
from the files in the **texts** subdirectory.
Do this when you have added or edited documents there.
When **adding a document**, make sure it
gets its own stanza at the appropriate position in **oldenglish.corpus.cfg**.

## updating descriptive labels
After you have edited a label definition file in *../lbl*, do one or more of
the following:

* labelman -d oldenglish -m -a graphical

* labelman -d oldenglish -m -a lexical

* labelman -d oldenglish -m -a syntactic

* labelman -d oldenglish -m -a prosodic

