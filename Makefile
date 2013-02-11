test: all
	nosetests

all:
	$(MAKE) -C pokeher

clean:
	$(MAKE) clean -C pokeher
