import unittest

from multiplayer_warning import replacements, verify_template


class MultiplayerWarningTests(unittest.TestCase):
    def test_keeps_existing_true_and_removes_old_version_header(self):
        original = b"version:3955\r\nfov:0.0\r\nskipMultiplayerWarning:true\r\nlanguage:ru_ru\r\n"
        result, operations = replacements(original)
        self.assertEqual(original.removeprefix(b"version:3955\r\n"), result)
        self.assertEqual([{"from": "version:3955\r\n", "to": ""}], operations)

    def test_new_author_template_resets_flag_and_changes_other_options(self):
        original = b"version:3956\nfov:0.25\nskipMultiplayerWarning:false\nlanguage:en_us"
        result, operations = replacements(original)
        self.assertEqual(b"fov:0.25\nskipMultiplayerWarning:true\nlanguage:en_us", result)
        self.assertEqual(2, len(operations))

    def test_new_author_template_drops_flag_but_keeps_its_version_header(self):
        original = b"version:3956\r\nfov:0.25\r\nlanguage:en_us"
        result, operations = replacements(original)
        self.assertEqual(b"skipMultiplayerWarning:true\r\nfov:0.25\r\nlanguage:en_us", result)
        self.assertEqual(1, len(operations))

    def test_new_author_template_drops_both_lines(self):
        original = b"fov:0.25\r\nlanguage:en_us"
        result, _ = replacements(original)
        self.assertEqual(b"skipMultiplayerWarning:true\r\n" + original, result)

    def test_keeps_compliant_template_byte_identical(self):
        original = b"fov:0.25\nskipMultiplayerWarning:true"
        self.assertEqual((original, []), replacements(original))

    def test_rejects_ambiguous_author_template_and_any_invalid_release_value(self):
        duplicate = b"skipMultiplayerWarning:true\nskipMultiplayerWarning:false"
        with self.assertRaises(ValueError):
            replacements(duplicate)
        for data in (duplicate, b"skipMultiplayerWarning:false", b"fov:0.25",
                     b"version:3955\nskipMultiplayerWarning:true"):
            with self.subTest(data=data), self.assertRaises(ValueError):
                verify_template(data)


if __name__ == "__main__":
    unittest.main()
