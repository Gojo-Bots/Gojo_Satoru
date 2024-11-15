.PHONY: test install run clean

test:
	@pre-commit run --all-files

install:
	@pip3 install --upgrade pip setuptools wheel
	sleep 3
	@pip3 install -r requirements.txt

run:
	@python3 -m Powers

clean:
	@rm -rf Powers/logs
	@pyclean .