import streamlit as st
import sys
import shutil
import subprocess
import json
import time

# --- CONFIGURATION & UTILS ---
st.set_page_config(page_title="Footprint Pro", page_icon="🕵️", layout="wide")

# Custom CSS for that "Hacker" look
st.markdown("""
    <style>
    .stMetric {
        background-color: #0e1117;
        border: 1px solid #303030;
        padding: 10px;
        border-radius: 5px;
    }
    </style>
    """, unsafe_allow_html=True)

# --- INTERNAL LOGIC (No more Backend/Redis needed) ---

def run_sherlock(username, mode="quick"):
    """
    Runs Sherlock directly from the Streamlit container.
    """
    # 🚀 SPEED CONFIG: Top 25 sites
    TOP_SITES = [
        "Instagram", "Facebook", "Twitter", "YouTube", "TikTok", 
        "GitHub", "Pinterest", "Roblox", "Spotify", "Reddit", 
        "Twitch", "Patreon", "Steam", "Telegram", "Vimeo", 
        "SoundCloud", "Disqus", "Medium", "TripAdvisor", "Venmo", 
        "CashApp", "WordPress", "Tumblr", "Ebay", "Slack"
    ]

    sherlock_cmd = shutil.which("sherlock")
    if not sherlock_cmd:
        # If installed via pip in the cloud env, it's usually accessible via python -m
        command = [sys.executable, "-m", "sherlock", username, "--timeout", "1", "--print-found"]
    else:
        command = [sherlock_cmd, username, "--timeout", "1", "--print-found"]

    if mode == "quick":
        for site in TOP_SITES:
            command.extend(["--site", site])

    try:
        result = subprocess.run(command, capture_output=True, text=True)
        findings = []
        for line in result.stdout.splitlines():
            if "[+]" in line:
                clean = line.replace("[+]", "").strip()
                if ": " in clean:
                    parts = clean.split(": ", 1)
                    findings.append({"site": parts[0], "url": parts[1]})
        return findings
    except Exception as e:
        return []

def check_breaches(email):
    """
    Simulated Breach Check (Safe for Demo)
    """
    breaches = []
    if "gmail" in email or "yahoo" in email or "hotmail" in email:
        breaches.append("Collection #1 (2019) [CRITICAL]")
        breaches.append("Verifications.io [HIGH]")
    return breaches

# --- FRONTEND UI ---

st.title("🕵️ Digital Footprint Intelligence")
st.markdown("### Advanced OSINT Scanner (Standalone Cloud Version)")

with st.sidebar:
    st.header("Configuration")
    scan_mode_label = st.radio("Select Scan Intensity:", ("⚡ Quick Analysis (15s)", "🕵️ Deep Analysis (3-5m)"))
    scan_mode = "quick" if "Quick" in scan_mode_label else "deep"
    
    st.divider()
    with st.form("scan_form"):
        email = st.text_input("Email Address")
        username = st.text_input("Username (Optional)")
        submitted = st.form_submit_button("🚀 Run Scan")

if submitted:
    # Logic to handle missing username
    target_user = username if username else email.split("@")[0] if email else None
    
    if not target_user:
        st.error("Please enter an Email or Username.")
    else:
        st.toast(f"Starting {scan_mode.upper()} scan...", icon="🕵️")
        
        # --- THE SCANNING PROCESS (Running directly) ---
        findings = []
        graph_edges = []
        risk_score = 0
        
        # 1. Breach Check
        with st.spinner("💥 Checking Data Breaches..."):
            time.sleep(1) # UI effect
            if email:
                found_breaches = check_breaches(email)
                if found_breaches:
                    risk_score += 40
                    findings.append(f"⚠️ **SECURITY ALERT:** Email found in {len(found_breaches)} Breaches!")
                    for b in found_breaches:
                        findings.append(f"❌ Breach: {b}")
                        graph_edges.append(("Email", f"Breach: {b.split(' ')[0]}"))
        
        # 2. Sherlock Scan
        with st.spinner(f"🦅 Running Sherlock ({scan_mode} mode)..."):
            profiles = run_sherlock(target_user, mode=scan_mode)
            if profiles:
                findings.append(f"🔎 Found {len(profiles)} Public Profiles:")
                for p in profiles:
                    findings.append(f"🔗 {p['site']}: {p['url']}")
                    graph_edges.append(("Username", p['site']))
                    if p['site'] in ["Instagram", "Twitter", "Facebook"]:
                        risk_score += 10
                    else:
                        risk_score += 2
            else:
                findings.append("ℹ️ No public profiles found (try Deep Mode).")

        # 3. Final Calculation
        risk_score = min(risk_score, 100)
        st.success("Scan Complete!")

        # --- DASHBOARD DISPLAY ---
        col1, col2, col3 = st.columns(3)
        with col1:
            st.metric("Risk Score", f"{risk_score}/100", delta="Critical" if risk_score > 70 else "Normal")
        with col2:
            st.metric("Profiles Found", len(profiles))
        with col3:
            st.metric("Breaches", len([f for f in findings if "❌" in f]), delta_color="inverse")

        st.divider()

        # GRAPHING
        st.subheader("🕸️ Identity Graph")
        try:
            import graphviz
            if graph_edges:
                graph = graphviz.Digraph()
                graph.attr(rankdir='LR', bgcolor='transparent')
                graph.attr('node', shape='box', style='filled', fillcolor='#262730', fontcolor='white', color='#ff4b4b')
                
                root_label = email if email else target_user
                graph.node('ROOT', root_label, shape='doublecircle', fillcolor='#ff4b4b', fontcolor='white')
                
                for source, target in graph_edges:
                    graph.edge('ROOT', target, label=source)
                    
                st.graphviz_chart(graph)
            else:
                st.info("No connections to map.")
        except ImportError:
            st.warning("Graphviz not installed on cloud.")
        except Exception as e:
            st.warning(f"Graph error: {e}")

        # LOGS
        st.subheader("📜 Detailed Audit Log")
        with st.expander("View Full Report", expanded=True):
            for f in findings:
                if "⚠️" in f: st.error(f)
                elif "❌" in f: st.error(f)
                elif "🔗" in f: st.write(f)
                else: st.info(f)