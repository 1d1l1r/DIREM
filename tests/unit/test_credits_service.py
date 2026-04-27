from direm.services.credits_service import render_credits


def test_credits_include_locked_names() -> None:
    output = render_credits()

    assert "1D1L1R" in output
    assert "Rein Hard V — architecture, scope lock, review" in output
    assert "Bushid Ronin V — implementation executor" in output


def test_credits_match_canonical_readme_text() -> None:
    assert render_credits() == (
        "Project Owner:\n"
        "- 1D1L1R\n"
        "\n"
        "Co-authors:\n"
        "- Rein Hard V — architecture, scope lock, review\n"
        "- Bushid Ronin V — implementation executor"
    )
