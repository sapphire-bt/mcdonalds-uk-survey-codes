import argparse

from datetime import datetime
from enum import IntEnum


CHARS = "CM7WD6N4RHF9ZL3XKQGVPBTJY"
BASE = len(CHARS)
EPOCH_BEGIN = datetime(2016, 2, 1)


class Reg(IntEnum):
    DELIVERY = 61
    APP = 300


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


def parse_datetime(val):
    return datetime.strptime(val, "%Y-%m-%d %H:%M")


def get_minutes_since_epoch(purchased):
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


def generate_code(store_id, order_id, purchased, reg):
    zero = encode(0)  # Used for padding
    if reg == Reg.DELIVERY:

        reg = 0
    elif reg == Reg.APP:
        reg = 1

    enc_store_id = encode(store_id).rjust(3, zero)
    enc_order_id = encode((order_id % 100) + (reg * 100)).rjust(3, zero)
    enc_minutes = encode(get_minutes_since_epoch(purchased)).rjust(5, zero)

    code = enc_store_id + enc_order_id + enc_minutes

    code += encode(get_check_digit(code))

    return "{}-{}-{}".format(
        code[0:4],
        code[4:8],
        code[8:12],
    )


def main(args):
    code = generate_code(**vars(args))
    print(code)


if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("-s", "--store-id", type=int, required=True)
    parser.add_argument("-o", "--order-id", type=int, required=True)
    parser.add_argument("-p", "--purchased", type=parse_datetime, required=True)
    parser.add_argument("-r", "--reg", type=int, default=20)
    args = parser.parse_args()
    main(args)
