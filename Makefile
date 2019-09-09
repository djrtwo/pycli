SPEC_DIR = ./eth2.0-specs

.PHONY: clean pyspec

all: pyspec

clean:
	cd $(SPEC_DIR) && $(MAKE) clean

pyspec:
	cd $(SPEC_DIR) && $(MAKE) pyspec

build: pyspec
	python3 -m venv venv; . venv/bin/activate; pip3 install -r requirements.txt
