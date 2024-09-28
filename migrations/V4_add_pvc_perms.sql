ALTER TABLE IF EXISTS public.guilds
    ADD COLUMN pvc_perms jsonb;

ALTER TABLE IF EXISTS public.guilds
    ADD COLUMN pvc_public integer DEFAULT 0;