# 🚖 Transportation & Mobility Analytics — Uber Ride Performance Analysis

## Executive Summary

An end-to-end analysis of 150,000 Uber ride bookings in Delhi NCR,
examining booking outcomes, unsuccessful bookings, fulfillment patterns,
demand and revenue using Python and Streamlit.

**🔗 Live Dashboard:** [View Dashboard](https://uber-rides-analysis-by-abhi.streamlit.app/)

## Business Problem

Successful bookings are critical to the performance of a ride-hailing business. In this dataset, approximately 150,000 Uber bookings were recorded, but only 62% resulted in completed rides, while 38% were unsuccessful.

A high proportion of unsuccessful bookings represents potential lost revenue opportunities and reduced customer satisfaction. This analysis aims to understand where, when, and why Uber bookings become unsuccessful by identifying the key patterns and factors associated with booking failures.

## Business Question

> **Where, when and why do Uber bookings end up unsuccessful?**

Out of 150,000 bookings, approximately **62% became completed rides**, while **38% were unsuccessful**.

Unsuccessful bookings include:

- Cancelled by Driver
- Cancelled by Customer
- No Driver Found
- Incomplete rides

This analysis investigates the patterns behind unsuccessful bookings by examining booking type, cancellation reasons, time of day, vehicle type, and pickup location.

The objective is to identify the key factors associated with unsuccessful bookings and uncover opportunities to improve the booking success rate and overall customer experience.

## Analytical Approach

### 1. Data Cleaning & Preparation

- Analysed missing values and identified patterns in missingness
- No missing-value imputation was performed, as the missing values were considered structural
- Converted date and time columns to the appropriate datetime format
- Created time-based categories to support temporal analysis
- Extracted relevant time features such as hour, day, and month

### 2. Exploratory Analysis

### Booking Performance
### Temporal Analysis
### Cancellation & Unsuccessful Booking Analysis
### Location & Vehicle Analysis
### Revenue & Payment Analysis

## Skills 

**Python:** Pandas, Matplotlib 
**Data Analysis:** Data Cleaning, EDA, Aggregation, KPI Development, Descriptive Analysis  
**Visualization & Dashboarding:** Matplotlib, Streamlit, Interactive Dashboard Development  

## Dashboard 

### Executive Overview

<img width="1905" height="1477" alt="Executive_Overview" src="https://github.com/user-attachments/assets/b84775af-6543-4a4e-add1-862d65afafb3" />

### Unsuccessful Rides Analysis

<img width="1918" height="1283" alt="Unsuccessful_Booking_Analysis" src="https://github.com/user-attachments/assets/522fcfce-9600-4a1b-b137-e8e5d45421cc" />

### Rides Fulfillment Analysis

<img width="1895" height="1774" alt="Ride_Fulfillment_Analysis" src="https://github.com/user-attachments/assets/ea7a64c2-27da-4471-843d-8aec058478d1" />

### Demand & Revenue Analysis

<img width="1915" height="1209" alt="Revenue" src="https://github.com/user-attachments/assets/4a698341-283d-4dda-a729-b91516a4ae72" />

## Key Findings

1. **38% of bookings were unsuccessful.** Of the 57,000 unsuccessful bookings, 27,000 were cancelled by drivers (47%), 10,500 were cancelled by customers (18%), 10,500 had No Driver Found (18%), and 9,000 were incomplete rides (16%).

2. **Unsuccessful rates are relatively consistent across time and vehicle type.** The unsuccessful rate is approximately 38% across time slots and 37.4%–38.6% across vehicle types. Monthly completion rates range from 61.5% to 62.6%. Morning and Evening account for about 60% of bookings, so they contain more unsuccessful bookings in absolute terms, but their unsuccessful rates are not higher.

3. **Stated cancellation reasons point in different directions.** Among driver cancellations, approximately 75% of the stated reasons refer to customers or passengers, while approximately 55% of customer cancellation reasons refer to the driver or vehicle. This grouping is my own classification of the reason text, and the reasons are self-reported by the party who cancelled.

4. **Revenue is concentrated in higher-volume vehicle and payment categories.** Completed rides generated approximately ₹47.3M in booking value, with an average fare of ₹508. Auto is the largest vehicle type by both bookings and revenue, while Uber XL accounts for approximately 3% of bookings. UPI accounts for approximately 45% of revenue and cash for approximately 25%.

## Recommendations

Based on the observed patterns, the following areas could be explored to improve booking completion and understand unsuccessful bookings:

1. **Investigate driver cancellation patterns**  
   Review the most common driver cancellation reasons, particularly passenger-related reasons, and assess whether clearer passenger information or booking rules could reduce avoidable cancellations.

2. **Investigate customer cancellation and wait-time patterns**  
   Customer-cancelled bookings show a higher average wait time than completed bookings. Further analysis could examine whether pickup delays, driver movement, or estimated wait times are associated with customer cancellations.

3. **Evaluate matching and dispatch performance**  
   Since unsuccessful rates are relatively consistent across time slots and vehicle types, investigate booking-to-driver matching and dispatch performance across the overall network rather than focusing only on peak-hour demand.

## Limitations

The dataset seems to be synthetic having no correlation between fare and ride distance and is evenly distributed. No driver found lacks any specific reason so it 
can't be determined whether it is driver shortage or its just an unmatched booking request. Furthermore payment methods are not available for all booking outcomes so they can't generally be compared to analyse which method is generally used for successful and unsuccessful bookings.








