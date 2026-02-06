#!/usr/bin/env python3
"""
Use Gemini API to enhance diagrams and generate professional content.
"""

import os
import json
import base64
import requests
from pathlib import Path

# Gemini API configuration
API_KEY = os.environ.get("GEMINI_API_KEY", "")
BASE_URL = "https://generativelanguage.googleapis.com/v1beta"

def list_models():
    """List available Gemini models."""
    url = f"{BASE_URL}/models?key={API_KEY}"
    response = requests.get(url)
    if response.status_code == 200:
        models = response.json().get("models", [])
        print("Available models:")
        for model in models:
            name = model.get("name", "").replace("models/", "")
            desc = model.get("description", "")[:60]
            print(f"  • {name}: {desc}...")
        return models
    else:
        print(f"Error: {response.status_code} - {response.text}")
        return []

def generate_content(prompt: str, model: str = "gemini-2.0-flash"):
    """Generate content using Gemini."""
    url = f"{BASE_URL}/models/{model}:generateContent?key={API_KEY}"

    payload = {
        "contents": [{
            "parts": [{"text": prompt}]
        }],
        "generationConfig": {
            "temperature": 0.7,
            "maxOutputTokens": 2048,
        }
    }

    response = requests.post(url, json=payload)
    if response.status_code == 200:
        result = response.json()
        text = result["candidates"][0]["content"]["parts"][0]["text"]
        return text
    else:
        print(f"Error: {response.status_code} - {response.text}")
        return None

def analyze_image(image_path: str, prompt: str, model: str = "gemini-2.0-flash"):
    """Analyze an image and get suggestions."""
    with open(image_path, "rb") as f:
        image_data = base64.b64encode(f.read()).decode()

    # Determine mime type
    ext = Path(image_path).suffix.lower()
    mime_types = {".png": "image/png", ".jpg": "image/jpeg", ".jpeg": "image/jpeg"}
    mime_type = mime_types.get(ext, "image/png")

    url = f"{BASE_URL}/models/{model}:generateContent?key={API_KEY}"

    payload = {
        "contents": [{
            "parts": [
                {"text": prompt},
                {
                    "inline_data": {
                        "mime_type": mime_type,
                        "data": image_data
                    }
                }
            ]
        }]
    }

    response = requests.post(url, json=payload)
    if response.status_code == 200:
        result = response.json()
        text = result["candidates"][0]["content"]["parts"][0]["text"]
        return text
    else:
        print(f"Error: {response.status_code} - {response.text}")
        return None

def generate_diagram_improvements():
    """Get AI suggestions for improving diagrams."""

    prompt = """You are a technical documentation expert. Generate a detailed specification for professional network architecture diagrams for a home network project called "Pi Command Center".

The project includes:
1. Raspberry Pi running Docker
2. Pi-hole for DNS and ad blocking
3. Unbound for recursive DNS resolution
4. WireGuard VPN with split routing
5. Telegram bot for remote control
6. Fail2ban and UFW for security

For each diagram type, provide:
1. Title and purpose
2. Color scheme (hex codes)
3. Node types and icons to use
4. Connection styles (solid, dashed, colors)
5. Layout recommendations
6. Labels and annotations

Diagram types needed:
- Network Architecture
- VPN Split Routing Flow
- Security Layers
- Docker Stack
- Bot Menu Structure

Be specific with colors, sizes, and professional design guidelines."""

    print("\n🤖 Generating diagram specifications with Gemini...\n")
    result = generate_content(prompt)

    if result:
        # Save to file
        with open("ai_diagram_spec.md", "w") as f:
            f.write("# AI-Generated Diagram Specifications\n\n")
            f.write(result)
        print("✓ Saved to ai_diagram_spec.md")
        return result
    return None

def analyze_existing_diagrams():
    """Analyze existing diagrams and suggest improvements."""
    diagrams = [
        "network_architecture.png",
        "vpn_split_routing.png",
        "security_layers.png",
        "bot_mockup.png"
    ]

    results = {}

    for diagram in diagrams:
        if Path(diagram).exists():
            print(f"\n🔍 Analyzing {diagram}...")

            prompt = f"""Analyze this technical diagram and provide:
1. Overall quality assessment (1-10)
2. Clarity of information
3. Visual design quality
4. Specific improvements needed
5. Professional suggestions for colors, layout, icons

Be constructive and specific. This is for a GitHub open-source project."""

            result = analyze_image(diagram, prompt)
            if result:
                results[diagram] = result
                print(f"✓ Analysis complete for {diagram}")

    # Save all analyses
    if results:
        with open("ai_diagram_analysis.md", "w") as f:
            f.write("# AI Diagram Analysis\n\n")
            for name, analysis in results.items():
                f.write(f"## {name}\n\n{analysis}\n\n---\n\n")
        print("\n✓ All analyses saved to ai_diagram_analysis.md")

    return results

def generate_readme_improvements():
    """Generate README improvements."""

    prompt = """As a technical writer expert, create an improved structure for a README.md for "Pi Command Center" - a privacy-focused home network management system.

The project:
- Uses Raspberry Pi + Docker
- Pi-hole + Unbound for private DNS
- WireGuard VPN with smart split routing
- Telegram bot for remote control
- Security monitoring (Fail2ban, UFW)

Create a modern, professional README structure with:
1. Eye-catching header section
2. Clear value proposition
3. Visual feature highlights
4. Quick start (one-liner install)
5. Architecture overview
6. Security considerations
7. Contributing guidelines
8. Professional badges

Use markdown best practices. Keep it concise but complete.
Make it visually appealing for GitHub."""

    print("\n📝 Generating README improvements...\n")
    result = generate_content(prompt)

    if result:
        with open("ai_readme_suggestions.md", "w") as f:
            f.write("# AI-Suggested README Improvements\n\n")
            f.write(result)
        print("✓ Saved to ai_readme_suggestions.md")
        return result
    return None

def main():
    if not API_KEY:
        print("❌ GEMINI_API_KEY not set")
        print("   Export it: export GEMINI_API_KEY='your_key'")
        return

    os.chdir(Path(__file__).parent)

    print("=" * 60)
    print("  Gemini API Enhancement Tool")
    print("=" * 60)

    # List available models
    print("\n📋 Checking available models...")
    list_models()

    # Generate improvements
    generate_diagram_improvements()
    generate_readme_improvements()
    analyze_existing_diagrams()

    print("\n" + "=" * 60)
    print("  ✓ All AI enhancements complete!")
    print("=" * 60)

if __name__ == "__main__":
    main()
