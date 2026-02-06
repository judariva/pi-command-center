#!/usr/bin/env python3
"""Create a professional logo for Pi Command Center."""

import matplotlib.pyplot as plt
import matplotlib.patches as patches
import numpy as np
import os

OUTPUT_DIR = os.path.dirname(os.path.abspath(__file__)) + '/assets'
os.makedirs(OUTPUT_DIR, exist_ok=True)

def create_logo():
    """Create the main logo."""
    fig, ax = plt.subplots(figsize=(4, 4), facecolor='none')
    ax.set_xlim(-1.2, 1.2)
    ax.set_ylim(-1.2, 1.2)
    ax.set_aspect('equal')
    ax.axis('off')

    # Outer circle (shield effect)
    circle_outer = patches.Circle((0, 0), 1.0, fill=True,
                                    facecolor='#1a1a2e', edgecolor='#16213e', linewidth=3)
    ax.add_patch(circle_outer)

    # Inner circle
    circle_inner = patches.Circle((0, 0), 0.85, fill=True,
                                    facecolor='#16213e', edgecolor='#0f3460', linewidth=2)
    ax.add_patch(circle_inner)

    # Raspberry Pi symbol (simplified)
    # Main berry body
    berry = patches.Circle((0, -0.1), 0.45, fill=True,
                            facecolor='#C51A4A', edgecolor='#8B0A2A', linewidth=2)
    ax.add_patch(berry)

    # Leaf
    leaf_points = np.array([
        [0, 0.35],
        [-0.15, 0.55],
        [0, 0.7],
        [0.15, 0.55],
    ])
    leaf = patches.Polygon(leaf_points, fill=True,
                           facecolor='#27AE60', edgecolor='#1E8449', linewidth=1.5)
    ax.add_patch(leaf)

    # Network lines (representing connectivity)
    angles = [30, 150, 270]
    for angle in angles:
        rad = np.radians(angle)
        x1, y1 = 0.45 * np.cos(rad), 0.45 * np.sin(rad) - 0.1
        x2, y2 = 0.75 * np.cos(rad), 0.75 * np.sin(rad) - 0.1
        ax.plot([x1, x2], [y1, y2], color='#00d4ff', linewidth=3, solid_capstyle='round')
        # Endpoint dot
        ax.plot(x2, y2, 'o', color='#00d4ff', markersize=8)

    # Save
    plt.savefig(f'{OUTPUT_DIR}/logo.png', dpi=150, bbox_inches='tight',
                transparent=True, pad_inches=0.1)
    plt.close()
    print(f"✓ Logo saved to {OUTPUT_DIR}/logo.png")


def create_banner():
    """Create a banner for social media."""
    fig, ax = plt.subplots(figsize=(12, 6), facecolor='#1a1a2e')
    ax.set_xlim(0, 12)
    ax.set_ylim(0, 6)
    ax.set_aspect('equal')
    ax.axis('off')

    # Gradient background effect (using rectangles)
    for i in range(20):
        alpha = 0.02
        rect = patches.Rectangle((0, i*0.3), 12, 0.3,
                                   facecolor='#0f3460', alpha=alpha)
        ax.add_patch(rect)

    # Logo area (simplified raspberry)
    berry = patches.Circle((2, 3), 1.2, fill=True,
                            facecolor='#C51A4A', edgecolor='#8B0A2A', linewidth=3)
    ax.add_patch(berry)

    # Leaf
    leaf = patches.Polygon([[2, 4.2], [1.7, 4.8], [2, 5.2], [2.3, 4.8]],
                           fill=True, facecolor='#27AE60', edgecolor='#1E8449', linewidth=2)
    ax.add_patch(leaf)

    # Network dots around berry
    for angle in [0, 60, 120, 180, 240, 300]:
        rad = np.radians(angle)
        x, y = 2 + 1.8 * np.cos(rad), 3 + 1.8 * np.sin(rad)
        ax.plot(x, y, 'o', color='#00d4ff', markersize=10, alpha=0.8)

    # Text
    ax.text(6.5, 4, 'Pi Command Center', fontsize=32, fontweight='bold',
            color='white', fontfamily='sans-serif', ha='left', va='center')
    ax.text(6.5, 2.5, 'Privacy-first home network control', fontsize=16,
            color='#00d4ff', fontfamily='sans-serif', ha='left', va='center')
    ax.text(6.5, 1.5, 'Pi-hole • VPN Split Routing • Telegram Bot', fontsize=12,
            color='#888888', fontfamily='sans-serif', ha='left', va='center')

    plt.savefig(f'{OUTPUT_DIR}/banner.png', dpi=150, bbox_inches='tight',
                facecolor='#1a1a2e', edgecolor='none')
    plt.close()
    print(f"✓ Banner saved to {OUTPUT_DIR}/banner.png")


if __name__ == '__main__':
    create_logo()
    create_banner()
