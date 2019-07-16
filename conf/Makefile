YAM = ../yang-modules
YANGLIB = ../jetconf_knot/yang-library-data.json
INST = data-nacmonly.json
.PHONY: validate

validate:
	@yangson -p $(YAM) $(YANGLIB) -v $(INST)
