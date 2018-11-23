all:
	python compile.py build
	rm -rf lib
	python compile.py install --prefix=./
	find ./lib -type f -name '*.py*' -exec rm {} \;
	mkdir -p bin
	cp -rf lib/python2.7/site-packages/trader bin/
	rm -rf lib
	find bin/trader -type d -exec touch {}/__init__.py \;
	cp -f trader/strategy/trade_size_strategy/__init__.py bin/trader/strategy/trade_size_strategy/__init__.py
	cp -f tools/binance_simulate.py bin/
	cp *.db bin/

clean:
	find trader -type f -name '*.c' -exec rm {} \;
	find trader -type f -name '*.pyc' -exec rm {} \;
	rm -rf build
	rm -rf bin
