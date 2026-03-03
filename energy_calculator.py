import streamlit as st

# =============================================================================
# ESC Home Energy Savings Calculator
# =============================================================================
# Baselines (Philly / PECO area averages)
# Electricity: ~$0.1626/kWh    Natural Gas: ~$1.50/therm
# Average monthly bill: $245   → Annual: $2,940
# Savings estimates: DOE, ENERGY STAR, PECO

st.set_page_config(page_title="ESC Home Energy Savings Calculator", layout="centered")

# Custom baby blue button styling
st.markdown("""
    <style>
    div.stButton > button:first-child {
        background-color: #89CFF0;     /* Baby blue */
        color: white;
        border: none;
        border-radius: 10px;
        padding: 14px 28px;
        font-size: 18px;
        font-weight: 600;
        width: 100%;
        box-shadow: 0 2px 8px rgba(0,0,0,0.1);
        transition: all 0.3s ease;
    }
    div.stButton > button:first-child:hover {
        background-color: #6ABFE8;     /* Slightly darker on hover */
        box-shadow: 0 6px 16px rgba(0,0,0,0.15);
        transform: translateY(-2px);
    }
    div.stButton > button:first-child:active {
        background-color: #5AAFE0;
        transform: translateY(0);
    }
    </style>
""", unsafe_allow_html=True)

# Display logo at the top
# CHANGE "logo.jpeg" TO YOUR EXACT FILENAME IF DIFFERENT (e.g. "logo.jpg", "EXPLORER.jpeg", etc.)
st.image("logo.jpeg", use_container_width=True, caption="Energy Saving Construction")

st.title("ESC Home Energy Savings Calculator")
st.markdown(
    "Estimate savings from efficiency upgrades like sealing, insulation, and more. "
    "**Estimates only** — actual results vary. Get a pro audit for precision!"
)

# ─────────────────────────────────────────────────────────────────────────────
# INPUT SECTION
# ─────────────────────────────────────────────────────────────────────────────

st.subheader("Basic Upgrades")

col1, col2 = st.columns([3, 2])

with col1:
    num_bulbs = st.number_input("Incandescent bulbs to replace with LEDs", min_value=0, step=1,
                                help="Swap 60–75W → 8–10W LEDs, ~3 hrs/day.")
    num_windows = st.number_input("Windows to caulk/seal", min_value=0, step=1,
                                  help="Reduces drafts around frames.")
    install_shades = st.selectbox("Install cellular/honeycomb shades?", ["No", "Yes"], index=0,
                                  help="Insulating shades cut heat loss/gain.")
    num_doors_weatherstrip = st.number_input("Doors for weatherstripping kits", min_value=0, step=1)
    num_doors_sweeps = st.number_input("Doors for bottom sweeps", min_value=0, step=1)

    home_sqft = st.number_input("Home size (sq ft)", min_value=0, step=100,
                                help="Typical Philly rowhome: 1,600–2,400 sq ft. Scales estimates. Required for accurate leak classification. Leave blank if unknown.")

# Advanced / Optional Inputs
st.subheader("Advanced Options (for more accuracy)")

# Blower Door / CFM50 Input (no max limit)
cfm50_input = st.number_input(
    "Blower door test result (CFM50) — optional",
    min_value=0.0, step=1.0,
    help="Cubic Feet per Minute at 50 Pascals from a professional blower door test. "
         "Typical ranges: Older/leaky homes often 2000–5000+ CFM50 (depending on size); After sealing: 1000–2000; "
         "Modern/good target: <1000–1500 for avg home. Higher CFM50 means more leakage "
         "(more natural air exchange — no suffocation risk; concern is too low CFM50 "
         "without ventilation like HRV). Leave blank to use manual leak level selector."
)

# Auto-classify leak level if CFM50 and home_sqft provided
if cfm50_input > 0 and home_sqft > 0:
    leakage_ratio = (cfm50_input / home_sqft) * 100  # % of sq ft
    if leakage_ratio <= 50:
        auto_leak = "Very Low"
        leak_factor = 0.60
    elif leakage_ratio <= 100:
        auto_leak = "Low"
        leak_factor = 0.80
    elif leakage_ratio <= 150:
        auto_leak = "Medium"
        leak_factor = 1.00
    elif leakage_ratio <= 200:
        auto_leak = "High"
        leak_factor = 1.20
    else:
        auto_leak = "Very High"
        leak_factor = 1.40
    
    st.caption(f"Auto-classified leak level based on CFM50 {cfm50_input:.0f} for {home_sqft} sq ft home "
               f"(ratio: {leakage_ratio:.1f}% of sq ft): **{auto_leak}** "
               f"— {auto_leak} leaks ({'≤' if auto_leak != 'Very High' else ''} {leakage_ratio:.1f}% of sq ft)")

elif cfm50_input > 0 and home_sqft == 0:
    st.warning("Please enter home sq ft for accurate leak classification based on CFM50.")
    leak_factor = 1.00  # Default to medium if no sq ft

else:
    # Manual selection fallback
    leak_options = {
        "Very Low":  {"multiplier": 0.60, "desc": "Minimal drafts (≤50% sq ft CFM50)"},
        "Low":       {"multiplier": 0.80, "desc": "Minor leaks (51–100% sq ft CFM50)"},
        "Medium":    {"multiplier": 1.00, "desc": "Typical older Philly home (101–150% sq ft CFM50)"},
        "High":      {"multiplier": 1.20, "desc": "Noticeable drafts (151–200% sq ft CFM50)"},
        "Very High": {"multiplier": 1.40, "desc": "Severe leaks (>200% sq ft CFM50)"}
    }

    selected_leak = st.selectbox(
        "Home leak level (manual selection)",
        options=list(leak_options.keys()),
        index=2,  # Medium default
        help="Adjusts savings — higher leaks = more potential from sealing."
    )
    st.caption(f"Selected: {selected_leak} — {leak_options[selected_leak]['desc']}")
    leak_factor = leak_options[selected_leak]["multiplier"]

# Attic Cellulose Insulation
st.subheader("Attic Insulation Upgrade")
attic_insulated = st.checkbox("Adding/improving cellulose insulation in attic?", value=False,
                              help="Blown cellulose to R-38+; great for Philly winters.")
attic_area_sqft = st.number_input("Attic area to insulate (sq ft)", 
                                  min_value=0, step=100,
                                  disabled=not attic_insulated,
                                  help="Typical full attic ≈ home sq ft. Leave blank if unknown.")

# ─────────────────────────────────────────────────────────────────────────────
# CALCULATION
# ─────────────────────────────────────────────────────────────────────────────

if st.button("Calculate Estimated Savings", use_container_width=True):

    # Core upgrades savings (annual $ baseline)
    bulb_savings         = num_bulbs * 50 if num_bulbs is not None else 0
    caulk_savings        = num_windows * 25 if num_windows is not None else 0
    shades_savings       = 250 if install_shades == "Yes" else 0
    weatherstrip_savings = num_doors_weatherstrip * 30 if num_doors_weatherstrip is not None else 0
    sweep_savings        = num_doors_sweeps * 15 if num_doors_sweeps is not None else 0

    total_core = bulb_savings + caulk_savings + shades_savings + weatherstrip_savings + sweep_savings

    # Scale by home size (if provided)
    size_factor = home_sqft / 2000.0 if home_sqft > 0 else 1.0
    total_adjusted = total_core * size_factor

    # Apply leak factor
    yearly_core_savings = total_adjusted * leak_factor

    # Attic cellulose savings
    attic_savings = 0
    if attic_insulated and attic_area_sqft > 0:
        attic_factor = attic_area_sqft / 2000.0
        attic_base = 300
        attic_savings = attic_base * attic_factor * leak_factor

    total_yearly_savings = yearly_core_savings + attic_savings
    monthly_savings = total_yearly_savings / 12

    # % reductions
    AVG_MONTHLY_BILL = 245
    AVG_YEARLY_BILL  = AVG_MONTHLY_BILL * 12
    monthly_pct = (monthly_savings / AVG_MONTHLY_BILL) * 100 if AVG_MONTHLY_BILL > 0 else 0
    yearly_pct  = (total_yearly_savings / AVG_YEARLY_BILL) * 100 if AVG_YEARLY_BILL > 0 else 0

    # Rough CO₂
    co2_lbs_per_year = (total_yearly_savings / 0.1626) * 0.00085 * 1000

    # ────────────────────────────────────────────────────────────────────────
    # RESULTS
    # ────────────────────────────────────────────────────────────────────────

    st.subheader("Your Estimated Savings", divider="green")

    st.metric("Yearly Savings (Total)", f"${total_yearly_savings:,.2f}")
    st.metric("Monthly Savings", f"${monthly_savings:,.2f}")

    col_a, col_b = st.columns(2)
    with col_a:
        st.metric("Monthly Bill Reduction", f"{monthly_pct:.1f}%")
    with col_b:
        st.metric("Yearly Bill Reduction", f"{yearly_pct:.1f}%")

    st.caption(f"Based on avg Philly household bill **${AVG_MONTHLY_BILL}/mo** / **${AVG_YEARLY_BILL:,}/yr**")

    if attic_insulated:
        st.info(f"Attic cellulose contribution: ~${attic_savings:,.0f}/year")

    st.info(f"Approx CO₂ savings: **{co2_lbs_per_year:,.0f} lbs/year**")

    st.markdown("---")
    st.caption("Range: 10–30%+ total reduction possible. Lower CFM50 = tighter home = lower ongoing savings potential from sealing.")

# ─────────────────────────────────────────────────────────────────────────────
# AUDIT SECTION WITH CONTACT
# ─────────────────────────────────────────────────────────────────────────────

with st.expander("Get a Professional Energy Audit (Highly Recommended)", expanded=False):
    st.markdown("""
    This tool is a good starting estimate, but a **professional energy audit** measures your actual CFM50 (blower door), insulation levels, and more — giving precise savings, rebates, and IRA tax credit eligibility.

    Typical audit includes:
    - Blower door test for exact air leakage
    - Infrared scans for insulation gaps & drafts
    - HVAC, appliance, and water heating checks
    - Customized report with prioritized improvements & ROI

    Cost: $200–$550 (often discounted or free via PECO/utility programs). Pays back fast!
    """)
    st.markdown("**Contact Energy Saving Construction:**")
    st.markdown("- Email: [info@energysavingconstruction.com](mailto:info@energysavingconstruction.com)")
    st.markdown("- Phone: [267-892-1992](tel:+12678921992)")

# Footer
st.markdown("---")
st.caption("Based on DOE, ENERGY STAR, PECO data. Not professional advice. Assumptions current as of 2025 Philly-area averages.")