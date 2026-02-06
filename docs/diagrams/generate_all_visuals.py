#!/usr/bin/env python3
"""
Pi Command Center - Unified Visual Asset Generator
===================================================
Generates ALL visual assets with a consistent, professional style.

This script creates:
1. Logo (SVG -> PNG)
2. Hero Banner
3. Architecture Overview
4. Security Shield
5. VPN Routing Diagram
6. All Technical Diagrams (from architecture_diagrams.py)

Requirements:
    pip install diagrams pillow svgwrite cairosvg

Usage:
    python3 generate_all_visuals.py
"""

import os
import sys
from pathlib import Path

# Change to script directory
SCRIPT_DIR = Path(__file__).parent.absolute()
os.chdir(SCRIPT_DIR)

# Check dependencies
MISSING_DEPS = []
try:
    from PIL import Image, ImageDraw, ImageFont
except ImportError:
    MISSING_DEPS.append("pillow")

try:
    import svgwrite
except ImportError:
    MISSING_DEPS.append("svgwrite")

try:
    import cairosvg
except ImportError:
    MISSING_DEPS.append("cairosvg")

if MISSING_DEPS:
    print(f"Missing dependencies: {', '.join(MISSING_DEPS)}")
    print(f"Install with: pip install {' '.join(MISSING_DEPS)}")
    sys.exit(1)

# ============================================================================
# STYLE CONSTANTS - Unified Visual Identity
# ============================================================================

# Color Palette (Professional Cybersecurity Theme)
COLORS = {
    "primary": "#1a1a2e",      # Dark navy (background)
    "secondary": "#16213e",    # Slightly lighter navy
    "accent": "#0f3460",       # Blue accent
    "highlight": "#e94560",    # Red/coral highlight
    "success": "#00d9ff",      # Cyan for success/active
    "text_primary": "#ffffff", # White text
    "text_secondary": "#94a3b8", # Gray text
    "gradient_start": "#667eea", # Purple gradient
    "gradient_end": "#764ba2",   # Violet gradient
    "green": "#10b981",        # Success green
    "orange": "#f59e0b",       # Warning orange
    "red": "#ef4444",          # Danger red
    "shield_blue": "#3b82f6",  # Shield blue
}

# Typography
FONTS = {
    "title": "DejaVuSans-Bold",
    "subtitle": "DejaVuSans",
    "mono": "DejaVuSansMono",
}


def get_font(name: str, size: int):
    """Get a font, falling back to default if not found."""
    font_paths = [
        f"/usr/share/fonts/truetype/dejavu/{name}.ttf",
        f"/usr/share/fonts/TTF/{name}.ttf",
        f"/System/Library/Fonts/{name}.ttf",
        f"C:\\Windows\\Fonts\\{name}.ttf",
    ]
    for path in font_paths:
        if os.path.exists(path):
            return ImageFont.truetype(path, size)
    return ImageFont.load_default()


# ============================================================================
# LOGO GENERATOR
# ============================================================================

def create_logo():
    """
    Create the Pi Command Center logo.
    A minimalist shield with Pi symbol and network nodes.
    """
    print("  Creating logo...")

    width, height = 512, 512
    img = Image.new("RGBA", (width, height), (0, 0, 0, 0))
    draw = ImageDraw.Draw(img)

    center_x, center_y = width // 2, height // 2

    # Outer shield shape (rounded hexagon-like)
    shield_color = COLORS["shield_blue"]
    shield_outline = COLORS["success"]

    # Draw shield background
    shield_points = [
        (center_x, 50),           # Top
        (center_x + 180, 120),    # Top right
        (center_x + 180, 340),    # Bottom right
        (center_x, 470),          # Bottom point
        (center_x - 180, 340),    # Bottom left
        (center_x - 180, 120),    # Top left
    ]
    draw.polygon(shield_points, fill=COLORS["primary"], outline=shield_outline)

    # Inner shield with gradient effect (simulated)
    inner_shield = [
        (center_x, 80),
        (center_x + 150, 140),
        (center_x + 150, 310),
        (center_x, 430),
        (center_x - 150, 310),
        (center_x - 150, 140),
    ]
    draw.polygon(inner_shield, fill=COLORS["secondary"])

    # Pi symbol in center
    try:
        pi_font = get_font("DejaVuSans-Bold", 180)
    except:
        pi_font = ImageFont.load_default()

    # Draw "π" symbol
    pi_text = "π"
    bbox = draw.textbbox((0, 0), pi_text, font=pi_font)
    text_width = bbox[2] - bbox[0]
    text_height = bbox[3] - bbox[1]
    draw.text(
        (center_x - text_width // 2, center_y - text_height // 2 - 20),
        pi_text,
        fill=COLORS["success"],
        font=pi_font
    )

    # Network nodes (small circles around the shield)
    node_positions = [
        (80, 180), (432, 180),    # Top corners
        (60, 320), (452, 320),    # Middle sides
        (120, 420), (392, 420),   # Lower sides
    ]

    for x, y in node_positions:
        # Outer glow
        draw.ellipse([x-15, y-15, x+15, y+15], fill=COLORS["accent"])
        # Inner node
        draw.ellipse([x-8, y-8, x+8, y+8], fill=COLORS["success"])

    # Connection lines from nodes to center
    for x, y in node_positions:
        draw.line([(x, y), (center_x, center_y)], fill=COLORS["accent"], width=2)

    # Save
    img.save("logo.png", "PNG")
    print("    ✓ logo.png")


# ============================================================================
# HERO BANNER GENERATOR
# ============================================================================

def create_hero_banner():
    """
    Create the hero banner for README.
    Professional dark theme with network visualization.
    """
    print("  Creating hero banner...")

    width, height = 1200, 400
    img = Image.new("RGB", (width, height), COLORS["primary"])
    draw = ImageDraw.Draw(img)

    # Background gradient effect (horizontal bands)
    for i in range(height):
        ratio = i / height
        r = int(26 + (22 - 26) * ratio)
        g = int(26 + (33 - 26) * ratio)
        b = int(46 + (62 - 46) * ratio)
        draw.line([(0, i), (width, i)], fill=(r, g, b))

    # Network grid pattern
    grid_color = (255, 255, 255, 30)
    for x in range(0, width, 60):
        draw.line([(x, 0), (x, height)], fill=(59, 130, 246, 40), width=1)
    for y in range(0, height, 60):
        draw.line([(0, y), (width, y)], fill=(59, 130, 246, 40), width=1)

    # Network nodes scattered
    import random
    random.seed(42)  # Reproducible

    nodes = []
    for _ in range(25):
        x = random.randint(50, width - 50)
        y = random.randint(50, height - 50)
        nodes.append((x, y))

    # Draw connections
    for i, (x1, y1) in enumerate(nodes):
        for x2, y2 in nodes[i+1:i+4]:
            draw.line([(x1, y1), (x2, y2)], fill=(0, 217, 255, 60), width=1)

    # Draw nodes
    for x, y in nodes:
        draw.ellipse([x-4, y-4, x+4, y+4], fill=COLORS["success"])

    # Central text area (semi-transparent box)
    text_box = [width//2 - 350, height//2 - 80, width//2 + 350, height//2 + 80]

    # Draw text box with rounded effect
    for offset in range(5, 0, -1):
        alpha = 40 + offset * 10
        box = [text_box[0]-offset, text_box[1]-offset, text_box[2]+offset, text_box[3]+offset]
        draw.rounded_rectangle(box, radius=15, fill=(26, 26, 46, alpha))
    draw.rounded_rectangle(text_box, radius=10, fill=(26, 26, 46, 220))

    # Title text
    title_font = get_font("DejaVuSans-Bold", 48)
    subtitle_font = get_font("DejaVuSans", 20)

    title = "Pi Command Center"
    bbox = draw.textbbox((0, 0), title, font=title_font)
    title_width = bbox[2] - bbox[0]
    draw.text(
        (width//2 - title_width//2, height//2 - 50),
        title,
        fill=COLORS["text_primary"],
        font=title_font
    )

    subtitle = "Enterprise Security for Your Home Network"
    bbox = draw.textbbox((0, 0), subtitle, font=subtitle_font)
    sub_width = bbox[2] - bbox[0]
    draw.text(
        (width//2 - sub_width//2, height//2 + 20),
        subtitle,
        fill=COLORS["text_secondary"],
        font=subtitle_font
    )

    # Shield icons on sides
    shield_positions = [(150, height//2), (width - 150, height//2)]
    for sx, sy in shield_positions:
        # Simple shield shape
        points = [
            (sx, sy - 40),
            (sx + 35, sy - 25),
            (sx + 35, sy + 20),
            (sx, sy + 45),
            (sx - 35, sy + 20),
            (sx - 35, sy - 25),
        ]
        draw.polygon(points, fill=COLORS["accent"], outline=COLORS["success"])

    img.save("hero_banner.png", "PNG")
    print("    ✓ hero_banner.png")


# ============================================================================
# ARCHITECTURE HERO
# ============================================================================

def create_architecture_hero():
    """
    Create the main architecture overview diagram.
    Shows the complete system in a visual flow.
    """
    print("  Creating architecture hero...")

    width, height = 1200, 600
    img = Image.new("RGB", (width, height), COLORS["primary"])
    draw = ImageDraw.Draw(img)

    # Background gradient
    for i in range(height):
        ratio = i / height
        r = int(26 * (1 - ratio * 0.3))
        g = int(26 * (1 - ratio * 0.3))
        b = int(46 * (1 - ratio * 0.2))
        draw.line([(0, i), (width, i)], fill=(r, g, b))

    # Fonts
    title_font = get_font("DejaVuSans-Bold", 28)
    label_font = get_font("DejaVuSans", 14)
    small_font = get_font("DejaVuSans", 11)

    # Title
    draw.text((width//2 - 150, 20), "System Architecture", fill=COLORS["text_primary"], font=title_font)

    # Component boxes
    def draw_component(x, y, w, h, title, items, color):
        # Box with glow
        for i in range(3, 0, -1):
            draw.rounded_rectangle(
                [x-i, y-i, x+w+i, y+h+i],
                radius=8,
                outline=color,
                width=1
            )
        draw.rounded_rectangle([x, y, x+w, y+h], radius=8, fill=COLORS["secondary"], outline=color, width=2)

        # Title bar
        draw.rounded_rectangle([x, y, x+w, y+30], radius=8, fill=color)
        draw.rectangle([x, y+20, x+w, y+30], fill=color)  # Square bottom of title

        # Title text
        bbox = draw.textbbox((0, 0), title, font=label_font)
        tw = bbox[2] - bbox[0]
        draw.text((x + w//2 - tw//2, y + 7), title, fill=COLORS["text_primary"], font=label_font)

        # Items
        for i, item in enumerate(items):
            draw.text((x + 10, y + 40 + i * 18), f"• {item}", fill=COLORS["text_secondary"], font=small_font)

    # LAN Devices
    draw_component(50, 150, 180, 140, "LAN Devices",
                   ["Laptops", "Phones", "Smart TVs", "IoT Devices"], COLORS["shield_blue"])

    # Pi-hole
    draw_component(320, 100, 180, 120, "Pi-hole DNS",
                   ["Ad Blocking", "Query Logging", "DHCP Server"], COLORS["green"])

    # Unbound
    draw_component(320, 280, 180, 100, "Unbound",
                   ["Recursive DNS", "DNSSEC", "Privacy"], COLORS["green"])

    # VPN Stack
    draw_component(580, 100, 180, 160, "VPN Stack",
                   ["WireGuard", "Split Routing", "ipset Rules", "Policy Routing"], COLORS["highlight"])

    # Security Stack
    draw_component(580, 320, 180, 120, "Security",
                   ["UFW Firewall", "Fail2ban IDS", "SSH Hardening"], COLORS["orange"])

    # Telegram Bot
    draw_component(840, 200, 180, 100, "Telegram Bot",
                   ["Remote Control", "Alerts", "Monitoring"], "#9333ea")

    # Internet
    draw_component(1020, 100, 130, 80, "Internet",
                   ["Root DNS", "Web"], COLORS["text_secondary"])

    # VPN Exit
    draw_component(1020, 280, 130, 80, "VPN Exit",
                   ["Encrypted", "Geo-unlock"], COLORS["highlight"])

    # Arrows
    arrow_color = COLORS["success"]

    # LAN -> Pi-hole
    draw.line([(230, 200), (320, 160)], fill=arrow_color, width=2)

    # Pi-hole -> Unbound
    draw.line([(410, 220), (410, 280)], fill=arrow_color, width=2)

    # Pi-hole -> VPN
    draw.line([(500, 160), (580, 180)], fill=arrow_color, width=2)

    # Unbound -> Internet
    draw.line([(500, 330), (1020, 140)], fill=arrow_color, width=2)

    # VPN -> VPN Exit
    draw.line([(760, 180), (1020, 320)], fill=COLORS["highlight"], width=2)

    # Bot -> Pi-hole
    draw.line([(840, 250), (500, 160)], fill="#9333ea", width=2)

    # Legend
    draw.text((50, 520), "Traffic Flow:", fill=COLORS["text_primary"], font=label_font)
    draw.line([(170, 528), (220, 528)], fill=arrow_color, width=3)
    draw.text((230, 520), "DNS/Direct", fill=COLORS["text_secondary"], font=small_font)
    draw.line([(330, 528), (380, 528)], fill=COLORS["highlight"], width=3)
    draw.text((390, 520), "VPN Tunnel", fill=COLORS["text_secondary"], font=small_font)
    draw.line([(490, 528), (540, 528)], fill="#9333ea", width=3)
    draw.text((550, 520), "Control", fill=COLORS["text_secondary"], font=small_font)

    img.save("architecture_hero.png", "PNG")
    print("    ✓ architecture_hero.png")


# ============================================================================
# DEFENSE IN DEPTH VISUAL
# ============================================================================

def create_defense_in_depth_visual():
    """
    Create a visual representation of defense in depth layers.
    Concentric security rings.
    """
    print("  Creating defense in depth visual...")

    width, height = 800, 800
    img = Image.new("RGB", (width, height), COLORS["primary"])
    draw = ImageDraw.Draw(img)

    center_x, center_y = width // 2, height // 2

    # Fonts
    title_font = get_font("DejaVuSans-Bold", 28)
    layer_font = get_font("DejaVuSans-Bold", 14)
    detail_font = get_font("DejaVuSans", 11)

    # Title
    draw.text((center_x - 140, 20), "Defense in Depth", fill=COLORS["text_primary"], font=title_font)

    # Layers (from outer to inner)
    layers = [
        (340, COLORS["highlight"], "LAYER 1: PERIMETER", ["UFW Firewall", "Default Deny", "Port Control"]),
        (280, COLORS["orange"], "LAYER 2: DETECTION", ["Fail2ban", "Auto-ban", "Log Analysis"]),
        (220, "#eab308", "LAYER 3: AUTH", ["SSH Keys", "User Whitelist", "No Passwords"]),
        (160, COLORS["green"], "LAYER 4: CRYPTO", ["WireGuard", "SSH Ed25519", "TLS 1.3"]),
        (100, COLORS["shield_blue"], "LAYER 5: APP", ["Input Validation", "Rate Limiting", "Sanitization"]),
    ]

    for radius, color, title, details in layers:
        # Draw ring
        for i in range(3):
            draw.ellipse(
                [center_x - radius - i, center_y - radius - i,
                 center_x + radius + i, center_y + radius + i],
                outline=color, width=2
            )

        # Fill ring (slightly transparent)
        draw.ellipse(
            [center_x - radius + 5, center_y - radius + 5,
             center_x + radius - 5, center_y + radius - 5],
            fill=COLORS["secondary"]
        )

    # Center protected asset
    draw.ellipse([center_x - 50, center_y - 50, center_x + 50, center_y + 50],
                 fill=COLORS["accent"], outline=COLORS["success"], width=3)
    draw.text((center_x - 35, center_y - 20), "Protected", fill=COLORS["text_primary"], font=detail_font)
    draw.text((center_x - 28, center_y), "Assets", fill=COLORS["text_primary"], font=detail_font)

    # Layer labels on the sides
    label_positions = [
        (50, 400, layers[0]),   # Layer 1
        (50, 330, layers[1]),   # Layer 2
        (50, 260, layers[2]),   # Layer 3
        (600, 330, layers[3]),  # Layer 4
        (600, 260, layers[4]),  # Layer 5
    ]

    for x, y, (_, color, title, details) in label_positions:
        draw.rectangle([x, y, x + 150, y + 80], fill=COLORS["secondary"], outline=color, width=2)
        draw.text((x + 5, y + 5), title.split(":")[1].strip(), fill=color, font=layer_font)
        for i, detail in enumerate(details):
            draw.text((x + 10, y + 25 + i * 14), f"• {detail}", fill=COLORS["text_secondary"], font=detail_font)

    # Arrows from labels to rings
    arrow_points = [
        (200, 400, center_x - 300, center_y),
        (200, 330, center_x - 240, center_y),
        (200, 280, center_x - 180, center_y),
        (600, 340, center_x + 120, center_y),
        (600, 280, center_x + 60, center_y),
    ]

    for ax, ay, tx, ty in arrow_points:
        draw.line([(ax, ay), (int(tx), int(ty))], fill=COLORS["text_secondary"], width=1)

    img.save("security_shield.png", "PNG")
    print("    ✓ security_shield.png (defense in depth)")


# ============================================================================
# VPN ROUTING VISUAL
# ============================================================================

def create_vpn_routing_visual():
    """
    Create VPN split routing visualization.
    Shows the decision flow for traffic routing.
    """
    print("  Creating VPN routing visual...")

    width, height = 900, 500
    img = Image.new("RGB", (width, height), COLORS["primary"])
    draw = ImageDraw.Draw(img)

    # Fonts
    title_font = get_font("DejaVuSans-Bold", 24)
    label_font = get_font("DejaVuSans-Bold", 12)
    small_font = get_font("DejaVuSans", 10)

    # Title
    draw.text((width//2 - 120, 15), "VPN Split Routing", fill=COLORS["text_primary"], font=title_font)

    def draw_box(x, y, w, h, title, color, items=None):
        draw.rounded_rectangle([x, y, x+w, y+h], radius=5, fill=COLORS["secondary"], outline=color, width=2)
        bbox = draw.textbbox((0, 0), title, font=label_font)
        tw = bbox[2] - bbox[0]
        draw.text((x + w//2 - tw//2, y + 8), title, fill=color, font=label_font)
        if items:
            for i, item in enumerate(items):
                draw.text((x + 10, y + 30 + i * 14), item, fill=COLORS["text_secondary"], font=small_font)

    def draw_arrow(x1, y1, x2, y2, color, label=None):
        draw.line([(x1, y1), (x2, y2)], fill=color, width=2)
        # Arrowhead
        import math
        angle = math.atan2(y2 - y1, x2 - x1)
        arrow_length = 10
        draw.polygon([
            (x2, y2),
            (x2 - arrow_length * math.cos(angle - 0.3), y2 - arrow_length * math.sin(angle - 0.3)),
            (x2 - arrow_length * math.cos(angle + 0.3), y2 - arrow_length * math.sin(angle + 0.3)),
        ], fill=color)
        if label:
            mid_x, mid_y = (x1 + x2) // 2, (y1 + y2) // 2
            draw.text((mid_x - 20, mid_y - 15), label, fill=COLORS["text_secondary"], font=small_font)

    # Client
    draw_box(30, 200, 100, 60, "Client", COLORS["shield_blue"])

    # DNS Query
    draw_box(180, 100, 120, 80, "Pi-hole DNS", COLORS["green"], ["Query: domain?"])

    # Domain Check
    draw_box(180, 250, 120, 80, "VPN Domains", COLORS["highlight"], ["vpn-domains.txt", "netflix.com", "reddit.com"])

    # Decision Diamond
    cx, cy = 420, 200
    diamond = [(cx, cy-40), (cx+50, cy), (cx, cy+40), (cx-50, cy)]
    draw.polygon(diamond, fill=COLORS["accent"], outline=COLORS["success"], width=2)
    draw.text((cx-25, cy-8), "Match?", fill=COLORS["text_primary"], font=small_font)

    # ipset + iptables
    draw_box(520, 100, 110, 70, "ipset", COLORS["highlight"], ["Add IP to set"])
    draw_box(520, 250, 110, 70, "iptables", COLORS["orange"], ["MARK 0x1"])

    # Routing
    draw_box(680, 100, 100, 70, "WireGuard", COLORS["highlight"], ["wg0 tunnel"])
    draw_box(680, 250, 100, 70, "Direct", COLORS["green"], ["eth0 ISP"])

    # Destinations
    draw_box(820, 100, 70, 50, "VPN", COLORS["highlight"])
    draw_box(820, 260, 70, 50, "ISP", COLORS["green"])

    # Arrows
    draw_arrow(130, 230, 180, 140, COLORS["shield_blue"], "DNS")
    draw_arrow(240, 180, 240, 250, COLORS["green"])
    draw_arrow(300, 150, 370, 185, COLORS["green"])
    draw_arrow(300, 290, 370, 215, COLORS["green"])

    # Yes path (VPN)
    draw_arrow(470, 180, 520, 135, COLORS["highlight"], "Yes")
    draw_arrow(575, 170, 575, 250, COLORS["highlight"])
    draw_arrow(630, 285, 680, 285, COLORS["highlight"])
    draw_arrow(630, 135, 680, 135, COLORS["highlight"])
    draw_arrow(780, 135, 820, 125, COLORS["highlight"])

    # No path (Direct)
    draw_arrow(470, 220, 520, 285, COLORS["green"], "No")
    draw_arrow(780, 285, 820, 285, COLORS["green"])

    # Legend
    draw.text((30, 450), "Legend:", fill=COLORS["text_primary"], font=label_font)
    draw.line([(100, 458), (150, 458)], fill=COLORS["highlight"], width=3)
    draw.text((160, 450), "VPN Traffic", fill=COLORS["text_secondary"], font=small_font)
    draw.line([(260, 458), (310, 458)], fill=COLORS["green"], width=3)
    draw.text((320, 450), "Direct Traffic", fill=COLORS["text_secondary"], font=small_font)

    img.save("vpn_routing.png", "PNG")
    print("    ✓ vpn_routing.png")


# ============================================================================
# MAIN EXECUTION
# ============================================================================

def main():
    """Generate all visual assets."""
    print("=" * 60)
    print("  Pi Command Center - Visual Asset Generator")
    print("=" * 60)
    print()

    # Generate branding assets
    print("📦 Generating branding assets...")
    create_logo()
    create_hero_banner()

    # Generate diagram assets
    print("\n📊 Generating diagram assets...")
    create_architecture_hero()
    create_defense_in_depth_visual()
    create_vpn_routing_visual()

    # Run the technical diagrams script
    print("\n🔧 Generating technical diagrams...")
    try:
        # Import and run the architecture diagrams
        from architecture_diagrams import main as generate_tech_diagrams
        generate_tech_diagrams()
    except ImportError as e:
        print(f"    ⚠ Could not import architecture_diagrams: {e}")
        print("    Run 'python3 architecture_diagrams.py' separately")
    except Exception as e:
        print(f"    ⚠ Error generating technical diagrams: {e}")

    print()
    print("=" * 60)
    print("  ✓ All visual assets generated!")
    print("=" * 60)
    print()
    print("Generated files:")
    for f in sorted(SCRIPT_DIR.glob("*.png")):
        size = f.stat().st_size / 1024
        print(f"  • {f.name} ({size:.1f} KB)")


if __name__ == "__main__":
    main()
