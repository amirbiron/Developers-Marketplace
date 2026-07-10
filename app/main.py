"""אפליקציית FastAPI — נקודת הכניסה. רישום ראוטרים, CORS, וטיפול שגיאות גנרי.

עקרון (דפוס CLAUDE.md 3): שום תשובת שגיאה לא חושפת מידע פנימי (stack traces,
מזהי DB, הודעות טכניות באנגלית). המשתמש מקבל הודעה גנרית בעברית; הפרטים נכתבים ללוג.
"""

from __future__ import annotations

import logging

from fastapi import FastAPI, Request
from fastapi.exceptions import RequestValidationError
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse

from app.config import get_settings
from app.routers import avatars, developers, match, meta, referrals

logger = logging.getLogger("marketplace")
logging.basicConfig(level=logging.INFO)

settings = get_settings()

app = FastAPI(
    title="מרקטפלייס להתאמת מפתחים",
    description="התאמת מפתחים ישראלים ללקוחות שבונים פרויקט מאפס. התאמה rule-based דטרמיניסטית.",
    version="0.1.0",
)

# CORS — עם origins="*" אסור allow_credentials=True (הדפדפן דוחה), והמערכת חסרת cookies.
_origins = settings.cors_origins
app.add_middleware(
    CORSMiddleware,
    allow_origins=_origins,
    allow_credentials=_origins != ["*"],
    allow_methods=["*"],
    allow_headers=["*"],
)

# --- רישום ראוטרים ---
app.include_router(developers.router)
app.include_router(avatars.router)
app.include_router(meta.router)
app.include_router(match.router)
app.include_router(referrals.router)


@app.get("/health", tags=["health"])
async def health() -> dict[str, str]:
    return {"status": "ok"}


# --- טיפול שגיאות גנרי ---
_VALUE_ERROR_PREFIX = "Value error, "


@app.exception_handler(RequestValidationError)
async def validation_exception_handler(
    request: Request, exc: RequestValidationError
) -> JSONResponse:
    """422 — מחזיר הודעה גנרית בעברית + רשימת שדות שגויים (בלי ערכי הקלט)."""
    errors = []
    for err in exc.errors():
        # מסלול השדה בלי הקידומת "body"
        field = ".".join(str(part) for part in err.get("loc", ()) if part != "body")
        message = err.get("msg", "")
        # Pydantic מוסיף "Value error, " לפני הודעות ValueError שלנו — מנקים
        if message.startswith(_VALUE_ERROR_PREFIX):
            message = message[len(_VALUE_ERROR_PREFIX) :]
        errors.append({"field": field, "message": message})
    return JSONResponse(
        status_code=422,
        content={"detail": "הקלט שנשלח אינו תקין", "errors": errors},
    )


@app.exception_handler(Exception)
async def unhandled_exception_handler(request: Request, exc: Exception) -> JSONResponse:
    """500 — שגיאה לא צפויה. הפרטים ללוג בלבד, למשתמש הודעה גנרית."""
    logger.exception("שגיאה לא מטופלת בבקשה %s %s", request.method, request.url.path)
    return JSONResponse(
        status_code=500,
        content={"detail": "אירעה שגיאה בשרת. נסו שוב מאוחר יותר."},
    )
