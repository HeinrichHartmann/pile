CNAME=docker.heinrichhartmann.net/pile

start:
	poetry install
	poetry run python -c 'from pile import srv; srv.main()'

dist:
	poetry build

clean:
	rm -r dist

install: dist
	cd dist; pip install *.whl

.PHONY: test
test:
	poetry run bash test.sh

image: dist
	docker build . --tag ${CNAME}
	docker tag ${CNAME} pile
	docker push ${CNAME}
