import streamlit as st
import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns
from wordcloud import WordCloud
import plotly.express as px
from streamlit_extras.metric_cards import style_metric_cards

st.set_page_config(page_title="Indian Food Explorer 🇮🇳", layout="wide")

# Load data
df = pd.read_csv("indian_food.csv")
df['total_time'] = df['prep_time'] + df['cook_time']

# Sidebar Filters
st.sidebar.markdown("<h1 style='text-align: center;'>🥗</h1>", unsafe_allow_html=True)
st.sidebar.header("🔍 Filter Recipes")
region = st.sidebar.multiselect("Select Region", options=df['region'].dropna().unique())
state = st.sidebar.multiselect("Select State", options=df['state'].unique())
diet = st.sidebar.multiselect("Select Diet", options=df['diet'].unique())
course = st.sidebar.multiselect("Select Course", options=df['course'].unique())
flavor = st.sidebar.multiselect("Select Flavor Profile", options=df['flavor_profile'].unique())
time_range = st.sidebar.slider("Total Time (Prep + Cook) in minutes", 0, 300, (0, 300))

# Apply Filters
filtered_df = df.copy()
if region:
    filtered_df = filtered_df[filtered_df['region'].isin(region)]
if state:
    filtered_df = filtered_df[filtered_df['state'].isin(state)]
if diet:
    filtered_df = filtered_df[filtered_df['diet'].isin(diet)]
if course:
    filtered_df = filtered_df[filtered_df['course'].isin(course)]
if flavor:
    filtered_df = filtered_df[filtered_df['flavor_profile'].isin(flavor)]
filtered_df = filtered_df[(filtered_df['total_time'] >= time_range[0]) & (filtered_df['total_time'] <= time_range[1])]

# Title
st.markdown("""
    <h1 style='text-align: center; color: #FF9933;'> Indian Food Recipes Dashboard</h1>
    <h5 style='text-align: center; color: #666;'>Nation united by diversified taste!</h5>
    <br>
""", unsafe_allow_html=True)

# Block 1: Summary Stats as Metric Cards
colA, colB, colC = st.columns(3)
colA.metric("📋 Number of Recipes", len(filtered_df))
colB.metric("🕒 Avg. Prep Time", f"{filtered_df['prep_time'].mean():.2f} min")
colC.metric("🔥 Avg. Cook Time", f"{filtered_df['cook_time'].mean():.2f} min")
style_metric_cards(border_left_color="#ff7f50", background_color="#333333")

# Block 2: Bar Charts
st.markdown("---")
col1, col2 = st.columns(2)
with col1:
    st.subheader("📍 Recipes by Region")
    region_counts = filtered_df['region'].value_counts().reset_index()
    region_counts.columns = ['Region', 'Recipe Count']
    st.plotly_chart(px.bar(region_counts, x='Region', y='Recipe Count', color='Region', title='Recipes per Region'))
with col2:
    st.subheader("😋 Flavor Profile Distribution")
    st.plotly_chart(px.pie(filtered_df, names='flavor_profile', title='Flavor Profile Share', hole=0.4))

# Block 3: Pie Chart for Diet Type
st.markdown("---")
st.subheader("🥗 Diet Distribution")
diet_counts = filtered_df['diet'].value_counts()
st.plotly_chart(px.pie(
    names=diet_counts.index, 
    values=diet_counts.values, 
    title='Diet Type Distribution', 
    hole=0.3,
    color=diet_counts.index, 
    color_discrete_map={'vegetarian': 'light green', 'non vegetarian': 'red'}
))

# Block 4: Word Cloud of Ingredients
st.markdown("---")
st.subheader("🌿 Most Common Ingredients")
ingredients_text = ' '.join(filtered_df['ingredients'].dropna().tolist())
wordcloud = WordCloud(width=800, height=400, background_color='white').generate(ingredients_text)
fig2, ax2 = plt.subplots(figsize=(10, 4))
ax2.imshow(wordcloud, interpolation='bilinear')
ax2.axis("off")
st.pyplot(fig2)

# Block 5: Variate Analysis Tabs
st.markdown("---")
st.subheader("🔬 Variate Analysis")
tab1, tab2, tab3 = st.tabs(["Univariate", "Bivariate", "Multivariate"])

with tab1:
    st.markdown("### 📊 Univariate Analysis")
    st.subheader("Diet Distribution")
    st.bar_chart(filtered_df['diet'].value_counts())
    
    st.subheader("Course Distribution")
    st.bar_chart(filtered_df['course'].value_counts())
    
    st.subheader("Region Distribution")
    st.bar_chart(filtered_df['region'].value_counts())
    
    st.subheader("Flavor Profile Distribution")
    st.bar_chart(filtered_df['flavor_profile'].value_counts())

with tab2:
    st.markdown("### 🔄 Bivariate Analysis ")
    # Supported 3D Scatter Plot
    st.plotly_chart(
        px.scatter_3d(
            filtered_df,
            x='prep_time',
            y='cook_time',
            z='total_time',
            color='diet',
            title="3D Scatter: Prep vs Cook vs Total Time by Diet"
        )
    )

    # Grouped 2D Bar Chart (as alternative to 3D bar)
    bar_data = filtered_df.groupby(['region', 'course'])['name'].count().reset_index(name='count')
    st.plotly_chart(
        px.bar(bar_data, x='region', y='count', color='course', barmode='group',
               title="Bar Chart: Dishes by Region and Course")
    )

    # 2D Box Plot
    st.plotly_chart(
        px.box(filtered_df, x='course', y='prep_time', color='diet',
               title="Box Plot: Prep Time by Course and Diet")
    )

with tab3:
    st.markdown("### 🔁 Multivariate Analysis")
    
    st.subheader("📊 Heatmap: Recipes by Region and Course")
    heatmap_data = filtered_df.groupby(['region', 'course']).size().unstack().fillna(0)
    fig4, ax4 = plt.subplots(figsize=(10, 5))
    sns.heatmap(heatmap_data, annot=True, cmap="Blues", fmt=".0f", ax=ax4)
    st.pyplot(fig4)

    st.subheader("📈 Scatter Plot: Prep Time by Course and Diet")
    st.plotly_chart(px.scatter(filtered_df, x='course', y='prep_time', color='diet', title="Prep Time by Course and Diet"), key='scatter_course_prep')

    st.subheader("🎥 Animated Bar Chart: Dishes by State and Course")
    animated_data = filtered_df.groupby(['state', 'course'])['name'].count().reset_index(name='count')
    fig5 = px.bar(animated_data, x='state', y='count', color='course', animation_frame='course', title="Dishes by State and Course")
    st.plotly_chart(fig5)

# Block 6: Ingredient Recommender (Basic Text Search)
st.markdown("---")
st.subheader("🔎 Ingredient Search")
search_input = st.text_input("Enter an ingredient to find recipes:")
if search_input:
    result_df = filtered_df[filtered_df['ingredients'].str.contains(search_input, case=False, na=False)]
    st.success(f"Found {len(result_df)} recipes with '{search_input}'")
    st.dataframe(result_df[['name', 'ingredients', 'diet', 'prep_time', 'cook_time', 'course', 'state', 'region']])

# Block 6: Meal Planner Suggestion
st.markdown("---")
st.subheader("📅 Sample Meal Planner")
meal_plan = {}
for crs in ['snack', 'main course', 'dessert']:
    crs_df = filtered_df[filtered_df['course'].str.lower() == crs]
    if not crs_df.empty:
        meal_plan[crs.title()] = crs_df.sample(1)[['name', 'state']].values[0]
if meal_plan:
    for course_name, (dish_name, state_name) in meal_plan.items():
        st.info(f"**{course_name}:** {dish_name} (_{state_name}_) 🥄")
else:
    st.warning("Not enough data for meal plan with current filters.")

# Block 7: Animated Graph - Top Dishes by Region & Course
st.markdown("---")
st.subheader("🎥 Animated Bar Chart: Top Dishes by Region & Course")
top_dishes = filtered_df.groupby(['region', 'course'])['name'].count().reset_index(name='count')
fig3 = px.bar(top_dishes,
             x='region',
             y='count',
             color='region',
             animation_frame='course',
             title='Top Dishes by Region and Course',
             labels={'count': 'Dish Count', 'region': 'Region', 'course': 'Course'})
fig3.update_layout(yaxis={'categoryorder':'total ascending'})
st.plotly_chart(fig3)

# Block 9: Show Filtered Data Table
st.markdown("---")
st.subheader("📋  Recipes Table")
st.dataframe(filtered_df[['name', 'ingredients', 'diet', 'prep_time', 'cook_time', 'course', 'state', 'region']])
           