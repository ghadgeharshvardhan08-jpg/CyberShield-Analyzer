from cybershield_api.risk import InvalidSubmittedUrl, analyze_url


def test_normalizes_host_without_claiming_safety():
    result = analyze_url(" Example.COM/path ")

    assert result["normalized_url"] == "https://example.com/path"
    assert result["score"] == 0
    assert result["category"] == "Low"
    assert "cannot verify" in result["recommendation"].lower()
    assert result["findings"] == []


def test_scores_explainable_indicators_and_redacts_sensitive_parts():
    result = analyze_url(
        "http://192.0.2.10/login/verify?session=private-session#private-fragment"
    )

    by_code = {finding["code"]: finding for finding in result["findings"]}
    assert {"insecure_transport", "ip_address_host", "suspicious_keywords"} <= set(by_code)
    assert result["score"] == 48
    assert result["category"] == "High"
    assert sum(finding["points"] for finding in result["findings"]) == result["score"]
    assert "private-session" not in result["submitted_url"]
    assert "private-fragment" not in result["submitted_url"]


def test_flags_brand_impersonation_encoded_separators_and_subdomains():
    result = analyze_url(
        "https://paypal.com.account.example.attacker.test/%2Fverify?token=do-not-store"
    )
    codes = {finding["code"] for finding in result["findings"]}

    assert "misleading_domain" in codes
    assert "encoded_obfuscation" in codes
    assert "excessive_subdomains" in codes
    assert "suspicious_keywords" in codes
    assert "do-not-store" not in result["normalized_url"]


def test_detects_punycode_and_caps_the_score():
    result = analyze_url("http://xn--pple-43d.com:8443/account/verify/login")
    codes = {finding["code"] for finding in result["findings"]}

    assert {"punycode_host", "unusual_port", "insecure_transport", "suspicious_keywords"} <= codes
    assert 0 <= result["score"] <= 100


def test_rejects_non_web_schemes_control_characters_and_bad_hosts():
    for value in ("javascript:alert(1)", "https://example.com/\npath", "https://"):
        try:
            analyze_url(value)
        except InvalidSubmittedUrl:
            continue
        raise AssertionError(f"Expected invalid URL to be rejected: {value!r}")


def test_rejects_excessive_query_fields_instead_of_returning_server_error():
    many_fields = "https://example.test/?" + "&".join(f"p{i}=x" for i in range(101))
    try:
        analyze_url(many_fields)
    except InvalidSubmittedUrl as exc:
        assert "too many" in str(exc).lower()
    else:
        raise AssertionError("Expected excessive query parameters to be rejected.")
