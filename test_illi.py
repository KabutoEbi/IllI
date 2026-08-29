import unittest

from illi import IllIError, Machine, compile_source


class MachineTests(unittest.TestCase):
    def test_increment_and_output(self):
        self.assertEqual(Machine(b"iii!").run(), b"\x03")

    def test_loop_and_pointer_movement(self):
        self.assertEqual(Machine(b"iii[li1I]l!").run(), b"\x03")

    def test_input_echo(self):
        self.assertEqual(Machine(b"|!", b"A").run(), b"A")

    def test_cells_wrap(self):
        self.assertEqual(Machine(b"I!").run(), b"\xff")

    def test_rejects_every_other_character(self):
        with self.assertRaisesRegex(IllIError, "forbidden character"):
            compile_source(b"i\n")

    def test_rejects_unmatched_brackets(self):
        for source in (b"[", b"]"):
            with self.subTest(source=source), self.assertRaises(IllIError):
                compile_source(source)


if __name__ == "__main__":
    unittest.main()
