import streamlit as st
import pandas as pd
from datetime import datetime
import os
import re



# ---------------- LOGIN SYSTEM ----------------
DEMO_EMAIL = "admin@test.com"
DEMO_PASSWORD = "12345"

# ---------------- PAGE CONFIG ----------------
st.set_page_config(page_title="Technical Compliance Checklit", layout="wide")

if "logged_in" not in st.session_state:
    st.session_state.logged_in = False

if not st.session_state.logged_in:
    st.title("🔐 Login to Compliance Audit App")

    email = st.text_input("Email")
    password = st.text_input("Password", type="password")

    if st.button("Login"):
        if email == DEMO_EMAIL and password == DEMO_PASSWORD:
            st.session_state.logged_in = True
            st.success("Login Successful ✅")
            st.rerun()
        else:
            st.error("Invalid Email or Password ❌")

    st.stop()   # ⛔ stops rest of app



# Professional Styling
st.markdown("""
    <style>
    .main-header { font-size: 24px; font-weight: bold; color: #1E3A8A; border-bottom: 3px solid #1E3A8A; padding-bottom: 10px; }
    .section-header { background-color: #f1f5f9; padding: 10px; border-radius: 5px; font-weight: bold; color: #1e293b; border-left: 5px solid #3b82f6; margin-top: 20px; }
    .row-item { border-bottom: 1px solid #e2e8f0; padding: 8px 0; font-size: 14px; }
    </style>
""", unsafe_allow_html=True)

# ---------------- THE COMPLETE DATA STRUCTURE ----------------
# Every single point you provided is mapped here
AUDIT_DATABASE = {
    "A-C: Stationary Gen-Set Safety": {
        "A. Electrical Safety": [
            "A.1 Generator neutral properly earthed and connected to earth grid",
            "A.2 Separate body earthing provided for alternator and engine frame",
            "A.3 Generator control panel provided with double body earthing",
            "A.4 AMF panel interlocking working properly",
            "A.5 Reverse power / earth fault / overcurrent protections tested",
            "A.6 Generator breaker rating matching alternator capacity",
            "A.7 Synchronization panel properly configured and functional",
            "A.8 Load sharing system operational for multiple gensets",
            "A.9 Battery charger operational with healthy indication",
            "A.10 Starting batteries properly housed, ventilated, and terminals insulated"
        ],
        "B. Gas System Safety": [
            "B.1 Heat tracer KOD flange connection and leak free",
            "B.2 Gas inlet pressure regulator Valve properly mounted and leak-free",
            "B.3 Flexible hoses free from cracks/damage",
            "B.4 Gas line free from corrosion, dents, or mechanical damage",
            "B.5 Proper color coding and gas flow direction marking provided",
            "B.6 Gas inlet pressure within permissible limit",
            "B.7 Emergency Shut-Off Valve (ESV) provided and functional",
            "B.8 Gas pipeline properly supported and clamped",
            "B.9 Corrosion testing/monitoring(NDT) schedule for Gas divider"
        ],
        "C. Mechanical & Fire Safety": [
            "C.1 Exhaust system insulated and guarded",
            "C.2 Exhaust outlet directed away from wells",
            "C.3 Adequate ventilation provided",
            "C.4 Fire extinguishers (CO2/DCP) near genset and within validity",
            "C.5 Engine vibration pads in good condition",
            "C.6 No oil leakage from engine body",
            "C.7 Radiator guard intact and fan guarded",
            "C.8 Lube Oil Top-Up provision/auto lube oil maintainer"
        ]
    },
    "D-F: Truck-Mounted Gas Gen-Set": {
        "D. Vehicle & Structural Safety": [
            "D.1 Generator skid securely bolted to truck chassis",
            "D.2 Anti-vibration mountings intact",
            "D.3 Wheel chokes used during operation",
            "D.4 Vehicle properly parked on level ground",
            "D.5 Proper grounding rod connected before operation",
            "D.6 Chassis bonded with generator frame"
        ],
        "E. Electrical Checks": [
            "E.1 Portable earth pits provided and tested",
            "E.2 Output cable rating adequate for load",
            "E.3 Cable lugs properly crimped and insulated",
            "E.4 Cable routing free from mechanical damage",
            "E.5 Temporary connections avoided",
            "E.6 Earth leakage protection provided",
            "E.7 Output breaker functional and tested",
            "E.8 Safety relays properly installed and locked"
        ],
        "F. Gas Safety (Mobile Setup)": [
            "F.1 Gas hose protected from sharp edges",
            "F.2 Quick shut-off valve accessible",
            "F.3 Gas leak detector installed inside canopy",
            "F.4 No gas smell near enclosure",
            "F.5 Adequate ventilation inside truck enclosure",
            "F.6 Jubilee clamps properly tightened and leak-free",
            "F.7 Fire extinguisher status in truck mounted GG set"
        ]
    },
    "G-I: Truck-Mounted Diesel Gen-Set": {
        "G. Vehicle & Structural": ["G.1 Skid bolted", "G.2 Mountings intact", "G.3 Wheel chokes", "G.4 Level ground", "G.5 Grounding rod", "G.6 Chassis bonding"],
        "H. Electrical Checks": ["H.1 Earth pits", "H.2 Cable rating", "H.3 Lugs crimped", "H.4 Cable routing", "H.5 No temporary connections", "H.6 Earth leakage protection", "H.7 Breaker functional", "H.8 Relays seated"],
        "I. Fuel (HSD) Safety": [
            "I.1 Tank leak-free", "I.2 Vent pipe function", "I.3 Fuel level indicator", "I.4 No accumulation below tank", 
            "I.5 Labeled FLAMMABLE", "I.6 Double clamping", "I.7 No leakage filter/pump", "I.8 No rubbing hoses",
            "I.9 Engine OFF during refueling", "I.11 Fire extinguisher nearby", "I.14 Fire extinguisher status"
        ]
    },
    "J: MAIN WBSEDCL INCOMER": {
        "J. Incomer Details": [
            "J.1 Transformer control/location", "J.2 Separate neutral earthing", "J.3 Separate body earthing", "J.4 Periodic pit testing",
            "J.7 Barricading/Fencing", "J.8 Danger signs", "J.11 SPD operational", "J.18 Rubber mats condition", "J.22 Cable entry sealing","J.23	Overall housekeeping of panel room and transformer yard satisfactory?","J.24	If main incomer panel room is of metallic enclosure/sheet structure, proper earthing of the enclosure provided?"

        ]
    },
    "K: Electrical Panel Room": {
        "K. Panel Room Details": [
            "K.1 All earth pits tested periodically and test records maintained?","K.2 Earth pit identification and latest earth resistance values displayed at site?","K.3 Double earthing provided for all panels and equipment bodies?","K.4 “DANGER” and “No Unauthorized Entry” signage prominently displayed?","K.5 Panel room free from vegetation growth; surrounding area properly maintained?","K.6 Incomer panel SPD (Surge Protection Device) operational with healthy indication?","K.7 All feeders clearly identified with permanent labeling?","K.8 Protection settings of incomer and feeder relays/MCBs/MCCBs properly set and documented?","K.9 No multiple tapping from single output socket?","K.10 Distribution panel doors properly aligned and lockable?","K.11 Panels properly mounted with adequate mechanical support above cable trench?","K.12 Cable trenches covered with properly fitted chequered plates?","K.13 All cables routed through trench/tray; no floor-level cable obstruction?","K.14 Emergency lighting available and functional inside panel room?","K.15 Adequate firefighting equipment available (CO? / DCP extinguishers / sand buckets) and within validity period?","K.16 Distribution panel lighting transformer operational?","K.17 All panel covers, gland plates, and blanking plates intact and secured?","K.18 Earthing continuity verified; earth strips free from corrosion, loose bolts, or damage?","K.19 Illumination level inside and outside panel room adequate?","K.20 VFD phase indication lamps (R-Y-B) functioning properly?","K.21 VFD display units functioning properly?","K.22 VFD internal cleaning carried out; no dust accumulation?","K.23 No unused/open holes inside VFD panels; proper blanking provided?","K.24 Input/output plug sockets properly insulated and safe?","K.25 VFD doors properly closed and locked?","K.26 Adequate clearance between panels for ventilation and maintenance access?","K.27 Electrical Safety “Do’s & Don’ts” displayed in panel room?","K.28 Electrical Shock Treatment Chart displayed prominently?","K.29 Insulating rubber mats provided in front of panels and in good condition?","K.30 Panel room exhaust fan operational?","K.31 Exhaust fan adequately guarded and installed safely?","K.32 No signs of overheating, loose connections, or discoloration inside panels?","K.33 Cable entry points properly sealed to prevent rodent/moisture ingress?","K.34 Panel room shed/structure properly earthed?","K.35 Lightning Protection System provided and functioning properly?","K.36 Overall housekeeping of panel room and surrounding area satisfactory?","K.37 Updated Single Line Diagram (SLD) displayed inside panel room?","K.38 Site-specific Electrical Operation SOP available and approved?","K.39 LOTO (Lockout-Tagout) procedure available and LOTO register maintained?","K.40 Earth Pit Layout drawing available and displayed?","K.41 Well Pad Electrical Layout drawing available and updated?","K.42 List of Authorized Electrical Personnel displayed with contact details?","K.43 Emergency contact numbers (Electrical, Fire, Ambulance, Site In-charge) displayed at panel room and security room?","K.44 Heat Tracer Panel Should be properly layed & earthed.","K.45 Any Substandard temporary/permanent Connection avaliable ? ","K.46 Under Ground Cable marking avaliable ?","K.47 Improper cable termination for unused cables.","K.48 All Electrical  control  panels installed at the Panel room for proper equipotential bonding with Common Earthing","K.49 Sand bucket filled with dry sand, should not empty"

        ]
    },
    "L: WELL SKID AREA": {
        "L. Well Area Details": [
            "L.1 Is zone layout is displayed","L.2 Is safety sinagest board displayed","L.3 Is material Safety Data Sheets (MSDS) are displayed","L.4 Fencing Condition","L.5 Is Well pad  having unused old water connect line and the associated equipment. ","L.6 SOP of the Bean changing","L.7 Is First-aid  box  is available  at  well  pad in security room","L.8 Is 3 Clours dustbin are available","L.9 Is Emergency contact list displayed","L.10 Well Pad Entry Gate","L.11 Produced Pit Fencing","L.12 Water pit liner condition","L.13 Is Lighting Arrestor available","L.14 DH Stuffing Box cover","L.15 Well Barrication","L.16 Manifold and Valve without blind","L.17 Scarp material in Well Pad","L.18 Flexible hose condition","L.19 Life Buoy near water Pit","L.20 PG Tapping point was should not be  plugged with the cloth and wooden stick.","L.21 If Solar lamp available not working condition, then remove","L.22 Temporary shed of iron rods and tin sheets of low height for cycle and vehicle parking","L.23 Unused gas or water line proper isolation","L.24 Adequate Illumination in Well Pad","L.25 Electrical bonding jumpers across the metallic flanged connection","L.26 Open cable found to be tapped inside security cabin.","L.27 Security guard should carry a stick for self-defense or to drive away cattle entering the premises.","L.28 Carbolic Acid bottle is not allowed in security room","L.29 Safety Guard room Don’t have Fan","L.30 Safety Guard room wiring condition","L.31 Emergency light in secuirty room","L.32 Motor provided with double body earthing?","L.33 Double body earthing connected through independent/dedicated risers?","L.34 Earthing terminations properly crimped, tightened, and corrosion-free?","L.35 No abnormal mechanical vibration observed during motor operation?","L.36 All gland plates and terminal cover bolts properly fitted and secured?","L.37 No unused/open holes in motor enclosure?","L.38 Drive head canopy cover provided and in proper condition?","L.39 Drive head stuffing box cover properly installed and locked?","L.40 No water leakage from drive head unit; arrangement provided to collect leakage water (if applicable)?","L.41 Motor base/stand properly grouted or fixed on concrete foundation; not supported on wooden blocks?","L.42 Double washer arrangement provided in drive head support stand foundation bolts?","L.43 Drive head oil leakage (if any) cleaned and area maintained properly?","L.44 Motor cable gland and terminations proper, tight, and free from damage?","L.45 No cable joints lying directly on ground; cables adequately supported and elevated from ground level?","L.46 No insulation damage or armour exposure in motor cables?","L.47 Vegetation growth around motor/drive head area trimmed and controlled?","L.48 All Area Pole Light Should be Properly earthed, No any holes in its terminals or covers"
        ]
    },
    "M-O: Process & Backup": {
        "M. Separator Skid": ["M.1 Separator body properly earthed through earth strip and in good condition?","M.2 Earth strip free from corrosion; rusted strips and nut-bolts replaced where required?","M.3 All scanners/instrumentation separately earthed (dedicated instrument earthing provided)?","M.4 SPD (Surge Protection Device) provided for scanner/instrument circuits and health status verified?","M.5 PSV (Pressure Safety Valve) testing records available and within valid calibration/test due date?","M.6 Separator hydrostatic test certificate available and within validity period?","M.7 Separator ultrasonic thickness (UT) test certificates available and within due date?","M.8 All earth pits properly maintained and periodically tested; records available?","M.9 Separate earth pits provided for equipment body earthing and instrument earthing?","M.10 Bird Mesh on Separator vessel","M.11 All water & Gas Pipe line and Hose Proper support","M.12 Separator Without PSV"],
        "N. Water Pump Area": ["N.1 Water pump feeder panel provided with double body earthing?","N.2 Feeder panel properly closed; internal cleanliness maintained?","N.3 Panel indication lamps functioning properly?","N.4 Water pump motor properly earthed?","N.5 Earth strip condition satisfactory (free from corrosion, damage, or loose connections)?","N.6 All rotating parts adequately covered with canopy/guard?","N.7 No water leakage observed at any point in the water pump system?","N.8 Vegetation growth around pump area controlled and trimmed?","N.9 Pressure gauge on discharge line functional and calibrated?","N.10 Sheet water tank (if provided) properly earthed?","N.11 Sacrificial anode properly connected to the water tank (for corrosion protection)?","N.12 No cables laid above ground; cables routed underground or through proper cable tray/trench?","N.13 No signs of overheating, loose connections, or discoloration inside panel?","N.14 No unused/open holes in panel enclosure?","N.15 Cable entry to panel provided with proper cable glands and sealing arrangement?"],
        "O. Back-up System Room": ["O.1 Batteries placed on properly designed and secured racks?","O.2 Battery racks properly earthed?","O.3 No cables laid directly on ground; cables routed through proper casing/conduit/tray?","O.4 Insulating rubber mats provided in front of panels and battery racks?","O.5 All electrical panels properly earthed with double body earthing?","O.6 Each battery bank provided with adequate circuit protection (MCCB/Fuse)?","O.7 All battery terminals covered with proper terminal caps; no exposed live terminals?","O.8 Latest battery testing and maintenance records available in battery room?","O.9 Room air-conditioned to maintain temperature below 25°C (or as per battery manufacturer recommendation)?","O.10 Room temperature monitoring system with hooter/alarm provision available?","O.11 No exposed/naked electrical terminations inside battery room?","O.12 Substandard or temporary wiring strictly avoided inside battery room/bunk house?","O.13 If bunk house provided, its metallic body separately earthed?","O.14 Bunk house flooring in proper and safe condition?","O.15 All openings/unused holes in bunk house properly sealed?","O.16 All doors and locking arrangements in proper working condition?","O.17 Adequate exhaust or cross ventilation provided (especially for concrete rooms)?","O.18 Battery operation “Do’s & Don’ts” displayed inside battery room?","O.19 Electrical panels properly mounted above cable trench level?","O.20 Cable trench properly covered with chequered plates?","O.21 Unarmoured (Univyne/PVC) cables and armoured cables routed separately?","O.22 CO? and DCP type fire extinguishers available inside battery room and within validity period?","O.23 Alarm/hooter sound clearly audible up to security room?","O.24 Dedicated earth pits inspected, tested, and properly maintained?","O.25 Vegetation growth around battery room controlled and trimmed?","O.26 Unwanted/scrap materials removed from panel/battery room?","O.27 Adequate illumination provided inside and outside battery room?","O.28 All internal wiring properly routed and covered with appropriate casing/conduit?"]
    }
}

# ---------------- APP LOGIC ----------------
st.markdown('<p class="main-header">📋 Comprehensive Site Compliance Audit</p>', unsafe_allow_html=True)

if "audit_responses" not in st.session_state:
    st.session_state.audit_responses = {}

with st.sidebar:
    st.header("📍 Location Data")

    

    # 👇 ADD THIS
    if st.button("Logout"):
        st.session_state.logged_in = False
        st.rerun()


    pad = st.selectbox("Well Pad", [f"Pad {i:02d}" for i in range(1, 11)])
    well = st.text_input("Well ID", "W-01")
    auditor = st.text_input("Collector Name")
    st.divider()
    st.write("Complete all items in each tab.")

# Display Tabs
tabs = st.tabs(list(AUDIT_DATABASE.keys()))

for i, (tab_name, sections) in enumerate(AUDIT_DATABASE.items()):
    with tabs[i]:
        for sec_title, items in sections.items():
            st.markdown(f'<div class="section-header">{sec_title}</div>', unsafe_allow_html=True)
            
            # Header
            h1, h2, h3, h4 = st.columns([4, 1.2, 1, 2.5])
            h2.caption("Status")
            h3.caption("Sev")
            h4.caption("Remarks")

            for item in items:
                key = f"{tab_name}_{sec_title}_{item}"
                c1, c2, c3, c4 = st.columns([4, 1.2, 1, 2.5])
                
                with c1:
                    st.markdown(f'<div class="row-item">{item}</div>', unsafe_allow_html=True)
                with c2:
                    status = st.radio("S", ["OK", "Obs", "N/A"], key=f"s_{key}", horizontal=True, label_visibility="collapsed")
                with c3:
                    is_obs = (status == "Obs")
                    sev = st.selectbox("V", ["-", "L", "M", "H"], key=f"v_{key}", disabled=not is_obs, label_visibility="collapsed")
                with c4:
                    rem = st.text_input("R", key=f"r_{key}", label_visibility="collapsed", placeholder="Details...")

                st.session_state.audit_responses[key] = {
                    "Tab": tab_name, "Section": sec_title, "Item": item,
                    "Status": status, "Severity": sev, "Remarks": rem
                }

# ---------------- SAVE LOGIC ----------------
st.divider()
if st.button("💾 Finalize and Save Audit", use_container_width=True, type="primary"):
    if not auditor:
        st.error("Enter Auditor Name")
    else:
        # File Path
        BASE_PATH = r"D:\python_project\Ram_sir_project"
        os.makedirs(BASE_PATH, exist_ok=True)
        pad_name = pad
        os.makedirs(os.path.join(BASE_PATH,pad_name), exist_ok=True)
        filename = f"Audit_{well}_{datetime.now().strftime('%Y%m%d')}.xlsx"
        full_path = os.path.join(BASE_PATH, pad_name,filename)
        
        try:
            with pd.ExcelWriter(full_path, engine='xlsxwriter') as writer:
                # Compile data and save
                df = pd.DataFrame(st.session_state.audit_responses.values())
                
                # Sheet Cleanup logic (Removes special chars for Excel)
                for t_name in df['Tab'].unique():
                    clean_name = re.sub(r'[\\/*?:\[\]]', '', t_name)[:31]
                    cat_df = df[df['Tab'] == t_name]
                    cat_df.to_excel(writer, sheet_name=clean_name, index=False)
                    
            st.success(f"Audit Saved: {full_path}")
        except Exception as e:
            st.error(f"Save failed: {e}")