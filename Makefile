all:
	python setup.py build_ext -i
	
check:
	pytest test.py -s

sdist:
	python setup.py sdist

clean:
	-rm -r build TPI.c TPI.so

