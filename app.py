import streamlit as st
import pandas as pd
import matplotlib.pyplot as plt
from matplotlib.ticker import FuncFormatter

st.set_page_config(
    page_title="Uber Ride Analytics Dashboard",
    page_icon="🚖",
    layout="wide"
)
df = pd.read_csv("Uber_Processed.csv")
completed = df[df["Booking Status"]=="Completed"].copy()
st.sidebar.title("Navigation")

page = st.sidebar.radio(
    "Go To",
    [
        "Executive Summary",
        "Revenue Analysis",
        "Ride Analysis",
        "Operational Insights"
    ]
)

# KPI Calculations

total_bookings = len(df)
completion_rate = (len(completed) / total_bookings) * 100
total_revenue = completed["Booking Value"].sum()
average_fare = completed["Booking Value"].mean()
unique_customers = df["Customer ID"].nunique()
average_driver_rating = completed["Driver Ratings"].mean()
average_customer_rating = completed["Customer Rating"].mean()
average_wait_time = df["Avg VTAT"].mean()
average_distance = completed["Ride Distance"].mean()

#Metrics for charts
# Revenue by Vehicle
revenue_vehicle = (
    completed.groupby('Vehicle Type')['Booking Value']
    .sum()
    .sort_values(ascending=False)
    .reset_index()
)

# Revenue by Payment Method
rev_pay_method = (
    completed.groupby('Payment Method')['Booking Value']
    .sum()
    .reset_index()
)

# Revenue by Time Slot
times = ['Morning','Afternoon','Evening','Night']

completed['time_category'] = pd.Categorical(
    completed['time_category'],
    categories=times,
    ordered=True
)

rev_by_time_slot = (
    completed.groupby('time_category')['Booking Value']
    .sum()
    .reset_index()
)

# Revenue by Pickup Location
pickup_revenue = (
    completed.groupby('Pickup Location')['Booking Value']
    .sum()
    .sort_values(ascending=False)
    .head(10)
    .reset_index()
)
# ---------------- Ride Analysis Data ---------------- #

# Bookings by Vehicle Type
bookings_vehicle = (
    df.groupby('Vehicle Type')
    .size()
    .sort_values(ascending=False)
    .reset_index(name='Bookings')
)

# Bookings by Month
month_order = [
    "January","February","March","April","May","June",
    "July","August","September","October","November","December"
]

df["Month"] = pd.Categorical(
    df["Month"],
    categories=month_order,
    ordered=True
)

bookings_month = (
    df.groupby("Month")
    .size()
    .reset_index(name="Bookings")
)

# Bookings by Time Slot

times = ['Morning', 'Afternoon', 'Evening', 'Night']

df['time_category'] = pd.Categorical(
    df['time_category'],
    categories=times,
    ordered=True
)

status_time = (
    df.groupby(['time_category', 'Booking Status'])
      .size()
      .unstack(fill_value=0)
)
# Top Pickup Locations
pickup_bookings = (
    df.groupby('Pickup Location')
    .size()
    .sort_values(ascending=False)
    .head(10)
    .reset_index(name='Bookings')
)

# Driver cancellation reasons
driver_cancel = (
    df.groupby('Driver Cancellation Reason')['Cancelled Rides by Driver']
    .sum()
    .sort_values(ascending=False)
    .reset_index()
)

# Customer cancellation reasons
customer_cancel = (
    df.groupby('Reason for cancelling by Customer')['Cancelled Rides by Customer']
    .sum()
    .sort_values(ascending=False)
    .reset_index()
)

# Incomplete ride reasons
incomplete_reason = (
    df.groupby('Incomplete Rides Reason')['Incomplete Rides']
    .sum()
    .sort_values(ascending=False)
    .reset_index()
)
status_vehicle = (
    df.groupby(['Vehicle Type', 'Booking Status'])
      .size()
      .unstack(fill_value=0)
)

if page=="Executive Summary":

    st.title("Executive Summary")
    st.markdown(
    """
    This dashboard provides an overview of Uber ride operations,
    revenue performance, customer experience, and operational efficiency.
    """
    )
# ---------- Row 1 ----------

    col1, col2, col3, col4 = st.columns(4)

    with col1:
        st.metric(
            "Total Bookings",
            f"{total_bookings:,}"
        )

    with col2:
        st.metric(
            "Total Revenue",
            f"₹{total_revenue/1_000_000:.1f} M"
        )

    with col3:
        st.metric(
            "Completion Rate",
            f"{completion_rate:.1f}%"
        )

    with col4:
        st.metric(
            "Unique Customers",
            f"{unique_customers:,}"
        )

# ---------- Row 2 ----------

    col5, col6, col7, col8 = st.columns(4)

    with col5:
        st.metric(
            "Average Fare",
            f"₹{average_fare:.2f}"
        )

    with col6:
        st.metric(
            "Driver Rating",
            f"{average_driver_rating:.2f} ⭐"
        )

    with col7:
        st.metric(
            "Customer Rating",
            f"{average_customer_rating:.2f} ⭐"
        )

    with col8:
        st.metric(
            "Average Wait Time",
            f"{average_wait_time:.1f} min"
        )
    st.markdown("---")

    col1, col2 = st.columns(2)
    with col1:

        booking_status = df["Booking Status"].value_counts()

        fig1, ax1 = plt.subplots(figsize=(5,5))

        ax1.pie(
            booking_status.values,
            labels=booking_status.index,
            autopct="%1.1f%%",
            startangle=90
        )

        ax1.set_title("Booking Status Distribution")

        st.pyplot(fig1)

    with col2:

        rev_monthly = (
            completed.groupby("Month")["Booking Value"]
            .sum()
            .reindex([
                "January","February","March","April",
                "May","June","July","August",
                "September","October","November","December"
            ])
        )

        fig2, ax2 = plt.subplots(figsize=(8,5))

        ax2.plot(
            rev_monthly.index,
            rev_monthly.values,
            marker="o",
            linewidth=2
        )

        ax2.set_title("Monthly Revenue")

        ax2.set_xlabel("Month")

        ax2.set_ylabel("Revenue (₹)")

        ax2.tick_params(axis="x", rotation=45)

        ax2.yaxis.set_major_formatter(
            FuncFormatter(
                lambda x,pos:f"{x/1_000_000:.1f} M"
            )
        )

        st.pyplot(fig2)

elif page=="Revenue Analysis":

    st.title("💰 Revenue Analysis")
    col1,col2 = st.columns(2)
    with col1:

        fig,ax=plt.subplots(figsize=(8,5))

        ax.bar(
            revenue_vehicle['Vehicle Type'],
            revenue_vehicle['Booking Value']
        )

        ax.set_title("Revenue by Vehicle Type")

        ax.yaxis.set_major_formatter(
            FuncFormatter(
                lambda x,pos:f"{x/1_000_000:.1f} M"
            )
        )

        plt.xticks(rotation=30)

        st.pyplot(fig)

    with col2:

        fig,ax=plt.subplots(figsize=(8,5))

        ax.bar(
            rev_pay_method['Payment Method'],
            rev_pay_method['Booking Value'],
            color="green"
        )

        ax.set_title("Revenue by Payment Method")
    
        ax.yaxis.set_major_formatter(
            FuncFormatter(
                lambda x,pos:f"{x/1_000_000:.1f} M"
            )
        )

        plt.xticks(rotation=30)

        st.pyplot(fig)

    col3,col4 = st.columns(2)
    with col3:

        fig,ax=plt.subplots(figsize=(8,5))

        ax.bar(
            rev_by_time_slot['time_category'],
            rev_by_time_slot['Booking Value'],
            color="orange"
        )

        ax.set_title("Revenue by Time Slot")

        ax.yaxis.set_major_formatter(
            FuncFormatter(
                lambda x,pos:f"{x/1_000_000:.1f} M"
            )
        )

        st.pyplot(fig)
    with col4:

        fig,ax=plt.subplots(figsize=(8,5))

        bars=ax.barh(
            pickup_revenue['Pickup Location'],
            pickup_revenue['Booking Value'],
            color="skyblue"
        )

        for bar in bars:

            width=bar.get_width()

            ax.text(
                width+20,
                bar.get_y()+bar.get_height()/2,
                f"{int(width):,}",
                va="center",
                fontsize=9
            )

        ax.invert_yaxis()

        ax.set_title("Top 10 Pickup Locations by Revenue")

        ax.xaxis.set_major_formatter(
            FuncFormatter(
                lambda x,pos:f"₹{x:,.0f}"
            )
        )

        st.pyplot(fig,use_container_width=True)

elif page == "Ride Analysis":

    st.title("🚖 Ride Analysis")

    st.markdown(
        "Analyze ride demand across vehicles, months, time slots and pickup locations."
    )
    col1, col2 = st.columns(2)
    with col1:

        fig, ax = plt.subplots(figsize=(8,5))

        ax.bar(
            bookings_vehicle['Vehicle Type'],
            bookings_vehicle['Bookings'],
            color='royalblue'
        )

        ax.set_title("Bookings by Vehicle Type")
        ax.set_xlabel("Vehicle Type")
        ax.set_ylabel("Bookings")

        plt.xticks(rotation=30)

        st.pyplot(fig,use_container_width=True)
    with col2:

        fig, ax = plt.subplots(figsize=(8,5))

        ax.plot(
            bookings_month['Month'],
            bookings_month['Bookings'],
            marker='o',
            linewidth=2
        )

        ax.set_title("Bookings by Month")
        ax.set_xlabel("Month")
        ax.set_ylabel("Bookings")

        plt.xticks(rotation=45)

        st.pyplot(fig) 
        
    col3, col4 = st.columns(2)
    with col3:

        # Booking Status by Time Slot

        fig, ax = plt.subplots(figsize=(8,5))

        status_time.plot(
            kind='bar',
            stacked=True,
            ax=ax
        )

        ax.set_title("Booking Status by Time Slot")
        ax.set_xlabel("Time Slot")
        ax.set_ylabel("Number of Bookings")

        ax.tick_params(axis='x', rotation=0)

        ax.legend(
            title="Booking Status",
            bbox_to_anchor=(1.02, 1),
            loc="upper left"
        )

        # Show values inside each stack
        for container in ax.containers:
            ax.bar_label(
            container,
            label_type="center",
            fontsize=8
        )

        fig.tight_layout()

        st.pyplot(fig, use_container_width=True)
    with col4:

        fig, ax = plt.subplots(figsize=(8,5))

        bars = ax.barh(
            pickup_bookings['Pickup Location'],
            pickup_bookings['Bookings'],
            color='orange'
        )

        for bar in bars:

            width = bar.get_width()

            ax.text(
                width + 5,
                bar.get_y() + bar.get_height()/2,
                f"{int(width):,}",
                va="center",
                fontsize=9
            )

        ax.set_title("Top 10 Pickup Locations")
        ax.set_xlabel("Bookings")

        ax.invert_yaxis()

        st.pyplot(fig)

elif page=="Operational Insights":

    st.title("⚙️ Operational Insights")
    col1,col2 = st.columns(2)
    with col1:

        fig,ax=plt.subplots(figsize=(8,5))

        bars=ax.barh(
            driver_cancel['Driver Cancellation Reason'],
            driver_cancel['Cancelled Rides by Driver'],
            color='tomato'
        )

        for bar in bars:

            width=bar.get_width()

            ax.text(
                width+5,
                bar.get_y()+bar.get_height()/2,
                f"{int(width):,}",
                va="center",
                fontsize=9
            )

        ax.invert_yaxis()

        ax.set_title("Driver Cancellation Reasons")

        st.pyplot(fig)
    with col2:

        fig,ax=plt.subplots(figsize=(8,5))

        bars=ax.barh(
            customer_cancel['Reason for cancelling by Customer'],
            customer_cancel['Cancelled Rides by Customer'],
            color='royalblue'
        )

        for bar in bars:

            width=bar.get_width()

            ax.text(
                width+5,
                bar.get_y()+bar.get_height()/2,
                f"{int(width):,}",
                va="center",
                fontsize=9
            )

        ax.invert_yaxis()

        ax.set_title("Customer Cancellation Reasons")

        st.pyplot(fig)
    col3,col4 = st.columns(2)
    with col3:
        
        

        fig,ax=plt.subplots(figsize=(9,5))

        bars=ax.barh(
            incomplete_reason['Incomplete Rides Reason'],
            incomplete_reason['Incomplete Rides'],
            color='green'
        )

        for bar in bars:

            width=bar.get_width()

            ax.text(
                width+5,
                bar.get_y()+bar.get_height()/2,
                f"{int(width):,}",
                va="center"
            )

        ax.invert_yaxis()

        ax.set_title("Incomplete Ride Reasons")

        st.pyplot(fig)
    with col4:
        fig, ax = plt.subplots(figsize=(10,6))

        status_vehicle.plot(
            kind='bar',
            stacked=True,
            ax=ax
        )

        ax.set_title("Booking Status by Vehicle Type")
        ax.set_xlabel("Vehicle Type")
        ax.set_ylabel("Number of Bookings")
        plt.xticks(rotation=30)
        plt.legend(title="Booking Status", bbox_to_anchor=(1.02,1), loc="upper left")

        st.pyplot(fig)
    
    st.markdown("---")
    st.header("📌 Key Insights & Recommendations")

    st.markdown("""
    ### 1. UPI is the most preferred payment method among customers. Ensuring a seamless digital payment experience and promoting UPI-based offers can further improve customer convenience.

    ### 2. Auto is the most preferred vehicle type and generates the highest overall revenue, whereas Uber XL receives the lowest number of bookings.
    ### 3. Morning (5am to 12pm) and Evening (5pm to 9pm) rides are peak demand period.
    ### 4. Driver cancellations are the primary operational challenge. This suggests the need for better driver training, performance-based incentives, and improved communication between drivers and customers.
    ### 5. No Driver found indicates the supply shortage that is demand is more than supply and these can be resolved by increasing active drivers during peak hours.
""")

    st.markdown("---")

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
  