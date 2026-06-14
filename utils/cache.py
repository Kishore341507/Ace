import asyncio
import json
import logging
import os
import discord

class CacheManager:
    def __init__(self, client, db_pool, redis_pool):
        self.client = client
        self.db = db_pool
        self.redis = redis_pool
        self.webhook = None

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
            # Create a copy for Redis serialization to prevent mutating returned 'data'
            redis_data = data.copy()
            if 'friends' in redis_data and redis_data['friends'] is not None:
                redis_data['friends'] = json.dumps(redis_data['friends'])
                
            clean_data = {k: ("" if v is None else int(v) if isinstance(v, bool) else v) for k, v in redis_data.items()}
            await self.redis.hset(key, mapping=clean_data)
            await self.redis.expire(key, 3600) # 1 hour TTL
            return data
        return None

    async def _get_webhook(self):
        """Lazily fetches or creates the Discord webhook for transaction logs."""
        if self.webhook is not None:
            return self.webhook

        channel_id = os.environ.get("TRANSACTION_LOG_CHANNEL_ID")
        if not channel_id:
            self.webhook = False
            return False

        try:
            channel_id_int = int(channel_id)
            channel = self.client.get_channel(channel_id_int)
            if not channel:
                channel = await self.client.fetch_channel(channel_id_int)
        except Exception:
            self.webhook = False
            return False

        if not channel:
            self.webhook = False
            return False

        try:
            webhooks = await channel.webhooks()
            for wh in webhooks:
                if wh.user == self.client.user:
                    self.webhook = wh
                    return self.webhook

            self.webhook = await channel.create_webhook(name=f"{self.client.user.name} Logger")
            return self.webhook
        except discord.Forbidden:
            self.webhook = False
            return False
        except Exception:
            self.webhook = False
            return False

    async def _log_transaction(self, guild_id: int, user_id: int, reason: str = None, cash: int = 0, bank: int = 0, pvc: int = 0, is_absolute: bool = False):
        """Builds and sends a detailed transaction log embed to the configured channel."""
        # Only skip logging if this is a relative change and all parameters are 0
        if not is_absolute and cash == 0 and bank == 0 and pvc == 0:
            return

        channel_id = os.environ.get("TRANSACTION_LOG_CHANNEL_ID")
        if not channel_id:
            return

        try:
            channel_id_int = int(channel_id)
            channel = self.client.get_channel(channel_id_int)
            if not channel:
                channel = await self.client.fetch_channel(channel_id_int)
        except Exception:
            return

        if not channel:
            return

        # Format amounts
        def format_amount(val: int) -> str:
            if is_absolute:
                return f"{val:,}"
            if val > 0:
                return f"+{val:,}"
            elif val < 0:
                return f"{val:,}"
            return "0"

        amounts = []
        # Cash / Bank are usually grouped
        amounts.append(f"Cash: `{format_amount(cash)}`")
        amounts.append(f"Bank: `{format_amount(bank)}`")
        if pvc != 0 or is_absolute:
            amounts.append(f"PVC: `{format_amount(pvc)}`")

        amount_str = " | ".join(amounts)

        # Embed side color: green for positive / set value, red for negative
        net_change = cash + bank + pvc
        color = discord.Color.from_rgb(67, 181, 129) if net_change >= 0 else discord.Color.from_rgb(240, 71, 71)

        embed = discord.Embed(color=color)
        embed.set_author(name="Balance updated", icon_url="https://cdn.discordapp.com/emojis/1187504974226268211.png" if self.client.user.avatar else None)
        
        prefix_lbl = "Amount set to:" if is_absolute else "Amount:"
        embed.description = (
            f"**User:** <@{user_id}>\n"
            f"**{prefix_lbl}** {amount_str}\n"
            f"**Reason:** {reason or 'Not specified'}"
        )
        embed.set_footer(text=f"User ID: {user_id}")
        embed.timestamp = discord.utils.utcnow()

        # Try Webhook send
        webhook = await self._get_webhook()
        if webhook:
            try:
                avatar = self.client.user.display_avatar.url if self.client.user.avatar else None
                await webhook.send(
                    embed=embed,
                    username=f"{self.client.user.name} Logger",
                    avatar_url=avatar
                )
                return
            except Exception:
                pass

        # Fallback to direct channel send
        try:
            await channel.send(embed=embed)
        except Exception as e:
            logging.error(f"Failed to send transaction log: {e}")

    async def increment_user_balance(self, guild_id: int, user_id: int, cash: int = 0, bank: int = 0, pvc: int = 0, reason: str = None):
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

        # 3. Asynchronously trigger logging if a reason is provided
        if reason:
            asyncio.create_task(
                self._log_transaction(guild_id, user_id, reason=reason, cash=cash, bank=bank, pvc=pvc)
            )

    async def update_user(self, guild_id: int, user_id: int, reason: str = None, **kwargs):
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

        # Asynchronously trigger logging if reason is specified and cash/bank/pvc are modified
        if reason and ('cash' in kwargs or 'bank' in kwargs or 'pvc' in kwargs):
            asyncio.create_task(
                self._log_transaction(
                    guild_id,
                    user_id,
                    reason=reason,
                    cash=kwargs.get('cash', 0),
                    bank=kwargs.get('bank', 0),
                    pvc=kwargs.get('pvc', 0),
                    is_absolute=True
                )
            )
