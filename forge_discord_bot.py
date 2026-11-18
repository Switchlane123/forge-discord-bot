"""
SPT Forge Discord Bot
Posts new SPT 4.1.x mods from https://sp-mod.com to a Discord channel.
"""

import os
import json
import asyncio
import aiohttp
import discord
from discord.ext import tasks
from datetime import datetime

DISCORD_TOKEN = os.getenv("DISCORD_TOKEN")
CHANNEL_ID = int(os.getenv("CHANNEL_ID", "0"))
POLL_INTERVAL_MINUTES = int(os.getenv("POLL_INTERVAL", "10"))
API_URL = "https://sp-mod.com/api/v0/mods"
SEEN_FILE = "seen_mods.json"
TARGET_SPT = "4.1"

intents = discord.Intents.default()
client = discord.Client(intents=intents)

def load_seen() -> set:
    if os.path.exists(SEEN_FILE):
        with open(SEEN_FILE, "r") as f:
            return set(json.load(f))
    return set()

def save_seen(seen: set):
    with open(SEEN_FILE, "w") as f:
        json.dump(list(seen), f)

seen_ids = load_seen()

def is_target_spt(constraint: str) -> bool:
    if not constraint:
        return False
    c = constraint.replace("~", "").replace("^", "").replace(" ", "").strip()
    return c.startswith(TARGET_SPT)

async def get_latest_version(session, mod_id):
    try:
        async with session.get(f"https://sp-mod.com/api/v0/mod/{mod_id}/versions?per_page=1") as resp:
            if resp.status != 200:
                return None, None
            data = await resp.json()
            versions = data.get("data", [])
            if not versions:
                return None, None
            v = versions[0]
            return v.get("version"), v.get("spt_version_constraint", "").strip()
    except Exception:
        return None, None

async def fetch_newest_mods(session):
    async with session.get(f"{API_URL}?per_page=20") as resp:
        if resp.status != 200:
            return []
        data = await resp.json()
        last_page = data.get("meta", {}).get("last_page", 1)
    async with session.get(f"{API_URL}?per_page=20&page={last_page}") as resp:
        if resp.status != 200:
            return []
        data = await resp.json()
        return data.get("data", [])

@client.event
async def on_ready():
    print(f"Logged in as {client.user}")
    check_new_mods.start()

@tasks.loop(minutes=POLL_INTERVAL_MINUTES)
async def check_new_mods():
    global seen_ids
    channel = client.get_channel(CHANNEL_ID)
    if not channel:
        print(f"Channel {CHANNEL_ID} not found")
        return

    async with aiohttp.ClientSession() as session:
        try:
            mods = await fetch_newest_mods(session)
        except Exception as e:
            print(f"Request failed: {e}")
            return

        new_mods = []
        for mod in mods:
            mod_id = str(mod.get("id"))
            if mod_id in seen_ids:
                continue
            version, spt = await get_latest_version(session, mod_id)
            if not is_target_spt(spt):
                seen_ids.add(mod_id)
                continue
            mod["_version"] = version or "?"
            mod["_spt"] = spt or "?"
            new_mods.append(mod)
            seen_ids.add(mod_id)
            await asyncio.sleep(0.3)

    for mod in reversed(new_mods):
        owner = mod.get("owner") or {}
        embed = discord.Embed(
            title=mod.get("name", "Unknown Mod"),
            url=mod.get("detail_url") or f"https://sp-mod.com/mod/{mod.get('id')}",
            description=(mod.get("teaser") or "")[:300],
            color=0x2b2d31,
            timestamp=datetime.utcnow()
        )
        embed.add_field(name="Version", value=mod.get("_version", "?"), inline=True)
        embed.add_field(name="SPT", value=mod.get("_spt", "?"), inline=True)
        embed.add_field(name="Author", value=owner.get("name", "?"), inline=True)
        if mod.get("downloads"):
            embed.set_footer(text=f"{mod['downloads']:,} downloads")
        if mod.get("thumbnail"):
            embed.set_thumbnail(url=mod["thumbnail"])
        await channel.send(embed=embed)
        await asyncio.sleep(1)

    if new_mods:
        save_seen(seen_ids)
        print(f"Posted {len(new_mods)} new SPT 4.1 mods")

if __name__ == "__main__":
    if not DISCORD_TOKEN or CHANNEL_ID == 0:
        print("Set DISCORD_TOKEN and CHANNEL_ID environment variables")
    else:
        client.run(DISCORD_TOKEN)
