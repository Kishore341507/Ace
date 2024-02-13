ALTER TABLE IF EXISTS public.store
ADD COLUMN buyers BIGINT[];

CREATE TABLE IF NOT EXISTS public.profiles(
    user_id BIGINT PRIMARY KEY,
    nick VARCHAR,
    description VARCHAR,
    bg VARCHAR,
    xp BIGINT
);