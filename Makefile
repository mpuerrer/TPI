all:
	python setup.py build_ext --inplace

install-user:
	python setup.py build_ext install --user
	
check:
	pytest test.py -s

sdist:
	python setup.py sdist

clean:
	-rm -r build TPI.c TPI.so

