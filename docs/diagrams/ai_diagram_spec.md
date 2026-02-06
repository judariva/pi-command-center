# AI-Generated Diagram Specifications

Okay, here's a detailed specification for professional network architecture diagrams for the "Pi Command Center" project.  This document outlines the visual standards and content requirements for each diagram type to ensure clarity, consistency, and professional presentation.

**Document Title:** Pi Command Center Network Diagram Specifications

**Version:** 1.0

**Date:** October 26, 2023

**Author:** AI Technical Documentation Expert

---

**I. General Diagram Guidelines:**

*   **Consistency:** Maintain a consistent style across all diagrams. Use the same node types, icons, colors, and connection styles whenever possible.
*   **Clarity:**  Prioritize clarity and readability. Avoid overcrowding the diagram.  Use whitespace effectively.
*   **Accuracy:** Ensure all information presented in the diagrams is accurate and reflects the actual network configuration.
*   **Target Audience:**  Assume the audience has a technical background (e.g., systems administrators, network engineers, advanced home users) but may not be intimately familiar with the specific project.
*   **Software Recommendation:**  Use a professional diagramming tool (e.g., Lucidchart, draw.io, Visio, Miro).
*   **Fonts:** Use a clear, sans-serif font like Arial, Helvetica, or Calibri. Font size should be large enough for comfortable reading (e.g., 10-12pt).
*   **Grid:** Use a grid in your diagramming software to keep elements aligned and spaced evenly.

**II. Color Scheme:**

*   **Primary:** `#3498db` (Blue) - Used for general nodes and important elements.
*   **Secondary:** `#2ecc71` (Green) - Used for security-related nodes and successful flows.
*   **Tertiary:** `#f39c12` (Orange) - Used for VPN-related nodes.
*   **Accent:** `#e74c3c` (Red) - Used for errors, potential vulnerabilities, and failed flows.
*   **Background:** `#f0f0f0` (Light Gray) - For a clean and professional look.
*   **Text:** `#333333` (Dark Gray) - For labels and annotations.

**III. Node Types and Icons:**

| Node Type          | Icon                                                                                                                                                                                                                                                                                                                                                                                                                                                                  | Description                                                                                                                    |
| ------------------ | -------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------- | ------------------------------------------------------------------------------------------------------------------------------ |
| Raspberry Pi       | <i class="fas fa-raspberry-pi"></i> (Font Awesome icon) or a custom Raspberry Pi icon.                                                                                                                                                                                                                                                                                                                                                                                                                                                                                              | Represents the Raspberry Pi hardware.                                                                                             |
| Router             | <i class="fas fa-router"></i> (Font Awesome icon) or a generic router icon.                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                     | Represents the home router.                                                                                                    |
| Internet           | <i class="fas fa-globe"></i> (Font Awesome icon) or a cloud icon.                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                    | Represents the internet.                                                                                                      |
| Client Device      | <i class="fas fa-laptop"></i> (Font Awesome icon), <i class="fas fa-mobile-alt"></i> (Font Awesome icon), or generic device icons.                                                                                                                                                                                                                                                                                                                                                                                                                                               | Represents devices on the network (e.g., laptops, phones).                                                                   |
| Pi-hole            | A custom Pi-hole logo or a generic DNS server icon.                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                   | Represents the Pi-hole DNS server.                                                                                              |
| Unbound            | A custom Unbound logo or a generic DNS resolver icon.                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                    | Represents the Unbound recursive DNS resolver.                                                                                 |
| WireGuard          | A custom WireGuard logo or a VPN tunnel icon.                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                     | Represents the WireGuard VPN server.                                                                                             |
| Docker Container   | <i class="fab fa-docker"></i> (Font Awesome icon) or a generic container icon.                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                | Represents a Docker container.                                                                                                   |
| Telegram Bot       | A custom Telegram logo or a bot icon.                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                     | Represents the Telegram bot.                                                                                                   |
| Fail2ban           | A shield icon or a lock icon.                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                     | Represents the Fail2ban intrusion prevention system.                                                                                                   |
| UFW                | A firewall icon.                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                     | Represents the Uncomplicated Firewall.                                                                                                   |

**IV. Connection Styles:**

*   **Solid Line:** `#333333` (Dark Gray) -  Represents a standard network connection or data flow.
*   **Dashed Line:** `#808080` (Gray) - Represents a less direct connection, a logical connection, or a VPN tunnel.
*   **Green Solid Line:** `#2ecc71` - Represents a secure or successful connection.
*   **Red Solid Line:** `#e74c3c` - Represents a blocked connection or a potential security risk.
*   **Arrowheads:** Use arrowheads to indicate the direction of data flow.

**V. Diagram Specifications:**

**1. Network Architecture Diagram:**

*   **Title:** Pi Command Center - Network Architecture
*   **Purpose:** To provide a high-level overview of the network topology, showing the relationships between all key components.
*   **Layout:**  A hierarchical layout is recommended.  The internet at the top, the router in the middle, and the Raspberry Pi and client devices at the bottom.  Group related components (e.g., Pi-hole and Unbound) together.
*   **Nodes:**
    *   Internet (Internet icon, Primary color)
    *   Router (Router icon, Primary color)
    *   Raspberry Pi (Raspberry Pi icon, Primary color)
    *   Client Devices (Laptop/Mobile icons, Primary color)
*   **Components within Raspberry Pi Node (Use nested nodes or annotations):**
    *   Pi-hole (Pi-hole icon, Primary color)
    *   Unbound (Unbound icon, Primary color)
    *   WireGuard (WireGuard icon, Orange color)
    *   Fail2ban (Shield Icon, Green color)
    *   UFW (Firewall Icon, Green color)
    *   Telegram Bot (Telegram Bot icon, Primary color)
*   **Connections:**
    *   Internet <-> Router (Solid Line, Dark Gray)
    *   Router <-> Raspberry Pi (Solid Line, Dark Gray)
    *   Router <-> Client Devices (Solid Line, Dark Gray)
    *   Pi-hole <-> Unbound (Solid Line, Dark Gray, within Raspberry Pi node)
*   **Labels:**
    *   Label each node clearly (e.g., "Internet", "Home Router", "Raspberry Pi - Pi Command Center", "Laptop", "Mobile Phone").
    *   Label the Raspberry Pi's IP address (e.g., 192.168.1.10).
    *   Label the router's IP address (e.g., 192.168.1.1).
*   **Annotations:**
    *   Add a brief description of each component's role.
    *   Indicate the DNS server used by the router (e.g., "Router uses Pi-hole as DNS server").
    *   Indicate the WireGuard subnet (e.g., "WireGuard Subnet: 10.6.0.0/24").
    *   Indicate which ports are forwarded to the Raspberry Pi (e.g., "Port 51820/UDP forwarded to Raspberry Pi for WireGuard").

**2. VPN Split Routing Flow Diagram:**

*   **Title:** Pi Command Center - VPN Split Routing
*   **Purpose:** To illustrate how traffic is routed through the VPN tunnel and which traffic bypasses it.
*   **Layout:**  A linear flow diagram from left to right.
*   **Nodes:**
    *   Client Device (Laptop/Mobile icon, Primary color)
    *   Router (Router icon, Primary color)
    *   Raspberry Pi (Raspberry Pi icon, Primary color)
    *   WireGuard (WireGuard icon, Orange color)
    *   Internet (Internet icon, Primary color)
*   **Connections:**
    *   Client Device -> Router (Solid Line, Dark Gray)
    *   Router -> Raspberry Pi (Solid Line, Dark Gray)
    *   Raspberry Pi -> WireGuard (Solid Line, Orange)  (Indicates VPN Tunnel)
    *   WireGuard -> Internet (Dashed Line, Orange) (Traffic through