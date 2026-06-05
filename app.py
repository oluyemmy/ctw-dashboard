import streamlit as st
import pandas as pd

st.markdown("""
<style>
#MainMenu {
    visibility: hidden;
}

footer {
    visibility: hidden;
}

header {
    visibility: hidden;
}

[data-testid="stToolbar"] {
    display: none;
}
</style>
""", unsafe_allow_html=True)

st.set_page_config(page_title="CTW Dashboard", layout="wide")

st.title("📊 Community Health Worker Dashboard")

# Load data
@st.cache_data(ttl=300)
def load_data():
    url = "https://docs.google.com/spreadsheets/d/1wXcFJsH7TjAYAYIc5fVQsk8oDwWLr0PP5OxQ14X8_iQ/export?format=csv&gid=1767108424"
    df = pd.read_csv(url)
    #df = pd.read_csv("cleaned_data.csv")
    
    # Convert date
    df["Date Created"] = pd.to_datetime(df["Date Created"])
    
    # Create age groups
    bins = [0,1,5,10,15,20,25,30,35,40,45,50,55,60,65,100]
    labels = ["<1","1-4","5-9","10-14","15-19","20-24","25-29",
              "30-34","35-39","40-44","45-49","50-54","55-59","60-64","65+"]
    
    df["Age Group"] = pd.cut(df["Age"], bins=bins, labels=labels, right=False)
    
    return df

df = load_data()

# Sidebar filters
st.sidebar.header("🔍 Filter")

ctw = st.sidebar.selectbox("Select Your Name", sorted(df["CTW"].dropna().unique()))

lga = st.sidebar.selectbox("Select LGA", sorted(df["LGA"].dropna().unique()))

date_range = st.sidebar.date_input("Select Date Range", [])

# Filter data
filtered_df = df[(df["CTW"] == ctw) & (df["LGA"] == lga)]

if len(date_range) == 2:
    filtered_df = filtered_df[
        (filtered_df["Date Created"] >= pd.to_datetime(date_range[0])) &
        (filtered_df["Date Created"] <= pd.to_datetime(date_range[1]))
    ]

# ---------------- METRICS ----------------
st.subheader(f"Summary for {ctw}")

col1, col2, col3, col4 = st.columns(4)

col1.metric("Screened", len(filtered_df))
col2.metric("Presumptive", (filtered_df["Presumptive"] == "Yes").sum())
col3.metric("Presumptive Evaluated", filtered_df["Test Method"].notna().sum())
col4.metric("Cases", (filtered_df["Test Result"] == "Positive").sum())

# ---------------- CHARTS ----------------

# st.subheader("📊 Age Distribution")
# age_chart = filtered_df["Age Group"].value_counts().sort_index()
# st.bar_chart(age_chart)

# st.subheader("👥 Gender Distribution")
# gender_chart = filtered_df["Gender"].value_counts()
# st.bar_chart(gender_chart)

# st.subheader("🧪 Test Results")
# test_chart = filtered_df["Test Result"].value_counts()
# st.bar_chart(test_chart)

# ---------------- TABLE ----------------
# ---------------- TABLE ----------------

col1, col2 = st.columns([4,1])

with col1:
    st.subheader("📋 Detailed Records")

with col2:
    result_filter = st.selectbox(
        "Test Result",
        ["All", "Positive", "Negative", "Not Tested"]
    )

# Create a copy specifically for the table
table_df = filtered_df.copy()

# Apply filter only to the table
if result_filter == "Positive":
    table_df = table_df[
        table_df["Test Result"].fillna("").str.upper() == "POSITIVE"
    ]

elif result_filter == "Negative":
    table_df = table_df[
        table_df["Test Result"].fillna("").str.upper() == "NEGATIVE"
    ]

elif result_filter == "Not Tested":
    table_df = table_df[
        table_df["Test Result"].isna() |
        (table_df["Test Result"].astype(str).str.strip() == "")
    ]

st.write(f"Showing **{len(table_df)}** record(s)")

st.dataframe(
    table_df,
    use_container_width=True,
    hide_index=True
)