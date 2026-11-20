import unittest

from graphly.tools import prepare, prepare_triple


class TestSparqlTermSerialization(unittest.TestCase):
    def test_preserves_zero_values(self):
        self.assertEqual("0", prepare(0))
        self.assertEqual("0.0", prepare(0.0))

    def test_escapes_literal_control_characters(self):
        self.assertEqual(
            "'O\\'Reilly\\\\q\\nnext\\tcolumn'",
            prepare("O'Reilly\\q\nnext\tcolumn"),
        )

    def test_supports_absolute_non_http_iris(self):
        self.assertEqual("<urn:example:entity>", prepare("urn:example:entity"))
        self.assertEqual("<mailto:person@example.org>", prepare("mailto:person@example.org"))

    def test_rejects_missing_or_invalid_terms(self):
        self.assertIsNone(prepare(None))
        with self.assertRaisesRegex(ValueError, "cannot contain None"):
            prepare_triple(("ex:s", "ex:p", None), ["ex"])
        with self.assertRaisesRegex(ValueError, "Invalid absolute IRI"):
            prepare("http://example.org/bad iri")
        with self.assertRaisesRegex(ValueError, "three terms"):
            prepare_triple(("ex:s", "ex:p"), ["ex"])

    def test_serializes_a_valid_triple(self):
        self.assertEqual(
            "ex:s ex:p 'line\\nbreak' .",
            prepare_triple(("ex:s", "ex:p", "line\nbreak"), ["ex"]),
        )


if __name__ == "__main__":
    unittest.main()
