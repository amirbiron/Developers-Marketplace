"""אימות בעלוּת על פרופיל מפתח דרך edit-token.

סוגר את פער ה-auth ל-POST/PATCH /developers: בהרשמה מייצרים אסימון סודי אקראי,
מחזירים אותו ללקוח **פעם אחת**, ושומרים ב-DB רק את ה-hash שלו. עריכה (PATCH)
דורשת את האסימון — משווים hash בזמן קבוע. האסימון בעל אנטרופיה גבוהה (256 ביט),
אז hash מהיר (SHA-256) מספיק — אין חשש dictionary attack כמו בסיסמאות.
"""

from __future__ import annotations

import hashlib
import hmac
import secrets

_TOKEN_BYTES = 32


def hash_edit_token(token: str) -> str:
    """SHA-256 hex של האסימון — זה מה שנשמר ב-DB."""
    return hashlib.sha256(token.encode("utf-8")).hexdigest()


def generate_edit_token() -> tuple[str, str]:
    """מחזיר (token גלוי, hash לשמירה). ה-token מוחזר ללקוח פעם אחת בלבד."""
    token = secrets.token_urlsafe(_TOKEN_BYTES)
    return token, hash_edit_token(token)


def verify_edit_token(token: str | None, stored_hash: str | None) -> bool:
    """השוואה בזמן קבוע. False אם חסר אסימון או hash (למשל פרופיל בלי בעלוּת)."""
    if not token or not stored_hash:
        return False
    return hmac.compare_digest(hash_edit_token(token), stored_hash)
