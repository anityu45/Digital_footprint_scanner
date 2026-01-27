import streamlit as st
import requests
import time
import json
import os

# --- CONFIGURATION ---
API_URL = "http://127.0.0.1:8000"
MAX_WAIT_TIME = 600  # Wait up to 10 minutes (Sherlock is slow but thorough)

st.set_page_config(page_title="Footprint Pro", page_icon="🕵️", layout="wide")

# --- CUSTOM CSS FOR REAL HACKER VIBES ---
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

st.title("🕵️ Digital Footprint Intelligence")
st.markdown("### Advanced OSINT Scanner (Sherlock + Breach + Graphing)")

# --- SIDEBAR INPUT ---
with st.sidebar:
    st.header("Target Input")
    st.info("💡 **Pro Tip:** Sherlock checks 400+ sites. This process takes 2-5 minutes. Do not close the tab.")
    with st.form("scan_form"):
        email = st.text_input("Email Address")
        username = st.text_input("Username (Optional)")
        domain = st.text_input("Domain (Optional)")
        submitted = st.form_submit_button("🚀 Run Deep Scan")

# --- MAIN LOGIC ---
if submitted:
    payload = {"email": email if email else None, "username": username if username else None, "domain": domain if domain else None}
    
    try:
        # 1. Start the Scan
        response = requests.post(f"{API_URL}/scan", json=payload)
        data = response.json()
        scan_id = data.get("scan_id")
        
        st.toast(f"Scan Initialized: {scan_id}", icon="✅")
        
        # 2. Status Container
        status_container = st.empty()
        progress_bar = st.progress(0)
        start_time = time.time()

        # 3. Long Polling Loop (Fixed Timeout Issue)
        scan_complete = False
        result_data = None

        # Loop for MAX_WAIT_TIME seconds
        while (time.time() - start_time) < MAX_WAIT_TIME:
            elapsed = int(time.time() - start_time)
            
            # Update Status Message dynamically
            if elapsed < 20:
                msg = f"⏳ Initializing Breach Checks... ({elapsed}s)"
            elif elapsed < 60:
                msg = f"🦅 Launching Sherlock Engine (Checking Social Media)... ({elapsed}s)"
            elif elapsed < 120:
                msg = f"🕵️ Still Scanning... Sherlock is checking 400+ sites. Please wait. ({elapsed}s)"
            else:
                msg = f"⚠️ Deep Scan in progress... Found extensive data. Organizing... ({elapsed}s)"
            
            status_container.info(msg)
            
            # Check for completion
            try:
                res = requests.get(f"{API_URL}/results/{scan_id}")
                if res.status_code == 200:
                    report = res.json()
                    if report["status"] == "Completed":
                        scan_complete = True
                        result_data = report
                        progress_bar.progress(100)
                        break
            except:
                pass
            
            time.sleep(3) # Check every 3 seconds

        # 4. Display Results
        status_container.empty() # Clear status message
        
        if not scan_complete:
            st.error("❌ The scan timed out. The backend is still running, but the frontend stopped waiting.")
        else:
            # --- DASHBOARD ---
            score = result_data.get("risk_score", 0)
            findings = result_data.get("findings", [])
            
            # Extract Graph Data & Clean Findings
            graph_edges = []
            clean_findings = []
            
            for f in findings:
                if isinstance(f, str) and f.startswith("GRAPH_DATA:"):
                    try:
                        graph_edges = json.loads(f.replace("GRAPH_DATA:", ""))
                    except:
                        pass
                else:
                    clean_findings.append(f)

            # Score Card
            col1, col2, col3 = st.columns(3)
            with col1:
                st.metric("Risk Score", f"{score}/100", delta="Critical" if score > 70 else "Normal")
            with col2:
                count_profiles = len([f for f in clean_findings if "🔗" in f])
                st.metric("Profiles Found", count_profiles)
            with col3:
                count_breaches = len([f for f in clean_findings if "❌" in f])
                st.metric("Breaches Detected", count_breaches, delta_color="inverse")

            st.divider()

            # Graph Section (Safe Import)
            st.subheader("🕸️ Identity Graph")
            try:
                import graphviz
                if graph_edges:
                    graph = graphviz.Digraph()
                    graph.attr(rankdir='LR', bgcolor='transparent')
                    graph.attr('node', shape='box', style='filled', fillcolor='#262730', fontcolor='white', color='#ff4b4b')
                    graph.attr('edge', color='gray')
                    
                    # Root Node
                    root_label = email if email else username
                    graph.node('ROOT', root_label, shape='doublecircle', fillcolor='#ff4b4b', fontcolor='white')
                    
                    for source, target in graph_edges:
                        graph.edge('ROOT', target, label=source)
                        
                    st.graphviz_chart(graph)
                else:
                    st.info("No connections found to graph.")
            except ImportError:
                st.warning("Graphviz library not found. Install it to see the graph.")
            except Exception as e:
                st.warning(f"Could not render graph: {e}")

            # Detailed Logs
            st.subheader("📜 detailed Audit Log")
            with st.expander("View Full Findings List", expanded=True):
                for item in clean_findings:
                    if "⚠️" in item: st.error(item)
                    elif "❌" in item: st.error(item)
                    elif "🔗" in item: st.markdown(f"- {item}") # Make links clickable
                    else: st.write(f"- {item}")

    except Exception as e:
        st.error(f"Connection Error: {e}")