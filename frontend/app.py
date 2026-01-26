import streamlit as st
import requests
import time
import json

API_URL = "http://localhost:8000"

st.set_page_config(page_title="OSINT Risk Scanner (MVP)", layout="centered")

st.title("🕵️ Digital Footprint Scanner")
st.markdown("### MVP Feasibility Test")

# Input Form
with st.form("scan_form"):
    email = st.text_input("Target Email")
    username = st.text_input("Target Username")
    domain = st.text_input("Target Domain (Optional)")
    submitted = st.form_submit_button("Start Scan")

if submitted:
    if not email or not username:
        st.error("Email and Username are required for this MVP.")
    else:
        # 1. Send Request to Backend
        payload = {"email": email, "username": username, "domain": domain}
        try:
            response = requests.post(f"{API_URL}/scan", json=payload)
            if response.status_code == 200:
                scan_data = response.json()
                scan_id = scan_data.get("scan_id")
                
                st.success(f"Scan started! ID: {scan_id}")
                
                # 2. Poll for Results
                status_placeholder = st.empty()
                result_placeholder = st.empty()
                
                # Max polling attempts (prevent infinite loop)
                attempts = 0
                while attempts < 30:
                    status_res = requests.get(f"{API_URL}/scan/{scan_id}")
                    if status_res.status_code == 200:
                        status_data = status_res.json()
                        status = status_data.get("status")
                        
                        if status == "PENDING":
                            status_placeholder.info(f"⏳ Scanning... ({attempts}s)")
                            time.sleep(2)
                            attempts += 2
                        elif status == "SUCCESS":
                            status_placeholder.empty()
                            
                            # 3. Display Results
                            risk_score = status_data.get("risk_score", 0)
                            # Safe JSON load
                            try:
                                findings = json.loads(status_data.get("result", "[]"))
                            except:
                                findings = []
                            
                            # Determine Level
                            if risk_score <= 30:
                                level = "LOW"
                                color = "green"
                            elif risk_score <= 60:
                                level = "MEDIUM"
                                color = "orange"
                            else:
                                level = "HIGH"
                                color = "red"
                                
                            st.divider()
                            col1, col2 = st.columns(2)
                            with col1:
                                st.metric("Risk Score", f"{risk_score}/100")
                            with col2:
                                st.markdown(f"### Level: :{color}[{level}]")
                            
                            st.subheader("🔎 Findings")
                            if findings:
                                for item in findings:
                                    st.write(f"- {item}")
                            else:
                                st.write("No public footprint found.")
                            break
                        else:
                            st.error("Unknown status received.")
                            break
                    else:
                        st.error("Failed to check status.")
                        break
                if attempts >= 30:
                    st.warning("Scan timed out.")
            else:
                st.error("Failed to start scan.")
                    
        except Exception as e:
            st.error(f"Connection Error: {e}")
            st.info("Make sure Backend and Redis are running.")