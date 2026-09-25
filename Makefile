PYTHON ?= python3
OUTPUT ?= ../kissing-verification-$(shell date +%Y%m%d-%H%M%S)

.PHONY: list verify test integrity reports reports-en reports-zh source-en source-zh
list:
	$(PYTHON) -B tools/reproduce.py --list
verify:
	$(PYTHON) -B tools/reproduce.py --suite all --output "$(OUTPUT)"
test:
	$(PYTHON) -B -m unittest discover -s tests -v
integrity:
	$(PYTHON) -B tools/check_package.py
reports:
	$(PYTHON) -B tools/build_reports.py --language all
reports-en:
	$(PYTHON) -B tools/build_reports.py --language en
reports-zh:
	$(PYTHON) -B tools/build_reports.py --language zh
source-en:
	$(PYTHON) -B tools/package_reports.py --language en
source-zh:
	$(PYTHON) -B tools/package_reports.py --language zh
