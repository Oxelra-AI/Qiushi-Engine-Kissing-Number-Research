PYTHON ?= python3
OUTPUT ?= ../kissing-verification-$(shell date +%Y%m%d-%H%M%S)

.PHONY: list verify test integrity paper source-paper reports reports-en reports-zh reports-full source-en source-zh source-full-en source-full-zh
list:
	$(PYTHON) -B tools/reproduce.py --list
verify:
	$(PYTHON) -B tools/reproduce.py --suite all --output "$(OUTPUT)"
test:
	$(PYTHON) -B -m unittest discover -s tests -v
integrity:
	$(PYTHON) -B tools/check_package.py
paper:
	cd paper && latexmk -xelatex -interaction=nonstopmode -halt-on-error -outdir=../build/paper main.tex
	cp build/paper/main.pdf paper/main.pdf
source-paper: paper
	$(PYTHON) -B tools/package_paper.py
reports:
	$(PYTHON) -B tools/build_reports.py --language all
reports-en:
	$(PYTHON) -B tools/build_reports.py --language en
reports-zh:
	$(PYTHON) -B tools/build_reports.py --language zh
reports-full:
	$(PYTHON) -B tools/build_reports.py --edition complete --language all
source-en:
	$(PYTHON) -B tools/package_reports.py --language en
source-zh:
	$(PYTHON) -B tools/package_reports.py --language zh
source-full-en:
	$(PYTHON) -B tools/package_reports.py --edition complete --language en
source-full-zh:
	$(PYTHON) -B tools/package_reports.py --edition complete --language zh
