#!/usr/bin/env python3
"""
Generate professional Telegram bot mockup image.
"""

from PIL import Image, ImageDraw, ImageFont
import os

# Colors (Telegram dark theme)
COLORS = {
    "bg": "#17212b",
    "header": "#242f3d",
    "bubble_in": "#182533",
    "bubble_out": "#2b5278",
    "text": "#ffffff",
    "text_dim": "#708499",
    "accent": "#5eb5f7",
    "green": "#5dd577",
    "red": "#ff6b6b",
    "orange": "#ffb347",
    "purple": "#a78bfa",
}

def create_telegram_mockup():
    """Create a professional Telegram bot interface mockup."""

    # Image dimensions (mobile-like)
    width, height = 400, 700
    img = Image.new("RGB", (width, height), COLORS["bg"])
    draw = ImageDraw.Draw(img)

    # Try to load a nice font, fallback to default
    try:
        font_large = ImageFont.truetype("/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf", 18)
        font_medium = ImageFont.truetype("/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf", 14)
        font_small = ImageFont.truetype("/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf", 12)
        font_emoji = ImageFont.truetype("/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf", 16)
    except:
        font_large = ImageFont.load_default()
        font_medium = font_large
        font_small = font_large
        font_emoji = font_large

    # Header bar
    draw.rectangle([0, 0, width, 60], fill=COLORS["header"])
    draw.ellipse([15, 12, 51, 48], fill=COLORS["accent"])
    draw.text((60, 12), "Pi Command Center", font=font_large, fill=COLORS["text"])
    draw.text((60, 35), "bot • online", font=font_small, fill=COLORS["green"])

    y = 80

    # Status message bubble
    bubble_width = 340
    bubble_x = 30

    # Main status card
    card_height = 200
    draw.rounded_rectangle(
        [bubble_x, y, bubble_x + bubble_width, y + card_height],
        radius=15,
        fill=COLORS["bubble_in"]
    )

    # Status content
    status_items = [
        ("🏠", "Pi Command Center", COLORS["text"]),
        ("", "━━━━━━━━━━━━━━━━━━━━", COLORS["text_dim"]),
        ("🌐", "Public IP: 85.xxx.xxx.xxx", COLORS["text"]),
        ("🛡️", "Ads blocked: 1,247 today", COLORS["green"]),
        ("📱", "Devices: 8 online", COLORS["accent"]),
        ("🔐", "VPN: Split Mode (15 domains)", COLORS["purple"]),
        ("🖥️", "CPU: 12% • RAM: 45% • 52°C", COLORS["text"]),
    ]

    text_y = y + 15
    for emoji, text, color in status_items:
        if emoji:
            draw.text((bubble_x + 15, text_y), f"{emoji}  {text}", font=font_medium, fill=color)
        else:
            draw.text((bubble_x + 15, text_y), text, font=font_small, fill=color)
        text_y += 25

    y += card_height + 20

    # Menu buttons - Row 1
    btn_width = 155
    btn_height = 45
    btn_gap = 15

    buttons_row1 = [
        ("🔍 Network", COLORS["accent"]),
        ("🛡️ Pi-hole", COLORS["green"]),
    ]

    for i, (label, color) in enumerate(buttons_row1):
        bx = bubble_x + i * (btn_width + btn_gap)
        draw.rounded_rectangle(
            [bx, y, bx + btn_width, y + btn_height],
            radius=10,
            fill=COLORS["header"],
            outline=color,
            width=2
        )
        # Center text
        bbox = draw.textbbox((0, 0), label, font=font_medium)
        tw = bbox[2] - bbox[0]
        draw.text((bx + (btn_width - tw) // 2, y + 12), label, font=font_medium, fill=color)

    y += btn_height + 10

    # Menu buttons - Row 2
    buttons_row2 = [
        ("🖥️ System", COLORS["orange"]),
        ("📱 Devices", COLORS["accent"]),
    ]

    for i, (label, color) in enumerate(buttons_row2):
        bx = bubble_x + i * (btn_width + btn_gap)
        draw.rounded_rectangle(
            [bx, y, bx + btn_width, y + btn_height],
            radius=10,
            fill=COLORS["header"],
            outline=color,
            width=2
        )
        bbox = draw.textbbox((0, 0), label, font=font_medium)
        tw = bbox[2] - bbox[0]
        draw.text((bx + (btn_width - tw) // 2, y + 12), label, font=font_medium, fill=color)

    y += btn_height + 10

    # Menu buttons - Row 3
    buttons_row3 = [
        ("🔐 VPN", COLORS["purple"]),
        ("🔒 Security", COLORS["red"]),
    ]

    for i, (label, color) in enumerate(buttons_row3):
        bx = bubble_x + i * (btn_width + btn_gap)
        draw.rounded_rectangle(
            [bx, y, bx + btn_width, y + btn_height],
            radius=10,
            fill=COLORS["header"],
            outline=color,
            width=2
        )
        bbox = draw.textbbox((0, 0), label, font=font_medium)
        tw = bbox[2] - bbox[0]
        draw.text((bx + (btn_width - tw) // 2, y + 12), label, font=font_medium, fill=color)

    y += btn_height + 10

    # Tools button (full width)
    draw.rounded_rectangle(
        [bubble_x, y, bubble_x + bubble_width, y + btn_height],
        radius=10,
        fill=COLORS["header"],
        outline=COLORS["text_dim"],
        width=2
    )
    label = "🔧 Tools"
    bbox = draw.textbbox((0, 0), label, font=font_medium)
    tw = bbox[2] - bbox[0]
    draw.text((bubble_x + (bubble_width - tw) // 2, y + 12), label, font=font_medium, fill=COLORS["text_dim"])

    y += btn_height + 15

    # Refresh button
    draw.rounded_rectangle(
        [bubble_x + 100, y, bubble_x + 240, y + 40],
        radius=20,
        fill=COLORS["accent"]
    )
    label = "🔄 Refresh"
    bbox = draw.textbbox((0, 0), label, font=font_medium)
    tw = bbox[2] - bbox[0]
    draw.text((bubble_x + 170 - tw // 2, y + 10), label, font=font_medium, fill=COLORS["text"])

    y += 60

    # Time stamp
    draw.text((width - 60, y), "12:34", font=font_small, fill=COLORS["text_dim"])

    # Input bar at bottom
    draw.rectangle([0, height - 55, width, height], fill=COLORS["header"])
    draw.rounded_rectangle(
        [15, height - 45, width - 70, height - 10],
        radius=20,
        fill=COLORS["bg"]
    )
    draw.text((30, height - 35), "Message...", font=font_medium, fill=COLORS["text_dim"])

    # Send button
    draw.ellipse([width - 55, height - 45, width - 15, height - 10], fill=COLORS["accent"])

    return img


def create_feature_cards():
    """Create feature highlight cards."""

    cards = [
        {
            "title": "Network-Wide Ad Blocking",
            "icon": "🛡️",
            "stats": ["1M+ domains blocked", "All devices protected", "No apps needed"],
            "color": COLORS["green"]
        },
        {
            "title": "Smart VPN Routing",
            "icon": "🔐",
            "stats": ["Split tunneling", "Domain-based routing", "No speed loss"],
            "color": COLORS["purple"]
        },
        {
            "title": "Security Monitoring",
            "icon": "🔒",
            "stats": ["Intrusion detection", "Auto IP banning", "Real-time alerts"],
            "color": COLORS["red"]
        },
    ]

    card_width = 280
    card_height = 140
    total_width = card_width * 3 + 40

    img = Image.new("RGB", (total_width, card_height + 20), "#0d1117")
    draw = ImageDraw.Draw(img)

    try:
        font_title = ImageFont.truetype("/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf", 16)
        font_body = ImageFont.truetype("/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf", 12)
    except:
        font_title = ImageFont.load_default()
        font_body = font_title

    for i, card in enumerate(cards):
        x = 10 + i * (card_width + 10)

        # Card background
        draw.rounded_rectangle(
            [x, 10, x + card_width, card_height],
            radius=12,
            fill="#161b22",
            outline=card["color"],
            width=2
        )

        # Icon and title
        draw.text((x + 15, 20), f"{card['icon']} {card['title']}", font=font_title, fill=COLORS["text"])

        # Stats
        y = 50
        for stat in card["stats"]:
            draw.text((x + 20, y), f"• {stat}", font=font_body, fill=COLORS["text_dim"])
            y += 22

    return img


if __name__ == "__main__":
    os.chdir(os.path.dirname(os.path.abspath(__file__)))

    print("Generating professional mockups...")

    # Bot interface mockup
    mockup = create_telegram_mockup()
    mockup.save("bot_mockup.png", quality=95)
    print("  ✓ bot_mockup.png")

    # Feature cards
    features = create_feature_cards()
    features.save("feature_cards.png", quality=95)
    print("  ✓ feature_cards.png")

    print("Done!")
