# LinkedIn Post Draft

## Option 1: Technical Focus

---

🔐 **I built a privacy-first home network control center**

After months of tinkering, I'm releasing my first open-source project: **Pi Command Center**.

**The problem I was solving:**
- ISPs log every DNS query you make
- VPNs slow down everything when you just want to protect specific traffic
- Managing home network security requires too much technical knowledge

**What I built:**
A Raspberry Pi-based solution that:

✅ Blocks ads network-wide (Pi-hole + Unbound recursive DNS)
✅ Smart VPN routing - only routes specific domains through VPN
✅ Control everything via Telegram - no apps to install
✅ Security monitoring with automatic intrusion detection

**The technical challenge I'm most proud of:**
Implementing VPN split routing using iptables mangle + fwmark + policy routing. Most guides say "all or nothing" but I wanted Netflix through VPN (US content) while my local banking stays fast.

```
netflix.com → VPN (USA) 🇺🇸
mybank.com → Direct (fast) 🏦
```

**Stack:**
🐳 Docker (Pi-hole, Unbound, custom bot)
🐍 Python (Telegram bot with async handlers)
🔒 WireGuard (VPN)
🛡️ Fail2ban + UFW (security)

**What I learned:**
- Linux networking is deep but rewarding
- Building for yourself is the best way to learn
- Documentation is as important as code

GitHub: github.com/judariva/pi-command-center

Would love feedback from anyone who's built similar home lab projects! What would you add?

#OpenSource #Privacy #RaspberryPi #HomeLab #Networking #Python #DevOps

---

## Option 2: Story Focus

---

🏠 **I turned a $35 Raspberry Pi into my home's security center**

A year ago, I realized my ISP could see every website I visit. Every. Single. One.

That rabbit hole led me here: a complete home network control center that I'm now releasing as open source.

**What started as paranoia became a genuine project:**

📱 Control my entire network from Telegram
🚫 Block ads on ALL devices (even the smart TV)
🔐 VPN that only activates when needed (not "all or nothing")
🔍 See every device that connects to my network
⚠️ Get alerts when something suspicious happens

**The "aha" moment:**
When I set up split VPN routing. Now Netflix thinks I'm in the USA (content unlocked 🇺🇸), but my local bank works perfectly. Best of both worlds.

**What surprised me most:**
How much you can do with just a Raspberry Pi and open-source software. No subscriptions. No cloud. Just your hardware, your rules.

This is my first open-source project. It's not perfect, but it works, and maybe it'll help someone else who values their privacy.

GitHub: github.com/judariva/pi-command-center

Anyone else running home lab projects? I'd love to see what you've built! 👇

#HomeLab #Privacy #OpenSource #RaspberryPi #CyberSecurity #Python

---

## Option 3: Problem-Solution Focus

---

**How I stopped my ISP from tracking my internet activity**

🔴 Problem: Your ISP sees every DNS query. Every website. Everything.

🟢 Solution: I built Pi Command Center - a Raspberry Pi-based privacy solution.

**What it does:**

1️⃣ **Private DNS** - Queries never leave your home (Unbound recursive resolver)

2️⃣ **Network-wide ad blocking** - Every device protected automatically

3️⃣ **Smart VPN routing** - Only sensitive traffic goes through VPN

4️⃣ **Telegram control** - Manage everything from your phone

5️⃣ **Security monitoring** - Automatic intrusion detection

**The technical win:**
VPN split routing. Most VPNs are "all or nothing" - slow everything down. Mine routes intelligently:

```
🔒 reddit.com → VPN (privacy)
🔒 netflix.com → VPN (US content)
⚡ google.com → Direct (speed)
⚡ mybank.com → Direct (local access)
```

**Cost:** ~$50 one-time (Raspberry Pi)
**Subscriptions:** $0
**Privacy gained:** Priceless

Now open source: github.com/judariva/pi-command-center

#Privacy #CyberSecurity #OpenSource #HomeLab #RaspberryPi

---

## Hashtag Recommendations

**Primary (always include):**
- #OpenSource
- #RaspberryPi
- #Privacy

**Secondary (choose 2-3):**
- #HomeLab
- #CyberSecurity
- #Networking
- #Python
- #DevOps
- #SelfHosted
- #Linux

**Engagement boosters:**
- End with a question
- Ask for feedback
- Invite others to share their projects

---

## Best Times to Post (LinkedIn)

- Tuesday-Thursday: 7-8 AM or 5-6 PM (local time)
- Avoid weekends

## Image Suggestions

1. The architecture diagram (docs/diagrams/network_architecture.png)
2. A screenshot of the Telegram bot interface
3. The banner image (docs/assets/banner.png)
4. A photo of your actual Raspberry Pi setup
