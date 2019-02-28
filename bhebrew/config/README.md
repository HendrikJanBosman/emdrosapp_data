# config - confguration files for emdros_application based programs

These files are meant to initiate a *Configuration* object
(in the emdros_application.utils package); they configure an EmdrosApplication
object for Biblical Hebrew with ETCBC style data.


##files
* **bhebrew.cfg**: This is the master configuration file, which sets some
  global options and points to the configuration files for the different 
  linguistic modes:

* **mode configuration files**: These files determine various mode-dependent 
settings, such as the object types relevant to the mode (and their natural 
hierarchy), and the JSON files used to display text in this mode. The files are:

    * bhs4.graphical.cfg 

    * bhs4.lexical.cfg 

    * bhs4.participants.cfg 

    * bhs4.prosodic.cfg 

    * bhs4.syntactic.cfg

* **json**: This directory contains JSON files which determine the output of
  programs using the *emdros_application.output.OutputManager*. You can add your  own files here. Make sure they are pointed to in the appropriate mode
  configuration files (or passed as the -j option to a program).


* **domains**: This directory contains MQL retrieval queries, which are written
  to retrieve specific subcorpora of the database (e.g. poetry; acrostic lines).
    If one of these files is passed to a program by the -q option, that program
    will only operate on the subcorpus specified in it.
    You can write your own domain files; if you do, put them in this directory
    so they can be found.

* **emdrostools**: This directory contains some configuration files for the
Emdros Query Tools (*eqtu* or *etqc*).
