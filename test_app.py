from app import make_brief

def test_make_brief_without_results():
    assert "No search results" in make_brief("example", [], "")

def test_fallback_returns_three_search_snippets():
    results = [
        {"title": f"Title {i}", "body": f"Body {i}", "url": f"https://example.com/{i}"}
        for i in range(1, 5)
    ]
    result = make_brief("example", results, "")
    assert "Title 1" in result
    assert "Title 3" in result
    assert "Title 4" not in result
