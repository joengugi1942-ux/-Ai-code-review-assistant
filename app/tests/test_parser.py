from app.services.code_parser import CodeParser


def test_code_parser_detects_language() -> None:
    parser = CodeParser()
    parsed = parser.parse("example.py", "print('hi')")
    assert parsed.language == "python"



