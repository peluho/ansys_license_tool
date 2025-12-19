# app.py
import streamlit as st
import plotly.graph_objects as go
from cost_logic import compute_costs
from prix_base import LICENSES

st.set_page_config(
    page_title="ANSYS Licence Cost Tool",
    layout="wide",
    initial_sidebar_state="expanded"
)

# make sidebar a bit wider (works for streamlit ≥ 1.28)
st.markdown(
    """
    <style>
        section[data-testid="stSidebar"] {
            width: 380px !important;  /* default 300 */
        }
    </style>
    """,
    unsafe_allow_html=True,
)

st.title("📊 ANSYS Licence Cost Evolution")
st.sidebar.header("Settings")

# ------------------------------------------------------------------
# 1.  Mode selector
# ------------------------------------------------------------------
mode = st.sidebar.radio(
    "Mode",
    options=["single", "compare_purchase_lease", "bundle_A_vs_B"],
    format_func=lambda x: x.replace("_", " ").title()
)

years = st.sidebar.slider("Projection horizon (years)", 1, 15, 8)
annual_budget = st.sidebar.number_input("Annual budget (€)", 0, value=25000)

# ------------------------------------------------------------------
# 2.  Reference-price table (no pandas)
# ------------------------------------------------------------------
with st.sidebar.expander("Reference prices (€)", expanded=True):
    header = ["Licence", "Purchase", "TECS/yr", "Lease/yr"]
    rows = [
        [name, f"{v['paid-up']:,}", f"{v['TECS']:,}", f"{v['lease']:,}"]
        for name, v in LICENSES.items()
    ]
    st.table([header] + rows)

# ------------------------------------------------------------------
# 3.  Licence-quantity helper
# ------------------------------------------------------------------
def licence_selector(label):
    st.sidebar.subheader(label)
    counts = {}
    for name in LICENSES:
        counts[name] = st.sidebar.number_input(
            name, min_value=0, max_value=10, value=0, key=label + name
        )
    return counts

# ------------------------------------------------------------------
# 4.  Build traces
# ------------------------------------------------------------------
traces = []  # list of (legend_name, cumulative_list)

if mode == "single":
    counts = licence_selector("Licence quantities")
    pl = st.sidebar.radio("Type", ["purchase", "lease"])
    cumu = compute_costs(counts, pl, years)
    traces.append((f"Total cost ({pl})", cumu))

elif mode == "compare_purchase_lease":
    counts = licence_selector("Licence quantities")
    purchase_cum = compute_costs(counts, "purchase", years)
    lease_cum = compute_costs(counts, "lease", years)
    traces.extend([("Purchase + TECS", purchase_cum), ("Lease", lease_cum)])

else:  # bundle A vs B
    st.sidebar.markdown("---")
    counts_A = licence_selector("Bundle A")
    type_A = st.sidebar.radio("Bundle A type", ["purchase", "lease"], key="typeA")
    st.sidebar.markdown("---")
    counts_B = licence_selector("Bundle B")
    type_B = st.sidebar.radio("Bundle B type", ["purchase", "lease"], key="typeB")

    cumu_A = compute_costs(counts_A, type_A, years)
    cumu_B = compute_costs(counts_B, type_B, years)
    traces.extend([(f"Bundle A ({type_A})", cumu_A),
                   (f"Bundle B ({type_B})", cumu_B)])

# ------------------------------------------------------------------
# 5.  Plot
# ------------------------------------------------------------------
budget_cum = [annual_budget * y for y in range(years)]

fig = go.Figure()
for name, data in traces:
    fig.add_trace(go.Scatter(x=list(range(years)), y=data,
                             mode='lines+markers', name=name))

fig.add_trace(go.Scatter(x=list(range(years)), y=budget_cum,
                         mode='lines', name='Budget', line=dict(dash='dash')))

fig.update_layout(title="Cumulative cost evolution",
                  xaxis_title="Year",
                  yaxis_title="Cumulative cost (€)")
st.plotly_chart(fig, use_container_width=True)

# ------------------------------------------------------------------
# 6.  Summary
# ------------------------------------------------------------------
st.subheader("Final summary")
for name, data in traces:
    st.write(f"**{name} at year {years-1}:** €{data[-1]:,.0f}")
st.write(f"**Budget at year {years-1}:** €{budget_cum[-1]:,.0f}")

if len(traces) == 2:
    diff = traces[1][1][-1] - traces[0][1][-1]
    st.write(f"**Difference ({traces[1][0]} – {traces[0][0]}):** €{diff:,.0f}")
