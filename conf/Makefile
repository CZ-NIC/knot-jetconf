YAM = ../yang-modules
YANGLIB = ../jetconf_knot/yang-library-data.json
INST = example-data-nacm.json
.PHONY: validate

validate:
	@yangson -p $(YAM) $(YANGLIB) -v $(INST)
