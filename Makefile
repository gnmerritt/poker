all: cython
	$(MAKE) -C pokeher

cython:
	python setup.py build_ext --inplace

test: all
	nosetests

clean:
	$(MAKE) clean -C pokeher
