import os
import sys
import unittest

sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", "hooks"))

from scan_staged import scan_diff  # noqa: E402


def diff(*lines, path="app.py"):
    """Build a staged-diff fragment for a single file."""
    header = [
        f"diff --git a/{path} b/{path}",
        "index 1111111..2222222 100644",
        f"--- a/{path}",
        f"+++ b/{path}",
        "@@ -1,3 +1,4 @@",
    ]
    return "\n".join(header + list(lines)) + "\n"


class ScanDiffTest(unittest.TestCase):
    def test_clean_diff_produces_no_findings(self):
        text = diff("+def add(a, b):", "+    return a + b")

        self.assertEqual(scan_diff(text), [])

    def test_aws_access_key_id_blocks(self):
        text = diff('+AWS_KEY = "AKIAIOSFODNN7EXAMPLE"')

        findings = scan_diff(text)

        self.assertEqual(len(findings), 1)
        self.assertTrue(findings[0].blocking)
        self.assertEqual(findings[0].file, "app.py")

    def test_secret_on_a_removed_line_is_ignored(self):
        text = diff('-AWS_KEY = "AKIAIOSFODNN7EXAMPLE"')

        self.assertEqual(scan_diff(text), [])

    def test_secret_on_a_context_line_is_ignored(self):
        text = diff(' AWS_KEY = "AKIAIOSFODNN7EXAMPLE"')

        self.assertEqual(scan_diff(text), [])

    def test_private_key_header_blocks(self):
        text = diff("+-----BEGIN RSA PRIVATE KEY-----")

        findings = scan_diff(text)

        self.assertEqual([f.rule for f in findings], ["private-key"])
        self.assertTrue(findings[0].blocking)

    def test_anthropic_api_key_blocks(self):
        text = diff('+client = Anthropic(api_key="sk-ant-api03-' + "A" * 32 + '")')

        self.assertEqual([f.rule for f in scan_diff(text)], ["anthropic-api-key"])

    def test_github_token_blocks(self):
        text = diff('+TOKEN = "ghp_' + "b" * 36 + '"')

        self.assertEqual([f.rule for f in scan_diff(text)], ["github-token"])

    def test_generic_secret_assignment_blocks(self):
        text = diff('+password = "hunter2-correct-horse"')

        self.assertEqual([f.rule for f in scan_diff(text)], ["generic-secret"])

    def test_short_assignment_value_is_not_a_secret(self):
        text = diff('+password = "abc"')

        self.assertEqual(scan_diff(text), [])

    def test_adding_a_dotenv_file_blocks(self):
        text = diff("+DATABASE_URL=postgres://localhost/dev", path=".env")

        findings = scan_diff(text)

        self.assertIn("env-file", [f.rule for f in findings])
        self.assertTrue(all(f.blocking for f in findings))

    def test_dotenv_example_file_is_allowed(self):
        text = diff("+DATABASE_URL=", path=".env.example")

        self.assertEqual([f.rule for f in scan_diff(text) if f.rule == "env-file"], [])

    def test_console_log_warns_but_does_not_block(self):
        text = diff('+  console.log("here")')

        findings = scan_diff(text)

        self.assertEqual([f.rule for f in findings], ["debug-leftover"])
        self.assertFalse(findings[0].blocking)

    def test_debugger_statement_warns(self):
        text = diff("+  debugger")

        self.assertEqual([f.rule for f in scan_diff(text)], ["debug-leftover"])

    def test_python_breakpoint_warns(self):
        text = diff("+    breakpoint()")

        self.assertEqual([f.rule for f in scan_diff(text)], ["debug-leftover"])

    def test_excerpt_masks_the_matched_secret(self):
        text = diff('+AWS_KEY = "AKIAIOSFODNN7EXAMPLE"')

        excerpt = scan_diff(text)[0].excerpt

        self.assertNotIn("AKIAIOSFODNN7EXAMPLE", excerpt)
        self.assertIn("AWS_KEY", excerpt)

    def test_allow_pattern_suppresses_a_matching_finding(self):
        text = diff('+AWS_KEY = "AKIAIOSFODNN7EXAMPLE"')

        self.assertEqual(scan_diff(text, allow_patterns=["AKIAIOSFODNN7EXAMPLE"]), [])

    def test_allow_pattern_leaves_other_findings_alone(self):
        text = diff(
            '+AWS_KEY = "AKIAIOSFODNN7EXAMPLE"',
            "+-----BEGIN RSA PRIVATE KEY-----",
        )

        findings = scan_diff(text, allow_patterns=["AKIAIOSFODNN7EXAMPLE"])

        self.assertEqual([f.rule for f in findings], ["private-key"])


if __name__ == "__main__":
    unittest.main()
