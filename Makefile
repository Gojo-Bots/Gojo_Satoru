test:
	@pre-commit run --all-files

install:

	@pip install -r requirements.txt

run:
	@python3 -m Powers

clean:
	@rm -rf Powers/logs
	@pyclean .
