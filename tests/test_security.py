"""טסטים ל-edit-token (בעלוּת על פרופיל). בלי DB."""

from __future__ import annotations

from app.security import generate_edit_token, hash_edit_token, verify_edit_token


class TestEditToken:
    def test_generate_returns_token_and_matching_hash(self):
        token, token_hash = generate_edit_token()
        assert token
        assert token_hash == hash_edit_token(token)
        assert token != token_hash  # לא שומרים את האסימון עצמו

    def test_tokens_are_unique(self):
        t1, _ = generate_edit_token()
        t2, _ = generate_edit_token()
        assert t1 != t2

    def test_verify_correct_token(self):
        token, token_hash = generate_edit_token()
        assert verify_edit_token(token, token_hash) is True

    def test_verify_wrong_token(self):
        _, token_hash = generate_edit_token()
        assert verify_edit_token("wrong-token", token_hash) is False

    def test_verify_missing_token(self):
        _, token_hash = generate_edit_token()
        assert verify_edit_token(None, token_hash) is False
        assert verify_edit_token("", token_hash) is False

    def test_verify_missing_hash(self):
        # פרופיל בלי בעלוּת (edit_token_hash = NULL) — לא ניתן לעריכה
        token, _ = generate_edit_token()
        assert verify_edit_token(token, None) is False
