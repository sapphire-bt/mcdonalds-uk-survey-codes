import argparse

from dataclasses import dataclass
from datetime import datetime, timedelta
from enum import IntEnum

CHARS = "CM7WD6N4RHF9ZL3XKQGVPBTJY"
BASE = len(CHARS)
EPOCH_BEGIN = datetime(2016, 2, 1)


@dataclass
class McDonaldsOrder:
    store_id: int
    order_id: int
    purchased: datetime
    reg: int

    def __post_init__(self):
        if isinstance(self.purchased, str):
            self.purchased = parse_datetime(self.purchased)

    def __eq__(self, other):
        return self.__dict__ == other.__dict__

    def get_code(self):
        enc_store_id = encode(self.store_id)
        enc_order_id = encode((self.order_id % 100) + (get_reg(self.reg) * 100))
        enc_minutes = encode(get_minutes_since_epoch(self.purchased))

        code = pad(enc_store_id, 3) + pad(enc_order_id, 3) + pad(enc_minutes, 5)
        code += encode(get_check_digit(code))

        return "{}-{}-{}".format(
            code[0:4],
            code[4:8],
            code[8:12],
        )

    @classmethod
    def from_code(cls, code: str):
        code = code.replace("-", "").upper()
        str_len = len(code)

        if str_len < 11 or str_len > 12:
            raise InvalidCode(f"Code must be 11-12 characters (got {str_len}: {code})")

        store_id = decode(code[0:3])
        order_reg = decode(code[3:6])
        order_id = order_reg % 100
        reg = order_reg // 100
        purchased = EPOCH_BEGIN + timedelta(minutes=decode(code[6:11]))

        return cls(store_id, order_id, purchased, reg)


class InvalidCode(Exception):
    pass


class Reg(IntEnum):
    DELIVERY = 61
    APP = 300


def encode(num: int):
    encoded = ""
    while num >= BASE:
        encoded = CHARS[num % BASE] + encoded
        num //= BASE
    return CHARS[num] + encoded


def decode(encoded: str):
    num = 0
    for x, c in enumerate(encoded):
        exp = len(encoded) - x - 1
        num += (BASE**exp) * CHARS.find(c)
    return num


def pad(val: str, amt: int, char: str=encode(0)):
    return val.rjust(amt, char)


def parse_datetime(val: str):
    return datetime.strptime(val, "%Y-%m-%d %H:%M")


def get_minutes_since_epoch(purchased: datetime):
    minutes_since_epoch = purchased - EPOCH_BEGIN
    return int(minutes_since_epoch.total_seconds() / 60)


def get_reg(reg: int):
    if reg == Reg.DELIVERY:
        return 0
    elif reg == Reg.APP:
        return 1
    else:
        return reg


def get_check_digit(code: str):
    """Base 25 version of the Luhn algorithm

    Note: this does not actually provide accurate check digits as the base must be even.
    """
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


def main(args: argparse.Namespace):
    order = McDonaldsOrder(**vars(args))
    print(order.get_code())


if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("-s", "--store-id", type=int, required=True)
    parser.add_argument("-o", "--order-id", type=int, required=True)
    parser.add_argument("-p", "--purchased", type=parse_datetime, required=True)
    parser.add_argument("-r", "--reg", type=int, default=20)
    args = parser.parse_args()
    main(args)
