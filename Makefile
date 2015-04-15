all: cython
	$(MAKE) -C pokeher

cython:
	python setup.py build_ext --inplace

test: all
	nosetests

zipfile: all
	zip -r bot.zip data/ pokeher/

clean:
	$(MAKE) clean -C pokeher
