all: cython
	$(MAKE) -C pokeher

cython:
	python setup.py build_ext --inplace
	cp pokeher/utility.py arena
	cp pokeher/utility.py standalone
	cp pokeher/utility.py agents

test: all
	nosetests

gauntlet: all
	python arena/gauntlet.py pokeher/theaigame_bot.py

zipfile: test
	zip -r bot.zip data/ pokeher/

clean:
	rm -f bot.zip
	rm -rf build
	$(MAKE) clean -C pokeher
