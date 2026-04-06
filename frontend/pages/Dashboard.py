import streamlit as st
import pandas as pd
from api import get_scans, get_scan_result, clear_all_scans

st.set_page_config(page_title="Operations Dashboard - Nexus", page_icon="📊", layout="wide")

if not st.session_state.get("access_token"):
    st.warning("UNAUTHORIZED. Please login via the main platform.")
    st.stop()

st.title("📊 Operations Dashboard")
st.markdown("Monitor and decrypt intelligence payloads from past operations.")

try:
    scans = get_scans()
except Exception:
    st.error("Backend Server (API) is offline. Please start it to view operations.")
    st.stop()

if not scans:
    st.info("No active operations found in the database. Head to 'New Scan' to initiate one.")
else:
    # High-level Metrics
    total_scans = len(scans)
    completed_scans = sum(1 for s in scans if s.get('status') == 'Completed')
    avg_risk = sum(s.get('risk_score', 0) for s in scans) / total_scans if total_scans > 0 else 0

    col1, col2, col3 = st.columns(3)
    col1.metric("Total Operations", total_scans)
    col2.metric("Successful Traces", completed_scans)
    col3.metric("Average Threat Risk", f"{int(avg_risk)} / 100")

    st.markdown("---")

    df = pd.DataFrame(scans)
    df = df[['scan_id', 'status', 'risk_score', 'email', 'username', 'domain', 'created_at']]

    # --- Trace History Header with Clear Button side by side ---
    title_col, btn_col = st.columns([4, 1])
    with title_col:
        st.subheader("Trace History")
    with btn_col:
        # Show a confirmation toggle before actually deleting
        if st.button("🗑️ Clear All History", type="secondary", use_container_width=True):
            st.session_state.confirm_clear = True

    # Confirmation step — prevents accidental deletion
    if st.session_state.get("confirm_clear"):
        st.warning("⚠️ This will permanently delete all your scan history. This cannot be undone.")
        confirm_col, cancel_col = st.columns(2)
        with confirm_col:
            if st.button("Yes, delete everything", type="primary", use_container_width=True):
                scan_ids = df['scan_id'].tolist()
                with st.spinner("Erasing all trace records..."):
                    deleted = clear_all_scans(scan_ids)
                st.session_state.confirm_clear = False
                st.success(f"✅ {deleted} operation(s) permanently erased from the database.")
                st.rerun()
        with cancel_col:
            if st.button("Cancel", use_container_width=True):
                st.session_state.confirm_clear = False
                st.rerun()

    st.dataframe(
        df,
        column_config={
            "scan_id": "Operation ID",
            "status": st.column_config.TextColumn("Status", help="Current state of the trace"),
            "risk_score": st.column_config.NumberColumn("Risk", format="%d - /100"),
            "email": "Target Email",
            "username": "Target User",
            "domain": "Target Domain",
            "created_at": st.column_config.DatetimeColumn("Timestamp", format="D MMM YY, h:mm a"),
        },
        use_container_width=True,
        hide_index=True
    )

    st.markdown("---")
    st.subheader("Decrypt Specific Payload")

    selected_scan = st.selectbox("Select Operation ID to analyze findings:", df['scan_id'])

    if st.button("Decrypt Payload Data", type="primary"):
        with st.spinner("Extracting secured data payload..."):
            result = get_scan_result(selected_scan)
            if result:
                status = result.get("status")
                findings = result.get("findings", [])

                if status == "Running":
                    st.info("This scan is still running. Please check back later.")
                elif status == "Failed":
                    st.error("This scan failed. Check the error details below.")
                    f_df = pd.DataFrame(findings)
                    st.dataframe(f_df, use_container_width=True, hide_index=True)
                else:
                    if findings:
                        st.success("Payload successfully decrypted.")
                        f_df = pd.DataFrame(findings)
                        st.dataframe(f_df, use_container_width=True, hide_index=True)
                    else:
                        st.info("Scan completed but yielded no critical footprint data.")
            else:
                st.error("Failed to retrieve payload from the database.")