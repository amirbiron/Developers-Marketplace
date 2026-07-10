-- ============================================================================
-- RLS ומדיניות פרטיות ל-Supabase (Spec §2.5 + סעיף RLS)
-- להרצה ב-SQL Editor של Supabase (או psql) *אחרי* `alembic upgrade head`.
--
-- עיקרון הפרטיות: whatsapp_e164 לעולם לא יוצא ל-client דרך anon key.
-- ה-backend (FastAPI) מתחבר בחיבור ישיר / service role ועוקף RLS *בכוונה* — הוא
-- הנתיב היחיד לנתונים. המדיניות כאן מגינה על משטח ה-anon (PostgREST) למקרה
-- שמפתח ה-anon ידלוף: גם אז אי אפשר לשלוף מספר וואטסאפ ישירות.
-- ============================================================================

-- ----------------------------------------------------------------------------
-- 1) View ציבורי — כל העמודות של developers חוץ מ-whatsapp_e164
--    (view רגיל רץ בהרשאות הבעלים, אז anon מקבל קריאה דרכו בלי גישה לטבלה עצמה)
-- ----------------------------------------------------------------------------
create or replace view public.developers_public as
select
    id,
    full_name,
    title,
    bio,
    highlight,
    avatar_url,
    project_types,
    stack,
    ai_tools,
    pricing_models,
    hourly_rate,
    availability,
    portfolio_url,
    links,
    is_verified,
    is_active,
    created_at,
    updated_at
from public.developers
where is_active = true;

-- ----------------------------------------------------------------------------
-- 2) הפעלת RLS על כל הטבלאות. ברירת המחדל של RLS היא deny-all כשאין policy —
--    לכן anon לא יכול לקרוא/לכתוב את הטבלאות ישירות (אין לנו policy ל-anon).
-- ----------------------------------------------------------------------------
alter table public.developers enable row level security;
alter table public.requests enable row level security;
alter table public.referrals enable row level security;

-- ----------------------------------------------------------------------------
-- 3) שלילת גישה ישירה של anon לטבלאות (הגנת עומק — גם ברמת GRANT, לא רק RLS)
-- ----------------------------------------------------------------------------
revoke all on public.developers from anon;
revoke all on public.requests from anon;
revoke all on public.referrals from anon;

-- ----------------------------------------------------------------------------
-- 4) גישת קריאה ל-anon רק ל-view הציבורי (בלי whatsapp_e164)
-- ----------------------------------------------------------------------------
grant select on public.developers_public to anon, authenticated;

-- ----------------------------------------------------------------------------
-- 5) Supabase Storage — bucket ציבורי לקריאה לתמונות פרופיל.
--    ההעלאה נעשית מצד השרת עם service key (ראה app/services/storage.py).
-- ----------------------------------------------------------------------------
insert into storage.buckets (id, name, public)
values ('avatars', 'avatars', true)
on conflict (id) do nothing;

-- קריאה ציבורית לתמונות ב-bucket avatars
drop policy if exists "avatars public read" on storage.objects;
create policy "avatars public read"
    on storage.objects for select
    using (bucket_id = 'avatars');
