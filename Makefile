PY?=python3

SRC=totp.py totp.ini LICENSE

.PHONY: pkg clean

pkg: dist dist/Totp.keypirinha-package

dist:
	mkdir -p dist

lib: requirements.txt
	mkdir -p lib
	$(PY) -m pip install -U --target lib -r requirements.txt

%.keypirinha-package: lib $(SRC)
	zip -r $@ $^ -x 'bin/*' 'share/*' '*/tests/*' '*/__pycache__/*' '*.dist-info/*'

clean:
	rm -rf lib dist
