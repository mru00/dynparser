.PHONY: test

test:
	$(MAKE) -C test test

dist:
	rm -rf dist
	mkdir -p dist/dynparser
	cp ./src/dynparser/*.py dist/dynparser
	cd dist && tar czf dynparser.tar.gz dynparser
