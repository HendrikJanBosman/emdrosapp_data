# emdrosapp_data

The data and configuration files which provide the databases
for the programs in the **emdrosapp_src** repo.

Also contains some 
Python 2.7 / EmdrosPy data import tools, which will need some tweaking
of path names etc. to run on other systems than my own.

## modules

* **bhebrew** is for Biblical Hebrew (ETCBC / bhs4 type databases).
  It presently only contains *threni_hjb*, the database of Lamentations
  I have compiled and used in my PhD research.
  It contains numerous additions to the underlying ETCBC data.

* **oldenglish** is an experimental database of some Anglo-Saxon texts. 
  Since I do not read Anglo-Saxon myself, the database merely serves as an 
  example of the appliccability of my programs to other languages,
  and has no linguistic prentensions.

* **esperanto** at present only provides the database *lamentoj*, an Esperanto
  version of the book of Lamentations. Again, it has no linguistic pretensions,
  but serves as an example, especially of how the program *labelman* can be 
  used to do morphological word parsing in a language with strong morphology.

