#!/usr/bin/env python3
"""
Generate professional images using Gemini's image generation capabilities.
"""

import os
import json
import base64
import requests
from pathlib import Path

API_KEY = os.environ.get("GEMINI_API_KEY", "")
BASE_URL = "https://generativelanguage.googleapis.com/v1beta"


def generate_with_gemini_native(prompt: str, output_name: str = "generated"):
    """Generate image using Gemini's native image generation."""

    # Use gemini-2.0-flash with image output
    url = f"{BASE_URL}/models/gemini-2.0-flash-exp:generateContent?key={API_KEY}"

    payload = {
        "contents": [{
            "parts": [{
                "text": f"Generate an image: {prompt}"
            }]
        }],
        "generationConfig": {
            "responseModalities": ["TEXT", "IMAGE"]
        }
    }

    print(f"  Generating with gemini-2.0-flash-exp...")
    response = requests.post(url, json=payload)

    if response.status_code == 200:
        result = response.json()
        candidates = result.get("candidates", [])
        if candidates:
            parts = candidates[0].get("content", {}).get("parts", [])
            for part in parts:
                if "inlineData" in part:
                    image_data = part["inlineData"].get("data", "")
                    mime_type = part["inlineData"].get("mimeType", "image/png")
                    if image_data:
                        ext = "png" if "png" in mime_type else "jpg"
                        output_path = f"{output_name}.{ext}"
                        with open(output_path, "wb") as f:
                            f.write(base64.b64decode(image_data))
                        print(f"  ✓ Saved: {output_path}")
                        return output_path
        print(f"  ⚠ No image in response")
        return None
    else:
        try:
            error = response.json().get("error", {}).get("message", "Unknown error")
        except:
            error = response.text[:200]
        print(f"  ✗ Error: {error}")
        return None


def generate_with_imagen(prompt: str, output_name: str = "generated"):
    """Generate image using Imagen 4.0."""

    url = f"{BASE_URL}/models/imagen-4.0-generate-001:predict?key={API_KEY}"

    payload = {
        "instances": [{
            "prompt": prompt
        }],
        "parameters": {
            "sampleCount": 1,
            "aspectRatio": "16:9"
        }
    }

    print(f"  Generating with imagen-4.0-generate-001...")
    response = requests.post(url, json=payload)

    if response.status_code == 200:
        result = response.json()
        predictions = result.get("predictions", [])
        if predictions:
            image_data = predictions[0].get("bytesBase64Encoded", "")
            if image_data:
                output_path = f"{output_name}.png"
                with open(output_path, "wb") as f:
                    f.write(base64.b64decode(image_data))
                print(f"  ✓ Saved: {output_path}")
                return output_path
        print(f"  ⚠ No predictions in response")
        return None
    else:
        try:
            error = response.json().get("error", {}).get("message", "Unknown error")
        except:
            error = response.text[:200] if response.text else f"Status {response.status_code}"
        print(f"  ✗ Error: {error}")
        return None


def generate_text_description(prompt: str) -> str:
    """Use Gemini to generate detailed image description for manual creation."""

    url = f"{BASE_URL}/models/gemini-2.0-flash:generateContent?key={API_KEY}"

    payload = {
        "contents": [{
            "parts": [{
                "text": f"""Based on this request, create a detailed specification for a professional image that a designer could create:

Request: {prompt}

Provide:
1. Exact dimensions and format
2. Color palette with hex codes
3. Layout description (precise positions)
4. Typography (if any)
5. Icon/element descriptions
6. SVG code if possible for simple elements

Be extremely specific and detailed."""
            }]
        }]
    }

    response = requests.post(url, json=payload)
    if response.status_code == 200:
        result = response.json()
        return result["candidates"][0]["content"]["parts"][0]["text"]
    return None


def main():
    if not API_KEY:
        print("❌ GEMINI_API_KEY not set")
        return

    os.chdir(Path(__file__).parent)

    print("=" * 60)
    print("  AI Image Generation")
    print("=" * 60)

    # Image prompts
    images = [
        {
            "name": "logo_picommand",
            "prompt": "Professional minimalist logo for 'Pi Command Center' tech project. Raspberry Pi icon combined with network shield. Colors: deep blue and raspberry red. Flat design, no text, square format."
        },
        {
            "name": "banner_hero",
            "prompt": "Wide tech banner for GitHub project. Abstract network visualization with glowing nodes and connections. Dark blue background with cyan and purple accents. Modern, professional, 16:9 ratio."
        },
        {
            "name": "network_visual",
            "prompt": "Isometric network diagram. Central Raspberry Pi connected to DNS servers, VPN tunnel, firewall, and home devices. Dark theme with glowing connections. Blue, purple, green color coding."
        }
    ]

    print(f"\n📸 Attempting to generate {len(images)} images...\n")

    generated = []
    specs = []

    for img in images:
        print(f"\n🎨 {img['name']}:")

        # Try native Gemini first
        result = generate_with_gemini_native(img["prompt"], img["name"])

        if not result:
            # Try Imagen
            result = generate_with_imagen(img["prompt"], img["name"])

        if result:
            generated.append(result)
        else:
            # Generate specification for manual creation
            print(f"  📝 Generating design specification instead...")
            spec = generate_text_description(img["prompt"])
            if spec:
                spec_file = f"{img['name']}_spec.md"
                with open(spec_file, "w") as f:
                    f.write(f"# Design Specification: {img['name']}\n\n")
                    f.write(f"**Prompt:** {img['prompt']}\n\n")
                    f.write("---\n\n")
                    f.write(spec)
                specs.append(spec_file)
                print(f"  ✓ Spec saved: {spec_file}")

    print("\n" + "=" * 60)
    print("  Summary")
    print("=" * 60)

    if generated:
        print(f"\n✓ Generated {len(generated)} images:")
        for g in generated:
            print(f"  • {g}")

    if specs:
        print(f"\n📝 Created {len(specs)} design specifications:")
        for s in specs:
            print(f"  • {s}")

    if not generated and not specs:
        print("\n⚠ No images or specs were generated.")
        print("  The API may require billing or specific permissions.")


if __name__ == "__main__":
    main()
