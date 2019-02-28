# bhebrew : data files for a Biblical Hebrew databases

In order for this repo to work with the programs in **emdrosapp_src**,
the file **bhebrew.py** must exist in the directory
**emdrosapp_src/emdros_application/syscfg**, and must be edited so that
it correctly lists the path names to the directories below:

## directories
* **data**: contains **threni_hjb.YY.MM.DD.mql**, latest MQL dump of the database used in my 
    PhD research. Run through *mql* to recreate the database. If you use an SQLite backend,
    this must be done from within the data directory, so the database ends up there.

* **config**: Configuration files for the various linguistic modes. Best left alone,
              unless you know what you are doing.

* **lbl**: Definitions of the descriptive labels assigned by **labelman**, in the form of MQL queries.
The user can alter and expand these files to assign other labels, or change the definitions of 
existing ones. See the repo emdrosapp_doc for a more detailed description of
*labelman* and lbl-files.


