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
            {"type": "text", "key": "emulator",      "name": ch("🔴","misery-emulator"),     "read": None, "write": "STAFF"},
            {"type": "text", "key": "internal",      "name": ch("🔴","misery-internal"),     "read": None, "write": "STAFF"},
            {"type": "text", "key": "skinchanger",   "name": ch("🎨","misery-skinchanger"),  "read": None, "write": "STAFF"},
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

        # ── Collect ticket info before deletion ───────────────────────────
        ticket_name   = interaction.channel.name
        closed_by     = interaction.user
        guild         = interaction.guild
        ticket_ch     = interaction.channel

        # Grab first 40 messages for the transcript snippet
        messages = []
        async for msg in ticket_ch.history(limit=40, oldest_first=True):
            if not msg.author.bot:
                messages.append(f"{msg.author.name}: {msg.content[:200]}")

        await asyncio.sleep(3)
        await interaction.channel.delete()

        # ── Post to ticket-logs ───────────────────────────────────────────
        logs_ch = discord.utils.get(guild.text_channels, name="📋-│-ᴛɪᴄᴋᴇᴛ-ʟᴏɢꜱ".lower())
        if not logs_ch:
            # fallback: find any channel with ticket-logs in the name
            logs_ch = discord.utils.find(
                lambda c: "ticket-log" in c.name.lower(), guild.text_channels
            )
        if logs_ch:
            transcript = "\n".join(messages) if messages else "No messages recorded."
            if len(transcript) > 900:
                transcript = transcript[:900] + "\n... (truncated)"
            e = discord.Embed(color=RED)
            e.set_thumbnail(url=LOGO_ATTACH)
            e.description = (
                "```ansi\n"
                "\u001b[1;31m  ╔══════════════════════════════════════╗\u001b[0m\n"
                "\u001b[1;31m  ║        📋  T I C K E T  L O G        ║\u001b[0m\n"
                "\u001b[1;31m  ╚══════════════════════════════════════╝\u001b[0m\n"
                "```\n"
                "```ansi\n"
                f"\u001b[1;37m  Ticket   \u001b[0m\u001b[2;37m{ticket_name}\u001b[0m\n"
                f"\u001b[1;37m  Closed   \u001b[0m\u001b[2;37mby {closed_by.name}\u001b[0m\n"
                f"\u001b[1;37m  Time     \u001b[0m\u001b[2;37m<t:{int(__import__('time').time())}:F>\u001b[0m\n"
                "```\n"
                "```ansi\n"
                "\u001b[1;31m  ── Transcript (last 40 msgs) ────────────\u001b[0m\n"
                f"\u001b[2;37m{transcript}\u001b[0m\n"
                "```"
            )
            e.set_footer(text="MISERY © 2025  ·  Ticket Logs")
            try:
                await logs_ch.send(embed=e, file=logo_file())
            except Exception as ex:
                log.error(f"Ticket log send failed: {ex}")

# ─────────────────────────────────────────────────────────────────────────────
#  SECURITY SYSTEM
# ─────────────────────────────────────────────────────────────────────────────
import time
import re as _re

# Role IDs
OWNER_ROLE_ID     = 1514460191465406544
DEVELOPER_ROLE_ID = 1514460196196450465
MOD_ROLE_ID       = 1514460200554463232
MEMBER_ROLE_ID    = 1514460210419204258
ALLOWED_INVITE_ROLES = {OWNER_ROLE_ID, DEVELOPER_ROLE_ID, MOD_ROLE_ID}

# Security state
security_active   = False
spam_tracker      = {}          # user_id → [timestamps]
nuke_tracker      = {}          # user_id → {"deletes": count, "last": timestamp}

SPAM_LIMIT        = 8           # messages in SPAM_WINDOW seconds = warning
SPAM_WINDOW       = 5
NUKE_DELETE_LIMIT = 3           # channel/role deletes in NUKE_WINDOW = kick
NUKE_WINDOW       = 10

INVITE_RE = _re.compile(r"(discord\.gg/|discord\.com/invite/|discordapp\.com/invite/)\S+", _re.IGNORECASE)

def has_any_role(member, role_ids):
    return any(r.id in role_ids for r in member.roles)

async def warn_user(channel, member, reason):
    """Send a styled warning into the channel."""
    e = discord.Embed(color=RED)
    e.description = (
        "```ansi\n"
        "\u001b[1;31m  ╔══════════════════════════════════════╗\u001b[0m\n"
        "\u001b[1;31m  ║         ⚠️   W A R N I N G           ║\u001b[0m\n"
        "\u001b[1;31m  ╚══════════════════════════════════════╝\u001b[0m\n"
        "```\n"
        "```ansi\n"
        f"\u001b[1;37m  User  \u001b[0m\u001b[2;37m{member.name}\u001b[0m\n"
        f"\u001b[1;31m  ╰─›  {reason}\u001b[0m\n"
        "```"
    )
    e.set_footer(text="MISERY © 2025  ·  Security System")
    try:
        await channel.send(embed=e, delete_after=10)
    except Exception:
        pass

# ── ANTI-NUKE: track audit log channel/role deletions ────────────────────────
@bot.event
async def on_guild_channel_delete(channel):
    if not security_active:
        return
    guild = channel.guild
    await asyncio.sleep(0.5)   # let audit log populate
    try:
        async for entry in guild.audit_logs(limit=1, action=discord.AuditLogAction.channel_delete):
            perpetrator = entry.user
            if perpetrator is None or perpetrator.bot:
                return
            # Owners (top staff) are exempt
            if perpetrator.id == guild.owner_id:
                return
            # Check if this person has a dangerous role (mod or below) doing deletions
            uid = perpetrator.id
            now = time.time()
            if uid not in nuke_tracker:
                nuke_tracker[uid] = {"deletes": 0, "last": now}
            tracker = nuke_tracker[uid]
            if now - tracker["last"] > NUKE_WINDOW:
                tracker["deletes"] = 0
            tracker["deletes"] += 1
            tracker["last"] = now
            log.warning(f"[ANTI-NUKE] {perpetrator} deleted a channel ({tracker['deletes']} in window)")
            if tracker["deletes"] >= NUKE_DELETE_LIMIT:
                nuke_tracker[uid] = {"deletes": 0, "last": now}
                # Remove all dangerous roles first
                try:
                    dangerous = [r for r in perpetrator.roles if r.id in {MOD_ROLE_ID, DEVELOPER_ROLE_ID}]
                    if dangerous:
                        await perpetrator.remove_roles(*dangerous, reason="Anti-nuke: mass channel delete")
                except Exception as ex:
                    log.error(f"[ANTI-NUKE] Role remove failed: {ex}")
                # Kick
                try:
                    await guild.kick(perpetrator, reason="Anti-nuke: mass channel deletion detected")
                    log.warning(f"[ANTI-NUKE] Kicked {perpetrator} for mass channel deletion.")
                except Exception as ex:
                    log.error(f"[ANTI-NUKE] Kick failed: {ex}")
    except Exception as ex:
        log.error(f"[ANTI-NUKE] Audit log error: {ex}")

@bot.event
async def on_guild_role_delete(role):
    if not security_active:
        return
    guild = role.guild
    await asyncio.sleep(0.5)
    try:
        async for entry in guild.audit_logs(limit=1, action=discord.AuditLogAction.role_delete):
            perpetrator = entry.user
            if perpetrator is None or perpetrator.bot:
                return
            if perpetrator.id == guild.owner_id:
                return
            uid = perpetrator.id
            now = time.time()
            if uid not in nuke_tracker:
                nuke_tracker[uid] = {"deletes": 0, "last": now}
            tracker = nuke_tracker[uid]
            if now - tracker["last"] > NUKE_WINDOW:
                tracker["deletes"] = 0
            tracker["deletes"] += 1
            tracker["last"] = now
            log.warning(f"[ANTI-NUKE] {perpetrator} deleted a role ({tracker['deletes']} in window)")
            if tracker["deletes"] >= NUKE_DELETE_LIMIT:
                nuke_tracker[uid] = {"deletes": 0, "last": now}
                try:
                    dangerous = [r for r in perpetrator.roles if r.id in {MOD_ROLE_ID, DEVELOPER_ROLE_ID}]
                    if dangerous:
                        await perpetrator.remove_roles(*dangerous, reason="Anti-nuke: mass role delete")
                except Exception as ex:
                    log.error(f"[ANTI-NUKE] Role remove failed: {ex}")
                try:
                    await guild.kick(perpetrator, reason="Anti-nuke: mass role deletion detected")
                    log.warning(f"[ANTI-NUKE] Kicked {perpetrator} for mass role deletion.")
                except Exception as ex:
                    log.error(f"[ANTI-NUKE] Kick failed: {ex}")
    except Exception as ex:
        log.error(f"[ANTI-NUKE] Audit log error: {ex}")

# ── MESSAGE SECURITY: spam + invite filter ────────────────────────────────────
@bot.event
async def on_message(message):
    if not message.guild or message.author.bot:
        await bot.process_commands(message)
        return

    member = message.author

    if security_active:
        # ── INVITE FILTER ──────────────────────────────────────────────────
        if INVITE_RE.search(message.content):
            if not has_any_role(member, ALLOWED_INVITE_ROLES):
                try:
                    await message.delete()
                except Exception:
                    pass
                await warn_user(
                    message.channel, member,
                    "Discord invites are not allowed."
                )
                log.info(f"[SECURITY] Deleted invite from {member}")
                await bot.process_commands(message)
                return

        # ── SPAM FILTER ────────────────────────────────────────────────────
        uid  = member.id
        now  = time.time()
        if uid not in spam_tracker:
            spam_tracker[uid] = []
        spam_tracker[uid] = [t for t in spam_tracker[uid] if now - t < SPAM_WINDOW]
        spam_tracker[uid].append(now)

        if len(spam_tracker[uid]) >= SPAM_LIMIT:
            spam_tracker[uid] = []
            try:
                await message.delete()
            except Exception:
                pass
            await warn_user(
                message.channel, member,
                "Slow down! You are sending messages too fast."
            )
            log.info(f"[SECURITY] Spam warning issued to {member}")
            await bot.process_commands(message)
            return

    await bot.process_commands(message)

# ── !securitystart ────────────────────────────────────────────────────────────
@bot.command(name="securitystart")
@commands.has_permissions(administrator=True)
async def security_start(ctx):
    global security_active
    security_active = True
    e = discord.Embed(color=RED)
    e.description = (
        "```ansi\n"
        "\u001b[1;31m  ╔══════════════════════════════════════╗\u001b[0m\n"
        "\u001b[1;31m  ║      🛡️   S E C U R I T Y  O N       ║\u001b[0m\n"
        "\u001b[1;31m  ╚══════════════════════════════════════╝\u001b[0m\n"
        "```\n"
        "```ansi\n"
        "\u001b[1;32m  ●  Anti-spam          ACTIVE\u001b[0m\n"
        "\u001b[1;32m  ●  Invite filter       ACTIVE\u001b[0m\n"
        "\u001b[1;32m  ●  Anti-nuke           ACTIVE\u001b[0m\n"
        "\n"
        "\u001b[2;37m  Allowed invites  ─  Owner · Developer · Mod\u001b[0m\n"
        "\u001b[2;37m  Spam limit       ─  8 msgs / 5 seconds\u001b[0m\n"
        "\u001b[2;37m  Nuke threshold   ─  3 deletes / 10 seconds\u001b[0m\n"
        "```"
    )
    e.set_footer(text="MISERY © 2025  ·  Security System")
    await ctx.send(embed=e)
    log.info(f"[SECURITY] Started by {ctx.author}")

# ── !securitystop ─────────────────────────────────────────────────────────────
@bot.command(name="securitystop")
@commands.has_permissions(administrator=True)
async def security_stop(ctx):
    global security_active
    security_active = False
    e = discord.Embed(color=0x555555)
    e.description = (
        "```ansi\n"
        "\u001b[2;37m  ╔══════════════════════════════════════╗\u001b[0m\n"
        "\u001b[2;37m  ║      🔴   S E C U R I T Y  O F F     ║\u001b[0m\n"
        "\u001b[2;37m  ╚══════════════════════════════════════╝\u001b[0m\n"
        "\u001b[2;37m  All security modules disabled.          \u001b[0m\n"
        "```"
    )
    e.set_footer(text="MISERY © 2025  ·  Security System")
    await ctx.send(embed=e)
    log.info(f"[SECURITY] Stopped by {ctx.author}")

# ── INTERNAL (updated prices + full feature list) ────────────────────────────
def embed_internal_v2(open_ticket_mention=""):
    e = discord.Embed(color=RED)
    e.set_thumbnail(url=LOGO_ATTACH)
    e.description = (
        "```ansi\n"
        "\u001b[1;31m  ╔══════════════════════════════════════╗\u001b[0m\n"
        "\u001b[1;31m  ║     🔴  MISERY  ─  INTERNAL CHEAT    ║\u001b[0m\n"
        "\u001b[1;31m  ╚══════════════════════════════════════╝\u001b[0m\n"
        "\u001b[2;37m  Flagship internal. Undetected.          \u001b[0m\n"
        "```\n"
        "```ansi\n"
        "\u001b[1;31m  ┌─  🎯  AIMBOT  ──────────────────────────\u001b[0m\n"
        "\u001b[2;37m  │  Enable · Calc Spread · 360 FOV         \u001b[0m\n"
        "\u001b[2;37m  │  Visible Check · Recoil Control          \u001b[0m\n"
        "\u001b[2;37m  │  Draw FOV · FOV RGB · Smoothness         \u001b[0m\n"
        "\u001b[2;37m  │  FOV Value · Aim Key · Target Bone       \u001b[0m\n"
        "\u001b[1;31m  ├─  👁  VISUALS  ─────────────────────────\u001b[0m\n"
        "\u001b[2;37m  │  Skeleton · Box 3D · Box 2D              \u001b[0m\n"
        "\u001b[2;37m  │  Box With Health · Box Corner · Head Box \u001b[0m\n"
        "\u001b[2;37m  │  Snapline · Health Bar · Agent · Distance\u001b[0m\n"
        "\u001b[2;37m  │  Weapon · Player Name · Rank · Ammo      \u001b[0m\n"
        "\u001b[2;37m  │  WireFrame · Chams · Chams RGB · Radar   \u001b[0m\n"
        "\u001b[2;37m  │  Sound ESP · Spectator · Spike Timer     \u001b[0m\n"
        "\u001b[2;37m  │  Abilities · Visible Check               \u001b[0m\n"
        "\u001b[1;31m  ├─  ⚙  MISC  ────────────────────────────\u001b[0m\n"
        "\u001b[2;37m  │  Skip Tutorial · FOV Changer             \u001b[0m\n"
        "\u001b[2;37m  │  Aspect Ratio · Watermark · Bullet Tracers\u001b[0m\n"
        "\u001b[2;37m  │  View Model · Damage Counter · Hit Sound \u001b[0m\n"
        "\u001b[2;37m  │  China Hat · Third Person · Hit Sound Sel\u001b[0m\n"
        "\u001b[1;31m  ├─  🎨  SKINS  ───────────────────────────\u001b[0m\n"
        "\u001b[2;37m  │  Unlock All Skins · Finishers             \u001b[0m\n"
        "\u001b[2;37m  │  Only Last Kill · Gun Buddy               \u001b[0m\n"
        "\u001b[1;31m  ├─  🎨  COLORS  ──────────────────────────\u001b[0m\n"
        "\u001b[2;37m  │  ESP Visible/Hidden · Health Colors       \u001b[0m\n"
        "\u001b[2;37m  │  Chams · Watermark · Glow Intensity       \u001b[0m\n"
        "\u001b[1;31m  ├─  💾  CONFIGS  ─────────────────────────\u001b[0m\n"
        "\u001b[2;37m  │  Clipboard Import/Export · Save/Load      \u001b[0m\n"
        "\u001b[2;37m  │  UNLOAD · Menu Key                        \u001b[0m\n"
        "\u001b[1;31m  ├─  💰  PRICING  ────────────────────────\u001b[0m\n"
        "\u001b[1;37m  │  ╰─›  3 Days    ─  $20\u001b[0m\n"
        "\u001b[1;37m  │  ╰─›  1 Week    ─  $30\u001b[0m\n"
        "\u001b[1;37m  │  ╰─›  1 Month   ─  $60\u001b[0m\n"
        "\u001b[1;31m  └─────────────────────────────────────────\u001b[0m\n"
        "```\n"
        f"**📩  To purchase, go to {open_ticket_mention or '`#open-ticket`'} and click Purchase**"
    )
    e.set_footer(text="MISERY © 2025  ·  Internal Cheat")
    return e

# ── SKINCHANGER ───────────────────────────────────────────────────────────────
def embed_skinchanger(open_ticket_mention=""):
    e = discord.Embed(color=RED)
    e.set_thumbnail(url=LOGO_ATTACH)
    e.description = (
        "```ansi\n"
        "\u001b[1;31m  ╔══════════════════════════════════════╗\u001b[0m\n"
        "\u001b[1;31m  ║    🎨  MISERY  ─  SKIN CHANGER       ║\u001b[0m\n"
        "\u001b[1;31m  ╚══════════════════════════════════════╝\u001b[0m\n"
        "\u001b[2;37m  Change any skin. Undetected.            \u001b[0m\n"
        "```\n"
        "```ansi\n"
        "\u001b[1;31m  ┌─  🛡  COMPATIBILITY  ───────────────────\u001b[0m\n"
        "\u001b[2;37m  │  ╰─›  Windows 10 & 11\u001b[0m\n"
        "\u001b[2;37m  │  ╰─›  All Motherboards & CPUs\u001b[0m\n"
        "\u001b[2;37m  │  ╰─›  HVCI On or Off\u001b[0m\n"
        "\u001b[1;31m  ├─  ⚔  FEATURES  ────────────────────────\u001b[0m\n"
        "\u001b[2;37m  │  ╰─›  Unlock All Skins\u001b[0m\n"
        "\u001b[2;37m  │  ╰─›  Unlock All Colours\u001b[0m\n"
        "\u001b[2;37m  │  ╰─›  Unlock All Buddies\u001b[0m\n"
        "\u001b[2;37m  │  ╰─›  Unlock All Sprays & Cards\u001b[0m\n"
        "\u001b[2;37m  │  ╰─›  Finishers & Gun Buddies\u001b[0m\n"
        "\u001b[2;37m  │  ╰─›  Client-sided · Easy one-click use\u001b[0m\n"
        "\u001b[1;31m  ├─  💰  PRICING  ────────────────────────\u001b[0m\n"
        "\u001b[1;37m  │  ╰─›  3 Days    ─  $10\u001b[0m\n"
        "\u001b[1;37m  │  ╰─›  1 Week    ─  $20\u001b[0m\n"
        "\u001b[1;37m  │  ╰─›  1 Month   ─  $50\u001b[0m\n"
        "\u001b[1;37m  │  ╰─›  Lifetime  ─  $100\u001b[0m\n"
        "\u001b[1;31m  └─────────────────────────────────────────\u001b[0m\n"
        "```\n"
        f"**📩  To purchase, go to {open_ticket_mention or '`#open-ticket`'} and click Purchase**"
    )
    e.set_footer(text="MISERY © 2025  ·  Skin Changer")
    return e

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
    "skinchanger":  embed_skinchanger,
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
                if key in ("emulator", "internal", "skinchanger"):
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
#  !add2  ─  adds misery-internal (updated) + misery-skinchanger to products
# ─────────────────────────────────────────────────────────────────────────────
@bot.command(name="add2")
@commands.has_permissions(administrator=True)
async def add2(ctx):
    guild    = ctx.guild
    role_map = {r.name: r for r in guild.roles}

    # Find the products category (case-insensitive partial match)
    products_cat = discord.utils.find(
        lambda c: "products" in c.name.lower(), guild.categories
    )
    if not products_cat:
        await ctx.send("❌  Could not find the PRODUCTS category. Run `!build` first.", delete_after=8)
        return

    # Permissions: everyone can read, only staff can write
    ow = build_overwrites(guild, None, "STAFF", role_map)

    # Find open-ticket channel for clickable mention in embeds
    open_ticket_ch = discord.utils.find(
        lambda c: "open-ticket" in c.name.lower(), guild.text_channels
    )
    open_ticket_mention = open_ticket_ch.mention if open_ticket_ch else "`#open-ticket`"

    status_msg = await ctx.send("⚙️  Adding channels...")

    # ── misery-internal (updated embed) ──────────────────────────────────────
    internal_ch = discord.utils.find(
        lambda c: "misery-internal" in c.name.lower(), guild.text_channels
    )
    if not internal_ch:
        internal_ch = await guild.create_text_channel(
            ch("🔴", "misery-internal"), category=products_cat, overwrites=ow
        )
        await status_msg.edit(content="⚙️  Created `misery-internal`...")
    else:
        await status_msg.edit(content="⚙️  `misery-internal` exists — updating embed...")

    # Clear old messages in internal channel (up to 10)
    try:
        await internal_ch.purge(limit=10)
    except Exception:
        pass
    await internal_ch.send(embed=embed_internal_v2(open_ticket_mention), file=logo_file())
    await asyncio.sleep(0.5)

    # ── misery-skinchanger (new channel) ─────────────────────────────────────
    skin_ch = discord.utils.find(
        lambda c: "skinchanger" in c.name.lower(), guild.text_channels
    )
    if not skin_ch:
        skin_ch = await guild.create_text_channel(
            ch("🎨", "misery-skinchanger"), category=products_cat, overwrites=ow
        )
        await status_msg.edit(content="⚙️  Created `misery-skinchanger`...")
    else:
        await status_msg.edit(content="⚙️  `misery-skinchanger` exists — updating embed...")

    try:
        await skin_ch.purge(limit=10)
    except Exception:
        pass
    await skin_ch.send(embed=embed_skinchanger(open_ticket_mention), file=logo_file())
    await asyncio.sleep(0.5)

    # Done
    e = discord.Embed(color=RED)
    e.description = (
        "```ansi\n"
        "\u001b[1;31m  ╔══════════════════════════════════════╗\u001b[0m\n"
        "\u001b[1;31m  ║       ✅   A D D 2   D O N E         ║\u001b[0m\n"
        "\u001b[1;31m  ╚══════════════════════════════════════╝\u001b[0m\n"
        "```\n"
        "```ansi\n"
        "\u001b[1;32m  ●  misery-internal    ─  updated\u001b[0m\n"
        "\u001b[1;32m  ●  misery-skinchanger ─  live\u001b[0m\n"
        "```"
    )
    e.set_footer(text="MISERY © 2025  ·  !add2")
    await status_msg.delete()
    await ctx.send(embed=e)
    log.info(f"[ADD2] Completed by {ctx.author}")

# ─────────────────────────────────────────────────────────────────────────────
#  !close  ─  staff command
# ─────────────────────────────────────────────────────────────────────────────
@bot.command(name="close")
async def close_cmd(ctx):
    if not is_staff(ctx.author):
        await ctx.send("Only staff can close tickets.", delete_after=4)
        return
    if any(x in ctx.channel.name for x in ("purchase-", "support-", "technical-")):
        ticket_name = ctx.channel.name
        guild       = ctx.guild
        ticket_ch   = ctx.channel

        messages = []
        async for msg in ticket_ch.history(limit=40, oldest_first=True):
            if not msg.author.bot:
                messages.append(f"{msg.author.name}: {msg.content[:200]}")

        await ctx.send("🔒  Closing in 3 seconds...")
        await asyncio.sleep(3)
        await ctx.channel.delete()

        logs_ch = discord.utils.find(
            lambda c: "ticket-log" in c.name.lower(), guild.text_channels
        )
        if logs_ch:
            transcript = "\n".join(messages) if messages else "No messages recorded."
            if len(transcript) > 900:
                transcript = transcript[:900] + "\n... (truncated)"
            e = discord.Embed(color=RED)
            e.set_thumbnail(url=LOGO_ATTACH)
            e.description = (
                "```ansi\n"
                "\u001b[1;31m  ╔══════════════════════════════════════╗\u001b[0m\n"
                "\u001b[1;31m  ║        📋  T I C K E T  L O G        ║\u001b[0m\n"
                "\u001b[1;31m  ╚══════════════════════════════════════╝\u001b[0m\n"
                "```\n"
                "```ansi\n"
                f"\u001b[1;37m  Ticket   \u001b[0m\u001b[2;37m{ticket_name}\u001b[0m\n"
                f"\u001b[1;37m  Closed   \u001b[0m\u001b[2;37mby {ctx.author.name}\u001b[0m\n"
                f"\u001b[1;37m  Time     \u001b[0m\u001b[2;37m<t:{int(__import__('time').time())}:F>\u001b[0m\n"
                "```\n"
                "```ansi\n"
                "\u001b[1;31m  ── Transcript (last 40 msgs) ────────────\u001b[0m\n"
                f"\u001b[2;37m{transcript}\u001b[0m\n"
                "```"
            )
            e.set_footer(text="MISERY © 2025  ·  Ticket Logs")
            try:
                await logs_ch.send(embed=e, file=logo_file())
            except Exception as ex:
                log.error(f"Ticket log send failed: {ex}")
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
