# Label definition files

The files in this directory are to be parsed and applied by the progam
*labelman* (emdrosapp_src repo). They are basically lists of labels
(on a separate line, marked by **//#**), followed by a list of MQL queries
that describe all text patterns to which a label is thought to apply.

## notes:
* The *.lbl files are organized according to linguistic mode and object type.
Each sensible combination of mode and type has its own file.
* Each query must describe **exactly one** object of the given type.
* Alternatively, the query must contain exactly one object with the **FOCUS**
  keyword of the given type. This can be used to specify the larger context
  of an object.
* As soon as a label has been defined,
  it can be used in any other label definitions, even in other *.lbl, provided
  these are parsed *after* this one. As a rule, files are parsed in *ascending*
  textual order, so: word - phrase - clause etc.
