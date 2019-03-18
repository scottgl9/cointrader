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
	mkdir -p bin/tools
	cython tools/binance_simulate.py --embed
	cython tools/binance_simulate_tab_plot.py --embed
	x86_64-linux-gnu-gcc -O2 -I/usr/include/python2.7 -L/usr/lib/x86_64-linux-gnu tools/binance_simulate.c -o bin/tools/binance_simulate -lpython2.7
	x86_64-linux-gnu-gcc -O2 -I/usr/include/python2.7 -L/usr/lib/x86_64-linux-gnu tools/binance_simulate_tab_plot.c -o bin/tools/binance_simulate_tab_plot -lpython2.7
	cp -f asset_info.json bin/
	cp -f asset_detail.json bin/
	cp -rf cache bin/
	cp *.db bin/
	rm -f bin/binance_simulate.py

clean_build:
	rm -rf build

clean: clean_build
	find trader -type f -name '*.c' -not -path *native* -exec rm {} \;
	find trader -type f -name '*.pyc' -exec rm {} \;
	rm -rf bin
