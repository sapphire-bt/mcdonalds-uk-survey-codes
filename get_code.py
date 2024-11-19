import random
from datetime import datetime, timedelta

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

# The date is checked to make sure it's not expired, so here we make sure it's within 2 days of current time
def random_minutes_from_epoch():
    EPOCH = datetime(2016, 2, 1)
    now = datetime.now()
    two_days_in_millis = 2 * 24 * 60 * 60 * 1000
    random_time = now + timedelta(milliseconds=random.uniform(-two_days_in_millis, two_days_in_millis))
    minutes_from_epoch = int((random_time - EPOCH).total_seconds() // 60)
    return minutes_from_epoch

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

def generate_code(store_id, order_id, purchased):
	enc_store_id = encode(store_id).rjust(3, encode(0))
	enc_order_id = encode((order_id % 100) + 125)
	enc_minutes = encode(purchased).rjust(5, encode(0))
	print(store_id, order_id, purchased)
	code = enc_store_id + encode(3) + enc_order_id + enc_minutes

	code += encode(get_check_digit(code))

	return "{}-{}-{}".format(
		code[0:4],
		code[4:8],
		code[8:12],
	)
def r(min, max):
    return int(random.random() * (max - min) + min)

if __name__ == "__main__":
	print(generate_code(r(1, 1000), r(10, 150), random_minutes_from_epoch()))
