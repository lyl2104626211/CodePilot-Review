import pytest

from app.services.pr_parser import PRParseError, parse_github_pr_url


def test_parse_valid_github_pr_url():
    result = parse_github_pr_url("https://github.com/acme/codepilot/pull/12")
    assert result.owner == "acme"
    assert result.repo == "codepilot"
    assert result.number == 12


def test_parse_url_with_trailing_slash():
    result = parse_github_pr_url("https://github.com/acme/codepilot/pull/12/")
    assert result.owner == "acme"
    assert result.repo == "codepilot"
    assert result.number == 12


def test_reject_non_github_url():
    with pytest.raises(PRParseError, match="Only GitHub pull request URLs are supported"):
        parse_github_pr_url("https://gitlab.com/acme/codepilot/pull/12")


def test_reject_url_without_pull_segment():
    with pytest.raises(PRParseError, match="Invalid GitHub PR URL"):
        parse_github_pr_url("https://github.com/acme/codepilot/issues/12")


def test_reject_non_number_pr_id():
    with pytest.raises(PRParseError, match="Invalid GitHub PR URL"):
        parse_github_pr_url("https://github.com/acme/codepilot/pull/abc")
