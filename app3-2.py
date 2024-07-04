#libs
import streamlit as st
import pandas as pd
import plotly.graph_objs as go
from plotly.subplots import make_subplots

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
st.title('مانیتورنگ اینورتر- دمو')

# Date selection 
dates = df['Date'].unique()
selected_date = st.date_input('Select Date', min_value=dates.min(), max_value=dates.max(), value=dates[0])
day_df = df[df['Date'] == selected_date]

def get_column_name(variable, number=None, inverter=None):
    if variable in ['Iac', 'Ipv']:
        return f'{variable}{number}(A)_inv_{inverter}'
    elif variable in ['Uac', 'Upv']:
        return f'{variable}{number}(V)_inv_{inverter}'
    elif variable in ['Pac', 'Pdc']:
        return f'{variable}(kW)_inv_{inverter}'
    
    else:  # Eac
        return f'{variable}(kWh)_inv_{inverter}'

#  subplots with 7 rows and 1 column
fig = make_subplots(rows=7, cols=1, subplot_titles=['Pdc', 'Pac', 'Iac', 'Ipv', 'Uac', 'Upv', 'Eac'], 
                    vertical_spacing=0.05)

plot_variables = ['Pdc', 'Pac', 'Iac', 'Ipv', 'Uac', 'Upv', 'Eac']

# Create two columns: one for plots and one for settings
plot_col, settings_col = st.columns([3, 1])

with settings_col:
    st.subheader("تنظیمات")
    for plot, variable in enumerate(plot_variables, 1):
        st.markdown(f"**{variable} Settings**")
        selected_inverter = st.selectbox(f'Inverter for {variable}', range(1, 7), key=f'inverter_{plot}')
        if variable in ['Iac', 'Ipv', 'Uac', 'Upv',]:
            num_options = 3 if variable in ['Iac', 'Uac'] else 4
            selected_number = st.selectbox(f'{variable} number', range(1, num_options + 1), key=f'number_{plot}')
            column_name = get_column_name(variable, selected_number, selected_inverter)
        else:
            column_name = get_column_name(variable, inverter=selected_inverter)
        
        if column_name not in day_df.columns:
            st.warning(f"Column '{column_name}' not found for {variable}")

with plot_col:
    for plot, variable in enumerate(plot_variables, 1):
        selected_inverter = st.session_state[f'inverter_{plot}']
        if variable in ['Iac', 'Ipv', 'Uac', 'Upv']:
            selected_number = st.session_state[f'number_{plot}']
            column_name = get_column_name(variable, selected_number, selected_inverter)
        else:
            column_name = get_column_name(variable, inverter=selected_inverter)
        
        if column_name in day_df.columns:
            fig.add_trace(
                go.Scatter(x=day_df['Hours'], y=day_df[column_name], name=f'{variable} (Inverter {selected_inverter})'),
                row=plot, col=1
            )
            fig.update_xaxes(title_text="Hour", row=plot, col=1)
            fig.update_yaxes(title_text=variable, row=plot, col=1)
            
            # subplot title
            subplot_title = f'{variable} (Inv {selected_inverter})'
            if variable in ['Iac', 'Ipv', 'Uac', 'Upv']:
                subplot_title += f' - {variable}{selected_number}'
            fig.layout.annotations[plot-1].update(text=subplot_title)

    # layout
    fig.update_layout(
    height=1400,  
    title_text=f'Inverter Data for {selected_date}',
    showlegend=True,
    autosize=True,
    margin=dict(l=50, r=50, t=100, b=50),
    hovermode="closest",
    )
    fig.update_layout(
    {f"xaxis{i + 1}": dict(title="Hour", domain=[0.05, 0.95]) for i in range(7)}
)
    fig.update_layout(
    {f"yaxis{i + 1}": dict(title=var, anchor="x", automargin=True) for i, var in enumerate(plot_variables)}

)
    for i, annotation in enumerate(fig['layout']['annotations'][:7]):
        annotation['y'] = 1 - (i * 1/7) 
        annotation['x'] = 0.5
        annotation['xanchor'] = 'center'
        annotation['yanchor'] = 'bottom'

    st.plotly_chart(fig, use_container_width=True)

# Debug information
#if st.checkbox("Show debug information"):
   # st.write(f"Number of rows for selected date: {len(day_df)}")
    #st.write("All column names:")
    #st.write(day_df.columns.tolist())