install:
	python3 setup.py install

lint:
	pylint pile.py

test: install
	bash test.sh

demo: install
	cd ~/Documents && pile table

demo-cgi: install
	curl -s 'http://localhost:8888/Documents/pile.cgi?ACTION=env' | jq .
	curl -s 'http://localhost:8888/Documents/pile.cgi?ACTION=args&hello=1&world=2' | jq .
	curl -s 'http://localhost:8888/Documents/pile.cgi?ACTION=list' | jq .
	curl -s 'http://localhost:8888/Stack/.pile.cgi?ACTION=stack&n=3' | jq .
