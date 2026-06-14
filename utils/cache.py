import asyncio
import json
import logging

class CacheManager:
    def __init__(self, db_pool, redis_pool):
        self.db = db_pool
        self.redis = redis_pool

    async def get_user(self, guild_id: int, user_id: int, initial_bank: int = 1000):
        """Fetches user from Redis, falls back to Postgres if missing, handles creation."""
        key = f"user:{guild_id}:{user_id}"
        cached = await self.redis.hgetall(key)
        if cached:
            # Parse numeric values correctly
            data = {k: int(v) if v.lstrip('-').isdigit() else v for k, v in cached.items()}
            if 'friends' in data and isinstance(data['friends'], str):
                try:
                    data['friends'] = json.loads(data['friends'])
                except:
                    data['friends'] = []
            return data
            
        # Fallback & Creation (1 query!)
        row = await self.db.fetchrow(
            """
            INSERT INTO users (id, guild_id, bank) 
            VALUES ($1, $2, $3)
            ON CONFLICT (guild_id, id) DO UPDATE 
            SET id = users.id 
            RETURNING *;
            """,
            user_id, guild_id, initial_bank
        )
        
        if row:
            data = dict(row)
            if 'friends' in data and data['friends']:
                data['friends'] = json.dumps(data['friends'])
                
            await self.redis.hset(key, mapping=data)
            await self.redis.expire(key, 3600) # 1 hour TTL
            return data
        return None

    async def increment_user_balance(self, guild_id: int, user_id: int, cash: int = 0, bank: int = 0, pvc: int = 0):
        """Atomically increments balances in Redis and asynchronously updates Postgres."""
        key = f"user:{guild_id}:{user_id}"
        
        # 1. Update Redis instantly
        if await self.redis.exists(key):
            pipeline = self.redis.pipeline()
            if cash != 0: pipeline.hincrby(key, "cash", cash)
            if bank != 0: pipeline.hincrby(key, "bank", bank)
            if pvc != 0: pipeline.hincrby(key, "pvc", pvc)
            await pipeline.execute()

        # 2. Fire and forget Postgres update
        asyncio.create_task(
            self.db.execute(
                "UPDATE users SET cash = cash + $1, bank = bank + $2, pvc = pvc + $3 WHERE id = $4 AND guild_id = $5",
                cash, bank, pvc, user_id, guild_id
            )
        )

    async def update_user(self, guild_id: int, user_id: int, **kwargs):
        """Atomically sets values in Redis and asynchronously updates Postgres."""
        key = f"user:{guild_id}:{user_id}"
        
        if await self.redis.exists(key):
            await self.redis.hset(key, mapping=kwargs)

        set_clause = ", ".join(f"{k} = ${i+1}" for i, k in enumerate(kwargs.keys()))
        values = list(kwargs.values())
        query = f"UPDATE users SET {set_clause} WHERE id = ${len(values)+1} AND guild_id = ${len(values)+2}"
        
        asyncio.create_task(
            self.db.execute(query, *values, user_id, guild_id)
        )
