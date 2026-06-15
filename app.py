import streamlit as st
import matplotlib.pyplot as plt
import matplotlib.patches as patches
import numpy as np

# --- 1. Page & Layout Configuration ---
st.set_page_config(page_title="RF Probe Layout Validator", layout="wide", initial_sidebar_state="collapsed")

# Professional UI Styling
st.markdown("""
    <style>
    section.main > div { padding-left: 2rem; padding-right: 2rem; }
    div[data-testid="stRadio"] label {
        font-family: 'Courier New', Courier, monospace !important;
        font-weight: bold; font-size: 1.05rem !important; white-space: pre; 
    }
    .stMarkdown h1 a, .stMarkdown h2 a, .stMarkdown h3 a, 
    .stHeader a, [data-testid="stHeader"] a, a.header-anchor { display: none !important; }
    [data-testid="stHeader"] svg, .stMarkdown svg { visibility: hidden !important; }
    h1:hover a, h2:hover a, h3:hover a { pointer-events: none !important; }
    [data-testid="column"] { flex: 1 1 0% !important; min-width: 140px !important; }
    </style>
""", unsafe_allow_html=True)

# =========================================================
# --- 2. Hierarchical Product Database ---
# =========================================================

UI_CONFIG = {
    "safe_dist": 0.025,       
    "safe_zone_color": "#90EE90", 
    "safe_zone_alpha": 0.3,
    "tip_color_ok": "blue", "tip_color_fail": "red", 
    "icon_ok": "✅", "icon_warn": "⚠️", "icon_fail": "❌"
}

BASE_SPECS = {
    "tip_d": 0.1, "probe_d": 0.28, "shield_d": 1.1,
    "tilt": 0.0, "tip_len": 0.7, "solder_h": 0.0,
    "blade_height": 0.6, "b_horiz_len": 0.25    
}

# The complete database structure provided
PRODUCT_DATABASE = {
    "Single-end": {
        "S-Probe (GS/SG)": {
            "16 GHz": [
                {"part_no": "SP-GR-181512", "pitch": 1.20},
                {"part_no": "SP-GR-181514", "pitch": 1.40},
                {"part_no": "SP-GR-161516", "pitch": 1.60}
            ],
            "18 GHz": [
                {"part_no": "SP-GR-181508", "pitch": 0.80},
                {"part_no": "SP-GR-181510", "pitch": 1.00}
            ],
            "20 GHz": [
                {"part_no": "SP-GR-2015025", "pitch": 0.25},
                {"part_no": "SP-GR-201504", "pitch": 0.40},
                {"part_no": "SP-GR-201505", "pitch": 0.50}
            ],
            "30 GHz": [
                {"part_no": "SP-GR-3015025", "pitch": 0.25},
                {"part_no": "SP-GR-301504", "pitch": 0.40},
                {"part_no": "SP-GR-301505", "pitch": 0.50}
            ]
        },
        "R-Probe (GS/SG)": {
            "12 GHz": [
                {"part_no": "RP-GR-121508", "pitch": 0.80},
                {"part_no": "RP-GR-121510", "pitch": 1.00}
            ],
            "15 GHz": [
                {"part_no": "RP-GR-151504", "pitch": 0.40},
                {"part_no": "RP-GR-151505", "pitch": 0.50}
            ],
            "18 GHz": [
                {"part_no": "RP-GR-181502", "pitch": 0.20},
                {"part_no": "RP-GR-181503", "pitch": 0.30}
            ]
        },
        "S-Probe (GSG)": {
            "40 GHz": [
                {"part_no": "SP-GSG-401504", "pitch": 0.4},
            ]
        }
    },
    "Differential": {
        "D-Probe (SS)": {
            "20 GHz": [
                {"part_no": "DP-SS-201503", "pitch": 0.30},
                {"part_no": "DP-SS-201504", "pitch": 0.40},
                {"part_no": "DP-SS-201505", "pitch": 0.50},
                {"part_no": "DP-SS-201508", "pitch": 0.80},
                {"part_no": "DP-SS-201510", "pitch": 1.00},
                {"part_no": "DP-SS-201512", "pitch": 1.20}
            ],
            "40 GHz": [
                {"part_no": "DP-SS-401502", "pitch": 0.20},
                {"part_no": "DP-SS-401503", "pitch": 0.30},
                {"part_no": "DP-SS-401504", "pitch": 0.40},
                {"part_no": "DP-SS-401505", "pitch": 0.50},
                {"part_no": "DP-SS-401506", "pitch": 0.60},
                 {"part_no": "DP-SS-351508", "pitch": 0.80}
            ]
        },
          "D-Probe (GSSG)": {
            "40 GHz": [
                {"part_no": "DP-GSSG-401503", "pitch": 0.30},
                {"part_no": "DP-GSSG-401504", "pitch": 0.40},
                {"part_no": "DP-GSSG-401505", "pitch": 0.50},
                {"part_no": "DP-GSSG-401508", "pitch": 0.60},
                {"part_no": "DP-GSSG-401508", "pitch": 0.80},
                {"part_no": "DP-GSSG-401509", "pitch": 0.90},
                {"part_no": "DP-GSSG-401510", "pitch": 1.00}
            ],
            "65 GHz": [
                {"part_no": "DP-GSSG-651503", "pitch": 0.30},
                {"part_no": "DP-GSSG-651504", "pitch": 0.40},
                {"part_no": "DP-GSSG-651505", "pitch": 0.50},
                {"part_no": "DP-GSSG-651505", "pitch": 0.60},
                {"part_no": "DP-GSSG-651508", "pitch": 0.80},
                {"part_no": "DP-GSSG-651509", "pitch": 0.90},
                {"part_no": "DP-GSSG-651510", "pitch": 1.00}
            ]
        },
    }
}

# Drawing constants based on series type
SERIES_MECHANICALS = {
    "S-Probe (GS/SG)": {"tilt": 0.0, "tip_len": 0.7, "solder_h": 0.0},
    "R-Probe (GS/SG)": {"tilt": 0.0, "tip_len": 0.7, "solder_h": 0.0},
    "S-Probe (GSG)":   {"tilt": 0.0, "tip_len": 0.7, "solder_h": 0.0},
    "D-Probe (SS)":    {"tilt": 52.0, "tip_len": 0.7, "solder_h": 0.8},
    "D-Probe (GSSG)":  {"tilt": 52.0, "tip_len": 0.92, "solder_h": 0.8}
}

# =========================================================
# --- 3. Functions: Geometric Calculation & Drawing ---
# =========================================================

def rotate_point(x, y, angle_deg, cx, cy):
    theta = np.radians(angle_deg)
    return cx + (x-cx)*np.cos(theta)-(y-cy)*np.sin(theta), cy + (x-cx)*np.sin(theta)+(y-cy)*np.cos(theta)

def get_pad_patch(xp, w, h, shape_type, offset=0):
    nw, nh = w - 2*offset, h - 2*offset
    if nw <= 0 or nh <= 0: return None
    if shape_type == "Rectangle": return patches.Rectangle((xp - nw/2, -nh/2), nw, nh)
    elif shape_type == "Circle": return patches.Circle((xp, 0), nw/2)
    elif shape_type == "Square":
        s = max(nw, nh)
        return patches.Rectangle((xp - s/2, -s/2), s, s)
    return None

def draw_probes(ax, x_tips, roles, angles, p_d, s_d, tip_len, b_h, s_height, t_d, series_name, is_compliant):
    shield_anchors, s_shield_edges = {}, []
    tip_color = UI_CONFIG["tip_color_ok"] if is_compliant else UI_CONFIG["tip_color_fail"]
    
    for i, role in enumerate(roles):
        if role == 'S':
            x_tip, ang = x_tips[i], angles[i]
            shield_pts = [[x_tip-s_d/2, tip_len], [x_tip+s_d/2, tip_len], [x_tip+s_d/2, tip_len+1.4], [x_tip-s_d/2, tip_len+1.4]]
            ax.add_patch(patches.Polygon([rotate_point(px, py, ang, x_tip, 0) for px, py in shield_pts], facecolor='none', edgecolor='black', lw=1.2, zorder=10))
            s_idx_list = [idx for idx, r in enumerate(roles) if r == 'S']
            edge_x = x_tip + s_d/2 if i == s_idx_list[0] else x_tip - s_d/2
            s_shield_edges.append({'bottom': rotate_point(edge_x, tip_len, ang, x_tip, 0), 'top': rotate_point(edge_x, tip_len+s_height, ang, x_tip, 0)})
            shield_anchors[i] = {'L': [rotate_point(x_tip-s_d/2, tip_len, ang, x_tip, 0), rotate_point(x_tip-s_d/2, tip_len+b_h, ang, x_tip, 0)],
                                'R': [rotate_point(x_tip+s_d/2, tip_len, ang, x_tip, 0), rotate_point(x_tip+s_d/2, tip_len+b_h, ang, x_tip, 0)]}
            inner_poly = [[x_tip, 0], [x_tip+p_d/2, 0.15], [x_tip+p_d/2, tip_len], [x_tip-p_d/2, tip_len], [x_tip-p_d/2, 0.15]]
            ax.add_patch(patches.Polygon([rotate_point(px, py, ang, x_tip, 0) for px, py in inner_poly], facecolor='none', edgecolor='black', lw=1.2, zorder=10))
            ax.add_patch(patches.Circle((x_tip, 0), t_d/2, color=tip_color, zorder=15))

    if ("D-Probe" in series_name) and s_height > 0 and len(s_shield_edges) >= 2:
        s_pts = [s_shield_edges[0]['bottom'], s_shield_edges[1]['bottom'], s_shield_edges[1]['top'], s_shield_edges[0]['top']]
        ax.add_patch(patches.Polygon(s_pts, facecolor='#D3D3D3', edgecolor='black', alpha=0.5, zorder=5))

    for i, role in enumerate(roles):
        if role == 'G':
            x_tip, ang = x_tips[i], angles[i]
            if "R-Probe" in series_name:
                adj_s_idx = i + 1 if (i + 1) in shield_anchors else i - 1
                if adj_s_idx in shield_anchors:
                    r_target_x = x_tips[adj_s_idx] - s_d/2 if i < adj_s_idx else x_tips[adj_s_idx] + s_d/2
                    path_pts = [[x_tip, 0], [r_target_x, 0.15], [r_target_x, tip_len]]
                    rotated_pts = [rotate_point(px, py, ang, x_tip, 0) for px, py in path_pts]
                    ax.plot([p[0] for p in rotated_pts], [p[1] for p in rotated_pts], color='black', lw=2.5, zorder=10)
                    ax.add_patch(patches.Circle((x_tip, 0), t_d/2, color=tip_color, zorder=15))
            else:
                adj_s_idx = (i+1 if (i+1) in shield_anchors else (i-1 if (i-1) in shield_anchors else None))
                if adj_s_idx is not None:
                    side = 'L' if i < adj_s_idx else 'R'
                    anchors, ext_dir = shield_anchors[adj_s_idx][side], (-1 if side == 'L' else 1)
                    _sx, _sa = x_tips[adj_s_idx], angles[adj_s_idx]
                    blade_pts = [[x_tips[i], 0], rotate_point(_sx+ext_dir*(p_d/2+0.05), 0.35, _sa, _sx, 0), 
                                 rotate_point(_sx+ext_dir*(p_d/2+0.05), tip_len, _sa, _sx, 0), anchors[0], anchors[1], 
                                 rotate_point(_sx+ext_dir*(s_d/2+0.25), tip_len+b_h, _sa, _sx, 0), [x_tips[i]+ext_dir*p_d, 0.1]]
                    ax.add_patch(patches.Polygon(blade_pts, facecolor='none', edgecolor='black', lw=1.2, zorder=10))
                    ax.add_patch(patches.Circle((x_tips[i], 0), t_d/2, color=tip_color, zorder=15))

# =========================================================
# --- 4. State Management ---
# =========================================================

MIL_TO_MM = 0.0254
default_val = 300.0
if 'p_w_val' not in st.session_state: st.session_state.p_w_val = default_val
if 'p_h_val' not in st.session_state: st.session_state.p_h_val = default_val
if 'pad_pitch_val' not in st.session_state: st.session_state.pad_pitch_val = default_val
if 'pad_layouts' not in st.session_state:
    st.session_state.pad_layouts = [{"name": "Layout 1", "w": default_val, "h": default_val, "pitch": default_val, "unit": "um", "shape": "Rectangle"}]
if 'active_layout_idx' not in st.session_state: st.session_state.active_layout_idx = 0
if 'unit_mode' not in st.session_state: st.session_state.unit_mode = "um"

def handle_unit_toggle():
    old, new = st.session_state.unit_mode, st.session_state.unit_selector
    if old != new:
        ratio = 25.4 if (old == "mil" and new == "um") else (1.0 / 25.4)
        st.session_state.p_w_val *= ratio
        st.session_state.p_h_val *= ratio
        st.session_state.pad_pitch_val *= ratio
        st.session_state.unit_mode = new

def set_active_layout(idx): st.session_state.active_layout_idx = idx

def align_value(val, step):
    return round(val / step) * step

# =========================================================
# --- 5. UI Flow ---
# =========================================================

st.title("RF Probe Layout Validator")

with st.expander("📌 Manage Multiple Target Pad Layouts", expanded=True):
    st.radio("Select Input Unit:", ["um", "mil"], key="unit_selector", on_change=handle_unit_toggle, horizontal=True)
    
    selected_step = st.radio(
        f"Select Adjustment Step ({st.session_state.unit_mode}):",
        options=[1.0, 5.0, 10.0, 50.0],
        index=0, horizontal=True
    )

    st.session_state.p_w_val = align_value(st.session_state.p_w_val, selected_step)
    st.session_state.p_h_val = align_value(st.session_state.p_h_val, selected_step)
    st.session_state.pad_pitch_val = align_value(st.session_state.pad_pitch_val, selected_step)

    c1, c2, c3, c4 = st.columns(4) 
    with c1: p_shape = st.selectbox("Pad Shape", ["Rectangle", "Circle", "Square"])
    with c2: p_w_in = st.number_input(f"Width ({st.session_state.unit_mode})", key="p_w_val", step=float(selected_step))
    with c3: 
        if p_shape in ["Square", "Circle"]:
            p_h_in = st.number_input(f"Height ({st.session_state.unit_mode})", value=p_w_in, disabled=True)
        else:
            p_h_in = st.number_input(f"Height ({st.session_state.unit_mode})", key="p_h_val", step=float(selected_step))
    with c4: 
        pitch_in = st.number_input(f"Pitch ({st.session_state.unit_mode})", key="pad_pitch_val", step=float(selected_step))
    
    if st.button("➕ Add Current Layout"):
        st.session_state.pad_layouts.append({
            "name": f"Layout {len(st.session_state.pad_layouts)+1}", 
            "w": p_w_in, "h": p_h_in, "pitch": pitch_in, 
            "unit": st.session_state.unit_mode, "shape": p_shape
        })

    for i, lay in enumerate(st.session_state.pad_layouts):
        cols = st.columns([5, 1])
        h_val = lay.get('h', lay['w']) 
        cols[0].info(f"**{lay['name']}**: Pitch {lay['pitch']}{lay['unit']} | Size {lay['w']}x{h_val}{lay['unit']}")
        if cols[1].button("🗑️", key=f"del_{i}"):
            st.session_state.pad_layouts.pop(i); st.rerun()

st.divider()

# --- Step 2. Hierarchical Product Selection with Frequency Filter ---
st.subheader("Step 2. Product Specification Filter")
col_type, col_series, col_freq = st.columns(3)

with col_type:
    sig_type = st.selectbox("Signal Type", list(PRODUCT_DATABASE.keys()))

with col_series:
    series = st.selectbox("Product Series", list(PRODUCT_DATABASE[sig_type].keys()))

with col_freq:
    # --- Frequency Selection with 'ALL' (Default) ---
    freq_options = ["ALL"] + list(PRODUCT_DATABASE[sig_type][series].keys())
    selected_freq = st.selectbox("Frequency Bandwidth", freq_options, index=0)

# Compliance Logic
mech = SERIES_MECHANICALS[series]
T_D, P_D, S_D, TILT, T_LEN, SOLDER = BASE_SPECS["tip_d"], BASE_SPECS["probe_d"], BASE_SPECS["shield_d"], mech["tilt"], mech["tip_len"], mech["solder_h"]
role_map = {"S-Probe (GS/SG)":['G','S'], "R-Probe (GS/SG)":['G','S'], "S-Probe (GSG)":['G','S','G'], "D-Probe (SS)":['S','S'], "D-Probe (GSSG)":['G','S','S','G']}
roles_list = role_map[series]; num_pins = len(roles_list)

model_labels, label_to_data = [], {}

# Logic to extract ALL items from ALL frequencies within the chosen series
# Logic to handle 'ALL' or specific frequency selection
if selected_freq == "ALL":
    filtered_items = []
    for f_key in PRODUCT_DATABASE[sig_type][series]:
        filtered_items.extend(PRODUCT_DATABASE[sig_type][series][f_key])
else:
    filtered_items = PRODUCT_DATABASE[sig_type][series][selected_freq]

for p in filtered_items:
    all_res = []
    for lay in st.session_state.pad_layouts:
        f = 0.001 if lay['unit'] == "um" else MIL_TO_MM
        pw_m, pi_m = lay['w'] * f, lay['pitch'] * f
        safe_lim = (pw_m / 2) - UI_CONFIG["safe_dist"] - (T_D / 2)
        xt = [(-(num_pins-1)*p['pitch']/2) + j*p['pitch'] for j in range(num_pins)]
        xp = [(-(num_pins-1)*pi_m/2) + j*pi_m for j in range(num_pins)]
        df = [xt[j] - xp[j] for j in range(num_pins)]; opt = (max(df) + min(df)) / 2
        all_res.append(all(abs(xt[j] - (xp[j] + opt)) <= (safe_lim + 1e-9) for j in range(num_pins)))
    
    icon = UI_CONFIG['icon_ok'] if all(all_res) else UI_CONFIG['icon_warn'] if any(all_res) else UI_CONFIG['icon_fail']
    lbl = f"{p['part_no']} (Pitch: {p['pitch']}mm)".ljust(35) + icon
    model_labels.append(lbl); label_to_data[lbl] = {"pitch": p['pitch'], "part_no": p['part_no'], "all_res": all_res}

selected_label = st.radio("Select Model for Validation:", model_labels)
data = label_to_data[selected_label]

st.write("🔍 **Individual Layout Compatibility (Click to Preview Simulation):**")
n_lay = len(st.session_state.pad_layouts)
if n_lay > 0:
    t_cols = st.columns(n_lay)
    for i, lay in enumerate(st.session_state.pad_layouts):
        is_ok = data['all_res'][i]
        with t_cols[i]:
            st.button(f"{'✅' if is_ok else '❌'} {lay['name']}", key=f"btn_{i}", use_container_width=True,
                      on_click=set_active_layout, args=(i,))

# =========================================================
# --- 6. Graphics Engine (Centered Labels & Compact View) ---
# =========================================================

if n_lay > 0:
    safe_idx = min(st.session_state.active_layout_idx, n_lay - 1)
    st.session_state.active_layout_idx = safe_idx
    curr_lay = st.session_state.pad_layouts[safe_idx]
    f = 0.001 if curr_lay['unit'] == "um" else MIL_TO_MM
    pw_m, ph_m, pi_m = curr_lay['w'] * f, curr_lay.get('h', curr_lay['w']) * f, curr_lay['pitch'] * f
    
    fig, ax = plt.subplots(figsize=(10, 6)); ax.set_aspect('equal')
    raw_tips = [(-(num_pins-1)*data['pitch']/2) + i*data['pitch'] for i in range(num_pins)]
    s_idx = [i for i, r in enumerate(roles_list) if r == 'S']
    x_tips = [t - (np.mean([raw_tips[i] for i in s_idx]) if s_idx else 0) for t in raw_tips]
    raw_pads = [(-(num_pins-1)*pi_m/2) + i*pi_m for i in range(num_pins)]
    df_list = [x_tips[i] - raw_pads[i] for i in range(num_pins)]
    x_pads = [p + (max(df_list) + min(df_list))/2 for p in raw_pads]

    for xp in x_pads:
        p_patch = get_pad_patch(xp, pw_m, ph_m, curr_lay['shape'])
        if p_patch: ax.add_patch(p_patch).set(facecolor='white', edgecolor='black', lw=1.2, zorder=1)
        s_patch = get_pad_patch(xp, pw_m, ph_m, curr_lay['shape'], offset=UI_CONFIG["safe_dist"]+T_D/2)
        if s_patch: ax.add_patch(s_patch).set(facecolor=UI_CONFIG["safe_zone_color"], alpha=UI_CONFIG["safe_zone_alpha"], ls='--', lw=1.0, zorder=2)

    # Angle calculation
    angs = [0] * num_pins
    if len(s_idx) > 0:
        for i in s_idx:
            angs[i] = TILT/2 if (len(s_idx) > 1 and i == s_idx[0]) else (-TILT/2 if len(s_idx) > 1 else TILT)
        for i, r in enumerate(roles_list):
            if r == 'G':
                if i+1 < num_pins and roles_list[i+1] == 'S': angs[i] = angs[i+1]
                elif i-1 >= 0 and roles_list[i-1] == 'S': angs[i] = angs[i-1]

    draw_probes(ax, x_tips, roles_list, angs, P_D, S_D, T_LEN, BASE_SPECS["blade_height"], SOLDER, T_D, series, data['all_res'][safe_idx])
    
    # Render Pad Pitch and Width centered between middle pads
    num_pads = len(x_pads)
    if num_pads > 1:
        m1 = (num_pads - 1) // 2
        m2 = m1 + 1
        
        # Render Pad Pitch Dimension Line centered between middle pads
        ax.annotate('', 
                    xy=(x_pads[m1], -ph_m/2 - 0.35), 
                    xytext=(x_pads[m2], -ph_m/2 - 0.35), 
                    arrowprops=dict(arrowstyle='<->', color='#404040', lw=1))
        
        # Render Pad Pitch Value Label
        ax.text((x_pads[m1] + x_pads[m2]) / 2, -ph_m/2 - 0.45, 
                f"Pad Pitch: {pi_m*1000:.0f} µm", 
                ha='center', va='top', fontsize=8, color='#404040')

    # Render Pad Width (W) Dimension centered on middle pad m1
    ax.annotate('', 
                xy=(x_pads[m1] - pw_m/2, -ph_m/2 - 0.05), 
                xytext=(x_pads[m1] + pw_m/2, -ph_m/2 - 0.05), 
                arrowprops=dict(arrowstyle='<->', color='#404040', lw=1))

    # Render Pad Width Value Label
    ax.text(x_pads[m1], -ph_m/2 - 0.1, 
            f"W:{pw_m * 1000 :.0f} µm", 
            ha='center', va='top', fontsize=7, color='#404040')

    # Positioned to the left of the pad to avoid overlap with Pitch/Width labels
    ax.annotate('', 
                xy=(x_pads[0] - pw_m/2 - 0.15, -ph_m/2), 
                xytext=(x_pads[0] - pw_m/2 - 0.15, ph_m/2), 
                arrowprops=dict(arrowstyle='<->', color='#404040', lw=1))

    # Render Height Value Label (Vertical Text)
    ax.text(x_pads[0] - pw_m/2 - 0.25, 0, 
            f"H:{ph_m * 1000 :.0f} µm", 
            ha='right', va='center', rotation=90, 
            fontsize=7, color='#404040')
    
    # PROBE PITCH ANNOTATION (TOP)
    g_idx_list = [i for i, r in enumerate(roles_list) if r == 'G']
    i1, i2 = (s_idx[0], s_idx[1]) if len(s_idx) >= 2 else (g_idx_list[0], s_idx[0]) if (g_idx_list and s_idx) else (0, 0)
    if i1 != i2:
        ax.annotate('', xy=(x_tips[i1], T_LEN+1.5), xytext=(x_tips[i2], T_LEN+1.5), arrowprops=dict(arrowstyle='<->', color='black', lw=1.2))
        ax.text((x_tips[i1]+x_tips[i2])/2, T_LEN+1.6, f"Probe Pitch: {data['pitch'] * 1000 :.0f} µm", ha='center', va='bottom', fontsize=9, color='black', fontweight='bold')

    max_ex = max(abs(min(x_tips[0]-S_D, x_pads[0]-pw_m)), abs(max(x_tips[-1]+S_D, x_pads[-1]+pw_m)))
    ax.set_xlim(-max_ex-0.5, max_ex+0.5)
    ax.set_ylim(-ph_m-1.2, T_LEN+1.8)
    ax.axis('off')

    # BRANDING TEXT
    fig.text(0.52, 0.21, f"{series}", ha='center', va='bottom', fontsize=14, fontweight='bold')
    fig.text(0.52, 0.15, "PacketMicro", ha='center', va='center', fontsize=22, fontweight='bold')

    _, col_c, _ = st.columns([3, 4, 3])
    with col_c: 
        st.pyplot(fig, use_container_width=True)
        is_ok_final = data['all_res'][st.session_state.active_layout_idx]
        if not is_ok_final: st.error(f"❌ MISALIGNMENT in {curr_lay['name']}.")
        else: st.success(f"✅ COMPLIANT with {curr_lay['name']}.")
