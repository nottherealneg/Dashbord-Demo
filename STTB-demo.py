# Libraries
import streamlit as st
import pandas as pd
from PIL import Image
import plotly.graph_objs as go
import plotly.express as px
import base64

# PAGE CONFIG
st.set_page_config(
    page_title="STTB Monitoring",
    page_icon='✅',
    layout='wide',
    initial_sidebar_state='expanded')

st.markdown("""
<style>
.custom-title {
    font-family: 'Abjad', 'Arial', sans-serif !important;
    font-size: 40px !important;
    font-weight: bold !important;
    color: YlGn !important;
    text-align: center !important;
}
</style>
""", unsafe_allow_html=True)

# Add background
def bg(image_file):
    with open(image_file, "rb") as image_file:
        encoded_string = base64.b64encode(image_file.read())
    st.markdown(
    f"""
    <style>
    .stApp {{
        background-image: url(data:image/{"png"};base64,{encoded_string.decode()});
        background-size: cover;
    }}
    </style>
    """,
    unsafe_allow_html=True
    )

bg('bg4.jpg')  

# Sidebar
st.markdown("""
<style>
    [data-testid="stSidebar"][aria-expanded="true"] > div:first-child {
        width: 200px;
    }
    [data-testid="stSidebar"][aria-expanded="false"] > div:first-child {
        width:200px;
        margin-left: -350px;
    }
</style>
""", unsafe_allow_html=True)

# Initialize session state variables
if 'logged_in' not in st.session_state:
    st.session_state.logged_in = False

def login():
    st.session_state.logged_in = True

def logout():
    st.session_state.logged_in = False

# Sidebar
with st.sidebar:
    st.markdown("#  خوش آمدید")
    if not st.session_state.logged_in:
        st.markdown(' ورود به سیستم')
        username = st.text_input('نام کاربری')
        password = st.text_input('رمز عبور', type='password')
        if st.button('ورود'):
            # authentication
            if username == 'admin' and password == 'password':
                login()
                st.experimental_rerun()
            else:
                st.error('نام کاربری یا رمز عبور اشتباه است')
    else:
        st.markdown(f'کاربر: {username}')
        if st.button('خروج'):
            logout()
            st.experimental_rerun()
    
    home = st.button("  🏠 خانه ")
    dashboard = st.button("📊 داشبورد")
    settings = st.button("⚙️ تنظیمات")

# Main content
if st.session_state.logged_in:
    st.write('شما وارد شده‌اید. محتوای اصلی اینجا نمایش داده می‌شود.')
else:
    st.write('← لطفا برای دسترسی به محتوا وارد شوید')

# Chatbot
prompt = st.chat_input("سلام،چه طور میتونم کمکتون کنم ؟ : 🤖")
if prompt:
    st.write(f"کاربر میهمان: {prompt}")

# Load data
@st.cache_data
def load_data():
    df = pd.read_excel('Dash2.xlsx')
    df = df.dropna(axis=1, how='all')
    df['TIMESTAMP'] = pd.to_datetime(df['TIMESTAMP'])
    df['Date'] = df['TIMESTAMP'].dt.date
    df['Hours'] = df['TIMESTAMP'].dt.hour + df['TIMESTAMP'].dt.minute / 60
    return df

df = load_data()
dates = df['Date'].unique()

# Add logo
logo = Image.open('logo.png')
col1, col2 = st.columns([1, 3]) 

with col1:
    st.image(logo, width=300)  

with col2:
    st.markdown('<p class="custom-title">مانیتورینگ هوشمند شرکت سـولار تابش توان بین الملل</p>', unsafe_allow_html=True) 

plot_variables = ['Pdc', 'Pac', 'Iac', 'Ipv', 'Uac', 'Upv', 'Eac', 'Eac Total', 'InvEfficient']

def get_column_name(variable, number=None, inverter=None):
    if variable in ['Iac', 'Ipv', 'Uac', 'Upv']:
        return f'{variable}{number}({get_unit(variable)})_inv_{inverter}'
    elif variable in ['Pac', 'Pdc']:
        return f'{variable}(kW)_inv_{inverter}'
    elif variable == 'Eac':
        return f'{variable}(kWh)_inv_{inverter}'
    elif variable == 'Eac Total':
        return f'{variable}(kWh)_inv_{inverter}'
    elif variable == 'InvEfficient':
        return f'{variable}(%)_inv_{inverter}'
    else:
        return f'{variable}_inv_{inverter}'

def get_unit(variable):
    if variable in ['Iac', 'Ipv']:
        return 'A'
    elif variable in ['Uac', 'Upv']:
        return 'V'
    else:
        return ''

def calculate_daily_peak_power(df, date, inverter):
    day_df = df[(df['Date'] == date) & (df[f'Pac(kW)_inv_{inverter}'].notna())]
    return day_df[f'Pac(kW)_inv_{inverter}'].max() if not day_df.empty else 0

def calculate_capacity_utilization(df, date, inverter, rated_capacity):
    day_df = df[(df['Date'] == date) & (df[f'Pac(kW)_inv_{inverter}'].notna())]
    avg_pac = day_df[f'Pac(kW)_inv_{inverter}'].mean() if not day_df.empty else 0
    return (avg_pac / rated_capacity) * 100 if rated_capacity > 0 else 0

def calculate_energy_yield(df, date, inverter):
    day_df = df[(df['Date'] == date) & (df[f'Eac(kWh)_inv_{inverter}'].notna())]
    return day_df[f'Eac(kWh)_inv_{inverter}'].max() if not day_df.empty else 0

# KPI Section
st.header("شاخص های کلیدی عملکرد", divider='rainbow')
kpi_date = st.date_input('انتخاب تاریخ جهت محاسبه شاخص ها', min_value=dates.min(), max_value=dates.max(), value=dates[0])

col1, col2, col3 = st.columns(3)
with col1:
    st.subheader("حداکثر توان روزانه")
    peak_power = max(calculate_daily_peak_power(df, kpi_date, i) for i in range(1, 7))
    st.metric("Peak Power", f"{peak_power:.2f} kW")

with col2:
    st.subheader("متوسط بهره برداری از ظرفیت")
    rated_capacity = 80  # Assuming 80kW rated capacity for each inverter
    avg_utilization = sum(calculate_capacity_utilization(df, kpi_date, i, rated_capacity) for i in range(1, 7)) / 6
    st.metric("Avg Utilization", f"{avg_utilization:.2f}%")

with col3:
    st.subheader(" تولید انرژی کل")
    energy_yields = [calculate_energy_yield(df, kpi_date, i) for i in range(1, 7)]
    total_energy = sum(energy_yields)
    st.metric("Total Energy", f"{total_energy:.2f} kWh")

########

st.markdown("مقایسه تولید انرژی بین اینورترها")

energy_yields = [calculate_energy_yield(df, kpi_date, i) for i in range(1, 7)]
colors = px.colors.sequential.YlGn
color_scale = [colors[i] for i in range(0, len(colors), len(colors)//6)][:6]

# the horizontal bar chart
fig = go.Figure()

for i, yield_value in enumerate(energy_yields):
    fig.add_trace(go.Bar(
        y=[f"Inverter {i+1}"],
        x=[yield_value],
        orientation='h',
        marker=dict(color=color_scale[i]),
        name=f"Inverter {i+1}"
    ))

fig.update_layout(
    title="Energy Yield Comparison",
    xaxis_title="Energy Yield (kWh)",
    yaxis_title="Inverters",
    height=400,
    barmode='stack',
    showlegend=False,
    xaxis=dict(range=[0, max(energy_yields) * 1.1])  
)

#labels
for i, yield_value in enumerate(energy_yields):
    fig.add_annotation(
        x=yield_value,
        y=i,
        text=f"{yield_value:.2f} kWh",
        showarrow=False,
        xanchor='left',
        xshift=10,
        font=dict(color="white")
    )

st.plotly_chart(fig, use_container_width=True)
###################

def calculate_avg_eac_total(df, selected_date):

    day_df = df[df['Date'] == selected_date]
    avg_eac_total = []
    for inverter in range(1, 7):
        column_name = f'Eac Total(kWh)_inv_{inverter}'
        avg = day_df[column_name].mean() if column_name in day_df.columns else 0
        avg_eac_total.append(avg)
    return avg_eac_total

#############

def create_plot(variable, selected_date, selected_inverter, selected_number=None):

    if variable == 'Eac Total' and selected_date:
        avg_eac_total = calculate_avg_eac_total(df, selected_date)
        fig = go.Figure(go.Scatter(
            x=list(range(1, 7)),
            y=avg_eac_total,
            mode='lines+markers',
            name='Avg Eac Total'
        ))
        fig.update_layout(
            title=f'Average Eac Total for {selected_date}',
            xaxis_title="اینورتر",
            yaxis_title=" (kWh) میانگین انرژی کل ",
            xaxis=dict(tickmode='linear', tick0=1, dtick=1),
            height=400,
            margin=dict(l=50, r=50, t=50, b=50),
        )
        return fig
    
    if variable in ['Iac', 'Ipv', 'Uac', 'Upv']:
        column_name = get_column_name(variable, selected_number, selected_inverter)
    else:
        column_name = get_column_name(variable, inverter=selected_inverter)
    
    day_df = df[df['Date'] == selected_date]
    
    if column_name in day_df.columns:
        if variable == 'InvEfficient':
            efficiency = day_df[column_name].mean()
            fig = go.Figure(go.Indicator(
                mode = "gauge+number",
                value = efficiency,
                domain = {'x': [0, 1], 'y': [0, 1]},
                title = {'text': f"بازده میانگین   اینورتر {selected_inverter}"},
                gauge = {
                    'axis': {'range': [None, 100]},
                    'bar': {'color': "darkblue"},
                    'steps' : [
                        {'range': [0, 50], 'color': "lightgray"},
                        {'range': [50, 80], 'color': "gray"},
                        {'range': [80, 100], 'color': "lightblue"}],
                    'threshold' : {'line': {'color': "red", 'width': 4}, 'thickness': 0.75, 'value': 90}}))
            fig.update_layout(height=400)
        elif variable in ['Eac', 'Eac Total']:
            fig = go.Figure(go.Scatter(x=day_df['Hours'], y=day_df[column_name], name=f'{variable} (Inverter {selected_inverter})'))
        else:
            fig = go.Figure(go.Scatter(x=day_df['Hours'], y=day_df[column_name], name=f'{variable} (Inverter {selected_inverter})'))
        
        y_axis_titles = {
            'Iac': "(A) AC جریان ",
            'Pdc': "(kW) DC توان ",
            'Pac': "(kW) AC توان",
            'Ipv': "(A) DC جریان ",
            'Uac': "(V) AC ولتاژ ",
            'Upv': "(V) DC ولتاژ ",
            'Eac': '(kWh)انرژی ',
            'Eac Total': '(kWh)کل انرژی ',
            'InvEfficient': '(%)کارایی اینورتر '
        }
        
        y_axis_title = y_axis_titles.get(variable, variable)  
        
        if variable != 'InvEfficient':
            fig.update_layout(
                title=f'inverter {selected_inverter}' + (f' - {variable}{selected_number}' if selected_number else ''),
                xaxis_title="زمان",
                yaxis_title=y_axis_title,
                height=400,
                margin=dict(l=50, r=50, t=50, b=50),
            )
        return fig
    else:
        return None

########
def create_settings(variable, key_prefix):
    with st.expander(f" تنظیمات ⚙️", expanded=False):
        st.markdown('<style>div[data-testid="stExpander"] div[role="button"] p {color: #0066cc;}</style>', unsafe_allow_html=True)
        selected_date = st.date_input('تاریخ', min_value=dates.min(), max_value=dates.max(), value=dates[0], key=f'{key_prefix}_date')
        
        if variable != 'Eac Total':
            selected_inverter = st.selectbox(f'شماره اینورتر', range(1, 7), key=f'{key_prefix}_inverter')
            if variable in ['Iac', 'Ipv', 'Uac', 'Upv']:
                num_options = 3 if variable in ['Iac', 'Uac'] else 4
                selected_number = st.selectbox(f'{variable.split()[-1] if "V" in variable else variable} شماره', 
                                               range(1, num_options + 1), 
                                               key=f'{key_prefix}_شماره')
            else:
                selected_number = None
        else:
            selected_inverter = None
            selected_number = None
        
    return selected_date, selected_inverter, selected_number

#######
def create_section_plots(header, variables):
    st.header(header)
    cols = st.columns(len(variables))
    for i, variable in enumerate(variables):
        with cols[i]:
            selected_date, selected_inverter, selected_number = create_settings(variable, f'plot_{variable}')
            fig = create_plot(variable, selected_date, selected_inverter, selected_number)
            if fig:
                st.plotly_chart(fig, use_container_width=True)
            else:
                st.warning(f"No data available for {variable}")

create_section_plots("بازده" , ['InvEfficient'])
create_section_plots("انرژی ", ['Eac', 'Eac Total'])
create_section_plots("توان", ['Pdc', 'Pac'])
create_section_plots("جریان", ['Iac', 'Ipv'])
create_section_plots("ولتاژ", ['Uac', 'Upv'])

# Data information
if st.checkbox("**نمایش دیتا**"):
   st.dataframe(df)  

# About Us section
if st.checkbox("**درباره ما**"):
    st.markdown("""
    Solar Tabesh Tavan BNL (STTB) Company was founded in 2014.
    STTB is a renewables technology and knowledge-based company 
    with specialized expertise in solar and wind energy, research 
    and development (R&D) management. STTB have a close cooperation 
    with the best research institutes like Fraunhofer & VDE ,
    universities, suppliers, laboratories in Germany, UK, Italy, Denmark and Switzerland.
    """)

# contact Us section
if st.checkbox("**تماس با ما**"):
    st.markdown("""
     **📧** info@solarttb.com
    """)
