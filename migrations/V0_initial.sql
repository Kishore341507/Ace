-- Revises: V0
-- Creation Date: 2022-04-25 03:26:29.804348 UTC
-- Reason: Initial migration

CREATE TABLE IF NOT EXISTS public.guilds
(
    id bigint NOT NULL,
    prefix character varying(1) COLLATE pg_catalog."default",
    coin character varying COLLATE pg_catalog."default",
    channels bigint[],
    manager bigint,
    am_channels bigint[],
    am_cash integer DEFAULT 200,
    am_pvc integer DEFAULT 0,
    pvc boolean NOT NULL DEFAULT false,
    pvc_channel bigint,
    pvc_category bigint,
    rate integer DEFAULT 500,
    work jsonb,
    disabled character varying[] COLLATE pg_catalog."default",
    pvc_vc bigint,
    pvc_coin character varying COLLATE pg_catalog."default",
    pvc_name character varying COLLATE pg_catalog."default",
    pvc_min integer NOT NULL DEFAULT 0,
    pvc_max integer NOT NULL DEFAULT 0,
    pvc_vc_limit integer NOT NULL DEFAULT 0,
    CONSTRAINT guilds_pkey PRIMARY KEY (id)
)

CREATE TABLE IF NOT EXISTS public.income
(
    guild_id bigint NOT NULL,
    role_id bigint NOT NULL,
    cash integer NOT NULL DEFAULT 0,
    pvc integer NOT NULL DEFAULT 0,
    bank integer NOT NULL DEFAULT 0,
    cooldown integer NOT NULL DEFAULT 43200,
    CONSTRAINT income_pkey PRIMARY KEY (guild_id, role_id)
)

CREATE TABLE IF NOT EXISTS public.pvcs
(
    guild_id bigint NOT NULL,
    id bigint NOT NULL,
    vcid bigint NOT NULL,
    duration integer NOT NULL DEFAULT 0,
    auto boolean NOT NULL DEFAULT false,
    CONSTRAINT pvcs_pkey PRIMARY KEY (guild_id, id)
)

CREATE TABLE IF NOT EXISTS public.store
(
    guild_id bigint NOT NULL,
    id integer NOT NULL DEFAULT nextval('store_id_seq'::regclass),
    name character varying COLLATE pg_catalog."default" NOT NULL,
    price integer NOT NULL,
    info text COLLATE pg_catalog."default",
    "limit" integer,
    roles bigint[],
    rroles bigint[],
    cash bigint DEFAULT 0,
    bank bigint DEFAULT 0,
    pvc bigint DEFAULT 0,
    currency integer DEFAULT 1,
    CONSTRAINT store_pkey PRIMARY KEY (id)
)

CREATE TABLE IF NOT EXISTS public.users
(
    guild_id bigint NOT NULL,
    id bigint NOT NULL,
    cash bigint NOT NULL DEFAULT 0,
    bank bigint NOT NULL DEFAULT 0,
    pvc integer NOT NULL DEFAULT 0,
    friends bigint[],
    temp bigint NOT NULL DEFAULT 0,
    CONSTRAINT users_pkey PRIMARY KEY (guild_id, id)
)