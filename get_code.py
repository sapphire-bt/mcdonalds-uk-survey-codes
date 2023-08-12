import sys
from datetime import datetime

CHARS = "CM7WD6N4RHF9ZL3XKQGVPBTJY"
BASE = len(CHARS)
EPOCH_BEGIN = datetime(2016, 2, 1)


def encode(num):
	encoded = ""
	while num >= BASE:
		encoded = CHARS[num % BASE] + encoded
		num //= BASE
	return CHARS[num] + encoded

def decode(encoded):
	num = 0
	for x, c in enumerate(encoded):
		exp = len(encoded) - x - 1
		num += (BASE**exp) * CHARS.find(c)
	return num

def get_order_flags(order_id, visit_type):
	# Not actually sure if these are "flags", and there doesn't appear to be any
	# validation when submitting survey codes with different flags.
	flags = 0

	unknown_flag_1 = decode("MC")  # 25  - only seems to apply when visit_type is 3 or 5
	unknown_flag_2 = decode("DC")  # 100 - always seems to be added

	if visit_type == 3 or visit_type == 5:
		flags += unknown_flag_1

	flags += unknown_flag_2

	return flags

def get_minutes_since_epoch(purchased):
	purchased = datetime.strptime(purchased, "%Y-%m-%d %H:%M")
	minutes_since_epoch = purchased - EPOCH_BEGIN
	return int(minutes_since_epoch.total_seconds() / 60)

def get_check_digit(code):
	"""Base 25 version of the Luhn algorithm"""
	check_digit = 0

	for x, char in enumerate(code[::-1]):
		val = decode(char)

		if (x % 2) == 0:
			val *= 2
			enc_val = encode(val)

			if len(enc_val) == 2:
				val = sum(map(decode, enc_val))

		check_digit += val

	check_digit %= BASE

	if check_digit > 0:
		check_digit = BASE - check_digit

	return check_digit

def generate_code(store_id, order_id, purchased, visit_type=3):
	enc_store_id = encode(store_id).rjust(3, encode(0))
	enc_visit_type = encode(visit_type)
	enc_order_id = encode((order_id % 100) + get_order_flags(order_id, visit_type))
	enc_minutes = encode(get_minutes_since_epoch(purchased)).rjust(5, encode(0))

	code = enc_store_id + enc_visit_type + enc_order_id + enc_minutes

	code += encode(get_check_digit(code))

	return "{}-{}-{}".format(
		code[0:4],
		code[4:8],
		code[8:12],
	)


def main(argc, argv):
	if argc < 4:
		print("Usage:")
		print("    get_code.py <store ID> <order ID> <purchased>")
		print()
		print("Purchase date/time must be in format: YYYY-MM-DD HH:mm")
		print()
		return 1

	store_id, order_id, purchased = argv[1:4]

	code = generate_code(int(store_id), int(order_id), purchased)

	print(code)

	return 0

if __name__ == "__main__":
	sys.exit(main(len(sys.argv), sys.argv))
