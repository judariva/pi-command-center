#!/usr/bin/env python3
"""
Pi Command Center - Professional Diagram Generator

Generates high-quality architecture diagrams from YAML configuration
using the 'diagrams' library (mingrammer/diagrams).

Usage:
    python generate.py                    # Generate all diagrams
    python generate.py --config alt.yaml  # Use alternative config
    python generate.py --only network     # Generate specific diagram

Requirements:
    pip install diagrams pyyaml
"""

import os
import sys
from pathlib import Path

import yaml

# Diagrams library imports
from diagrams import Cluster, Diagram, Edge
from diagrams.aws.compute import EC2
from diagrams.aws.network import VPC
from diagrams.generic.network import Firewall, Router, Switch
from diagrams.generic.storage import Storage
from diagrams.onprem.client import Client, User
from diagrams.onprem.compute import Server
from diagrams.onprem.container import Docker
from diagrams.onprem.database import PostgreSQL
from diagrams.onprem.iac import Ansible
from diagrams.onprem.logging import Loki
from diagrams.onprem.monitoring import Grafana, Prometheus
from diagrams.onprem.network import Internet, Nginx
from diagrams.onprem.security import Vault
from diagrams.programming.language import Python
from diagrams.saas.chat import Telegram

# Custom node mapping
NODE_TYPES = {
    # Network
    "internet": Internet,
    "router": Router,
    "firewall": Firewall,
    "switch": Switch,
    "network": Switch,
    "vpn": Vault,

    # Compute
    "server": Server,
    "container": Docker,
    "application": Python,
    "script": Ansible,

    # Storage
    "storage": Storage,
    "volume": Storage,
    "dns": Nginx,  # Using Nginx as DNS placeholder

    # Security
    "key": Vault,
    "auth": Vault,
    "ids": Vault,
    "hacker": User,
    "scanner": Client,

    # Clients
    "client": Client,
    "user": User,

    # SaaS
    "saas": Telegram,
    "api": Server,

    # Monitoring
    "logging": Loki,
    "notification": Grafana,
    "monitoring": Prometheus,
}

# Color schemes
COLORS = {
    "primary": "#3498db",
    "success": "#27ae60",
    "warning": "#f39c12",
    "danger": "#e74c3c",
    "purple": "#9b59b6",
    "telegram": "#0088cc",
    "gray": "#95a5a6",
}


class DiagramGenerator:
    """Professional diagram generator from YAML config."""

    def __init__(self, config_path: str = "config.yaml"):
        self.config_path = Path(config_path)
        self.config = self._load_config()
        self.output_dir = Path(self.config.get("metadata", {}).get("output_dir", "."))
        self.format = self.config.get("metadata", {}).get("format", "png")

    def _load_config(self) -> dict:
        """Load YAML configuration."""
        if not self.config_path.exists():
            raise FileNotFoundError(f"Config not found: {self.config_path}")

        with open(self.config_path) as f:
            return yaml.safe_load(f)

    def _get_node(self, node_type: str, label: str):
        """Get diagram node by type."""
        node_class = NODE_TYPES.get(node_type, Server)
        return node_class(label)

    def _get_edge_style(self, conn: dict) -> Edge:
        """Create styled edge from connection config."""
        color = conn.get("color", COLORS["primary"])
        style = "dashed" if conn.get("style") == "dashed" else "solid"
        label = conn.get("label", "")

        return Edge(label=label, color=color, style=style)

    def generate_diagram(self, name: str, diagram_config: dict):
        """Generate a single diagram from config."""
        title = diagram_config.get("title", name)
        direction = diagram_config.get("direction", "TB")
        zones = diagram_config.get("zones", {})
        connections = diagram_config.get("connections", [])

        output_path = self.output_dir / title

        # Graph attributes for professional look
        graph_attr = {
            "fontsize": "20",
            "fontname": "Helvetica Neue",
            "bgcolor": "white",
            "pad": "0.5",
            "splines": "spline",
            "nodesep": "0.8",
            "ranksep": "1.0",
        }

        node_attr = {
            "fontsize": "12",
            "fontname": "Helvetica Neue",
        }

        edge_attr = {
            "fontsize": "10",
            "fontname": "Helvetica Neue",
        }

        with Diagram(
            "",
            filename=str(output_path),
            outformat=self.format,
            direction=direction,
            show=False,
            graph_attr=graph_attr,
            node_attr=node_attr,
            edge_attr=edge_attr,
        ):
            nodes = {}

            # Create zones (clusters) and nodes
            for zone_id, zone_config in zones.items():
                zone_label = zone_config.get("label", zone_id)
                zone_nodes = zone_config.get("nodes", [])

                if zone_nodes:
                    with Cluster(zone_label):
                        for node_config in zone_nodes:
                            node_id = node_config["id"]
                            node_type = node_config.get("type", "server")
                            node_label = node_config.get("label", node_id)
                            nodes[node_id] = self._get_node(node_type, node_label)

            # Create connections
            for conn in connections:
                from_node = nodes.get(conn["from"])
                to_node = nodes.get(conn["to"])

                if from_node and to_node:
                    edge = self._get_edge_style(conn)
                    from_node >> edge >> to_node

        print(f"  ✓ {title}.{self.format}")

    def generate_all(self, only: str = None):
        """Generate all diagrams from config."""
        print(f"\n{'='*60}")
        print(f"  Pi Command Center - Diagram Generator")
        print(f"  Config: {self.config_path}")
        print(f"  Output: {self.output_dir.absolute()}")
        print(f"{'='*60}\n")

        # Diagram sections to process
        diagram_sections = ["network", "vpn_routing", "security", "bot", "docker"]

        for section in diagram_sections:
            if only and section != only:
                continue

            if section in self.config:
                try:
                    self.generate_diagram(section, self.config[section])
                except Exception as e:
                    print(f"  ✗ {section}: {e}")

        print(f"\n{'='*60}")
        print(f"  ✓ Done!")
        print(f"{'='*60}\n")


def main():
    """Main entry point."""
    import argparse

    parser = argparse.ArgumentParser(description="Generate architecture diagrams")
    parser.add_argument("--config", default="config.yaml", help="Config file path")
    parser.add_argument("--only", help="Generate only specific diagram")
    args = parser.parse_args()

    # Change to script directory
    os.chdir(Path(__file__).parent)

    generator = DiagramGenerator(args.config)
    generator.generate_all(only=args.only)


if __name__ == "__main__":
    main()
