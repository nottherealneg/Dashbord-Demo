# Solar PV Plant Monitoring Dashboard 🌤️

This project is a Streamlit-based monitoring dashboard for Solar Tabesh Tavan BNL (STTB) Company. It provides real-time visualization and analysis of solar power plant data, weather information, and key performance indicators.

## Features

- Interactive data visualization for solar power plant metrics
- Weather data analysis and display
- Key Performance Indicators (KPIs) calculation and presentation
- User authentication system
- Responsive design for various screen sizes

## Installation

1. Clone this repository:
   ```
   git clone https://github.com/yourusername/sttb-monitoring.git
   ```
2. Navigate to the project directory:
   ```
   cd sttb-monitoring
   ```
3. Install the required packages:
   ```
   pip install -r requirements.txt
   ```

## Usage

Run the Streamlit app:

```
streamlit run app.py
```

Then open your web browser and go to `http://localhost:8501`.

## Data Sources

The dashboard uses three main data sources:
- `Dash2.xlsx`: Contains inverter data
- `Data-weather2.xlsx`: Contains detailed weather data
- `Data-weather1.xlsx`: Contains additional weather information

Ensure these files are present in the project directory.

