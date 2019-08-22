all: tmp

trades: tmp
	tmp/readme.md

tmp:
	mkdir -p tmp

tmp/readme.md:
	./cerberus.py | tee tmp/readme.md
	echo Generated $(shell date) > tmp/readme.md

deploy:
	mv tmp/readme.md readme.md
