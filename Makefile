
BINPATH := /usr/bin

install:
	python setup.py install	
	echo "BINPATH=\"$(BINPATH)\"" > $(BINPATH)/msre.conf
	cp msre $(BINPATH)/.
	cp msr.py $(BINPATH)/.

clean:
	-rm msr_ensemble/*.pyc
	-rm msr_ensemble/context/*.pyc
	-rm msr_ensemble/facts/*.pyc
	-rm msr_ensemble/front_end/*.pyc
	-rm msr_ensemble/front_end/compile/*.pyc
	-rm msr_ensemble/front_end/compile/checkers/*.pyc
	-rm msr_ensemble/front_end/compile/transformers/*.pyc
	-rm msr_ensemble/front_end/parser/*.pyc
	-rm msr_ensemble/interpret/*.pyc
	-rm msr_ensemble/misc/*.pyc
	-rm msr_ensemble/python/*.pyc
	-rm msr_ensemble/rules/*.pyc
	-rm *.log
	-rm *.out
	-rm *.pyc
	-rm -r build

