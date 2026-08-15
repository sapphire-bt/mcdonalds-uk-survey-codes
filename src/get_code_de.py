#!/usr/bin/env python3
"""Encode and decode German McDonald's receipt survey codes.

The decimal payload layout is:
    SSSS MM DD hh mm PP OO CC

Examples:
    python get_code_de.py encode 0554 08 07 14 38 25 31
    python get_code_de.py encode 055408071438253120
    python get_code_de.py decode btyd-wjw4-vigi
"""

from __future__ import annotations

import argparse
import re
import sys

from dataclasses import dataclass


ALPHABET = "0123456789abcdefghijklmnopqrstuvwxyz"
KEY = "betteraskthe"

FIELD_NAMES = (
    "Store ID",
    "Month",
    "Day",
    "Hour",
    "Minute",
    "POS/register ID",
    "Order number modulo 100",
)
FIELD_WIDTHS = (4, 2, 2, 2, 2, 2, 2)
FIELD_RANGES = (
    (0, 9999),
    (1, 12),
    (1, 31),
    (0, 23),
    (0, 59),
    (1, 40),
    (0, 99),
)


@dataclass(frozen=True)
class ReceiptData:
    payload: str
    check_value: str

    @property
    def number(self) -> str:
        return self.payload + self.check_value

    @property
    def fields(self) -> tuple[str, ...]:
        result = []
        offset = 0
        for width in FIELD_WIDTHS:
            result.append(self.payload[offset : offset + width])
            offset += width
        return tuple(result)

    @property
    def grouped(self) -> str:
        return " ".join((*self.fields, self.check_value))


def calculate_check_value(payload: str) -> str:
    """Return the two-digit check value for a 16-digit payload."""
    if not re.fullmatch(r"\d{16}", payload):
        raise ValueError("The payload must contain exactly 16 decimal digits.")
    return f"{sum(int(digit) for digit in payload) % 36:02d}"


def to_base36(number: int) -> str:
    if number < 0:
        raise ValueError("Negative numbers are not supported.")
    if number == 0:
        return "0"

    result = []
    while number:
        number, remainder = divmod(number, 36)
        result.append(ALPHABET[remainder])
    return "".join(reversed(result))


def shift_text(value: str, *, decode: bool = False) -> str:
    """Apply or reverse the position-dependent Base 36 shift."""
    direction = -1 if decode else 1
    result = []
    for position, character in enumerate(value):
        character_index = ALPHABET.index(character)
        key_index = ALPHABET.index(KEY[position % len(KEY)])
        result.append(
            ALPHABET[(character_index + direction * key_index) % len(ALPHABET)]
        )
    return "".join(result)


def validate_fields(fields: tuple[str, ...]) -> tuple[str, ...]:
    if len(fields) != 7:
        raise ValueError("Expected seven fields: SSSS MM DD hh mm PP OO.")

    normalized = []
    for value, name, width, limits in zip(
        fields, FIELD_NAMES, FIELD_WIDTHS, FIELD_RANGES
    ):
        if not value.isdecimal():
            raise ValueError(f"{name} must be a decimal number: {value!r}")
        if len(value) > width:
            raise ValueError(f"{name} may contain at most {width} digits.")

        numeric_value = int(value)
        minimum, maximum = limits
        if not minimum <= numeric_value <= maximum:
            raise ValueError(f"{name} must be between {minimum} and {maximum}.")
        normalized.append(f"{numeric_value:0{width}d}")
    return tuple(normalized)


def split_payload(payload: str) -> tuple[str, ...]:
    fields = []
    offset = 0
    for width in FIELD_WIDTHS:
        fields.append(payload[offset : offset + width])
        offset += width
    return tuple(fields)


def parse_number(values: list[str]) -> ReceiptData:
    """Parse seven/eight fields or one compact 16/18-digit value."""
    supplied_check_value = None

    if len(values) == 1:
        compact = re.sub(r"\s+", "", values[0])
        if not compact.isdecimal() or len(compact) not in (16, 18):
            raise ValueError("A compact value must contain 16 or 18 decimal digits.")

        payload = compact[:16]
        validate_fields(split_payload(payload))
        if len(compact) == 18:
            supplied_check_value = compact[16:]
    elif len(values) in (7, 8):
        payload = "".join(validate_fields(tuple(values[:7])))
        if len(values) == 8:
            supplied_check_value = values[7].zfill(2)
            if (
                not supplied_check_value.isdecimal()
                or len(supplied_check_value) != 2
            ):
                raise ValueError("CC must be a one- or two-digit decimal value.")
    else:
        raise ValueError(
            "Expected seven fields, eight fields including CC, or one compact value."
        )

    expected_check_value = calculate_check_value(payload)
    if (
        supplied_check_value is not None
        and supplied_check_value != expected_check_value
    ):
        raise ValueError(
            "Invalid check value: "
            f"received {supplied_check_value}, expected {expected_check_value}."
        )
    return ReceiptData(payload, expected_check_value)


def encode(data: ReceiptData) -> str:
    base36 = to_base36(int(data.number)).rjust(12, "0")
    if len(base36) != 12:
        raise ValueError("The decimal value does not fit in 12 Base 36 characters.")

    encoded = shift_text(base36)
    return f"{encoded[:4]}-{encoded[4:8]}-{encoded[8:]}"


def decode(code: str) -> ReceiptData:
    compact = re.sub(r"[-\s]", "", code).lower()
    if len(compact) != 12 or any(char not in ALPHABET for char in compact):
        raise ValueError(
            "The code must contain 12 Base 36 characters, for example "
            "xxxx-xxxx-xxxx."
        )

    base36 = shift_text(compact, decode=True)
    decimal = str(int(base36, 36))
    if len(decimal) > 18:
        raise ValueError("The code decodes to a decimal value longer than 18 digits.")

    number = decimal.zfill(18)
    data = ReceiptData(number[:16], number[16:])
    expected_check_value = calculate_check_value(data.payload)
    if data.check_value != expected_check_value:
        raise ValueError(
            "Invalid check value: "
            f"code contains {data.check_value}, expected {expected_check_value}."
        )

    validate_fields(data.fields)
    return data


def print_data(data: ReceiptData) -> None:
    print(f"Number: {data.number}")
    print(f"Fields: {data.grouped}")
    for name, value in zip(
        (*FIELD_NAMES, "Check value"), (*data.fields, data.check_value)
    ):
        print(f"  {name}: {value}")


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        description="Encode and decode German McDonald's receipt survey codes."
    )
    subparsers = parser.add_subparsers(dest="command", required=True)

    encode_parser = subparsers.add_parser(
        "encode", aliases=["e"], help="convert receipt fields into a code"
    )
    encode_parser.add_argument(
        "values",
        nargs="+",
        metavar="VALUE",
        help="SSSS MM DD hh mm PP OO [CC], or one 16/18-digit value",
    )

    decode_parser = subparsers.add_parser(
        "decode", aliases=["d"], help="convert a code into receipt fields"
    )
    decode_parser.add_argument("code", help="code in xxxx-xxxx-xxxx format")
    return parser


def main(argv: list[str] | None = None) -> int:
    parser = build_parser()
    args = parser.parse_args(argv)
    try:
        if args.command in ("encode", "e"):
            data = parse_number(args.values)
            print(f"Code:   {encode(data)}")
            print_data(data)
        else:
            print_data(decode(args.code))
    except ValueError as error:
        parser.error(str(error))
    return 0


if __name__ == "__main__":
    sys.exit(main())
