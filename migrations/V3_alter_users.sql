ALTER TABLE IF EXISTS public.users
    ADD COLUMN frozen bool DEFAULT false;