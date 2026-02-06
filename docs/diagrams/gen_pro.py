#!/usr/bin/env python3
"""
Professional image generation with advanced prompts.
Uses Imagen 4.0 with carefully crafted prompts for high-quality output.
"""

import os
import base64
import requests
from pathlib import Path

API_KEY = os.environ.get("GEMINI_API_KEY", "")
BASE_URL = "https://generativelanguage.googleapis.com/v1beta"


def generate_image(prompt: str, name: str, aspect: str = "1:1"):
    """Generate high-quality image with Imagen 4.0."""

    url = f"{BASE_URL}/models/imagen-4.0-generate-001:predict?key={API_KEY}"

    payload = {
        "instances": [{"prompt": prompt}],
        "parameters": {
            "sampleCount": 1,
            "aspectRatio": aspect,
            "personGeneration": "dont_allow",
            "safetyFilterLevel": "block_few"
        }
    }

    print(f"\n🎨 Generating: {name}")
    print(f"   Aspect: {aspect}")

    response = requests.post(url, json=payload, timeout=120)

    if response.status_code == 200:
        result = response.json()
        predictions = result.get("predictions", [])
        if predictions and "bytesBase64Encoded" in predictions[0]:
            img_data = predictions[0]["bytesBase64Encoded"]
            output = f"{name}.png"
            with open(output, "wb") as f:
                f.write(base64.b64decode(img_data))
            size = os.path.getsize(output) / 1024
            print(f"   ✓ Saved: {output} ({size:.0f} KB)")
            return output

    error = response.json().get("error", {}).get("message", "Unknown")[:100]
    print(f"   ✗ Error: {error}")
    return None


# Advanced prompts - engineering grade
PROMPTS = {
    "logo": {
        "name": "logo",
        "aspect": "1:1",
        "prompt": """A minimal, geometric logo icon for a network security software product.

Design specifications:
- Central element: A stylized hexagonal shield with circuit board patterns inside
- Color palette: Deep navy blue (#1a237e) and electric cyan (#00bcd4) gradient
- Style: Flat design, clean vector-like appearance, no gradients except the main element
- Background: Pure white or transparent
- Composition: Perfectly centered, symmetrical
- Details: Subtle network node dots connected by thin lines within the shield
- Quality: Ultra sharp edges, professional corporate branding quality
- NO text, NO letters, NO words - pure iconography only

Reference style: Similar to Cloudflare, Tailscale, or WireGuard logos - modern tech security aesthetic."""
    },

    "banner": {
        "name": "hero_banner",
        "aspect": "16:9",
        "prompt": """A sophisticated dark-themed hero banner for a technology GitHub repository.

Design specifications:
- Background: Deep space gradient from #0d1117 (GitHub dark) to #161b22
- Central visual: Abstract 3D network topology visualization
- Elements: Glowing nodes connected by luminescent lines forming a mesh
- Color accents: Cyan (#58a6ff) nodes, purple (#8957e5) connections, subtle green (#3fb950) highlights
- Depth: Multiple layers creating parallax-like depth effect
- Style: Clean, modern, inspired by Vercel/Linear/Raycast aesthetics
- Composition: Central focal point with elements fading to edges
- Light effects: Subtle ambient glow around nodes, no harsh lighting
- Quality: 4K resolution appearance, crisp details

NO text, NO logos - pure abstract visualization. Professional SaaS landing page quality."""
    },

    "network": {
        "name": "architecture_hero",
        "aspect": "16:9",
        "prompt": """A professional isometric 3D technical illustration of a home network architecture.

Design specifications:
- Style: Clean isometric projection, technical illustration quality
- Background: Soft gradient from #f8fafc to #e2e8f0 (light mode friendly)
- Central hub: A detailed Raspberry Pi device rendered in 3D isometric view
- Connected elements arranged in organized layers:
  * Top layer: Cloud icons representing internet services
  * Middle layer: The Raspberry Pi with visible ports and status LEDs
  * Bottom layer: Various device icons (laptop, phone, TV, IoT devices)
- Connection lines: Smooth curved paths with directional flow indicators
- Color coding:
  * Blue (#3b82f6) for DNS/network paths
  * Purple (#8b5cf6) for VPN tunnels
  * Green (#22c55e) for security elements
  * Orange (#f97316) for monitoring/alerts
- Labels: Small, clean sans-serif typography for key components
- Quality: Vector-illustration quality, suitable for technical documentation

Professional technical diagram aesthetic like Tailscale or Cloudflare documentation."""
    },

    "security": {
        "name": "security_shield",
        "aspect": "1:1",
        "prompt": """A modern security concept illustration showing layered defense architecture.

Design specifications:
- Concept: Concentric protective shields/barriers around a central core
- Style: Semi-abstract, modern infographic illustration
- Background: Dark gradient #1e293b to #0f172a
- Layers (outside to inside):
  * Outer ring: Red/orange glow representing blocked threats (#ef4444)
  * Second ring: Amber warning layer (#f59e0b)
  * Third ring: Blue firewall layer (#3b82f6)
  * Inner core: Green safe zone (#22c55e) with subtle circuit patterns
- Visual elements: Abstract threat particles being deflected by outer layers
- Lighting: Dramatic rim lighting on each layer
- Style reference: Modern cybersecurity marketing visuals, Palo Alto Networks aesthetic
- Quality: High-end marketing material quality

NO text, pure visual metaphor for defense-in-depth security."""
    },

    "vpn": {
        "name": "vpn_routing",
        "aspect": "16:9",
        "prompt": """A clean technical diagram showing VPN split tunneling concept.

Design specifications:
- Style: Modern flat design with subtle depth
- Background: Clean white or very light gray (#fafafa)
- Layout: Left-to-right flow diagram
- Elements:
  * Left side: Single source point (device icon)
  * Center: Decision/routing node with branching
  * Right side top: Secure tunnel path (enclosed in tube/pipe visual) leading to shield icon
  * Right side bottom: Direct path (open line) leading to globe icon
- Visual distinction:
  * VPN path: Purple (#7c3aed) with lock icons, enclosed tunnel effect
  * Direct path: Blue (#2563eb) with speed indicators, open flow
- Flow indicators: Animated-looking arrows or particles showing direction
- Labels: Minimal, clean typography
- Quality: Technical documentation illustration quality

Similar to Mullvad VPN or Tailscale documentation diagrams."""
    }
}


def main():
    if not API_KEY:
        print("❌ Set GEMINI_API_KEY environment variable")
        return

    os.chdir(Path(__file__).parent)

    print("=" * 60)
    print("  Professional Image Generation - Imagen 4.0")
    print("=" * 60)

    results = []

    for key, config in PROMPTS.items():
        result = generate_image(
            config["prompt"],
            config["name"],
            config["aspect"]
        )
        if result:
            results.append(result)

    print("\n" + "=" * 60)
    if results:
        print(f"  ✓ Generated {len(results)}/{len(PROMPTS)} images")
        for r in results:
            print(f"    • {r}")
    else:
        print("  ✗ No images generated")
    print("=" * 60)


if __name__ == "__main__":
    main()
