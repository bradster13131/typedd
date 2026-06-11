import discord
from discord.ext import commands
import asyncio
import os
import logging
import sys

# ─────────────────────────────────────────────────────────────────────────────
#  LOGGING  (Railway streams stdout)
# ─────────────────────────────────────────────────────────────────────────────
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s  [%(levelname)s]  %(message)s",
    handlers=[logging.StreamHandler(sys.stdout)],
)
log = logging.getLogger("MISERY")

# ─────────────────────────────────────────────────────────────────────────────
#  CONFIG  — all secrets from environment variables (set in Railway dashboard)
# ─────────────────────────────────────────────────────────────────────────────
BOT_TOKEN         = os.environ["BOT_TOKEN"]          # set in Railway → Variables
TICKET_CHANNEL_ID = int(os.environ.get("TICKET_CHANNEL_ID", "1514471738715537480"))
TICKET_CHANNEL_URL = os.environ.get(
    "TICKET_CHANNEL_URL",
    "https://discord.com/channels/1514452472939413545/1514471738715537480"
)
STAFF_ROLE_IDS    = {1514460196196450465, 1514460191465406544, 1514460200554463232}

# ─────────────────────────────────────────────────────────────────────────────
#  BRAND
# ─────────────────────────────────────────────────────────────────────────────
RED           = 0xB22222
LOGO_PATH     = os.path.join(os.path.dirname(os.path.abspath(__file__)), "misery_logo.png")
LOGO_FILENAME = "misery_logo.png"
LOGO_ATTACH   = f"attachment://{LOGO_FILENAME}"

def logo_file():
    return discord.File(LOGO_PATH, filename=LOGO_FILENAME)

# ─────────────────────────────────────────────────────────────────────────────
#  INTENTS
# ─────────────────────────────────────────────────────────────────────────────
intents = discord.Intents.default()
intents.members         = True
intents.message_content = True
bot = commands.Bot(command_prefix="!", intents=intents)

# ─────────────────────────────────────────────────────────────────────────────
#  SMALL-CAPS UNICODE FONT
# ─────────────────────────────────────────────────────────────────────────────
_SC = {
    'a':'ᴀ','b':'ʙ','c':'ᴄ','d':'ᴅ','e':'ᴇ','f':'ꜰ','g':'ɢ','h':'ʜ',
    'i':'ɪ','j':'ᴊ','k':'ᴋ','l':'ʟ','m':'ᴍ','n':'ɴ','o':'ᴏ','p':'ᴘ',
    'q':'Q','r':'ʀ','s':'ꜱ','t':'ᴛ','u':'ᴜ','v':'ᴠ','w':'ᴡ','x':'x',
    'y':'ʏ','z':'ᴢ', '-':'-', ' ':'-',
}
def styled(name): return ''.join(_SC.get(c, c) for c in name.lower())
def ch(emoji, name): return f"{emoji} │ {styled(name)}"
def cat(emoji, name): return f"{emoji} ── {name.upper()} ──"

# ─────────────────────────────────────────────────────────────────────────────
#  ROLE GROUPS
# ─────────────────────────────────────────────────────────────────────────────
STAFF_NAMES  = ["⚰️ Owner", "💀 Developer", "🩸 Mod"]
BUYERS_NAMES = ["⚰️ Owner", "💀 Developer", "🩸 Mod", "🔑 Customer"]
ALL_NAMES    = ["⚰️ Owner", "💀 Developer", "🩸 Mod", "🔑 Customer", "👤 Members"]

# ─────────────────────────────────────────────────────────────────────────────
#  SERVER LAYOUT
# ─────────────────────────────────────────────────────────────────────────────
SERVER_LAYOUT = [
    {
        "category": None,
        "channels": [
            {"type": "voice", "key": None,             "name": "🟢 │ WORKING",        "read": None,    "write": None},
            {"type": "voice", "key": None,             "name": "💀 │ SHOWCASE",        "read": None,    "write": None},
        ],
    },
    {
        "category": cat("☠️", "info"),
        "channels": [
            {"type": "text", "key": "announcement",   "name": ch("📣","announcement"), "read": None,    "write": "STAFF"},
            {"type": "text", "key": "tos",            "name": ch("📜","tos"),           "read": None,    "write": "STAFF"},
            {"type": "text", "key": "changelog",      "name": ch("🔥","change-log"),    "read": None,    "write": "STAFF"},
            {"type": "text", "key": "status",         "name": ch("⚡","status"),        "read": None,    "write": "STAFF"},
            {"type": "text", "key": "vouches",        "name": ch("⭐","vouches"),       "read": None,    "write": "BUYERS"},
            {"type": "text", "key": "media",          "name": ch("🎥","media"),         "read": None,    "write": "ALL"},
            {"type": "text", "key": "reselling",      "name": ch("🔗","reselling"),     "read": None,    "write": "STAFF"},
        ],
    },
    {
        "category": cat("🔴", "products"),
        "channels": [
            {"type": "text", "key": "emulator",       "name": ch("🔴","misery-emulator"), "read": None, "write": "STAFF"},
            {"type": "text", "key": "internal",       "name": ch("🔴","misery-internal"), "read": None, "write": "STAFF"},
        ],
    },
    {
        "category": cat("🎫", "support"),
        "channels": [
            {"type": "text", "key": "openticket",     "name": ch("🎫","open-ticket"),   "read": None,    "write": "ALL"},
            {"type": "text", "key": None,             "name": ch("📋","ticket-logs"),   "read": "STAFF", "write": "STAFF"},
        ],
    },
    {
        "category": cat("💬", "community"),
        "channels": [
            {"type": "text", "key": None,             "name": ch("💬","general"),       "read": None,    "write": "ALL"},
            {"type": "text", "key": None,             "name": ch("💀","memes"),         "read": None,    "write": "ALL"},
            {"type": "text", "key": None,             "name": ch("🤖","bot-commands"),  "read": None,    "write": "ALL"},
        ],
    },
    {
        "category": cat("🛡️", "staff"),
        "channels": [
            {"type": "text", "key": None,             "name": ch("🛡️","staff-chat"),    "read": "STAFF", "write": "STAFF"},
            {"type": "text", "key": None,             "name": ch("📊","staff-logs"),    "read": "STAFF", "write": "STAFF"},
            {"type": "text", "key": None,             "name": ch("⚙️","staff-cmds"),    "read": "STAFF", "write": "STAFF"},
        ],
    },
]

# ─────────────────────────────────────────────────────────────────────────────
#  PERMISSION BUILDER
# ─────────────────────────────────────────────────────────────────────────────
def resolve_group(key):
    if key is None:      return None
    if key == "STAFF":   return STAFF_NAMES
    if key == "BUYERS":  return BUYERS_NAMES
    if key == "ALL":     return ALL_NAMES
    return key

def build_overwrites(guild, read_key, write_key, role_map):
    read_roles  = resolve_group(read_key)
    write_roles = resolve_group(write_key)
    ow = {}

    # read_key is set → channel is restricted to those roles only
    if read_roles is not None:
        ow[guild.default_role] = discord.PermissionOverwrite(view_channel=False, send_messages=False)
        for rn in read_roles:
            r = role_map.get(rn)
            if r:
                can_write = bool(write_roles and rn in write_roles)
                ow[r] = discord.PermissionOverwrite(
                    view_channel=True, send_messages=can_write, read_message_history=True
                )
    else:
        # read_key is None → everyone can see the channel
        if write_roles is None:
            # No write restriction either → everyone can read and write freely
            ow[guild.default_role] = discord.PermissionOverwrite(
                view_channel=True, send_messages=True, read_message_history=True
            )
        elif write_roles == ALL_NAMES:
            # write="ALL" → literally everyone (including @everyone) can send messages
            ow[guild.default_role] = discord.PermissionOverwrite(
                view_channel=True, send_messages=True, read_message_history=True
            )
        else:
            # write restricted to specific roles, everyone can only read
            ow[guild.default_role] = discord.PermissionOverwrite(
                view_channel=True, send_messages=False, read_message_history=True
            )
            for rn in write_roles:
                r = role_map.get(rn)
                if r:
                    ow[r] = discord.PermissionOverwrite(
                        view_channel=True, send_messages=True, read_message_history=True
                    )
    return ow

# ─────────────────────────────────────────────────────────────────────────────
#  EMBEDS
# ─────────────────────────────────────────────────────────────────────────────
DIV = "```\n▰▰▰▰▰▰▰▰▰▰▰▰▰▰▰▰▰▰▰▰▰▰▰▰▰▰▰▰▰▰▰▰▰\n```"

def embed_announcement():
    e = discord.Embed(color=RED)
    e.description = (
        "```ansi\n"
        "\u001b[1;31m"
        "  ███╗   ███╗██╗███████╗███████╗██████╗ ██╗   ██╗\n"
        "  ████╗ ████║██║██╔════╝██╔════╝██╔══██╗╚██╗ ██╔╝\n"
        "  ██╔████╔██║██║███████╗█████╗  ██████╔╝ ╚████╔╝ \n"
        "  ██║╚██╔╝██║██║╚════██║██╔══╝  ██╔══██╗  ╚██╔╝  \n"
        "  ██║ ╚═╝ ██║██║███████║███████╗██║  ██║   ██║   \n"
        "  ╚═╝     ╚═╝╚═╝╚══════╝╚══════╝╚═╝  ╚═╝   ╚═╝  \n"
        "\u001b[0m"
        "```\n"
        "```ansi\n"
        "\u001b[1;31m  ☠  THE MOST POWERFUL CHEAT ON THE MARKET  ☠\u001b[0m\n"
        "\u001b[2;37m  Undetected  ·  Untouchable  ·  Unstoppable\u001b[0m\n"
        "```\n"
        "** **\n"
        "```ansi\n"
        "\u001b[1;31m  ╔══════════════════════════════════════╗\u001b[0m\n"
        "\u001b[1;31m  ║           SERVER NAVIGATION          ║\u001b[0m\n"
        "\u001b[1;31m  ╚══════════════════════════════════════╝\u001b[0m\n"
        "\u001b[0m\n"
        f"\u001b[1;37m  📣\u001b[0m  \u001b[2;37mannouncements\u001b[0m   \u001b[1;31m›\u001b[0m  Updates & news\n"
        f"\u001b[1;37m  📜\u001b[0m  \u001b[2;37mtos\u001b[0m             \u001b[1;31m›\u001b[0m  Rules you agree to\n"
        f"\u001b[1;37m  🔴\u001b[0m  \u001b[2;37mproducts\u001b[0m        \u001b[1;31m›\u001b[0m  Browse & pricing\n"
        f"\u001b[1;37m  🎫\u001b[0m  \u001b[2;37mopen-ticket\u001b[0m     \u001b[1;31m›\u001b[0m  Buy or get support\n"
        "```"
    )
    e.set_image(url=LOGO_ATTACH)
    e.set_footer(text="MISERY © 2025  ·  Undetected. Untouchable. Unstoppable.")
    return e

def embed_tos():
    e = discord.Embed(color=RED)
    e.set_thumbnail(url=LOGO_ATTACH)
    e.description = (
        "```ansi\n"
        "\u001b[1;31m  ╔══════════════════════════════════════╗\u001b[0m\n"
        "\u001b[1;31m  ║       📜  TERMS  OF  SERVICE         ║\u001b[0m\n"
        "\u001b[1;31m  ╚══════════════════════════════════════╝\u001b[0m\n"
        "\u001b[2;37m  By using any MISERY product you agree   \u001b[0m\n"
        "\u001b[2;37m  to all terms listed below.              \u001b[0m\n"
        "```\n"
        "```ansi\n"
        "\u001b[1;31m  §1  ─  NO CHARGEBACKS\u001b[0m\n"
        "\u001b[2;37m  ╰─›  All sales are final. Chargebacks result\u001b[0m\n"
        "\u001b[2;37m       in a permanent ban and fraud report.\u001b[0m\n"
        "\n"
        "\u001b[1;31m  §2  ─  NO LEAKING\u001b[0m\n"
        "\u001b[2;37m  ╰─›  Do not share, redistribute or resell any\u001b[0m\n"
        "\u001b[2;37m       software without written authorisation.\u001b[0m\n"
        "\n"
        "\u001b[1;31m  §3  ─  ACCOUNT RESPONSIBILITY\u001b[0m\n"
        "\u001b[2;37m  ╰─›  MISERY is not liable for bans, suspensions\u001b[0m\n"
        "\u001b[2;37m       or losses on your game account.\u001b[0m\n"
        "\n"
        "\u001b[1;31m  §4  ─  BUG REPORTING\u001b[0m\n"
        "\u001b[2;37m  ╰─›  Exploiting bugs instead of reporting them\u001b[0m\n"
        "\u001b[2;37m       = permanent ban, no refund.\u001b[0m\n"
        "\n"
        "\u001b[1;31m  §5  ─  STAFF AUTHORITY\u001b[0m\n"
        "\u001b[2;37m  ╰─›  Staff decisions are final. Arguing results\u001b[0m\n"
        "\u001b[2;37m       in removal with no appeal.\u001b[0m\n"
        "```"
    )
    e.set_footer(text="MISERY © 2025  ·  Terms of Service")
    return e

def embed_changelog():
    e = discord.Embed(color=RED)
    e.set_thumbnail(url=LOGO_ATTACH)
    e.description = (
        "```ansi\n"
        "\u001b[1;31m  ╔══════════════════════════════════════╗\u001b[0m\n"
        "\u001b[1;31m  ║         🔥  C H A N G E L O G        ║\u001b[0m\n"
        "\u001b[1;31m  ╚══════════════════════════════════════╝\u001b[0m\n"
        "```\n"
        "```ansi\n"
        "\u001b[1;31m  ▸  v1.0.0  ─  Initial Release\u001b[0m\n"
        "\u001b[2;37m     ╰─›  Vanguard Emulator launched\u001b[0m\n"
        "\u001b[2;37m     ╰─›  Internal Cheat launched\u001b[0m\n"
        "\u001b[2;37m     ╰─›  Auth system online\u001b[0m\n"
        "\n"
        "\u001b[1;37m  Staff will post future updates here.\u001b[0m\n"
        "```"
    )
    e.set_footer(text="MISERY © 2025  ·  Changelog")
    return e

def embed_status():
    e = discord.Embed(color=RED)
    e.set_thumbnail(url=LOGO_ATTACH)
    e.description = (
        "```ansi\n"
        "\u001b[1;31m  ╔══════════════════════════════════════╗\u001b[0m\n"
        "\u001b[1;31m  ║        ⚡  L I V E  S T A T U S      ║\u001b[0m\n"
        "\u001b[1;31m  ╚══════════════════════════════════════╝\u001b[0m\n"
        "```\n"
        "```ansi\n"
        "\u001b[1;32m  ●  MISERY EMULATOR    \u001b[0m\u001b[2;37m─────  \u001b[1;32mONLINE\u001b[0m\n"
        "\u001b[1;32m  ●  MISERY INTERNAL    \u001b[0m\u001b[2;37m─────  \u001b[1;32mONLINE\u001b[0m\n"
        "\u001b[1;32m  ●  AUTH / LOADER      \u001b[0m\u001b[2;37m─────  \u001b[1;32mONLINE\u001b[0m\n"
        "\u001b[1;32m  ●  UPDATE SERVER      \u001b[0m\u001b[2;37m─────  \u001b[1;32mONLINE\u001b[0m\n"
        "\u001b[1;32m  ●  API                \u001b[0m\u001b[2;37m─────  \u001b[1;32mONLINE\u001b[0m\n"
        "\u001b[1;32m  ●  BYPASS CORE        \u001b[0m\u001b[2;37m─────  \u001b[1;32mONLINE\u001b[0m\n"
        "```"
    )
    e.set_footer(text="MISERY © 2025  ·  Status last updated by staff")
    return e

def embed_vouches():
    e = discord.Embed(color=RED)
    e.set_thumbnail(url=LOGO_ATTACH)
    e.description = (
        "```ansi\n"
        "\u001b[1;31m  ╔══════════════════════════════════════╗\u001b[0m\n"
        "\u001b[1;31m  ║          ⭐  V O U C H E S           ║\u001b[0m\n"
        "\u001b[1;31m  ╚══════════════════════════════════════╝\u001b[0m\n"
        "\u001b[2;37m  Real reviews from real customers.       \u001b[0m\n"
        "```\n"
        "```ansi\n"
        "\u001b[1;37m  HOW TO VOUCH\u001b[0m\n"
        "\u001b[2;37m  ╰─›  Must be a verified customer\u001b[0m\n"
        "\u001b[2;37m  ╰─›  Include product + duration purchased\u001b[0m\n"
        "\u001b[2;37m  ╰─›  Fake vouches = permanent ban\u001b[0m\n"
        "```"
    )
    e.set_footer(text="MISERY © 2025  ·  Vouches")
    return e

def embed_media():
    e = discord.Embed(color=RED)
    e.set_thumbnail(url=LOGO_ATTACH)
    e.description = (
        "```ansi\n"
        "\u001b[1;31m  ╔══════════════════════════════════════╗\u001b[0m\n"
        "\u001b[1;31m  ║           🎥  M E D I A              ║\u001b[0m\n"
        "\u001b[1;31m  ╚══════════════════════════════════════╝\u001b[0m\n"
        "\u001b[2;37m  Clips, screenshots & showcases.         \u001b[0m\n"
        "```\n"
        "```ansi\n"
        "\u001b[1;37m  SUBMISSION RULES\u001b[0m\n"
        "\u001b[2;37m  ╰─›  Must feature MISERY products only\u001b[0m\n"
        "\u001b[2;37m  ╰─›  No watermarks from other providers\u001b[0m\n"
        "\u001b[2;37m  ╰─›  Staff may remove off-topic content\u001b[0m\n"
        "```"
    )
    e.set_footer(text="MISERY © 2025  ·  Media")
    return e

def embed_reselling():
    e = discord.Embed(color=RED)
    e.set_thumbnail(url=LOGO_ATTACH)
    e.description = (
        "```ansi\n"
        "\u001b[1;31m  ╔══════════════════════════════════════╗\u001b[0m\n"
        "\u001b[1;31m  ║        🔗  R E S E L L I N G         ║\u001b[0m\n"
        "\u001b[1;31m  ╚══════════════════════════════════════╝\u001b[0m\n"
        "```\n"
        "```ansi\n"
        "\u001b[1;37m  INTERESTED IN RESELLING MISERY?\u001b[0m\n"
        "\u001b[2;37m  ╰─›  Open a ticket to apply\u001b[0m\n"
        "\u001b[2;37m  ╰─›  Must have an established community\u001b[0m\n"
        "\u001b[2;37m  ╰─›  Reseller pricing available on request\u001b[0m\n"
        "\u001b[2;37m  ╰─›  Unauthorised reselling = permanent ban\u001b[0m\n"
        "```"
    )
    e.set_footer(text="MISERY © 2025  ·  Reselling")
    return e

def embed_emulator(open_ticket_mention=""):
    e = discord.Embed(color=RED)
    e.set_thumbnail(url=LOGO_ATTACH)
    e.description = (
        "```ansi\n"
        "\u001b[1;31m  ╔══════════════════════════════════════╗\u001b[0m\n"
        "\u001b[1;31m  ║   🔴  MISERY  ─  VANGUARD EMULATOR   ║\u001b[0m\n"
        "\u001b[1;31m  ╚══════════════════════════════════════╝\u001b[0m\n"
        "\u001b[2;37m  The #1 Vanguard bypass on the market.   \u001b[0m\n"
        "\u001b[2;37m  Undetected · Updated within hours.      \u001b[0m\n"
        "```\n"
        "```ansi\n"
        "\u001b[1;31m  ┌─  🛡  COMPATIBILITY  ───────────────────\u001b[0m\n"
        "\u001b[2;37m  │  ╰─›  Windows 10 & 11\u001b[0m\n"
        "\u001b[2;37m  │  ╰─›  All Motherboards\u001b[0m\n"
        "\u001b[2;37m  │  ╰─›  All CPUs & GPUs\u001b[0m\n"
        "\u001b[2;37m  │  ╰─›  HVCI On or Off\u001b[0m\n"
        "\u001b[1;31m  ├─  ⚔  FEATURES  ────────────────────────\u001b[0m\n"
        "\u001b[2;37m  │  ╰─›  Play completely without anticheat\u001b[0m\n"
        "\u001b[2;37m  │  ╰─›  Bypasses VAN 152 & -102 errors\u001b[0m\n"
        "\u001b[2;37m  │  ╰─›  Bypasses VALORANT 5\u001b[0m\n"
        "\u001b[2;37m  │  ╰─›  No game restart required\u001b[0m\n"
        "\u001b[2;37m  │  ╰─›  Bypasses HVCI · TPM · Secure Boot\u001b[0m\n"
        "\u001b[2;37m  │  ╰─›  One-click Vanguard emulation\u001b[0m\n"
        "\u001b[1;31m  ├─  💰  PRICING  ────────────────────────\u001b[0m\n"
        "\u001b[1;37m  │  ╰─›  3 Days    ─  £4.99\u001b[0m\n"
        "\u001b[1;37m  │  ╰─›  1 Week    ─  £14.99\u001b[0m\n"
        "\u001b[1;37m  │  ╰─›  1 Month   ─  £29.99\u001b[0m\n"
        "\u001b[1;37m  │  ╰─›  Lifetime  ─  £249.99\u001b[0m\n"
        "\u001b[1;31m  └─────────────────────────────────────────\u001b[0m\n"
        "```\n"
        "\n"
        f"**📩  To purchase, go to {open_ticket_mention or '`#open-ticket`'} and click Purchase**"
    )
    e.set_footer(text="MISERY © 2025  ·  Vanguard Emulator")
    return e

def embed_internal(open_ticket_mention=""):
    e = discord.Embed(color=RED)
    e.set_thumbnail(url=LOGO_ATTACH)
    e.description = (
        "```ansi\n"
        "\u001b[1;31m  ╔══════════════════════════════════════╗\u001b[0m\n"
        "\u001b[1;31m  ║     🔴  MISERY  ─  INTERNAL CHEAT    ║\u001b[0m\n"
        "\u001b[1;31m  ╚══════════════════════════════════════╝\u001b[0m\n"
        "\u001b[2;37m  Flagship internal. Full-featured.       \u001b[0m\n"
        "\u001b[2;37m  Undetected across all anticheat systems.\u001b[0m\n"
        "```\n"
        "```ansi\n"
        "\u001b[1;31m  ┌─  ⚔  FEATURES  ────────────────────────\u001b[0m\n"
        "\u001b[2;37m  │  ╰─›  Aimbot  ─  bone priority · smooth · FOV\u001b[0m\n"
        "\u001b[2;37m  │  ╰─›  ESP     ─  box · skeleton · health · dist\u001b[0m\n"
        "\u001b[2;37m  │  ╰─›  Triggerbot + silent aim\u001b[0m\n"
        "\u001b[2;37m  │  ╰─›  Radar hack\u001b[0m\n"
        "\u001b[2;37m  │  ╰─›  No-recoil & no-spread\u001b[0m\n"
        "\u001b[2;37m  │  ╰─›  Config save & cloud sync\u001b[0m\n"
        "\u001b[2;37m  │  ╰─›  HWID spoofer included\u001b[0m\n"
        "\u001b[1;31m  ├─  💰  PRICING  ────────────────────────\u001b[0m\n"
        "\u001b[1;37m  │  ╰─›  3 Days    ─  £9.99\u001b[0m\n"
        "\u001b[1;37m  │  ╰─›  1 Week    ─  £19.99\u001b[0m\n"
        "\u001b[1;37m  │  ╰─›  1 Month   ─  £49.99\u001b[0m\n"
        "\u001b[1;37m  │  ╰─›  Lifetime  ─  £349.99\u001b[0m\n"
        "\u001b[1;31m  └─────────────────────────────────────────\u001b[0m\n"
        "```\n"
        "\n"
        f"**📩  To purchase, go to {open_ticket_mention or '`#open-ticket`'} and click Purchase**"
    )
    e.set_footer(text="MISERY © 2025  ·  Internal Cheat")
    return e

def embed_ticket_panel():
    e = discord.Embed(color=RED)
    e.description = (
        "```ansi\n"
        "\u001b[1;31m  ╔══════════════════════════════════════╗\u001b[0m\n"
        "\u001b[1;31m  ║        🎫  O P E N  T I C K E T      ║\u001b[0m\n"
        "\u001b[1;31m  ╚══════════════════════════════════════╝\u001b[0m\n"
        "\u001b[2;37m  Select a category below to open a       \u001b[0m\n"
        "\u001b[2;37m  private ticket with our staff.          \u001b[0m\n"
        "```\n"
        "```ansi\n"
        "\u001b[1;31m  ┌─  CATEGORIES  ─────────────────────────\u001b[0m\n"
        "\u001b[1;37m  │  🛒  PURCHASE  \u001b[0m\u001b[2;37m─  Buy or upgrade a license\u001b[0m\n"
        "\u001b[1;37m  │  🛠  SUPPORT   \u001b[0m\u001b[2;37m─  Account & general help\u001b[0m\n"
        "\u001b[1;37m  │  ⚙  TECHNICAL \u001b[0m\u001b[2;37m─  Loader · crash · inject\u001b[0m\n"
        "\u001b[1;31m  └─────────────────────────────────────────\u001b[0m\n"
        "```"
    )
    e.set_image(url=LOGO_ATTACH)
    e.set_footer(text="MISERY © 2025  ·  Do not abuse the ticket system.")
    return e

# ─────────────────────────────────────────────────────────────────────────────
#  STAFF CHECK
# ─────────────────────────────────────────────────────────────────────────────
def is_staff(member: discord.Member) -> bool:
    return any(r.id in STAFF_ROLE_IDS for r in member.roles)

# ─────────────────────────────────────────────────────────────────────────────
#  TICKET VIEWS
# ─────────────────────────────────────────────────────────────────────────────
class TicketView(discord.ui.View):
    def __init__(self):
        super().__init__(timeout=None)

    # ── PURCHASE — creates private purchase ticket channel ──────────────────
    @discord.ui.button(label="Purchase", emoji="🛒", style=discord.ButtonStyle.danger, custom_id="ticket_purchase")
    async def purchase(self, interaction: discord.Interaction, button: discord.ui.Button):
        await self._create_ticket(interaction, "purchase")

    # ── SUPPORT — creates private ticket channel ──────────────────────────────
    @discord.ui.button(label="Support", emoji="🛠️", style=discord.ButtonStyle.secondary, custom_id="ticket_support")
    async def support(self, interaction: discord.Interaction, button: discord.ui.Button):
        await self._create_ticket(interaction, "support")

    # ── TECHNICAL — creates private ticket channel ────────────────────────────
    @discord.ui.button(label="Technical Issue", emoji="⚙️", style=discord.ButtonStyle.secondary, custom_id="ticket_technical")
    async def technical(self, interaction: discord.Interaction, button: discord.ui.Button):
        await self._create_ticket(interaction, "technical")

    # ── SHARED TICKET CREATOR ─────────────────────────────────────────────────
    async def _create_ticket(self, interaction: discord.Interaction, ticket_type: str):
        await interaction.response.defer(ephemeral=True)

        guild    = interaction.guild
        member   = interaction.user
        role_map = {r.name: r for r in guild.roles}

        safe_name   = member.name.lower().replace(" ", "-")
        ticket_name = f"{ticket_type}-{safe_name}"

        existing = discord.utils.get(guild.text_channels, name=ticket_name)
        if existing:
            await interaction.followup.send(
                f"⚠️  You already have an open ticket: {existing.mention}", ephemeral=True
            )
            return

        ticket_cat = discord.utils.get(guild.categories, name="🎟️ ── TICKETS ──")
        if not ticket_cat:
            ticket_cat = await guild.create_category("🎟️ ── TICKETS ──")

        ow = {
            guild.default_role: discord.PermissionOverwrite(view_channel=False),
            member: discord.PermissionOverwrite(
                view_channel=True, send_messages=True,
                read_message_history=True, attach_files=True, embed_links=True
            ),
        }
        for role in guild.roles:
            if role.id in STAFF_ROLE_IDS:
                ow[role] = discord.PermissionOverwrite(
                    view_channel=True, send_messages=True, read_message_history=True
                )

        ticket_ch = await guild.create_text_channel(ticket_name, category=ticket_cat, overwrites=ow)

        labels = {
            "purchase":  ("🛒  Purchase Ticket",  "What product are you looking to buy? State the license length."),
            "support":   ("🛠️  Support Ticket",   "Describe your issue in detail. Staff will assist you shortly."),
            "technical": ("⚙️  Technical Ticket", "State your OS, loader version and the exact error you see."),
        }
        title, prompt = labels.get(ticket_type, ("🎫 Ticket", "Describe your issue."))

        e = discord.Embed(color=RED)
        e.set_thumbnail(url=LOGO_ATTACH)
        e.description = (
            "```ansi\n"
            f"\u001b[1;31m  ╔══════════════════════════════════════╗\u001b[0m\n"
            f"\u001b[1;31m  ║  {title:<38}║\u001b[0m\n"
            f"\u001b[1;31m  ╚══════════════════════════════════════╝\u001b[0m\n"
            "```\n"
            "```ansi\n"
            f"\u001b[1;37m  Welcome \u001b[0m\u001b[2;37m{member.name}\u001b[0m\u001b[1;37m  ─  staff will be with you shortly.\u001b[0m\n"
            "\n"
            f"\u001b[1;31m  ╰─›  \u001b[0m\u001b[2;37m{prompt}\u001b[0m\n"
            "\n"
            "\u001b[2;37m  Staff can close this ticket with the button below.\u001b[0m\n"
            "```"
        )
        e.set_footer(text="MISERY © 2025  ·  Support Ticket")

        pings = member.mention
        for role in guild.roles:
            if role.id in STAFF_ROLE_IDS and role.mentionable:
                pings += f"  │  {role.mention}"

        await ticket_ch.send(content=pings, embed=e, file=logo_file(), view=CloseView())
        await interaction.followup.send(f"✅  Ticket opened: {ticket_ch.mention}", ephemeral=True)
        log.info(f"Ticket created: {ticket_name} by {member} ({member.id})")


class CloseView(discord.ui.View):
    def __init__(self):
        super().__init__(timeout=None)

    @discord.ui.button(label="Close Ticket", emoji="🔒", style=discord.ButtonStyle.danger, custom_id="close_ticket")
    async def close(self, interaction: discord.Interaction, button: discord.ui.Button):
        if not is_staff(interaction.user):
            await interaction.response.send_message("Only staff can close tickets.", ephemeral=True)
            return
        await interaction.response.send_message("🔒  Closing ticket in 3 seconds...")
        log.info(f"Ticket closed: {interaction.channel.name} by {interaction.user}")
        await asyncio.sleep(3)
        await interaction.channel.delete()

# ─────────────────────────────────────────────────────────────────────────────
#  EMBED MAP
# ─────────────────────────────────────────────────────────────────────────────
EMBED_MAP = {
    "announcement": embed_announcement,
    "tos":          embed_tos,
    "changelog":    embed_changelog,
    "status":       embed_status,
    "vouches":      embed_vouches,
    "media":        embed_media,
    "reselling":    embed_reselling,
    "emulator":     embed_emulator,
    "internal":     embed_internal,
}

# ─────────────────────────────────────────────────────────────────────────────
#  !build  ─  full server deploy
# ─────────────────────────────────────────────────────────────────────────────
@bot.command(name="build")
@commands.has_permissions(administrator=True)
async def build(ctx):
    guild  = ctx.guild
    author = ctx.author

    async def dm(msg):
        try:    await author.send(msg)
        except: pass

    await dm("☠️  **MISERY** build starting — do not touch the server.")
    log.info("BUILD STARTED")

    # 1. Wipe existing channels then categories
    for ch_ in list(guild.channels):
        if not isinstance(ch_, discord.CategoryChannel):
            try:    await ch_.delete()
            except: pass
            await asyncio.sleep(0.4)
    for cat_ in list(guild.categories):
        try:    await cat_.delete()
        except: pass
        await asyncio.sleep(0.4)
    log.info("Server wiped.")

    # 2. Role map
    role_map = {r.name: r for r in guild.roles}

    # 3. Build channels
    key_to_channel = {}
    for section in SERVER_LAYOUT:
        cat_name = section.get("category")
        category = None
        if cat_name:
            category = await guild.create_category(cat_name)
            await asyncio.sleep(0.4)

        for ch_def in section["channels"]:
            ow = build_overwrites(guild, ch_def.get("read"), ch_def.get("write"), role_map)
            if ch_def["type"] == "voice":
                ch_ = await guild.create_voice_channel(ch_def["name"], category=category, overwrites=ow)
            else:
                ch_ = await guild.create_text_channel(ch_def["name"], category=category, overwrites=ow)
            if ch_def.get("key"):
                key_to_channel[ch_def["key"]] = ch_
            log.info(f"Channel created: {ch_def['name']}")
            await asyncio.sleep(0.4)

    await dm("✅  Channels built.")

    # 4. Send embeds
    open_ticket_ch = key_to_channel.get("openticket")
    open_ticket_mention = open_ticket_ch.mention if open_ticket_ch else "`#open-ticket`"

    for key, fn in EMBED_MAP.items():
        ch_obj = key_to_channel.get(key)
        if ch_obj:
            try:
                if key in ("emulator", "internal"):
                    embed = fn(open_ticket_mention)
                else:
                    embed = fn()
                await ch_obj.send(embed=embed, file=logo_file())
                log.info(f"Embed sent → {key}")
            except Exception as ex:
                log.error(f"Embed error [{key}]: {ex}")
            await asyncio.sleep(0.5)

    # 5. Ticket panel
    ch_obj = key_to_channel.get("openticket")
    if ch_obj:
        try:
            await ch_obj.send(embed=embed_ticket_panel(), file=logo_file(), view=TicketView())
            log.info("Ticket panel sent.")
        except Exception as ex:
            log.error(f"Ticket panel error: {ex}")

    log.info("BUILD COMPLETE")
    await dm("☠️  **MISERY** build complete! Everything is live.")

# ─────────────────────────────────────────────────────────────────────────────
#  !close  ─  staff command
# ─────────────────────────────────────────────────────────────────────────────
@bot.command(name="close")
async def close_cmd(ctx):
    if not is_staff(ctx.author):
        await ctx.send("Only staff can close tickets.", delete_after=4)
        return
    if any(x in ctx.channel.name for x in ("support-", "technical-")):
        await ctx.send("🔒  Closing in 3 seconds...")
        await asyncio.sleep(3)
        await ctx.channel.delete()
    else:
        await ctx.send("This isn't a ticket channel.", delete_after=4)

# ─────────────────────────────────────────────────────────────────────────────
#  READY
# ─────────────────────────────────────────────────────────────────────────────
@bot.event
async def on_ready():
    bot.add_view(TicketView())
    bot.add_view(CloseView())
    log.info(f"Online ─ {bot.user}  (ID: {bot.user.id})")
    log.info("Type  !build  in your server to deploy everything.")

# ─────────────────────────────────────────────────────────────────────────────
#  ENTRY POINT
# ─────────────────────────────────────────────────────────────────────────────
if __name__ == "__main__":
    bot.run(BOT_TOKEN, log_handler=None)   # logging already configured above
