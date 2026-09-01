import streamlit as st
import pandas as pd
import plotly.express as px

# ---------------------------------------------------------
# MEMBER 1: DATA ENGINE (Data Cleaning & Risk Logic)
# ---------------------------------------------------------
@st.cache_data
def load_and_clean_data():
    # 1. Load the data
    df = pd.read_csv("diabetes_risk_prediction_dataset-selected-columns.csv")
    
    # 2. Fill missing height, weight, glucose, and HbA1c values with

    # the median value of the corresponding dataset column.
    columns_to_fill = ['Height_cm', 'Weight_kg', 'Blood_Glucose', 'HbA1c']

    for col in columns_to_fill:
        if col in df.columns:
            df[col] = df[col].fillna(df[col].median())

    # Calculate BMI for records where BMI is not provided,
    # using height in meters and weight in kilograms.
    if 'BMI' in df.columns:
        missing_bmi = df['BMI'].isna()

        df.loc[missing_bmi, 'BMI'] = (
            df.loc[missing_bmi, 'Weight_kg']
            / (df.loc[missing_bmi, 'Height_cm'] / 100) ** 2
        )

    # 3. Macro Cohort Segmentation Rules
    def assign_risk(row):
        # High Risk Logic
        if row['HbA1c'] >= 6.5 or row['Blood_Glucose'] >= 140 or row['BMI'] >= 30:
            return "High Risk"
        # Moderate Risk Logic
        elif row['HbA1c'] >= 5.7 or row['Blood_Glucose'] >= 100 or row['BMI'] >= 25:
            return "Moderate Risk"
        # Low Risk Logic
        else:
            return "Low Risk"

    df['Health_Risk_Tier'] = df.apply(assign_risk, axis=1)
    return df

df = load_and_clean_data()

# ---------------------------------------------------------
# UI SETUP 
# ---------------------------------------------------------
st.set_page_config(page_title="Metabolic Risk App", layout="wide")
st.title("🩺 Interactive Metabolic Risk Calculator & Cohort Dashboard")

# Create two tabs so the dashboard and calculator are separate
tab1, tab2 = st.tabs(["📊 Global Population Dashboard", "🧮 Personal Risk Calculator"])

# ---------------------------------------------------------
# MEMBER 2: DASHBOARD DEVELOPER (Global Dashboard)
# ---------------------------------------------------------
with tab1:
    st.header("Global Population Dashboard")

        # Country-wise distribution of estimated risk tiers.
    country_risk = (
        df.groupby(['Country', 'Health_Risk_Tier'])
        .size()
        .reset_index(name='Count')
    )

    fig_country_risk = px.bar(
        country_risk,
        x='Country',
        y='Count',
        color='Health_Risk_Tier',
        title="Risk Tier Distribution by Country",
        barmode='stack'
    )

    st.plotly_chart(fig_country_risk, use_container_width=True)

    st.caption(
        "This chart compares the number of people in each estimated risk tier "
        "across the 25 countries represented in the dataset."
    )

        # Compare average metabolic measurements across countries.
    country_metrics = (
        df.groupby('Country')[['BMI', 'Blood_Glucose', 'HbA1c']]
        .mean()
        .reset_index()
    )

    fig_country_metrics = px.bar(
        country_metrics,
        x='Country',
        y=['BMI', 'Blood_Glucose', 'HbA1c'],
        title="Average Risk Factors by Country",
        barmode='group'
    )

    st.plotly_chart(fig_country_metrics, use_container_width=True)

    st.caption(
        "Average BMI, blood glucose, and HbA1c values are shown for each "
        "country in the dataset."
    )
    
    col1, col2 = st.columns(2)
    
    with col1:
        # Visualizing tier distributions
        tier_counts = df['Health_Risk_Tier'].value_counts().reset_index()
        tier_counts.columns = ['Tier', 'Count']
        fig_pie = px.pie(tier_counts, names='Tier', values='Count', title="Population Risk Tier Distribution")
        st.plotly_chart(fig_pie, use_container_width=True)
  
          # Blood glucose distribution by estimated risk tier.
        glucose_bins = pd.cut(df['Blood_Glucose'], bins=40)

        glucose_distribution = (
            df.groupby(['Health_Risk_Tier', glucose_bins], observed=True)
            .size()
            .reset_index(name='Count')
        )

        glucose_distribution['Blood_Glucose'] = (
            glucose_distribution['Blood_Glucose']
            .apply(lambda x: x.mid)
        )

        fig_bg = px.line(
            glucose_distribution,
            x='Blood_Glucose',
            y='Count',
            color='Health_Risk_Tier',
            markers=True,
            title="Blood Glucose Distribution by Risk Tier",
            labels={
                'Blood_Glucose': 'Blood Glucose Level',
                'Count': 'Number of People',
                'Health_Risk_Tier': 'Risk Tier'
            }
        )

        st.plotly_chart(fig_bg, use_container_width=True)

    with col2:

                # HbA1c distribution by estimated risk tier.
        hba1c_bins = pd.cut(df['HbA1c'], bins=40)

        hba1c_distribution = (
            df.groupby(['Health_Risk_Tier', hba1c_bins], observed=True)
            .size()
            .reset_index(name='Count')
        )

        hba1c_distribution['HbA1c'] = (
            hba1c_distribution['HbA1c']
            .apply(lambda x: x.mid)
        )

        fig_hba1c = px.line(
            hba1c_distribution,
            x='HbA1c',
            y='Count',
            color='Health_Risk_Tier',
            markers=True,
            title="HbA1c Distribution by Risk Tier",
            labels={
                'HbA1c': 'HbA1c Level',
                'Count': 'Number of People',
                'Health_Risk_Tier': 'Risk Tier'
            }
        )

        st.plotly_chart(fig_hba1c, use_container_width=True)

        # Average age per tier
        avg_age = df.groupby('Health_Risk_Tier')['Age'].mean().reset_index()
        fig_age = px.bar(avg_age, x='Health_Risk_Tier', y='Age', title="Average Age per Risk Tier")
        st.plotly_chart(fig_age, use_container_width=True)
        
                # BMI distribution by estimated risk tier.
        bmi_bins = pd.cut(df['BMI'], bins=40)

        bmi_distribution = (
            df.groupby(['Health_Risk_Tier', bmi_bins], observed=True)
            .size()
            .reset_index(name='Count')
        )

        bmi_distribution['BMI'] = (
            bmi_distribution['BMI']
            .apply(lambda x: x.mid)
        )

        fig_bmi = px.line(
            bmi_distribution,
            x='BMI',
            y='Count',
            color='Health_Risk_Tier',
            markers=True,
            title="BMI Distribution by Risk Tier",
            labels={
                'BMI': 'BMI',
                'Count': 'Number of People',
                'Health_Risk_Tier': 'Risk Tier'
            }
        )

        st.plotly_chart(fig_bmi, use_container_width=True)

# ---------------------------------------------------------
# MEMBER 3 & 4: CALCULATOR ARCHITECT & PROJECT MANAGER
# ---------------------------------------------------------
with tab2:
    st.header("Personal Risk Assessment Calculator")
    
    # Input Form
    with st.form("user_inputs"):
        col_a, col_b = st.columns(2)
        with col_a:
            u_age = st.number_input("Age", min_value=1, max_value=120, value=30)
            u_gender = st.selectbox("Gender", ["Male", "Female", "Other"])
            u_height = st.number_input("Height (cm)", min_value=50.0, value=170.0)
            u_weight = st.number_input("Weight (kg)", min_value=10.0, value=70.0)
        with col_b:
            u_waist = st.number_input(
                "Waist Circumference (cm)",
                min_value=50.0,
                max_value=140.0,
                value=80.0
            )
            u_glucose = st.number_input("Blood Glucose (optional)", min_value=0.0, value=90.0)
            u_hba1c = st.number_input("HbA1c (optional)", min_value=0.0, value=5.0)
            
        submitted = st.form_submit_button("Calculate My Risk")

    if submitted:
        # 1. Dynamically Calculate BMI
        height_m = u_height / 100
        u_bmi = u_weight / (height_m * height_m)

         # Define the project reference range for waist circumference based on gender.
        if u_gender == "Female":
            waist_lower = 60
            waist_upper = 80
        else:
            waist_lower = 70
            waist_upper = 94

        # Check whether the user's waist circumference falls within the
        # reference range for their selected gender.
        waist_in_range = waist_lower <= u_waist <= waist_upper
        
        # 2. Assign Health Risk Tier using HbA1c, blood glucose, and BMI thresholds.
        if u_hba1c >= 6.5 or u_glucose >= 140 or u_bmi >= 30:
            u_tier = "High Risk"
        elif u_hba1c >= 5.7 or u_glucose >= 100 or u_bmi >= 25:
            u_tier = "Moderate Risk"
        else:
            u_tier = "Low Risk"
            
        # 3. Report Percentile Standing
        # Calculate what percentage of the dataset has a BMI lower than the user
        percentile = (df['BMI'] < u_bmi).mean() * 100

                # Calculate the user's waist position relative to waist measurements in the dataset.
                # Calculate the percentage of dataset records with a waist measurement below the user.
        waist_percentile = (
            df['Waist_Circumference_cm'] < u_waist
        ).mean() * 100

        # The remaining percentage represents records with a waist measurement
        # equal to or above the user's measurement.
        waist_above_percent = 100 - waist_percentile

        # Define the visual scale used for the waist circumference indicator.
        waist_scale_min = 50
        waist_scale_max = 140

        # Convert the user's waist measurement into a position on the 50–120 cm scale.
        waist_bar_position = (
            (u_waist - waist_scale_min)
            / (waist_scale_max - waist_scale_min)
        )

        st.write("**Waist Circumference Position**")
        st.progress(waist_bar_position)

        st.caption(
            f"{waist_scale_min} cm ───────────────────────── "
            f"{waist_scale_max} cm"
        )

        st.write(
            f"**Your waist:** {u_waist:.1f} cm"
        )

        st.caption(
            f"Reference range for {u_gender}: "
            f"{waist_lower}–{waist_upper} cm"
        )
        
        st.caption(
            f"**{waist_percentile:.1f}%** of people in the dataset "
            f"have a lower waist measurement, while "
            f"**{waist_above_percent:.1f}%** have a higher measurement."
        )
        
        st.divider()
        st.subheader("Your Results")

                # Clarify that the calculator provides an estimated project-based risk tier,
        # not a medical diagnosis.
        st.info(
            "⚠️ This tool provides an estimated risk tier based on the project's "
            "data and thresholds. It is not a medical diagnosis or a substitute "
            "for professional medical advice."
        )

        st.write(f"**Your calculated BMI is:** {u_bmi:.2f}")

        # Show whether the user's waist is below, within, or above the reference range.
        if u_waist < waist_lower:
            st.warning(
                f"🔴 Below the reference range of {waist_lower}–{waist_upper} cm."
            )
        elif u_waist > waist_upper:
            st.warning(
                f"🔴 Above the reference range of {waist_lower}–{waist_upper} cm."
            )
        else:
            st.success(
                f"🟢 Within the reference range of {waist_lower}–{waist_upper} cm."
            )
                # Explain the BMI percentile as a comparison with the project dataset only.
        st.write(
            f"**BMI Percentile:** Your BMI is higher than "
            f"**{percentile:.1f}%** of the people in our dataset."
        )
        st.caption(
            "This percentile is calculated from our dataset and is not a "
            "comparison with the general population."
        )

                # Display the estimated risk tier using a color-coded status box.
        if u_tier == "High Risk":
            st.error(f"🔴 **Estimated Risk Tier:** {u_tier}")
        elif u_tier == "Moderate Risk":
            st.warning(f"🟡 **Estimated Risk Tier:** {u_tier}")
        else:
            st.success(f"🟢 **Estimated Risk Tier:** {u_tier}")
        
                # Provide suggestions based on the individual measurements that contribute to risk.
        st.subheader("Personalized Lifestyle Suggestions")

        suggestions = []

        if u_bmi >= 30:
            suggestions.append(
                "Your BMI is in the high range. Consider discussing healthy weight "
                "management with a healthcare provider."
            )
        elif u_bmi >= 25:
            suggestions.append(
                "Your BMI is above the project's reference threshold. Focus on "
                "balanced nutrition and regular physical activity."
            )

        if u_glucose >= 140:
            suggestions.append(
                "Your blood glucose is elevated. Consider discussing this result "
                "with a healthcare provider."
            )
        elif u_glucose >= 100:
            suggestions.append(
                "Your blood glucose is above the project's moderate-risk threshold. "
                "Monitoring your glucose and maintaining balanced meals may be helpful."
            )

        if u_hba1c >= 6.5:
            suggestions.append(
                "Your HbA1c is elevated. Consider discussing this result with a "
                "healthcare provider."
            )
        elif u_hba1c >= 5.7:
            suggestions.append(
                "Your HbA1c is above the project's moderate-risk threshold. "
                "Regular monitoring and balanced nutrition may be helpful."
            )

        if not waist_in_range:
            if u_waist < waist_lower:
                suggestions.append(
                    f"Your waist circumference is below the project reference range "
                    f"of {waist_lower}–{waist_upper} cm for your selected gender."
                )
            else:
                suggestions.append(
                    f"Your waist circumference is above the project reference range "
                    f"of {waist_lower}–{waist_upper} cm for your selected gender."
                )

        if not suggestions:
            suggestions.append(
                "Your current measurements do not trigger any of the project's "
                "specific suggestion thresholds. Continue maintaining healthy habits "
                "and regular health monitoring."
            )

        for i, suggestion in enumerate(suggestions[:3], start=1):
            st.write(f"* **Action {i}:** {suggestion}")