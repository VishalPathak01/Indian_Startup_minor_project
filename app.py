import pandas as pd 
import numpy as np 
import streamlit as st 
import seaborn as sns 
import matplotlib.pyplot as plt 
from collections import Counter

df = pd.read_csv('startup_cleaned.csv')
df['Date'] = pd.to_datetime(df['Date'], errors='coerce')
df['year'] = df['Date'].dt.year
df['month'] = df['Date'].dt.month
st.set_page_config(layout='wide', page_title='Indian Start UP Analysis')
plt.style.use('seaborn-v0_8-whitegrid')
if 'page' not in st.session_state:
    st.session_state.page = 'Home'

def load_startup(selected_start_up):
    st.title(selected_start_up)
    start_up_df = df[df['Start Up'] == selected_start_up]
    r1c1, r1c2, r1c3 = st.columns([4, 4, 2])
    vertical = start_up_df['Vertical'].mode()[0]   
    sub_vertical = start_up_df['SubVertical'].mode()[0]
    city = start_up_df['City'].mode()[0]
    Round = start_up_df['Round'].mode()[0]
    with r1c1:
        st.metric("Sector", vertical)
    with r1c2:
        st.metric("Sub Sector", sub_vertical)
    with r1c3:
        st.metric('Location', city)
    
    st.subheader("Investors ")
    r2c1, r2c2 = st.columns(2)
    Investors = start_up_df['Investors'].str.strip().str.split(", ").explode().value_counts().reset_index().rename(columns={
        "count" : "No of times Invested"
    })
    with r2c1:
        st.dataframe(Investors)
    with r2c2:
        fig, ax = plt.subplots(figsize=(5, 5))
        ax.pie(Investors['No of times Invested'], labels=Investors['Investors'], autopct='%0.01f%%')
        st.pyplot(fig)
    
    st.subheader("Investment History")
    year = st.selectbox('Choose Year', ['Overall'] + sorted(start_up_df['year'].dropna().unique().astype(str).tolist()))
    if year == 'Overall':
        temp_df = start_up_df.copy()
    else:
        temp_df = start_up_df[start_up_df['year'] == int(year)]

    r3c3, r3c4 = st.columns(2)
    with r3c3:
        st.dataframe(temp_df[['Date', 'Round', 'Amount']])
    with r3c4:
        fig2, ax2 = plt.subplots(figsize=(8, 8))
        scatter = ax2.scatter(temp_df['Round'], temp_df['Amount'], c=temp_df['year'], cmap='YlOrRd', s=200)
        fig2.colorbar(scatter, label='Year')
        ax2.set_xlabel("Round")
        ax2.set_ylabel("Amount (INR cr)")
        ax2.spines['top'].set_visible(False)
        ax2.spines['right'].set_visible(False)
        st.pyplot(fig2)
        
    similar_startups = df[~(df['Start Up'] == selected_start_up)]
    similar_startups = similar_startups.groupby('Start Up').agg({
        'Vertical':lambda x: x.mode()[0],
        'SubVertical': lambda x: x.mode()[0],
        'Round': lambda x: x.mode()[0],
        'City': lambda x: x.mode()[0] 
    })
    similar_startups['Score'] = (
        (similar_startups['Vertical'] == vertical).astype(int) +
        (similar_startups['SubVertical'] == sub_vertical).astype(int) +
        (similar_startups['City'] == city).astype(int) + 
        (similar_startups['Round'] == Round).astype(int)
    )
    similar_startups = similar_startups.sort_values(by='Score', ascending=False).head(3).reset_index()['Start Up']
    
    r6col1, r6col2 = st.columns([10, 1])
    with r6col1:
        st.subheader('See Similar Startups:  ')
        st.write(f'Most Similar Start Up:  {similar_startups.iloc[0]}')
        st.write(f'Second Most Similar Start Up:  {similar_startups.iloc[1]}')
        st.write(f'Third Most Similar Start Up:  {similar_startups.iloc[2]}')
    with r6col2:
        go_button1 = st.button(' GO1 ==>')
        go_button2 = st.button(' GO2 ==>')
        go_button3 = st.button(' GO3 ==>')
        
    if go_button1:
        st.session_state.page = f'Startup_{similar_startups.iloc[0]}'
    elif go_button2:
        st.session_state.page = f'Startup_{similar_startups.iloc[1]}'
    elif go_button3:
        st.session_state.page = f'Startup_{similar_startups.iloc[2]}'
    
def load_overall():
    r1c1, r1c2, r1c3, r1c4 = st.columns(4)
    
    # total funding for indian startups 
    with r1c1:
        total_funding_in_startup = np.round(df['Amount'].sum(), 2)
        st.metric("Total Funding ", str(total_funding_in_startup), 'Cr')
        
    # maximum total funding on a startup  
    with r1c2:
        max_funding_in_startup = np.round(df.groupby('Start Up')['Amount'].sum().max(), 2)
        st.metric("Maximum Funding ", str(max_funding_in_startup), 'Cr')
        
    # average funding of startups
    with r1c3:
        avg_funding_in_startup = np.round(df.groupby('Start Up')['Amount'].sum().mean(), 2)
        st.metric("Average Funding ", str(avg_funding_in_startup), 'Cr')
    
    # total number of startups funded
    with r1c4:
        no_of_startups = df['Start Up'].nunique()
        st.metric("No of Startups Funded ", str(no_of_startups), ' .')
    
    # Mom Chart DataFrame Creation
    mom_total_funding = df.groupby(['year', 'month'])['Amount'].sum().reset_index()
    mom_no_of_startups = df.groupby(['year', 'month'])['Start Up'].count().reset_index()
    mom_total_funding['x_axis'] = mom_total_funding['year'].astype(str) + '/' + mom_total_funding['month'].astype(str)  
    mom_no_of_startups['x_axis'] = mom_no_of_startups['year'].astype(str) + '/' + mom_no_of_startups['month'].astype(str)

    # renaming useful columns and dropping optional columns
    mom_no_of_startups.drop(columns=['year', 'month'], inplace=True)    
    mom_no_of_startups.rename(columns={'Start Up': 'y_axis'}, inplace=True)
    mom_total_funding.drop(columns=['year', 'month'], inplace=True)
    mom_total_funding.rename(columns={'Amount': 'y_axis'}, inplace=True)
    
    # mom section 
    st.subheader("Month over Month Funding Trend (Amount & Deal Count)")
    opt = st.selectbox('Tip: To view the full image click at the square button, present at top-right corner of image', ['Amount', 'Count'])
    
    if opt == 'Amount':
        fig, ax = plt.subplots(figsize=(25,8))
        ax.plot(mom_total_funding['x_axis'], mom_total_funding['y_axis'], color='black')
        ax.tick_params(axis='x', rotation=-55)
        st.pyplot(fig)
    elif opt == 'Count':
        fig2, ax2 = plt.subplots(figsize=(25,8))
        ax2.plot(mom_no_of_startups['x_axis'], mom_no_of_startups['y_axis'], color='black')
        ax2.tick_params(axis='x', rotation=-55)
        st.pyplot(fig2)
    
    # top startups section
    st.subheader("Top Startups(Overall & Year-Wise)")
    year_opt = st.selectbox('Choose any year to look for',['Overall'] + sorted(df['year'].dropna().unique().astype(str).tolist()))
    if year_opt == 'Overall':
        temp_df = df.copy()   
    else:
        temp_df = df[df['year'] == int(year_opt)]
    
    startups = temp_df.groupby(['Start Up'])['Amount'].sum().sort_values(ascending=False).head(10)
    fig5, ax5 = plt.subplots(figsize=(17, 5))
    ax5.bar(startups.index,startups.values, color='#E63946')
    ax5.set_xlabel('Startups')
    ax5.set_ylabel('Funding Amount')
    st.pyplot(fig5)     

    # top sectors by deal funding section 
    st.subheader("Top 10 Funding Rounds by Total Amount - Log Scale")
    type_of_funding = np.round(df.groupby("Round")['Amount'].sum().sort_values(ascending=False), 2)
    type_of_funding = type_of_funding[type_of_funding > 0]  
    # Figure
    fig3, ax3 = plt.subplots(figsize=(17, 5))
    ax3.bar(type_of_funding.index[:10], type_of_funding.values[:10], log=True, color='#E63946')
    ax3.set_xlabel('Funding Round')
    ax3.set_ylabel('Funding Amount (INR crores)')
    ax3.tick_params(axis='x', rotation=0)
    st.pyplot(fig3)
    

    # city wise funding section
    st.subheader("Top 10 Cities by Total Funding - Log Scale ")
    city_funding = np.round(df.groupby("City")['Amount'].sum().sort_values(ascending=False), 2)
    city_funding = city_funding[city_funding > 0] 
    # Figure
    fig4, ax4 = plt.subplots(figsize=(17, 5))
    ax4.bar(city_funding.index[:10], city_funding.values[:10], log=True , color='#E63946')
    ax4.set_xlabel('Cities')
    ax4.set_ylabel('Funding Amount (INR crores)')
    ax4.tick_params(axis='x', rotation=0)
    st.pyplot(fig4)       
    
    # Heatmap section 
    st.subheader(f"Heatmap({int(df['year'].min())} - {int(df['year'].max())}) of Sector Wise Funding ")
    top_sector_df = df.groupby(['Vertical'])['Amount'].sum().sort_values(ascending=False).head(10)
    top_sector_df = df[df['Vertical'].isin(top_sector_df.index)]
    sector_year_funding = top_sector_df.pivot_table(index='Vertical', columns='year', values='Amount', aggfunc='sum').fillna(0)
    
    with plt.style.context('default'):
        fig7, ax7 = plt.subplots(figsize=(12, 6))
        im = ax7.imshow(sector_year_funding, cmap='YlOrRd', aspect='auto')

        for i in range(len(sector_year_funding.index)):
            for j in range(len(sector_year_funding.columns)):
                ax7.text(j, i, f'{sector_year_funding.iloc[i, j]:0.0f}', 
                        ha='center', va='center', fontsize=8)
                
        ax7.set_xticks(range(len(sector_year_funding.columns)))
        ax7.set_xticklabels(sector_year_funding.columns)  
        ax7.set_yticks(range(len(sector_year_funding.index)))
        ax7.set_yticklabels(sector_year_funding.index)        
        
        fig7.colorbar(im, ax=ax7, label='Amount (INR cr)')
        ax7.set_xlabel("Year")
        ax7.set_ylabel("Sector")
        st.pyplot(fig7)

    # Top Investors
    investor_df = df['Investors'].str.strip().str.split(", ").explode().dropna()
    investor_df = investor_df.value_counts().head(5).reset_index().rename(columns={"count":"Total Investments"})
    st.subheader("Top 5 Investors by Deal Count")
    st.table(investor_df)


def load_investors(selected_investors):
    st.title(selected_investors)
    st.subheader('Recent Investments')
    
    # recent 5 investments
    investor_df = df[df['Investors'].str.contains(selected_investors, na=False)]
    st.dataframe(investor_df.head(5)[['Date', 'Start Up', 'Vertical', 'City', 'Round', 'Amount']])
    
    #top 5 investments overall 
    r1col1, r1col2 = st.columns(2)
    with r1col1:
        st.subheader('Biggest Investments (TOP 10)')
        biggest_investments = np.round(investor_df.groupby('Start Up')['Amount'].sum().sort_values(ascending=False).head(10), 2)
        st.dataframe(biggest_investments)
    with r1col2 :
        fig, ax = plt.subplots(figsize=(10,10))
        ax.bar(biggest_investments.index, biggest_investments.values, log=True, color="#E63946") 
        ax.set_xticks(range(len(biggest_investments.index)))
        ax.set_xticklabels(biggest_investments.index, rotation=25)
        st.pyplot(fig)
        
    # Sector Investments 
    r2col1, r2col2 = st.columns(2)
    with r2col1:
        st.subheader('Sector Wise Investments (TOP 10 Only)')
        st.markdown("<p style='font-size:13px'> To ensure readability sections having percentage less than 1% are dropped </p>", unsafe_allow_html=True)
        sector_wise_investments = np.round(investor_df.groupby('Vertical')['Amount'].sum().sort_values(ascending=False).head(10), 2)
        st.dataframe(sector_wise_investments)
    with r2col2:
        fig1, ax1 = plt.subplots(figsize=(8,12))
        mask = (((sector_wise_investments / sector_wise_investments.sum()) * 100) >= 1)
        sector_wise_investments = sector_wise_investments[mask]
        ax1.pie(sector_wise_investments.values, labels=sector_wise_investments.index, autopct='%0.01f%%')
        ax1.set_aspect(1.2)
        st.pyplot(fig1)


    # Round Investments
    r3col1, r3col2 = st.columns(2)
    with r3col1:
        st.subheader('Stage Wise Investments (TOP 10 Only)')
        st.markdown("<p style='font-size:13px'> To ensure readability sections having percentage less than 1% are dropped </p>", unsafe_allow_html=True)
        stage_wise_investments = np.round(investor_df.groupby('Round')['Amount'].sum().sort_values(ascending=False).head(10), 2)
        st.dataframe(stage_wise_investments)
    with r3col2 :
        fig2, ax2 = plt.subplots(figsize=(9,12))
        mask = (((stage_wise_investments / stage_wise_investments.sum()) * 100) >= 1)
        stage_wise_investments = stage_wise_investments[mask]
        ax2.pie(stage_wise_investments.values, labels=stage_wise_investments.index, autopct='%0.01f%%')
        st.pyplot(fig2)

    # City Investments    
    r4col1, r4col2 = st.columns(2)
    with r4col1:
        st.subheader('City Wise Investments (TOP 10 Only)')
        st.markdown("<p style='font-size:13px'> To ensure readability sections having percentage less than 1% are dropped </p>", unsafe_allow_html=True)
        City_wise_investments = np.round(investor_df.groupby('City')['Amount'].sum().sort_values(ascending=False).head(10), 2)
        st.dataframe(City_wise_investments)
    with r4col2:
        fig3, ax3 = plt.subplots(figsize=(9,12))
        mask = (((City_wise_investments / City_wise_investments.sum()) * 100) >= 1)
        City_wise_investments = City_wise_investments[mask]
        ax3.pie(City_wise_investments.values, labels=City_wise_investments.index, autopct='%0.01f%%')
        st.pyplot(fig3)


    r5col1, r5col2 = st.columns(2)
    with r5col1:
        temp_df = df.copy()
        st.subheader('Year over Year Investment ')
        Year_wise_investments = temp_df[temp_df['Investors'].str.contains(selected_investors, na=False)].groupby('year')['Amount'].sum()
        st.dataframe(Year_wise_investments)
        
    with r5col2:
        fig4, ax4 = plt.subplots(figsize=(7,7))
        ax4.plot(Year_wise_investments.index, Year_wise_investments.values, color='black')
        ax4.set_xlabel("Year")
        ax4.set_ylabel("Amount (INR cr)")
        ax4.set_xticks(Year_wise_investments.index)
        ax4.set_xticklabels(Year_wise_investments.index)
        st.pyplot(fig4)

    r6col1, r6col2 = st.columns([10, 1])
    with r6col1:
        similar_investors = list(df[df['Investors'].str.contains(selected_investors, na=False)]['Investors'].str.strip().str.split(", ").sum())
        c = Counter(similar_investors)
        if selected_investors in c: c.pop(selected_investors)
        c = sorted(c.items(), key=lambda x: x[1], reverse=True)
        
        st.subheader('See Similar Investors:  ')
        st.write(f'Most Similar Investor:  {c[0][0]}')
        st.write(f'Second Most Similar Investor:  {c[1][0]}')
        st.write(f'Third Most Similar Investor:  {c[2][0]}')
    with r6col2:
        go_button1 = st.button(' GO1 ==>')
        go_button2 = st.button(' GO2 ==>')
        go_button3 = st.button(' GO3 ==>')
        
        if go_button1:
            st.session_state.page = f'Investor_{c[0][0]}'
        elif go_button2:
            st.session_state.page = f'Investor_{c[1][0]}'
        elif go_button3:
            st.session_state.page = f'Investor_{c[2][0]}'
        
     
side = st.sidebar
opt = side.selectbox('Choose Category', ['Overall Analysis', 'Startups', 'Investors'])
if opt == 'Overall Analysis':
    st.session_state.page = 'Overall Analysis'
    st.title("Indian Startup Overall Analysis")
    load_overall()
elif opt == 'Startups':
    # st.session_state.page = 'Start up'
    st.title("Startup Analysis")
    selected_start_up = side.selectbox('Startups', list(df['Start Up'].unique()))
    btn = side.button("Find Startup Details")

    if btn:
        st.session_state.page = f'Startup_{selected_start_up}'
    
    if st.session_state.page.startswith('Startup_'):
        startup_name = st.session_state.page.replace('Startup_', '')
        load_startup(startup_name)
elif opt=='Investors':
    # st.session_state.page = 'Investor'
    st.title('Investor analysis')
    selected_investors = side.selectbox('Investors', sorted(set(df['Investors'].str.split(", ").sum())))
    btn = side.button("Find Investors Details")
    
    if btn:
        st.session_state.page = f'Investor_{selected_investors}'
    
    if st.session_state.page.startswith('Investor_'):
        investor_name = st.session_state.page.replace('Investor_', '')
        load_investors(investor_name)
