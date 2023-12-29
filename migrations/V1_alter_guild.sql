ALTER TABLE IF EXISTS public.guilds
    ADD COLUMN economy jsonb;

ALTER TABLE IF EXISTS public.guilds
    ADD COLUMN games jsonb;