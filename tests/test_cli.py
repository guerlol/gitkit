import os
import sys
import tempfile
import unittest

sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", "hooks"))

from scan_staged import (  # noqa: E402
    Finding,
    is_git_commit_command,
    load_allow_patterns,
    render_report,
)


class LoadAllowPatternsTest(unittest.TestCase):
    def test_missing_file_yields_no_patterns(self):
        with tempfile.TemporaryDirectory() as root:
            self.assertEqual(load_allow_patterns(root), [])

    def test_comments_and_blank_lines_are_skipped(self):
        with tempfile.TemporaryDirectory() as root:
            with open(os.path.join(root, ".gitkit-allow"), "w") as fh:
                fh.write("# fixtures use a fake key\n\nAKIAIOSFODNN7EXAMPLE\n  \n")

            self.assertEqual(load_allow_patterns(root), ["AKIAIOSFODNN7EXAMPLE"])


class RenderReportTest(unittest.TestCase):
    def test_no_findings_exits_zero_with_no_output(self):
        text, code = render_report([])

        self.assertEqual(code, 0)
        self.assertEqual(text, "")

    def test_blocking_finding_exits_two(self):
        findings = [Finding(True, "aws-access-key-id", "app.py", 'KEY = "AKIA…REDACTED"')]

        text, code = render_report(findings)

        self.assertEqual(code, 2)
        self.assertIn("aws-access-key-id", text)
        self.assertIn("app.py", text)

    def test_warning_only_finding_exits_zero_but_still_reports(self):
        findings = [Finding(False, "debug-leftover", "app.js", 'console.log("here")')]

        text, code = render_report(findings)

        self.assertEqual(code, 0)
        self.assertIn("debug-leftover", text)

    def test_allowlist_hint_is_shown_when_blocking(self):
        findings = [Finding(True, "aws-access-key-id", "app.py", "KEY")]

        text, _ = render_report(findings)

        self.assertIn(".gitkit-allow", text)


class IsGitCommitCommandTest(unittest.TestCase):
    def test_plain_commit_matches(self):
        self.assertTrue(is_git_commit_command('git commit -m "fix thing"'))

    def test_amend_matches(self):
        self.assertTrue(is_git_commit_command("git commit --amend --no-edit"))

    def test_commit_after_a_cd_matches(self):
        self.assertTrue(is_git_commit_command("cd /tmp/repo && git commit -m x"))

    def test_commit_with_a_git_c_flag_matches(self):
        self.assertTrue(is_git_commit_command("git -C /tmp/repo commit -m x"))

    def test_other_git_commands_do_not_match(self):
        self.assertFalse(is_git_commit_command("git status --short"))

    def test_unrelated_commands_do_not_match(self):
        self.assertFalse(is_git_commit_command("npm test"))

    def test_log_mentioning_commit_does_not_match(self):
        self.assertFalse(is_git_commit_command("git log --format=%H commit"))


if __name__ == "__main__":
    unittest.main()
