import websocket
import base64
import utils
import time


wss_url = "wss://gaming-svc.aax.com"
user_agent_header = "Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:106.0) Gecko/20100101 Firefox/106.0"

# for testing:
# with open("json.txt", "r") as f:
# 	history = utils.parse_message( f.readline() )
# 	if history is not None:
# 		utils.write_csv( history )


def message(str):
	# Via the Chrome inspector, we can get the Base64 values of each message
	return base64.b64decode(str)


def decode_message(str):
	return bytes(str).decode("utf-8")


def on_open(ws):
	# Login / Start data streaming (from the server to this client)
	ws.send( message("GwAAABUAAAB7ImkiOiJCZWFyZXIgbnVsbCJ9") )

	# Request list of the 10 most recent multipliers (page 1)
	ws.send( message("FAAAABkAAAB7InBhZ2UiOiIxIn0=") )


def on_message(ws, data):

	try:
		history = utils.parse_message( decode_message(data) )
	except Exception as e:
		print("\n ! ERROR -", e)
		print("DUMP -> ", e, "\n\n")

	if history is not None:
		# If this message is the one that contains the multiplier history
		ws.close()
		utils.write_csv( history )
		print('.', end='', flush=True)


if __name__ == '__main__':

	try:
		while True:
			ws = websocket.WebSocketApp(wss_url, on_open=on_open, on_message=on_message, header={"User-Agent": user_agent_header})
			ws.run_forever()

			time.sleep( 10 * 5 )	# the message contains the multipliersof the
				# last 10 matches. Each match has a previous countdown of 5 seconds.
				# So in case every game ends soon, 10 games will still be over 50 seconds
				# Alternative, we can wait longer and send messages to get the other pages
				# of the history

	except KeyboardInterrupt:
		print("\nTerminated by CTRL+C ...")
		ws.close()