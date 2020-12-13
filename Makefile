CNAME=docker.heinrichhartmann.net:5000/pile

run:
	poetry install
	poetry run python -c 'from pile import src; srv.main()'

dist:
	poetry build

clean:
	rm -r dist

install: dist
	cd dist; pip install *.whl

test:
	poetry run bash test.sh

image: dist
	docker build . --tag ${CNAME}
	docker tag  ${CNAME} pile

push:
	docker push ${CNAME}
