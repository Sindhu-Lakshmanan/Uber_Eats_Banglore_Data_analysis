import plotly.express as px
import streamlit as st
import sqlite3
import pandas as pd
conn = sqlite3.connect("uber_eats.db")

st.set_page_config(
    page_title="Uber Eats Dashboard",
    layout="wide")
st.title("🍔 Uber Eats Bangalore Dashboard")


# KPI Queries

total_restaurants = pd.read_sql(
    "SELECT COUNT(DISTINCT name) AS unique_restaurants FROM restaurants",conn
).iloc[0, 0]

avg_rating = pd.read_sql(
    "SELECT ROUND(AVG(rate),2) AS avg_rating FROM restaurants",
    conn
).iloc[0, 0]

avg_cost = pd.read_sql(
    'SELECT ROUND(AVG("approx_cost(for two people)"),0) AS avg_cost FROM restaurants',
    conn
).iloc[0, 0]

total_locations = pd.read_sql(
    "SELECT COUNT(DISTINCT location) AS total_locations FROM restaurants",
    conn
).iloc[0, 0]

total_orders = pd.read_sql(
    "SELECT COUNT(*) AS total_orders FROM Order_details",
    conn
).iloc[0, 0]

total_revenue = pd.read_sql(
    "SELECT ROUND(SUM(order_value),2) AS total_revenue FROM Order_details",
    conn
).iloc[0, 0]

avg_order_value = pd.read_sql(
    "SELECT ROUND(AVG(order_value),2) AS avg_order_value FROM Order_details",
    conn
).iloc[0, 0]

avg_restaurant_revenue = pd.read_sql(
    """
    SELECT
    ROUND(
        (SELECT SUM(order_value) FROM Order_details) * 1.0 /
        (SELECT COUNT(DISTINCT name) FROM restaurants),
        2
    ) AS avg_restaurant_revenue
    """,
    conn
).iloc[0,0]
col1, col2, col3, col4 = st.columns(4)

col1.metric("Restaurants", f"{total_restaurants:,}")
col2.metric("Avg Rating", avg_rating)
col3.metric("Avg Cost for Two", f"₹{avg_cost:,.0f}")
col4.metric("Locations", total_locations)

col5, col6, col7, col8 = st.columns(4)

col5.metric("Total Orders", f"{total_orders:,}")
col6.metric("Total Revenue", f"₹{total_revenue:,.0f}")
col7.metric("Avg Order Value", f"₹{avg_order_value}")
col8.metric("Revenue per Restaurant", f"₹{avg_restaurant_revenue:,.0f}")
st.divider()
st.subheader("🔎 Explore Restaurants")
st.caption("Results are retrieved dynamically from the SQLite database using SQL filters.")
# -----------------------------
# Get filter values
# -----------------------------

locations = pd.read_sql_query(
    "SELECT DISTINCT location FROM restaurants WHERE location IS NOT NULL ORDER BY location",
    conn
)["location"].tolist()

cuisines = pd.read_sql_query(
    "SELECT DISTINCT cuisines FROM restaurants WHERE cuisines IS NOT NULL ORDER BY cuisines",
    conn
)["cuisines"].tolist()

# -----------------------------
# Filters
# -----------------------------

col1, col2, col3 = st.columns(3)

with col1:
    selected_location = st.selectbox(
    "📍 Location",
    ["All"] + locations
)

with col2:
    selected_cuisine = st.selectbox(
    "🍽️ Cuisine",
    ["All"] + cuisines
)

with col3:
 online_order = st.selectbox(
    "🛒 Online Order",
    ["All", "Yes", "No"]
)

col4, col5 = st.columns(2)

with col4:
    book_table = st.selectbox(
    "🪑 Table Booking",
    ["All", "Yes", "No"]
)

with col5:
    min_rating = st.slider(
    "⭐ Minimum Rating",
    0.0,
    5.0,
    0.0,
    0.1
)
# -----------------------------
# SQL Query
# -----------------------------

query = """
SELECT
    location,
    rest_type,
    cuisines,
    rate,
    votes,
    online_order,
    book_table,
    phone,
    dish_liked
FROM restaurants
WHERE 1=1
"""

params = []

if selected_location != "All":
    query += " AND location = ?"
    params.append(selected_location)

if selected_cuisine != "All":
    query += " AND cuisines LIKE ?"
    params.append("%" + selected_cuisine + "%")

if online_order != "All":
    query += " AND online_order = ?"
    params.append(online_order)

if book_table != "All":
    query += " AND book_table = ?"
    params.append(book_table)

if min_rating > 0:
    query += " AND rate >= ?"
    params.append(min_rating)

query += " ORDER BY rate DESC"

# -----------------------------
# Execute query
# -----------------------------

df = pd.read_sql_query(
    query,
    conn,
    params=params
)

st.subheader("Filtered Restaurant Data")

st.write(f"Restaurants Found: {len(df):,}")

st.dataframe(
    df,
    use_container_width=True,
    hide_index=True
)



st.markdown("""

### Project Overview
This dashboard analyzes Bangalore restaurant and order data to identify
customer preferences, revenue trends, location performance, pricing strategies,
and restaurant onboarding opportunities for Uber Eats.
""")



#1.Which Bangalore locations have the highest average restaurant ratings?
#Business Value: Identifies premium-performing areas suitable for brand positioning and new partner onboarding.

query1 = """
SELECT location , round(AVG(RATE),2) as Avg_rating FROM restaurants
group by location
ORDER BY Avg_rating desc
LIMIT 10
"""
q1 = pd.read_sql(query1, conn)



# Query 1 - Plotly Chart
fig1 = px.bar(
    q1,
    x="Avg_rating",
    y="location",
    orientation="h",
    text="Avg_rating",
    title="Top 10 Locations by Average Rating",
    color_discrete_sequence=["#F5AFAF"]
)
fig1.update_traces(textposition="outside")

fig1.update_layout(
    height=500,
    width=800,
    margin=dict(l=200, r=20, t=50, b=50),
    xaxis=dict(range=[4.0, 4.3]),
    yaxis=dict(autorange="reversed"),
    yaxis_title="",
    xaxis_title="<b>Average Rating</b>"
)




# 2.Which locations are over-saturated with restaurants?
query2 = """
SELECT location,
    COUNT(*) AS restaurant_count
FROM restaurants
GROUP BY location
ORDER BY restaurant_count DESC
limit 10;
"""
q2 = pd.read_sql(query2, conn)

#query 2 - Plotly Chart

fig2 = px.bar(
    q2,
    x="restaurant_count",
    y="location",
    orientation="h",
    text="restaurant_count",
    title="oversaturated location with restaurant",
    color_discrete_sequence=["#dec0f1"]
)
fig2.update_traces(textposition="outside")

fig2.update_layout(
    height=500,
    width=1000,
    margin=dict(l=200, r=30, t=50, b=150),
    
    xaxis=dict(range=[600,1900]),
    #yaxis=dict(range=[600,2000]),
    yaxis=dict(autorange="reversed"),
# xaxis=dict(tickangle=-90),
    yaxis_title="",
    xaxis_title="<b>restaurant_count</b>"
)

#3. Does online ordering improve restaurant ratings?

query3= """
SELECT online_order,round(AVG(RATE),2) as Avg_rating FROM restaurants
group by online_order
"""

q3= pd.read_sql(query3, conn)


# query 3 : Plotly chart
fig3 = px.bar(
    q3,
    x="online_order",
    y="Avg_rating",
    #orientation="h",
    text="Avg_rating",
    title="Online Ordering Vs Restaurant Rating",
    color_discrete_sequence=["#8be7ad"]
)

fig3.update_traces(textposition="outside")

fig3.update_layout(
    height=500,
    width=600,
    #template="plotly_white",
    margin=dict(l=50, r=30, t=50, b=30),
    
    #xaxis=dict(range=[600,1900]),
    yaxis=dict(range=[3.7,4]),
# yaxis=dict(autorange="reversed"),
# xaxis=dict(tickangle=-90),
    yaxis_title="Rating",
    xaxis_title="<b>Online_order </b>"
)


# 4.Does table booking correlate with higher customer ratings?
query4 = """
SELECT book_table,round(avg(rate),2) as Avg_rating FROM restaurants
group by book_table

"""

q4 = pd.read_sql(query4, conn)

# query 4 - plotly chart
fig4 = px.bar(
    q4,
    x="book_table",
    y="Avg_rating",
    #orientation="h",
    text="Avg_rating",
    title="Correlation between Table booking and Rating",
    color_discrete_sequence=["#d25d4b"]
)

fig4.update_traces(textposition="outside")

fig4.update_layout(
    height=500,
    width=600,
    #template="plotly_white",
    margin=dict(l=50, r=30, t=50, b=30),
    
    #xaxis=dict(range=[600,1900]),
    yaxis=dict(range=[3.5,4.3]),
# yaxis=dict(autorange="reversed"),
# xaxis=dict(tickangle=-90),
    yaxis_title="<b>Rating</b>",
    xaxis_title="<b>Table booking </b>"
)


#5.What price range delivers the best customer satisfaction?
query5 = """
SELECT
    CASE
    WHEN "approx_cost(for two people)" <= 400 THEN 'Low'
    WHEN "approx_cost(for two people)" <= 1000 THEN 'Mid'
    ELSE 'Premium'
END as price_segment,

    ROUND(AVG(rate),2) AS avg_rating,
    COUNT(*) AS restaurant_count

FROM restaurants

GROUP BY price_segment
order by avg_rating desc
"""
q5= pd.read_sql(query5, conn)


#query5- plotly chart
fig5 = px.bar(
    q5,
    x="price_segment",
    y="avg_rating",
    #orientation="h",
    text="avg_rating",
    title="Segment performing well",
    color_discrete_sequence=["#003049"]
)

fig5.update_traces(textposition="outside")

fig5.update_layout(
    height=500,
    width=600,
    #template="plotly_white",
    margin=dict(l=50, r=30, t=50, b=30),
    
    #xaxis=dict(range=[600,1900]),
    #yaxis=dict(range=[3.5,4.3]),
# yaxis=dict(autorange="reversed"),
# xaxis=dict(tickangle=-90),
    yaxis_title="<b>Average rating</b>",
    xaxis_title="<b>price segment </b>"
)


#6.How do low, mid, and premium-priced restaurants perform in terms of ratings?


query6 = """
SELECT
    CASE
    WHEN "approx_cost(for two people)" <= 400 THEN 'Low'
    WHEN "approx_cost(for two people)" <= 1000 THEN 'Mid'
    ELSE 'Premium'
END as price_segment,

    ROUND(AVG(rate),2) AS avg_rating,
    COUNT(*) AS restaurant_count

FROM restaurants

GROUP BY price_segment
order by avg_rating desc
"""
q6= pd.read_sql(query6, conn)


# query 6 - Plotly chart
fig6 = px.bar(
    q6,
    x="price_segment",
    y="avg_rating",
    text="avg_rating",
    title="SEGMENT WISE PERFORMANCE",
    color="price_segment",
    color_discrete_sequence=["#F5AFAF", "#AFCBFF", "#C7F0BD"],
)

fig6.update_traces(textposition="outside")

fig6.update_layout(
    height=500,
    width=600,
    #template="plotly_white",
    margin=dict(l=50, r=30, t=50, b=30))

st.sidebar.title("Uber Eats Dashboard")

#11.Which locations are ideal for premium restaurant onboarding?

query11='''SELECT   
    location,
    ROUND(AVG(rate),2) AS avg_rating,
    ROUND(AVG("approx_cost(for two people)"),2) AS avg_cost,
    COUNT(*) AS restaurants
FROM restaurants
GROUP BY location
HAVING avg_rating > 4
ORDER BY avg_cost DESC
limit 10;'''
q11= pd.read_sql(query11, conn)
fig11 = px.bar(
    q11,
    x="location",
    y="avg_cost",
    text="avg_cost",
    title="Best location for premium restaurant onboarding",
    color_discrete_sequence=["#dbb42c"]
)

fig11.update_traces(textposition="outside")

fig11.update_layout(
    height=500,
    width=700,
    #template="plotly_white",
    margin=dict(l=50, r=50, t=50, b=100),
    xaxis_title="",
    yaxis_title="<b>Average Cost</b>")


#12.Which locations show high demand but lower average ratings?

query12 = """
SELECT
    location,
    ROUND(AVG(rate),2) AS avg_rating,
    COUNT(*) AS restaurant_count
FROM restaurants
GROUP BY location
HAVING COUNT(*) > 500
ORDER BY avg_rating , restaurant_count ASC;"""
# query 12 - plotly

q12 = pd.read_sql(query12, conn)

query12_sub = """
SELECT
    MIN(avg_rating) AS min_rating,
    MAX(avg_rating) AS max_rating,
    MIN(restaurant_count) AS min_count,
    MAX(restaurant_count) AS max_count
FROM (
    SELECT
        ROUND(AVG(rate),2) AS avg_rating,
        COUNT(*) AS restaurant_count
    FROM restaurants
    GROUP BY location
)
"""

q12_sub=pd.read_sql(query12_sub,conn)


fig12 = px.bar(
    q12,
    x="restaurant_count",
    y="location",
    orientation="h",
    text="restaurant_count",
    title="High Demand Locations with Lower Ratings",
    color="avg_rating",
    color_continuous_scale="Reds_r"
)

fig12.update_layout(
    yaxis=dict(autorange="reversed"),
    margin=dict(l=300, r=50, t=50, b=100),
    yaxis_title=""
)

# 13.Do restaurants offering both online ordering and table booking perform better?

query13 = """
SELECT
    online_order,
    book_table,
    ROUND(AVG(rate),2) AS avg_rating,
    COUNT(*) AS restaurant_count
FROM restaurants
GROUP BY online_order, book_table
ORDER BY avg_rating DESC
"""

q13 = pd.read_sql(query13, conn)



#Query 13- plotly chart

q13["Online_order/Book_table"] = q13["online_order"] + " / " + q13["book_table"]
fig13_avg = px.bar(
    q13,
    x="Online_order/Book_table",
    y="avg_rating",
    text="avg_rating",
    title="Average Rating by Service Combination",
    color="Online_order/Book_table",
    color_discrete_sequence=["#afab23"]
)

fig13_avg.update_traces(textposition="outside",showlegend=False)

fig13_avg.update_layout(
    height=500,
    width=600,
    #template="plotly_white",
    margin=dict(l=50, r=30, t=50, b=30),
    
    #xaxis=dict(range=[600,1900]),
    #yaxis=dict(range=[3.5,4.3]),
# yaxis=dict(autorange="reversed"),
# xaxis=dict(tickangle=-90),
    yaxis_title="<b>Average rating</b>",
    xaxis_title="<b>Online order / Book table </b>"
)

q13["Online_order/Book_table"] = q13["online_order"] + " / " + q13["book_table"]
fig13_count = px.bar(
    q13,
    x="Online_order/Book_table",
    y="restaurant_count",
    text="restaurant_count",
    title=" Restaurant count by Service Combination",
    color="Online_order/Book_table",
    color_discrete_sequence=["#afab23"]
)

fig13_count.update_traces(textposition="outside",showlegend=False)

fig13_count.update_layout(
    height=500,
    width=600,
    #template="plotly_white",
    margin=dict(l=50, r=30, t=50, b=30),
    
    #xaxis=dict(range=[600,1900]),
    #yaxis=dict(range=[3.5,4.3]),
# yaxis=dict(autorange="reversed"),
# xaxis=dict(tickangle=-90),
    yaxis_title="<b>Restaurant count</b>",
    xaxis_title="<b>Online order / Book table </b>"
)


#15.Which restaurants are top performers within each pricing segment?
query15_low = """
SELECT
    name,
    location,
    ROUND(AVG(rate),2) AS rate,
    MAX(votes) AS votes,
    MAX("approx_cost(for two people)") AS cost
FROM restaurants
WHERE "approx_cost(for two people)" <= 400
GROUP BY name, location
ORDER BY rate DESC, votes DESC
LIMIT 5;
"""
q15_low = pd.read_sql(query15_low, conn)

query15_mid = """
SELECT
    name,
    location,
    ROUND(AVG(rate),2) AS rate,
    MAX(votes) AS votes,
    MAX("approx_cost(for two people)") AS cost
FROM restaurants
WHERE "approx_cost(for two people)" > 400
AND "approx_cost(for two people)" <= 1000
GROUP BY name, location
ORDER BY rate DESC, votes DESC
LIMIT 5;"""
q15_mid=pd.read_sql(query15_mid,conn)

query15_premium = """
SELECT
    name,
    location,
    ROUND(AVG(rate),2) AS rate,
    MAX(votes) AS votes,
    MAX("approx_cost(for two people)") AS cost
FROM restaurants
WHERE "approx_cost(for two people)" > 1000
GROUP BY name, location
ORDER BY rate DESC, votes DESC
LIMIT 5;"""
q15_premium=pd.read_sql(query15_premium,conn)



#Query 15 - Plotly chart

q15_low["restaurant_name"] = (q15_low["name"] + " (" + q15_low["location"] + ")")
fig15_low = px.bar(
    q15_low,
    x="restaurant_name",
    y="rate",
    hover_data=["votes"],
    color_discrete_sequence=["#00FFBF"]
)


fig15_low.update_layout(
    height=500,
    width=700,
    yaxis=dict(range=[4.7,5]),
    #yaxis=dict(autorange="reversed"),
    margin=dict(l=50, r=130, t=50, b=160),
    yaxis_title="Rating"
)

q15_mid["restaurant_name"] = (
    q15_mid["name"].str[:20] + "... (" + q15_mid["location"] + ")"
)
fig15_mid = px.bar(
    q15_mid,
    x="restaurant_name",
    y="rate",
    hover_data=["name", "location", "votes"],
    color_discrete_sequence=["#00FF7F"]
    
)


fig15_mid.update_layout(
    height=500,
    width=700,
    #s=dict(range=[4.7,5]),
    #yaxis=dict(autorange="reversed"),
    margin=dict(l=50, r=130, t=50, b=160),
    yaxis_title="Rating",
    xaxis_title="",
    yaxis=dict(range=[4.6,5])
)


fig15_premium= px.bar(
    q15_premium,
    x="name",
    y="rate",
    hover_data=["name", "location", "votes"],
    color_discrete_sequence=["#76FF7A"]
)


fig15_premium.update_layout(
    height=500,
    width=700,
    yaxis=dict(range=[4.7,5]),
    #yaxis=dict(autorange="reversed"),
    margin=dict(l=50, r=130, t=50, b=160),
    yaxis_title="Rating",
    xaxis_title=""
)


#order table query
##1.which is the Most used payment method?
Order_query1="""
select payment_method,count(*) as total_count
from Order_details
group by payment_method	
order by total_count desc"""
Order_q1=pd.read_sql(Order_query1,conn)



# order query 1 - plotly
fig_o1= px.pie(
    Order_q1,
    names="payment_method",
    values="total_count",
    title="Payment Method Distribution",
    color_discrete_sequence=["#DAA06D","#954535","#AF6E4D"]
)
fig_o1.update_traces(
    textposition="inside",
    textinfo="percent+label"
)

##2.which restaurant has Highest order volume 
Order_query2="""
select restaurant_name,count(*) as total_count
from Order_details
group by restaurant_name
order by total_count desc
Limit 10"""
Order_q2=pd.read_sql(Order_query2,conn)

# order query 2 - plotly
fig_o2 = px.bar(
    Order_q2,
    x="total_count",
    y="restaurant_name",
    orientation="h",
    text="total_count",
    title="Top 10 Restaurants by Order Volume",
    color_discrete_sequence=["#905D5D"]
)

fig_o2.update_traces(textposition="outside")

fig_o2.update_layout(
    height=500,
    width=800,
    margin=dict(l=200, r=30, t=50, b=30),
    yaxis=dict(autorange="reversed"),
    xaxis_title="<b>Total Orders</b>",
    yaxis_title=""
)

#3.which restaurant has Highest revenue earnings?
Order_query3="""
select restaurant_name,sum(order_value) as total_revenue
from Order_details
group by restaurant_name
order by total_revenue desc
Limit 10"""
Order_q3=pd.read_sql(Order_query3,conn)

# order 3 - plotly chart
fig_o3 = px.bar(
    Order_q3,
    x="total_revenue",
    y="restaurant_name",
    orientation="h",
    text="total_revenue",
    title="Top 10 Restaurants by Revenue",
    color="total_revenue",
    color_continuous_scale="Greens"
)

fig_o3.update_traces(textposition="outside")

fig_o3.update_layout(
    height=500,
    width=800,
    xaxis=dict(range=[16000,20000]),
    margin=dict(l=140, r=30, t=50, b=30),
    yaxis=dict(autorange="reversed"),
    xaxis_title="<b>Total Revenue</b>",
    yaxis_title=""
)
fig_o3.update_traces(
    texttemplate="₹%{x:,.0f}",
    textposition="outside"
)

##4.which day of the week has Highest order ?
Order_query4 = """
SELECT
    CASE strftime('%w', order_date)
        WHEN '0' THEN 'Sunday'
        WHEN '1' THEN 'Monday'
        WHEN '2' THEN 'Tuesday'
        WHEN '3' THEN 'Wednesday'
        WHEN '4' THEN 'Thursday'
        WHEN '5' THEN 'Friday'
        WHEN '6' THEN 'Saturday'
    END AS day_name,
    COUNT(*) AS total_count
FROM Order_details
GROUP BY day_name
ORDER BY total_count 
"""
Order_q4 = pd.read_sql(Order_query4, conn)


# plotly chart- order query 4
day_order = [
    "Monday", "Tuesday", "Wednesday",
    "Thursday", "Friday", "Saturday", "Sunday"
]

Order_q4["day_name"] = pd.Categorical(
    Order_q4["day_name"],
    categories=day_order,
    ordered=True
)

Order_q4 = Order_q4.sort_values("day_name")
fig_o4 = px.line(
    Order_q4,
    x="day_name",
    y="total_count",
    markers=True,
    title="Orders by Day of Week"
)

#5.Which day of the week generates the highest revenue?
Order_query5 = """
SELECT
    CASE strftime('%w', order_date)
        WHEN '0' THEN 'Sunday'
        WHEN '1' THEN 'Monday'
        WHEN '2' THEN 'Tuesday'
        WHEN '3' THEN 'Wednesday'
        WHEN '4' THEN 'Thursday'
        WHEN '5' THEN 'Friday'
        WHEN '6' THEN 'Saturday'
    END AS day_name,sum(order_value) as total_value
    
FROM Order_details
GROUP BY day_name
ORDER BY total_value DESC
"""
Order_q5 = pd.read_sql(Order_query5, conn)

Order_q5_display = Order_q5.copy()

Order_q5_display["total_value"] = Order_q5_display["total_value"].apply(
    lambda x: f"₹{x:,.2f}"
)


# plotly chart
fig_o5 = px.line(
    Order_q5,
    x="day_name",
    y="total_value",
    markers=True,
    title="Revenue Generated by Day of Week"
)

fig_o5.update_traces(
    line_width=3
)

fig_o5.update_layout(
    height=500,
    width=700,
    xaxis_title="<b>Day</b>",
    yaxis_title="<b>Total Revenue (₹)</b>"
)







restaurant_question = st.sidebar.selectbox(
    "Restaurant Analytics",
    [
        "Select",
        "Q1 - Highest Rated Locations",
        "Q2 - Over-Saturated Locations",
        "Q3 - Online Ordering Impact",
        "Q4 - Table Booking Impact",
        "Q5 - Best Price Range",
        "Q6 - Price Segment Performance",
        "Q11 - Premium Onboarding Locations",
        "Q12 - High Demand Low Rating Areas",
        "Q13 - Online Order + Table Booking",
        "Q15 - Top Performers by Price Segment"
    ]
)

order_question = st.sidebar.selectbox(
    "Order Analytics    ",
    [
        "Select",
        "O1 - Most Used Payment Method",
        "O2 - Highest Order Volume Restaurant",
        "O3 - Highest Revenue Restaurant",
        "O4 - Highest Order Day of Week",
        "O5 - Highest Revenue Day of Week"
    ]
)






if restaurant_question == "Q1 - Highest Rated Locations":

    st.header(
        "Q1. Which Bangalore locations have the highest average restaurant ratings?"
    )

    col1, col2 = st.columns([2,3])

    with col1:
        st.dataframe(q1)

    with col2:
        st.plotly_chart(fig1, width="stretch")
    st.subheader("Business Insight")
    st.write(
    """
    **Answer:** Lavelle Road has the highest Average rating  

    **Business Value:** This location might have good customer service, hygiene foods , easy transport. uber eats should prioritize more hotels in this location
    """)
elif restaurant_question == "Q2 - Over-Saturated Locations":

    st.header("Q2. Which locations are over-saturated with restaurants?")

    col1, col2 = st.columns([2,3])

    with col1:
        st.dataframe(q2, hide_index=True)

    with col2:
        st.plotly_chart(fig2, width="stretch")
    st.subheader("Business Insight")
    st.write(
    """
    **Answer:**   Koramangala 5th Block has higher restaurant counts of 1782 restaurants 

    **Business Value:** Uber eats can consider other less dense location with high demand for restaurant expansion
    """)
        
elif restaurant_question =="Q3 - Online Ordering Impact":
    
    st.header("Q3. Does online ordering improve restaurant ratings?")

    col1, col2 = st.columns([2, 3])

    with col1:
        st.dataframe(q3, hide_index=True, use_container_width=True)

    with col2:
        st.plotly_chart(fig3, use_container_width=True)

    st.subheader("💡 Business Insight")
    st.write("""
    **Answer:** Restaurants without online ordering have a higher average rating in this dataset.

    **Business Value:** This indicates an association between online-order availability
    and restaurant ratings, but it does not establish that online ordering causes the rating difference.
    """)

elif restaurant_question == "Q4 - Table Booking Impact":
    st. header("Does table booking correlate with higher customer ratings?")
    col1,col2=st.columns([2,3])
    with col1:
        st.dataframe(q4,hide_index=True)
    with col2:
        st.plotly_chart(fig4,width="stretch")
    st.subheader("Business Insight")
    st.write(
    """
    **Answer:**   Yes table booking correlate with higher customer rating 

    **Business Value:** As per the data , Table booking has impact on rating. So expanding hotels with table booking improves profit
    """)

elif restaurant_question == "Q5 - Best Price Range":
    st. header("Does table booking correlate with higher customer ratings?")
    col1,col2=st.columns([2,3])
    with col1:
        st.dataframe(q5,hide_index=True)
    with col2:
        st.plotly_chart(fig5,width="stretch")
    st.info("""
    Price Segment Definition:
        • Low: ≤ ₹400
        • Mid: ₹401–₹1000
        • Premium: > ₹1000
""")
    st.subheader("Business Insight")
    st.write(
    """
    **Answer:**   Premium  segment

    **Business Value:** AS per the data, customer like premium restaurant more than the normal one
    """)
    
elif restaurant_question == "Q6 - Price Segment Performance":
    st. header("How do low, mid, and premium-priced restaurants perform in terms of ratings?")
    col1,col2=st.columns([2,3])
    with col1:
        st.dataframe(q6,hide_index=True)
    with col2:
        st.plotly_chart(fig6,width="stretch")
    st.info("""
    Price Segment Definition:
        • Low: ≤ ₹400
        • Mid: ₹401–₹1000
        • Premium: > ₹1000""")
    st.subheader("Business Insight")
    st.write("""
**Answer:** The Premium segment has the highest average rating, followed by the Mid and Low segments.

**Business Value:** Higher-priced restaurants show stronger average customer ratings in this dataset. 
This can help Uber Eats identify locations and restaurant segments where premium positioning may be suitable.""")

elif restaurant_question == "Q11 - Premium Onboarding Locations":
    st. header("Which locations are ideal for premium restaurant onboarding?")
    col1,col2=st.columns([2,3])
    with col1:
        st.dataframe(q11,hide_index=True)
    with col2:
        st.plotly_chart(fig11,width="stretch")
    st.subheader("Business Insight")
    st.write(
    """
    **Answer:**   As per the average cost, Sankey road is top in the list followed by Lavelle road, Richmond Road

    **Business Value:** In terms of restaurant count, we should improve branches in Sankey road, since it has less restaurant count with highest average cost
    """)
    
elif restaurant_question == "Q12 - High Demand Low Rating Areas":
    st. header("Which locations show high demand but lower average ratings?")

    col1,col2=st.columns([2,3])
    with col1:
        st.subheader("High demand and average rating")

        st.dataframe(q12,hide_index=True)
        st.subheader("Min and max of rating and reastaurant counts")
        st.dataframe(q12_sub)
    with col2:
        st.plotly_chart(fig12,width="stretch")
    st.subheader("Business Insight")
    st.write(
    """
    **Answer:**   Marathahalli has rating of 3.73 with 680 restaurants

    **Business Value:** Even with 680 restaurants, Marathahalli has performed low. Here, I have filtered restaurant counts greater than 500 
    for identifying the high demand and average rating. 
    """)
elif restaurant_question == "Q13 - Online Order + Table Booking":
    st. header("Do restaurants offering both online ordering and table booking perform better?")
    st.dataframe(q13[["Online_order/Book_table","avg_rating","restaurant_count"]],hide_index=True)
    col1,col2=st.columns([2,2])
    
    with col1:
        st.plotly_chart(fig13_count,width="stretch")
    with col2:
        st.plotly_chart(fig13_avg,width="stretch")
    st.subheader("Business Insight")
    st.write(
    """
    **Answer:**   Yes , it performs better in terms of rating

    **Business Value:** When we look at the restaurant count, online ordering restaurants with no table booking option has higher restaurant count .
    Restaurants with table booking show higher average ratings.so we should improve table booking hotels more 
    """)
    
    
elif restaurant_question == "Q15 - Top Performers by Price Segment":
    st. header("Which restaurants are top performers within each pricing segment?")
    col1,col2=st.columns([2,2])
    with col1:
        
        st.plotly_chart(fig15_low,width="stretch")
    with col2:
        st. subheader("Top performers of Low segment ")
        st.dataframe(q15_low[["restaurant_name","rate","votes"]],hide_index=True)
    col3,col4=st.columns([2,2])
    with col3:
        
        st.plotly_chart(fig15_mid,width="stretch")
    with col4:
        st. subheader("Top performers of mid segment ")
        st.dataframe(q15_mid[["restaurant_name","rate","votes"]],hide_index=True)
    col5,col6=st.columns([2,2])
    with col5:
    
        st.plotly_chart(fig15_premium,width="stretch")
    with col6:
        st. subheader("Top performers of Premium segment ")
        st.dataframe(q15_premium,hide_index=True)
    st.subheader("Business Insight")
    st.write(
    """
    **Answer:**  Milano Ice Cream (Indiranagar) in low segment,  
                SantÃÂÃÂÃÂÃÂ... (Indiranagar) in mid segment , 
                Byg Brewski Brewing Company(Sarjapur Road ) in premium segment,  
                performed better


    **Business Value:** Hotels from Indira nagar performed well in low and mid segment .But in premium segment hotel from Sarjapur road won
    """)
    

if order_question=="O1 - Most Used Payment Method":
    st. header("Which is the Most used payment method?")
    col1, col2 = st.columns([2,3])

    with col1:
        st.dataframe(Order_q1)

    with col2:
        st.plotly_chart(fig_o1, width="stretch")
    st.subheader("Business Insight")

    st.write(
    """
    **Answer:** Cash is the most frequently used payment method with 8,384 orders,
    followed closely by Card and UPI.

    **Business Value:** Restaurants should continue supporting all major payment
    methods, but ensuring smooth cash and card transactions can help reduce
    payment friction and improve customer experience.
    """
)


elif order_question== "O2 - Highest Order Volume Restaurant":
    st. header("Which restaurant has Highest order volume ?")
    col1, col2 = st.columns([2,4])

    with col1:
        st.dataframe(Order_q2)

    with col2:
        st.plotly_chart(fig_o2, width="stretch")
    st.subheader("Business Insight")
    st.write(
    """
    **Answer:** Cake cafe and Andhra Grills has the highest order count of 19 .

    **Business Value:** These restaurants has more reputation around the customers making it highest order volume restaurant
    """
    )

elif order_question ==  "O3 - Highest Revenue Restaurant":
    st. header("Which restaurant has Highest revenue earnings?")
    col1, col2 = st.columns([2,4])

    with col1:
        st.dataframe(Order_q3,hide_index=True)

    with col2:
        st.plotly_chart(fig_o3, width="stretch")
    st.subheader("Business Insight")
    st.write(
    """
    **Answer:** Bob's Bar has highest earnings of Rs. 19518.14

    **Business Value:** Following Bob's Bar ,Cake cafe has the 2nd highest income.
    so menu similar  to Bob's Bar, cake cafe will improve the sales 
    """
    )


elif order_question == "O4 - Highest Order Day of Week":
    st. header("Which day of the week has Highest order ?")
    col1, col2 = st.columns([2,3])

    with col1:
        st.dataframe(Order_q4,hide_index="True")

    with col2:
        st.plotly_chart(fig_o4, width="stretch")
    st.subheader("Business Insight")
    st.write(
    """
    **Answer:** Thursday has the highest order count 

    **Business Value:** Thursday has highest order count of 3623,followed by monday with  3613 .
    similarly sunday has less orders than other day..
    We should prepare our menu as per this demand 
    """)

elif order_question == "O5 - Highest Revenue Day of Week":
    st. header("Which day of the week generates the highest revenue?")
    col1, col2 = st.columns([2,2])

    with col1:
        st.dataframe(Order_q5_display)

    with col2:
        st.plotly_chart(fig_o5, width="stretch")
    st.subheader("Business Insight")
    st.write(
    """
    **Answer:** Monday generates the highest revenue among all days of the week 

    **Business Value:** Even though the order count on Thursday is high . Revenue generation is high on Monday only.
    """)
    