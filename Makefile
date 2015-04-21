all: cython
	$(MAKE) -C pokeher

cython:
	python setup.py build_ext --inplace
	cp pokeher/utility.py arena
	cp pokeher/utility.py standalone

test: all
	nosetests

zipfile: test
	zip -r bot.zip data/ pokeher/

clean:
	rm -r bot.zip
	rm -rf build
	$(MAKE) clean -C pokeher
