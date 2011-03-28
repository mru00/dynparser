.PHONY: test dist doc

doc:
	$(MAKE) -C doc doc 

test:
	$(MAKE) -C test test

dist:
	git diff --quiet HEAD || ( echo "uncommited changes; abort"; exit 1; )
	rm -rf dist
	mkdir -p dist/dynparser
	(git rev-parse --verify HEAD; date) > dist/dynparser/VERSION
	cp ./src/dynparser/*.py dist/dynparser
	cd dist && tar czf dynparser.tar.gz dynparser
