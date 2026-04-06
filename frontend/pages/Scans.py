import time
import streamlit as st

from api import analyze_image, get_scan_result, start_scan
from style_manager import apply_custom_page_style, apply_theme_attribute, render_theme_toggle


# =========================
# NEW: CARD UI COMPONENT
# =========================
def render_target_cards():
    st.markdown("""
    <style>
    .target-card {
        border-radius: 14px;
        padding: 20px;
        border: 1px solid rgba(255,255,255,0.1);
        background: linear-gradient(135deg, rgba(79,172,254,0.06), rgba(118,75,162,0.06));
        transition: all 0.25s ease;
        height: 130px;
        display: flex;
        align-items: center;
        gap: 15px;
    }

    .target-card:hover {
        transform: translateY(-5px);
        border: 1px solid #4facfe;
        box-shadow: 0 8px 25px rgba(79, 172, 254, 0.25);
    }

    .target-card-selected {
        border: 2px solid #22c55e !important;
        box-shadow: 0 0 20px rgba(34, 197, 94, 0.5);
    }

    .icon-circle {
        width: 48px;
        height: 48px;
        border-radius: 50%;
        display: flex;
        align-items: center;
        justify-content: center;
        font-size: 20px;
        background: radial-gradient(circle, rgba(79,172,254,0.3), rgba(0,0,0,0));
        border: 1px solid rgba(79,172,254,0.5);
        flex-shrink: 0;
    }

    .card-text {
        display: flex;
        flex-direction: column;
    }

    .card-title {
        font-size: 18px;
        font-weight: 600;
    }

    .card-desc {
        font-size: 13px;
        color: #b8bcc4;
    /* Ensure the cards have pointer cursors */
    .target-card {
        cursor: pointer;
    }
    </style>
    """, unsafe_allow_html=True)

    if "target_type" not in st.session_state:
        st.session_state.target_type = "Email"

    col1, col2, col3 = st.columns(3)

    def card(col, label, desc, icon):
        selected = st.session_state.target_type == label
        class_name = "target-card target-card-selected" if selected else "target-card"

        with col:
            st.markdown(f"""
                <div class="{class_name}" id="target-card-{label}">
                    <div class="icon-circle">{icon}</div>
                    <div class="card-text">
                        <div class="card-title">{label}</div>
                        <div class="card-desc">{desc}</div>
                    </div>
                </div>
                <div id="target-anchor-{label}" style="display:none;"></div>
            """, unsafe_allow_html=True)
            
            if st.button(" ", key=f"{label}_btn", use_container_width=True):
                st.session_state.target_type = label
                st.rerun()

    card(col1, "Email", "Trace digital footprint of an email address", "✉️")
    card(col2, "Username", "Trace online activity linked to a username", "👤")
    card(col3, "Domain", "Investigate information associated with a domain", "🌐")

    # Robust Javascript to bind clicks to the hidden buttons
    import streamlit.components.v1 as components
    components.html("""
    <script>
        setTimeout(() => {
            const labels = ['Email', 'Username', 'Domain'];
            labels.forEach(label => {
                const doc = parent.document;
                const card = doc.getElementById('target-card-' + label);
                const anchor = doc.getElementById('target-anchor-' + label);
                
                if (card && anchor) {
                    const anchorContainer = anchor.closest('.element-container');
                    if (anchorContainer && anchorContainer.nextElementSibling) {
                        const buttonContainer = anchorContainer.nextElementSibling;
                        const btn = buttonContainer.querySelector('button');
                        
                        if (btn) {
                            // Hide the streamlit button container completely
                            buttonContainer.style.display = 'none';
                            
                            // Bind the click on the HTML card to the Streamlit button
                            card.onclick = function() {
                                btn.click();
                            };
                        }
                    }
                }
            });
            
            // Clean up the iframe containers so they don't break layout
            const iframes = parent.document.querySelectorAll('iframe');
            iframes.forEach(iframe => {
                if(iframe.height === '0' || iframe.getAttribute('height') === '0') {
                    const container = iframe.closest('.element-container');
                    if(container) {
                        container.style.display = 'none';
                    }
                }
            });
        }, 100);
    </script>
    """, width=0, height=0)

    return st.session_state.target_type
# =========================
# EXISTING FUNCTIONS
# =========================
def render_findings(rows):
    if not rows:
        st.info("No findings available.")
        return

    header_cols = st.columns(5)
    for col, header in zip(
        header_cols,
        ["Source Database", "Severity Level", "Data Type", "Value/Evidence", "Source URL"],
    ):
        col.caption(f"**{header}**")

    for row in rows:
        cols = st.columns(5)
        cols[0].write(row.get("source") or "-")
        cols[1].write(row.get("severity") or "-")
        cols[2].write(row.get("type") or "-")
        cols[3].write(row.get("value") or "-")
        url = row.get("url")
        if url:
            cols[4].markdown(f"[Open Link]({url})")
        else:
            cols[4].write("-")


def render_image_analysis(uploaded_file):
    col1, col2 = st.columns([1, 1.5])

    with col1:
        st.subheader("Target Visual")
        st.image(uploaded_file, use_container_width=True, caption=f"File: {uploaded_file.name}")

        if st.button("Run Forensic Analysis", type="primary", use_container_width=True):
            st.session_state.analyze_clicked = True

    with col2:
        if st.session_state.get("analyze_clicked", False):
            with st.spinner("Executing forensic subroutines..."):
                res = analyze_image(
                    uploaded_file.getvalue(),
                    uploaded_file.name,
                    uploaded_file.type,
                )

            if res.status_code == 200:
                data = res.json()
                st.success("Forensic Analysis Complete. Metadata extracted.")

                if data.get("location"):
                    st.subheader("Geospatial Evidence Discovered")
                    lat = data["location"]["latitude"]
                    lon = data["location"]["longitude"]

                    st.map(latitude=[lat], longitude=[lon], zoom=12)
                    st.markdown(f"**Maps Link**: [View on Google Maps]({data['location']['google_maps']})")
                else:
                    st.info("No geospatial (GPS) coordinates found in the image.")

                with st.expander("View Raw Discovered Metadata", expanded=True):
                    st.json(data.get("metadata", {}))
            else:
                st.error(f"Extraction sequence failed: {res.text}")


# =========================
# PAGE CONFIG
# =========================
st.set_page_config(page_title="Scans - Nexus", page_icon="🔎", layout="wide")

if "access_token" not in st.session_state:
    st.session_state.access_token = None
if "analyze_clicked" not in st.session_state:
    st.session_state.analyze_clicked = False

if not st.session_state.get("access_token"):
    st.warning("UNAUTHORIZED - Please login first")
    if st.button("Go to Login"):
        st.switch_page("Login.py")
    st.stop()

try:
    render_theme_toggle()
    apply_theme_attribute()
except ImportError:
    pass

apply_custom_page_style("Scan")


# =========================
# SIDEBAR
# =========================
with st.sidebar:
    st.markdown("---")
    username = st.session_state.get("username", "User")
    st.caption(f"Logged in as: **{username}**")

    if st.button("Logout", use_container_width=True):
        st.session_state.access_token = None
        st.session_state.username = None
        st.session_state.clear()
        st.switch_page("Login.py")


# =========================
# MAIN UI
# =========================
st.title("Scans")
st.markdown("Run footprint tracing and image forensics from one workspace.")

tab1, tab2 = st.tabs(["Target Scan", "Image Forensics"])


# =========================
# TAB 1 - UPDATED UI
# =========================
with tab1:
    st.subheader("Intelligence Target Scan")
    st.markdown("Initiate a comprehensive digital footprint trace across global databases.")

    with st.container(border=True):

        st.markdown("### Select Target Type")
        target_type = render_target_cards()

        st.markdown("")

        target_value = st.text_input(
            f"Enter target {target_type.lower()}...",
            placeholder=f"e.g., target.{target_type.lower()}@example.com",
        )

    final_data = None
    
    col1, col2, col3 = st.columns([1, 2, 1])

    with col2:
        if st.button("Start Trace Scan", type="primary", use_container_width=True):
            if not target_value:
                st.error("Target identification parameter is required.")
            else:
                payload = {"email": "", "username": "", "domain": ""}
                payload[target_type.lower()] = target_value

                res_container = st.empty()

                with res_container.container():
                    st.info("Initializing communication with scan engines...")
                    try:
                        res = start_scan(payload)
                    except Exception:
                        st.error("Connection Failed: Backend server is unreachable. Please run: 'uvicorn backend.main:app --reload'")
                        st.stop()

                    if res.status_code == 202:
                        scan_id = res.json().get("scan_id")
                        st.success(f"Trace assigned ID: {scan_id}")

                        progress_container = st.container()
                        with progress_container:
                            progress_bar = st.progress(0)
                            status_text = st.empty()

                            for i in range(300):
                                time.sleep(2)

                                visual_progress = min(95, int((i + 1) * 0.5) + 5)
                                progress_bar.progress(visual_progress)
                                status_text.caption(f"Querying distributed networks... ({visual_progress}%)")

                                check = get_scan_result(scan_id)
                                if check:
                                    status = check.get("status")
                                    if status == "Completed":
                                        progress_bar.progress(100)
                                        status_text.success("DATA SECURED & ANALYZED.")
                                        final_data = check
                                        break
                                    if status == "Failed":
                                        progress_bar.progress(100)
                                        status_text.error("SCAN FAILED OR TIMED OUT.")
                                        final_data = check
                                        break
                            else:
                                st.warning("Trace taking longer than expected.")
                    else:
                        st.error(f"System Error: {res.text}")

    # Render results OUTSIDE of the narrow col2 so it spans the full screen width
    if final_data:
        findings = final_data.get("findings", [])
        st.markdown("---")
        st.subheader("Intelligence Report")

        risk = final_data.get("risk_score", 0)
        r_col1, r_col2 = st.columns(2)
        r_col1.metric("Risk Score", f"{risk}/100")
        r_col2.metric("Total Findings", len(findings))
        
        st.markdown(f"**Status:** `{final_data.get('status')}`")

        if findings:
            render_findings(findings)
        else:
            st.info("No critical footprint data discovered for this target.")


# =========================
# TAB 2
# =========================
with tab2:
    st.subheader("Digital Forensics")
    st.markdown("Upload image payloads to inspect hidden metadata, device information, and geospatial coordinates.")

    with st.container(border=True):
        uploaded_file = st.file_uploader(
            "Drop target image here...",
            type=["jpg", "jpeg", "png"],
            key="scan_image_uploader",
        )

    if uploaded_file is not None:
        st.markdown("---")
        render_image_analysis(uploaded_file)