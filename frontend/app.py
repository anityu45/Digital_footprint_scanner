import streamlit as st
import requests
import time

API_URL = "http://127.0.0.1:8000"

st.set_page_config(page_title="Footprint MVP", page_icon="🕵️")

st.title("🕵️ Digital Footprint Analyzer")
st.markdown("Enter your email. We will automatically check for your username across the web.")

with st.form("scan_form"):
    email = st.text_input("Email Address")
    username = st.text_input("Username (Optional - Leave blank to auto-detect)")
    domain = st.text_input("Domain (Optional)")
    submitted = st.form_submit_button("Run Scan")

if submitted:
    payload = {"email": email if email else None, "username": username if username else None, "domain": domain if domain else None}
    
    try:
        response = requests.post(f"{API_URL}/scan", json=payload)
        data = response.json()
        scan_id = data.get("scan_id")
        
        # Show auto-detection message
        if data.get("auto_detected_username"):
             st.info(f"🔹 Auto-detected username: **{data['auto_detected_username']}**")

        st.success(f"Scan started! ID: {scan_id}")

        # Polling for results
        with st.spinner("Scanning dark corners of the web..."):
            for _ in range(20):
                time.sleep(2)
                res = requests.get(f"{API_URL}/results/{scan_id}")
                if res.status_code == 200:
                    report = res.json()
                    if report["status"] == "Completed":
                        
                        # --- RISK SCORE DISPLAY ---
                        score = report.get("risk_score", 0)
                        if score < 30: color = "green"; level = "Low Risk"
                        elif score < 70: color = "orange"; level = "Medium Risk"
                        else: color = "red"; level = "High Risk"
                        
                        st.divider()
                        col1, col2 = st.columns(2)
                        with col1:
                            st.metric("Risk Score", f"{score}/100")
                        with col2:
                            st.markdown(f"### :{color}[{level}]")

                        # --- FINDINGS LIST ---
                        st.subheader("🔎 Technical Findings")
                        findings = report.get("findings", [])
                        if findings:
                            for item in findings:
                                st.write(f"- {item}")
                        else:
                            st.write("No public footprint found.")

                        # --- SECURITY ADVICE ---
                        st.markdown("---")
                        st.subheader("🛡️ What should you do?")
                        
                        if any("Spotify" in f or "Adobe" in f for f in findings):
                            st.warning("⚠️ **Phishing Risk:** Attackers know you use Spotify/Adobe. Be careful of fake 'Payment Failed' emails.")
                        
                        if any("Gravatar" in f for f in findings):
                            st.warning("⚠️ **Identity Leak:** Your real name/photo is publicly linked to this email via Gravatar.")

                        if score > 50:
                            st.error("🚨 **Action Required:** Your digital footprint is large. We recommend enabling 2FA on all linked accounts immediately.")
                        else:
                            st.success("✅ Your footprint is relatively small.")
                        
                        break
    except Exception as e:
        st.error(f"Connection Error: {e}")