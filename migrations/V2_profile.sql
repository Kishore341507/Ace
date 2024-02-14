ALTER TABLE IF EXISTS public.store
ADD COLUMN buyers BIGINT[];

CREATE TABLE IF NOT EXISTS public.profiles(
    user_id BIGINT PRIMARY KEY,
    xp BIGINT,
    nick VARCHAR,
    description VARCHAR,
    bg_blur INT,
    bg_url VARCHAR
);