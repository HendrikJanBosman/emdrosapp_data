DOC = lamentoj
ABBR = Lam

all: $(DOC) postproc sentences labels backup

$(DOC): $(DOC).txt
	plaintextimport -s -d $(DOC) $(DOC).txt > $(DOC).schema;
	plaintextimport -d $(DOC) $(DOC).txt -o $(DOC).mql;
	cat $(DOC).schema $(DOC).mql $(DOC).pros_units.mql | mql
	touch .data
    
postproc: .data
	python postproc.py $(DOC) $(DOC) $(ABBR)
	touch .postproc

sentences: .postproc
	labelman -k esperanto -d $(DOC) -m graphical word
	python sentences.py $(DOC)
	touch .sentences

labels: .sentences
	labelman -k esperanto -d $(DOC) -sa
	touch .labels

new: clean all

clean:
	touch $(DOC) $(DOC).schema $(DOC).mql .data .postproc .labels;
	rm $(DOC) $(DOC).schema $(DOC).mql .data .postproc .labels

backup:
	mqldump --batch-create-objects $(DOC) > $(DOC).`date +%y_%m_%d`.mql; 
	mqldump -n $(DOC) colon verseline strophe > $(DOC).pros_units.`date +%y_%m_%d`.mql;
	touch $(DOC).pros_units.mql; rm $(DOC).pros_units.mql;
	cp $(DOC).pros_units.`date +%y_%m_%d`.mql $(DOC).pros_units.mql

