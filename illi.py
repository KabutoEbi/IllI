#!/usr/bin/env python3
"""Interpreter for IllI, an eight-character esoteric language."""

from __future__ import annotations

import argparse
import sys
from dataclasses import dataclass


INSTRUCTIONS = frozenset(b"iIl!|[]1")


class IllIError(Exception):
    """A source-code error with a human-readable location."""


def compile_source(source: bytes) -> dict[int, int]:
    """Validate source and return matching bracket positions."""
    stack: list[int] = []
    jumps: dict[int, int] = {}

    for position, instruction in enumerate(source):
        if instruction not in INSTRUCTIONS:
            shown = repr(bytes([instruction]).decode("ascii", errors="replace"))
            raise IllIError(f"{position + 1}: forbidden character {shown}")
        if instruction == ord("["):
            stack.append(position)
        elif instruction == ord("]"):
            if not stack:
                raise IllIError(f"{position + 1}: unmatched ']'")
            opening = stack.pop()
            jumps[opening] = position
            jumps[position] = opening

    if stack:
        raise IllIError(f"{stack[-1] + 1}: unmatched '['")
    return jumps


@dataclass
class Machine:
    """An IllI machine with an unbounded, zero-filled tape of byte cells."""

    source: bytes
    input_data: bytes = b""

    def run(self) -> bytes:
        jumps = compile_source(self.source)
        tape: dict[int, int] = {}
        pointer = 0
        cursor = 0
        input_cursor = 0
        output = bytearray()

        while cursor < len(self.source):
            instruction = self.source[cursor]
            value = tape.get(pointer, 0)

            if instruction == ord("i"):
                tape[pointer] = (value + 1) & 0xFF
            elif instruction == ord("I"):
                tape[pointer] = (value - 1) & 0xFF
            elif instruction == ord("l"):
                pointer += 1
            elif instruction == ord("1"):
                pointer -= 1
            elif instruction == ord("!"):
                output.append(value)
            elif instruction == ord("|"):
                tape[pointer] = (
                    self.input_data[input_cursor]
                    if input_cursor < len(self.input_data)
                    else 0
                )
                input_cursor += 1
            elif instruction == ord("[") and value == 0:
                cursor = jumps[cursor]
            elif instruction == ord("]") and value != 0:
                cursor = jumps[cursor]

            cursor += 1

        return bytes(output)


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(
        prog="illi", description="Run a program made only from i I l ! | [ ] 1"
    )
    parser.add_argument("program", help="path to an IllI source file")
    parser.add_argument(
        "--input", default="", help="text supplied to the program's | instruction"
    )
    args = parser.parse_args(argv)

    try:
        with open(args.program, "rb") as source_file:
            source = source_file.read()
        result = Machine(source, args.input.encode()).run()
    except (OSError, IllIError) as error:
        print(f"illi: {error}", file=sys.stderr)
        return 1

    sys.stdout.buffer.write(result)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
