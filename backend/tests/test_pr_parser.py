import pytest

from app.services.pr_parser import PRParseError, parse_github_pr_url


def test_parse_valid_github_pr_url():
    """验证合法 GitHub PR URL 能正确解析 owner、repo、number"""
    result = parse_github_pr_url("https://github.com/acme/codepilot/pull/12")
    assert result.owner == "acme"
    assert result.repo == "codepilot"
    assert result.number == 12


def test_parse_url_with_trailing_slash():
    """验证末尾带斜杠的 URL 仍能正确解析"""
    result = parse_github_pr_url("https://github.com/acme/codepilot/pull/12/")
    assert result.owner == "acme"
    assert result.repo == "codepilot"
    assert result.number == 12


def test_reject_non_github_url():
    """验证非 GitHub 域名（如 GitLab）被拒绝"""
    with pytest.raises(PRParseError, match="Only GitHub pull request URLs are supported"):
        parse_github_pr_url("https://gitlab.com/acme/codepilot/pull/12")


def test_reject_url_without_pull_segment():
    """验证缺少 /pull/ 路径段的 URL 被拒绝"""
    with pytest.raises(PRParseError, match="Invalid GitHub PR URL"):
        parse_github_pr_url("https://github.com/acme/codepilot/issues/12")


def test_reject_non_number_pr_id():
    """验证 PR 编号非数字时被拒绝"""
    with pytest.raises(PRParseError, match="Invalid GitHub PR URL"):
        parse_github_pr_url("https://github.com/acme/codepilot/pull/abc")
