DB = oldenglish
MQL = $(DB).mql

EMDROS_SRC = ../../../emdrosapp_src
LABELMAN   = $(EMDROS_SRC)/labelman.py

SRC        = ../src
IMPORT     = $(SRC)/OldEnglishImporter.py
DELIMIT    = $(SRC)/delimit.py 
ARGS = -k oldenglish -d $(DB)

SCHEMA   = $(DB).schema
CORPUS_CFG = $(DB).corpus.cfg
TODAYS_BACKUP=$(DB).`date +%y_%m_%d`.mql

### MAIN TARGETS ####
all: reload

database: $(DB) 

reload:
	make db_clean; make database wordgrammar labels backup

$(DB): $(CORPUS_CFG) .texts
	make db_clean;
	python $(IMPORT) $(ARGS) -c $(CORPUS_CFG) | mql -b s3; 
	$(DELIMIT) $(ARGS) | mql -d $(DB); touch .delimit

wordgrammar: .wordgrammar

labels: .labels

texts: .texts

backup: .backup

### HELPER TARGETS #####
.texts:
	cd originals; make
	cd ..;
	touch .texts

.wordgrammar: .delimit
	$(LABELMAN) $(ARGS) -m graphical word;
	$(LABELMAN) $(ARGS) -m lexical word;
	$(LABELMAN) $(ARGS) -m morphological word;
	touch .wordgrammar

.labels: .wordgrammar
	$(LABELMAN) $(ARGS) -m syntactic -a;
	$(LABELMAN) $(ARGS) -m prosodic -a;
	touch .labels

.backup: .labels
	mqldump -u hjb --batch-create-objects $(DB) > $(TODAYS_BACKUP)
	cp $(TODAYS_BACKUP) $(DB).mql
	touch .backup


### GENERAL TARGETS ####

db_clean:
	touch $(DB); rm $(DB);

clean:
	make db_clean;
	touch *.txt labelman.log;
	rm *.txt labelman.log;
	touch .texts .data .wordgrammar .delimit .labels .backup;
	rm .texts .data .wordgrammar .delimit .labels .backup

new:
	make clean; cd originals; make; cd ..; make all
