
# system python interpreter. used only to create virtual environment
PY = python3
VENV = venv
BIN=$(VENV)/bin
USB ?= /dev/ttyUSB0

gui: $(VENV)
	@ ./launcher.py

ls_serial_view: $(VENV)
	@ ./$(BIN)/python ./ls_serial_view.py $(USB)

ls_serial_view_devkit: $(VENV)
	@ ./$(BIN)/python ./ls_serial_view_devkit.py $(USB)

show_pip: $(VENV)
	./$(BIN)/pip freeze

test: $(VENV)
	@./Misc/test_python3_compatibility.sh $(BIN) InMsgs

$(VENV): requirements.txt
	$(PY) -m venv $(VENV)
	$(BIN)/pip install --upgrade -r requirements.txt
	touch $(VENV)

clean:
	rm -rf $(VENV)
	find . -type f -name *.pyc -delete
	find . -type d -name __pycache__ -delete

