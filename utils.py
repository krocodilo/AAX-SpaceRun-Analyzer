from os import path, makedirs
from json import loads as loadJSON

folder_name = "multiplier-logs"
last_timestamp = 0


def parse_history(json):
	# receives JSON list of past multipliers
	# returns an array of arrays, each containing the timestamp and multiplier
		# sorted by timestamp
	rows = []
	for obj in json:
		if 'roundid' in obj and 'multiple' in obj:
			rows.append( [ obj['roundid'], obj['multiple'] ] )

	if len(rows) > 0:
		return sorted(rows)
	else:
		return None


def parse_message(str):
	# Parse JSON from the message and check if is the type of message
	# which contains the multiplier history
	jay = loadJSON( str )
	jay = loadJSON( jay["mgs"][0] )
	history = None

	if "mg" in jay and 'rt' in jay['mg']:
		# If it is a message of the regular structure
		jay = jay['mg']['rt']

		if 'list' in jay:
			# if this is the message that contains the history of multipliers of the game
			history = parse_history( jay['list'] )
			
	else:
		raise Exception("Unexpected JSON content ->  ", str, "\n")

	# history either is None or contains an array of arrays of the past multipliers
	return history


def open_csv_file(day):
	# open file to append. Create one if non-existent
	global last_timestamp

	if not path.exists(path.join(folder_name)):
		makedirs(path.join(folder_name))
		print("-> Created directory: '" + folder_name + "'")

	filepath = path.join(folder_name, day+".csv")

	if path.exists(path.join(filepath)):
		f = open( filepath, "a+")

		f.seek(0)		# move cursor to beginning in order to check if there is content in the file
		lines = f.readlines()

		# read the last timestamp, assuming the file is in the correct format
		if last_timestamp == 0 and len(lines) > 1:
			# if its not just the CSV header line, read the last line
			for line in reversed(lines):
				if line.strip() == "":		# if its empty
					continue

				str = line.replace(" ", "").split(",")[0]
				if str.isdigit():
					last_timestamp = int(str)
					break

		if lines[-1].strip() != "" and lines[-1].endswith('\n') is not True:
			# if the last line does not end with the newline character
			f.write('\n')

	else:
		# Create file
		f = open( filepath, "w")
		f.write('Timestamp, Multiplier\n')		# CSV header
		print("\n-> Created file: " + filepath)

	return f


def write_csv(arrayofarrays):
	global last_timestamp

	day = arrayofarrays[0][0][:8]	# first 8 digits of the timestamp of the first object
	f = open_csv_file(day)

	for array in arrayofarrays:

		if int(array[0]) <= last_timestamp:
			# If this multiplier has already been saved
			continue

		if int(array[0][:8]) > int(day):
			# If this mult belongs to a new day
			day = array[0][:8]	# first 8 digits of the timestamp
			f.close()
			f = open_csv_file(day)

		f.write(array[0] + ", " + array[1] + "\n")
		last_timestamp = int(array[0])
		# print("added -", array)

	f.close()