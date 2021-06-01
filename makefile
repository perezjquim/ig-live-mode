PORT=7070

main: run-flask

run-flask:
	@FLASK_APP=main.py \
		python3 -m flask run \
		--port=$(PORT)