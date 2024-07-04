# Libraries
import streamlit as st
import pandas as pd
from PIL import Image
import plotly.graph_objs as go
import plotly.express as px
import base64

# PAGE CONFIG
st.set_page_config(
    page_title='STTB-monitoring-demo-dash',
    page_icon='✅',
    layout='wide'
)

# Font
st.markdown("""
<style>
.custom-title {
    font-family: 'Abjad', 'Arial', sans-serif !important;
    font-size: 32px !important;
    font-weight: bold !important;
    color: #0066cc !important;
    text-align: right !important;
}

/* New styles for the expander */
.streamlit-expanderHeader {
    background-color: white !important;
    color: #0066cc !important;
    font-weight: bold !important;
}
.streamlit-expanderContent {
    background-color: white !important;
    color: #0066cc !important;
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
with st.sidebar:
    st.markdown(' خوش آمدید' )
    home = st.button("  🏠 خانه ")
    dashboard = st.button("📊 داشبورد")
    settings = st.button("⚙️ تنظیمات")

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
    st.image(logo, width=200)  

with col2:
    st.markdown('<p class="custom-title">مانیتورینگ هوشمند شرکت سـولار تابش توان بین الملل</p>', unsafe_allow_html=True)

def get_column_name(variable, number=None, inverter=None):
    if variable in ['Iac', 'Ipv']:
        return f'{variable}{number}(A)_inv_{inverter}'
    elif variable in ['Uac', 'Upv']:
        return f'{variable}{number}(V)_inv_{inverter}'
    elif variable in ['Pac', 'Pdc']:
        return f'{variable}(kW)_inv_{inverter}'
    else: # Eac
        return f'{variable}(kWh)_inv_{inverter}'

plot_variables = ['Pdc', 'Pac', 'Iac', 'Ipv', 'Uac', 'Upv', 'Eac']

# Create plot
def create_plot(variable, selected_date, selected_inverter, selected_number=None):
    if variable in ['Iac', 'Ipv', 'Uac', 'Upv']:
        column_name = get_column_name(variable, selected_number, selected_inverter)
    else:
        column_name = get_column_name(variable, inverter=selected_inverter)
    
    day_df = df[df['Date'] == selected_date]
    
    if column_name in day_df.columns:
        fig = go.Figure()
        fig.add_trace(
            go.Scatter(x=day_df['Hours'], y=day_df[column_name], name=f'{variable} (Inverter {selected_inverter})')
        )
        fig.update_layout(
            title=f'{variable} (Inv {selected_inverter})' + (f' - {variable}{selected_number}' if selected_number else ''),
            xaxis_title="Hour",
            yaxis_title=variable,
            height=400,
            margin=dict(l=50, r=50, t=50, b=50),
        )
        return fig
    else:
        return None

# Create settings
def create_settings(variable, key_prefix):
    with st.expander(f"{variable} تنظیمات", expanded=False):
        st.markdown('<style>div[data-testid="stExpander"] div[role="button"] p {color: #0066cc;}</style>', unsafe_allow_html=True)
        selected_date = st.date_input('تاریخ', min_value=dates.min(), max_value=dates.max(), value=dates[0], key=f'{key_prefix}_date')
        selected_inverter = st.selectbox(f'شماره اینورتر', range(1, 7), key=f'{key_prefix}_inverter')
        if variable in ['Iac', 'Ipv', 'Uac', 'Upv', 'AC P-V', 'DC P-V']:
            num_options = 3 if variable in ['Iac', 'Uac', 'AC P-V'] else 4
            selected_number = st.selectbox(f'{variable.split()[-1] if "V" in variable else variable} شماره', 
                                           range(1, num_options + 1), 
                                           key=f'{key_prefix}_شماره')
        else:
            selected_number = None
    return selected_date, selected_inverter, selected_number

# Create plots for a section
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

# Create sections with their respective plots
create_section_plots("توان", ['Pdc', 'Pac'])
create_section_plots("جریان", ['Iac', 'Ipv'])
create_section_plots("ولتاژ", ['Uac', 'Upv'])
create_section_plots("انرژی", ['Eac'])

def create_pv_plot(variable, selected_date, selected_inverter, selected_number):
    if variable == 'AC P-V':
        power_var, voltage_var = 'Pac', 'Uac'
    else:  # DC P-V
        power_var, voltage_var = 'Pdc', 'Upv'
    
    power_col = get_column_name(power_var, inverter=selected_inverter)
    voltage_col = get_column_name(voltage_var, number=selected_number, inverter=selected_inverter)
    
    day_df = df[df['Date'] == selected_date]
    
    if power_col in day_df.columns and voltage_col in day_df.columns:
        fig = px.line(day_df, x=voltage_col, y=power_col,
                         title=f'{variable} (Inv {selected_inverter}, {voltage_var}{selected_number})')
        
        fig.update_layout(
            xaxis_title=f"{voltage_var} (V)",
            yaxis_title=f"{power_var} (kW)",
            height=400,
            margin=dict(l=50, r=50, t=50, b=50),
            legend_title_text='Legend'
        )
        
        fig.update_traces(name=f'Inverter {selected_inverter}')
        
        return fig
    else:
        return None

st.header("توان - ولتاژ")
pv_cols = st.columns(2)
for i, pv_var in enumerate(['AC P-V', 'DC P-V']):
    with pv_cols[i]:
        selected_date, selected_inverter, selected_number = create_settings(pv_var, f'plot_{pv_var}')
        fig = create_pv_plot(pv_var, selected_date, selected_inverter, selected_number)
        if fig:
            st.plotly_chart(fig, use_container_width=True)
        else:
            st.warning(f"No data available for {pv_var}")

# Data information
if st.checkbox("### نمایش دیتا",key="show_data"):
   st.dataframe(df)  

# About Us section
if st.checkbox("**ABOUT US**",key="about_us"):
    st.markdown("""
    Solar Tabesh Tavan BNL (STTB) Company was founded in 2014.
    STTB is a renewables technology and knowledge-based company 
    with specialized expertise in solar and wind energy, research 
    and development (R&D) management. STTB have a close cooperation 
    with the best research institutes like Fraunhofer & VDE ,
    universities, suppliers, laboratories in Germany, UK, Italy, Denmark and Switzerland.
    """)