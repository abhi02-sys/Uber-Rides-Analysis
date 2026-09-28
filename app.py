import streamlit as st
import pandas as pd
import matplotlib.pyplot as plt
from matplotlib.ticker import FuncFormatter

st.set_page_config(
    page_title="Uber Ride Analytics: Why Bookings Don't Complete",
    page_icon="🚖",
    layout="wide"
)
st.title("🚖 Uber Ride Analytics")
BUSINESS_QUESTION = "Where, when and why do Uber bookings end up unsuccessful?"

MONTHS = [
    "January", "February", "March", "April", "May", "June",
    "July", "August", "September", "October", "November", "December"
]
TIME_SLOTS = ["Morning", "Afternoon", "Evening", "Night"]

# One colour per status, reused in every chart so the story stays consistent
STATUS_COLORS = {
    "Completed": "#2ca02c",
    "Incomplete": "#d62728",
    "No Driver Found": "#9467bd",
    "Cancelled by Customer": "#1f77b4",
    "Cancelled by Driver": "#ff7f0e",
}
STATUS_ORDER = list(STATUS_COLORS.keys())

M_FMT = FuncFormatter(lambda x, pos: f"{x / 1_000_000:.1f} M")



@st.cache_data
def load_data():
    data = pd.read_csv("Uber_Processed.csv")
    data["Month"] = pd.Categorical(data["Month"], categories=MONTHS, ordered=True)
    data["time_category"] = pd.Categorical(
        data["time_category"], categories=TIME_SLOTS, ordered=True
    )
    data["is_failed"] = data["Booking Status"] != "Completed"
    data["is_ndf"] = data["Booking Status"] == "No Driver Found"
    return data


df = load_data()
completed = df[df["Booking Status"] == "Completed"].copy()
failed = df[df["Booking Status"] != "Completed"].copy()

# ------------------------------------------------------------------ #
# KPIs
# ------------------------------------------------------------------ #
total_bookings = len(df)
n_failed = len(failed)
completion_rate = len(completed) / total_bookings * 100
failure_rate = 100 - completion_rate

total_revenue = completed["Booking Value"].sum()
average_fare = completed["Booking Value"].mean()

n_completed = len(completed)

# ------------------------------------------------------------------ #
# DERIVED TABLES
# ------------------------------------------------------------------ #
# Failure breakdown
fail_breakdown = failed["Booking Status"].value_counts()
fail_share = fail_breakdown / n_failed * 100

# Booking volume
bookings_vehicle = df["Vehicle Type"].value_counts()


# Status mix (in %) for any grouping column
def status_share(col):
    counts = (
        df.groupby([col, "Booking Status"], observed=False)
        .size()
        .unstack(fill_value=0)
    )
    counts = counts[[s for s in STATUS_ORDER if s in counts.columns]]
    return counts.div(counts.sum(axis=1), axis=0) * 100


slot_share = status_share("time_category")
vehicle_share = status_share("Vehicle Type").loc[bookings_vehicle.index]
slot_fail = 100 - slot_share["Completed"]
vehicle_fail = 100 - vehicle_share["Completed"]

# Rates by pickup location (rate, not volume)
loc_stats = df.groupby("Pickup Location").agg(
    bookings=("is_failed", "size"),
    fail_rate=("is_failed", "mean"),
    ndf_rate=("is_ndf", "mean"),
)
loc_stats[["fail_rate", "ndf_rate"]] = loc_stats[["fail_rate", "ndf_rate"]] * 100
loc_stats = loc_stats[loc_stats["bookings"] >= 100]
loc_top_fail = loc_stats.sort_values("fail_rate", ascending=False).head(10)
loc_top_ndf = loc_stats.sort_values("ndf_rate", ascending=False).head(10)

# No Driver Found rate by time slot
ndf_slot = slot_share["No Driver Found"] if "No Driver Found" in slot_share else None

# Revenue
rev_vehicle = (
    completed.groupby("Vehicle Type")["Booking Value"].sum().sort_values(ascending=False)
)
rev_payment = completed.groupby("Payment Method")["Booking Value"].sum()
rev_slot = completed.groupby("time_category", observed=False)["Booking Value"].sum()
rev_month = completed.groupby("Month", observed=False)["Booking Value"].sum()

# Cancellation reasons
driver_cancel = (
    df.groupby("Driver Cancellation Reason")["Cancelled Rides by Driver"]
    .sum()
    .sort_values(ascending=False)
    .reset_index()
)
customer_cancel = (
    df.groupby("Reason for cancelling by Customer")["Cancelled Rides by Customer"]
    .sum()
    .sort_values(ascending=False)
    .reset_index()
)
incomplete_reason = (
    df.groupby("Incomplete Rides Reason")["Incomplete Rides"]
    .sum()
    .sort_values(ascending=False)
    .reset_index()
)


# Wait time by outcome (ignore 0 / missing values)
wait_by_status = (
    df[df["Avg VTAT"] > 0].groupby("Booking Status")["Avg VTAT"].mean()
)

#Hupothesis Calc

#H1
top_failure = fail_breakdown.idxmax()
h1_result = (
    f"{top_failure}: {fail_share[top_failure]:.0f}% "
    f"of unsuccessful bookings"
)

# H2
h2_result = (
    f"Unsuccessful rate: {slot_fail.min():.1f}%–"
    f"{slot_fail.max():.1f}% across time slots"
)

# H3
h3_result = (
    f"Unsuccessful rate: {vehicle_fail.min():.1f}%–"
    f"{vehicle_fail.max():.1f}% across vehicle types"
)

# H4
comp_wait = df[
    (df["Booking Status"] == "Completed") &
    (df["Avg VTAT"] > 0)
]["Avg VTAT"]

cust_wait = df[
    (df["Booking Status"] == "Cancelled by Customer") &
    (df["Avg VTAT"] > 0)
]["Avg VTAT"]

if len(comp_wait) > 0 and len(cust_wait) > 0:
    h4_result = (
        f"Avg wait: {cust_wait.mean():.1f} min "
        f"(customer-cancelled) vs "
        f"{comp_wait.mean():.1f} min (completed)"
    )
else:
    h4_result = "Wait time not available for these outcomes"

# ------------------------------------------------------------------ #
# CHART HELPERS
# ------------------------------------------------------------------ #
def show(fig):
    st.pyplot(fig)
    plt.close(fig)


def hbar(labels, values, title, colors, texts=None, figsize=(8, 4.5)):
    fig, ax = plt.subplots(figsize=figsize)
    values = list(values)
    bars = ax.barh(list(labels), values, color=colors)
    if texts is None:
        texts = [f"{v:,.0f}" for v in values]
    ax.bar_label(bars, labels=texts, padding=3, fontsize=9)
    ax.invert_yaxis()
    ax.set_xlim(0, max(values) * 1.2)
    ax.set_title(title)
    fig.tight_layout()
    return fig


def vbar(labels, values, title, color, money=False, rotate=0, ylabel=None):
    fig, ax = plt.subplots(figsize=(8, 4.5))
    ax.bar([str(l) for l in labels], list(values), color=color)
    ax.set_title(title)
    if money:
        ax.yaxis.set_major_formatter(M_FMT)
    if ylabel:
        ax.set_ylabel(ylabel)
    plt.setp(ax.get_xticklabels(), rotation=rotate)
    fig.tight_layout()
    return fig


def stacked_pct(share_df, title, xlabel, rotate=0):
    fig, ax = plt.subplots(figsize=(8, 4.5))
    share_df.plot(
        kind="bar", stacked=True, ax=ax,
        color=[STATUS_COLORS.get(c, "grey") for c in share_df.columns]
    )
    for container in ax.containers:
        ax.bar_label(container, fmt="%.1f%%", label_type="center", fontsize=7)
    ax.set_title(title)
    ax.set_xlabel(xlabel)
    ax.set_ylabel("% of bookings")
    ax.set_ylim(0, 100)
    ax.legend(title="Booking Status", bbox_to_anchor=(1.02, 1), loc="upper left", fontsize=8)
    plt.setp(ax.get_xticklabels(), rotation=rotate)
    fig.tight_layout()
    return fig


# ------------------------------------------------------------------ #
# NAVIGATION
# ------------------------------------------------------------------ #
st.sidebar.title("Navigation")
st.sidebar.markdown(f"**Question**\n\n{BUSINESS_QUESTION}")

page = st.sidebar.radio(
    "Go To",
    [
        "Executive Overview",
        "Unsuccessful Booking Analysis",
        "Ride Fulfillment Analysis",
        "Demand & Revenue",
    ],
)

# ================================================================== #
# PAGE 1 - EXECUTIVE OVERVIEW
# ================================================================== #
if page == "Executive Overview":

    st.title("Executive Overview")
    st.info(
        f"**Question:** {BUSINESS_QUESTION}\n\n"
        f"**Headline:** {failure_rate:.0f}% of bookings ({n_failed:,} of {total_bookings:,}) "
        f"were unsuccessful. {top_failure} were the largest cause."
    )

    c1, c2, c3, c4, c5 = st.columns(5)
    c1.metric("Total Bookings", f"{total_bookings:,}")
    c2.metric("Completed Bookings", f"{n_completed:,}")
    c3.metric("Unsuccessful Rate", f"{failure_rate:.1f}%",
              help=f"{n_failed:,} bookings were cancelled, unmatched or incomplete.")
    c4.metric("Total Revenue", f"₹{total_revenue / 1_000_000:.1f} M",
              help="Booking value of completed rides.")
    c5.metric("Average Fare", f"₹{average_fare:.2f}")

    st.markdown("---")

    col1, col2 = st.columns(2)
    with col1:
        outcome = df["Booking Status"].value_counts()
        outcome = outcome.reindex([s for s in STATUS_ORDER if s in outcome.index])
        fig, ax = plt.subplots(figsize=(8, 4.5))
        wedges, _, autotexts = ax.pie(
            outcome.values,
            colors=[STATUS_COLORS.get(s, "grey") for s in outcome.index],
            autopct="%1.0f%%",
            pctdistance=0.8,
            startangle=90,
            counterclock=False,
            wedgeprops=dict(width=0.45, edgecolor="white"),
            textprops=dict(color="white", fontsize=9),
        )
        ax.text(0, 0, f"{failure_rate:.0f}%\nunsuccessful", ha="center", va="center",
                fontsize=13, fontweight="bold")
        ax.legend(wedges, outcome.index, loc="center left", bbox_to_anchor=(1.0, 0.5))
        ax.set_title("Booking Outcome Distribution")
        fig.tight_layout()
        show(fig)
    with col2:
        fig, ax = plt.subplots(figsize=(8, 4.5))
        ax.plot(rev_month.index.astype(str), rev_month.values, marker="o", linewidth=2)
        ax.set_ylim(0, rev_month.max() * 1.2)
        ax.set_ylabel("Revenue (₹)")
        ax.yaxis.set_major_formatter(M_FMT)
        ax.set_title("Monthly Revenue")
        plt.setp(ax.get_xticklabels(), rotation=45)
        fig.tight_layout()
        show(fig)

    st.markdown("---")
    st.subheader("Hypotheses Tested")
    hypotheses = [
    ["H1", "Which booking outcome accounts for the largest share of unsuccessful bookings?", h1_result],
    ["H2", "How does unsuccessful rate vary across time slots?", h2_result],
    ["H3", "Do failure rates differ across vehicle types?", h3_result],
    ["H4", "How do wait times compare across booking outcomes?", h4_result],
    ]

    st.table(
        pd.DataFrame(
            hypotheses,
            columns=["#", "Question", "Finding"]
        )
    )
    
# ================================================================== #
# PAGE 2 - UNSUCCESSFUL BOOKING ANALYSIS : why?
# ================================================================== #
elif page == "Unsuccessful Booking Analysis":

    st.title("Unsuccessful Booking Analysis")
    st.markdown("**Why are bookings unsuccessful?**")

    col1, col2 = st.columns(2)
    with col1:
        texts = [f"{n:,} ({fail_share[s]:.0f}%)" for s, n in fail_breakdown.items()]
        show(hbar(
            fail_breakdown.index, fail_breakdown.values,
            "Unsuccessful Bookings by Type",
            [STATUS_COLORS.get(s, "grey") for s in fail_breakdown.index],
            texts=texts,
        ))
       
    with col2:
        show(hbar(driver_cancel["Driver Cancellation Reason"],
                  driver_cancel["Cancelled Rides by Driver"],
                  "Why Do Drivers Cancel?", "tomato"))

    col3, col4 = st.columns(2)
    with col3:
        show(hbar(customer_cancel["Reason for cancelling by Customer"],
                  customer_cancel["Cancelled Rides by Customer"],
                  "Why Do Customers Cancel?", "royalblue"))
    with col4:
        show(hbar(incomplete_reason["Incomplete Rides Reason"],
                  incomplete_reason["Incomplete Rides"],
                  "Why Do Rides End Up Incomplete?", "green"))

    ndf = fail_breakdown.get("No Driver Found", 0)
    st.info(
        f"**No Driver Found:** {ndf:,} bookings ({ndf / total_bookings * 100:.0f}% of all "
        f"bookings) were not matched with a driver. The dataset has no reason field for these, "
        f"so they are examined by time and location on the next page."
    )

# ================================================================== #
# PAGE 3 - RIDE FULFILLMENT ANALYSIS : where and when?
# ================================================================== #
elif page == "Ride Fulfillment Analysis":

    st.title("Ride Fulfillment Analysis")
    st.markdown("**Where and when are bookings more likely to succeed or be unsuccessful?**")

    col1, col2 = st.columns(2)
    with col1:
        show(stacked_pct(vehicle_share, "Booking Outcome by Vehicle Type",
                         "Vehicle Type", rotate=30))
        st.caption(
            f"Failure rate ranges {vehicle_fail.min():.1f}%–{vehicle_fail.max():.1f}% "
            f"across vehicle types."
        )
    with col2:
        show(stacked_pct(slot_share, "Booking Outcome by Time Slot", "Time Slot"))
        st.caption(
            f"Failure rates are similar across time slots ranging from"
            f"({slot_fail.min():.1f}%–{slot_fail.max():.1f}%), despite higher booking "
        )

    col3, col4 = st.columns(2)
    with col3:
        if len(loc_stats) > 0:
            show(hbar(loc_top_fail.index, loc_top_fail["fail_rate"].values,
                      "Pickup Locations with Highest Unsuccessful Rate", "#9467bd",
                      texts=[f"{r:.1f}%  (n={int(n):,})"
                             for r, n in zip(loc_top_fail["fail_rate"],
                                             loc_top_fail["bookings"])]))
            st.caption(
                f"Locations with 100+ bookings only are included."
            )
    with col4:
        show(hbar(wait_by_status.index, wait_by_status.values,
                  "Average Wait Time by Booking Outcome (min)",
                  [STATUS_COLORS.get(s, "grey") for s in wait_by_status.index],
                  texts=[f"{v:.1f}" for v in wait_by_status.values]))
        st.caption(
            "Wait time = time for the driver to reach the pickup point. "
            "No Driver Found has none because no driver was assigned."
        )

    col5, col6 = st.columns(2)
    with col5:
        if ndf_slot is not None:
            show(vbar(ndf_slot.index, ndf_slot.values,
                      "No Driver Found Rate by Time Slot (% of bookings)", "#9467bd",
                      ylabel="% of bookings"))
            st.caption(
                f"No Driver Found accounts for about {ndf_slot.min():.1f}% of bookings in each time slot."
                
            )
    with col6:
        if len(loc_stats) > 0:
            show(hbar(loc_top_ndf.index, loc_top_ndf["ndf_rate"].values,
                      "Pickup Locations with Highest No Driver Found Rate", "#9467bd",
                      texts=[f"{r:.1f}%  (n={int(n):,})"
                             for r, n in zip(loc_top_ndf["ndf_rate"],
                                             loc_top_ndf["bookings"])]))
            st.caption(
                f"Locations with 100+ bookings only."
            )

# ================================================================== #
# PAGE 4 - DEMAND & REVENUE
# ================================================================== #
elif page == "Demand & Revenue":

    st.title("Demand & Revenue")
    st.markdown("**Where are demand and booking value concenterated?**")

    col1, col2 = st.columns(2)
    with col1:
        show(vbar(rev_vehicle.index, rev_vehicle.values, "Revenue by Vehicle Type",
                  "#1f77b4", money=True, rotate=30))
    with col2:
        show(vbar(rev_slot.index, rev_slot.values, "Revenue by Time Slot",
                  "orange", money=True))

    col3, _ = st.columns(2)
    with col3:
        show(vbar(rev_payment.index, rev_payment.values, "Revenue by Payment Method",
                  "green", money=True, rotate=30))

    #st.caption(
     #   "Revenue is the booking value of completed rides. Payment method is recorded only "
     #   "for completed and incomplete rides."
    #)
    

# ------------------------------------------------------------------ #
# FOOTER
# ------------------------------------------------------------------ #
st.markdown(
    """
    <style>
    .footer {
        position: fixed;
        left: 0;
        bottom: 0;
        width: 100%;
        background-color: #0E1117;
        color: white;
        text-align: center;
        padding: 8px;
        font-size: 14px;
        border-top: 1px solid #444;
        z-index: 999;
    }
    </style>

    <div class="footer">
        Developed by  <b>Abhijeet Kaur</b> • © 2026
    </div>
    """,
    unsafe_allow_html=True
)
