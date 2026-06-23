from app.gui import theme


def test_palette_tokens_are_distinct_colors():
    tokens = [theme.BG, theme.PANEL, theme.CARD, theme.BORDER,
              theme.TEXT, theme.TEXT_DIM, theme.ACCENT, theme.FADER_CAP]
    assert len(set(tokens)) == len(tokens)


def test_stylesheet_contains_every_core_token():
    for token in (theme.BG, theme.TEXT, theme.CARD, theme.BORDER, theme.ACCENT):
        assert token in theme.STYLE_MAIN
