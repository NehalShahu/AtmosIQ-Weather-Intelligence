
import requests
import pandas as pd
import plotly.graph_objects as go
import streamlit as st

st.set_page_config(
    page_title="AtmosIQ | Weather Intelligence",
    page_icon="🌦️",
    layout="wide",
)

st.markdown("""
<style>
.stApp {
    background: linear-gradient(135deg, #07111f, #102943);
    color: #e9f4ff;
}
[data-testid="stMetric"] {
    background: #122a40;
    border: 1px solid #284b66;
    border-radius: 16px;
    padding: 16px;
}
h1, h2, h3 { color: #83e1ef; }
</style>
""", unsafe_allow_html=True)

st.title("🌦️ AtmosIQ")
st.caption("WEATHER INTELLIGENCE • HISTORICAL CLIMATE ANALYTICS")

city = st.sidebar.text_input("Search city", "Nagpur")
years = st.sidebar.slider("Historical window (years)", 1, 10, 5)

def fetch_json(url, params):
    response = requests.get(url, params=params, timeout=30)
    response.raise_for_status()
    return response.json()

try:
    place_data = fetch_json(
        "https://geocoding-api.open-meteo.com/v1/search",
        {"name": city, "count": 1, "language": "en", "format": "json"}
    )

    if not place_data.get("results"):
        st.error("City not found. Try another city name.")
        st.stop()

    place = place_data["results"][0]
    lat, lon = place["latitude"], place["longitude"]

    live = fetch_json(
        "https://api.open-meteo.com/v1/forecast",
        {
            "latitude": lat,
            "longitude": lon,
            "current": (
                "temperature_2m,relative_humidity_2m,"
                "apparent_temperature,precipitation,wind_speed_10m"
            ),
            "daily": (
                "temperature_2m_max,temperature_2m_min,"
                "precipitation_sum,weather_code"
            ),
            "forecast_days": 7,
            "timezone": "auto",
        },
    )

    current = live["current"]
    daily = pd.DataFrame(live["daily"])
    daily["date"] = pd.to_datetime(daily["time"])

    st.subheader(
        f"{place['name']}, {place.get('country', '')}"
    )

    a, b, c, d = st.columns(4)
    a.metric("Temperature", f"{current['temperature_2m']} °C")
    b.metric("Feels like", f"{current['apparent_temperature']} °C")
    c.metric("Humidity", f"{current['relative_humidity_2m']}%")
    d.metric("Wind", f"{current['wind_speed_10m']} km/h")

    st.subheader("Seven-day forecast")

    forecast_fig = go.Figure()
    forecast_fig.add_trace(go.Scatter(
        x=daily["date"],
        y=daily["temperature_2m_max"],
        name="Maximum",
        mode="lines+markers",
        line=dict(color="#ffad66", width=3),
    ))
    forecast_fig.add_trace(go.Scatter(
        x=daily["date"],
        y=daily["temperature_2m_min"],
        name="Minimum",
        mode="lines+markers",
        line=dict(color="#63d2ef", width=3),
    ))
    forecast_fig.update_layout(
        template="plotly_dark",
        paper_bgcolor="rgba(0,0,0,0)",
        plot_bgcolor="rgba(0,0,0,0)",
        yaxis_title="Temperature (°C)",
        hovermode="x unified",
    )
    st.plotly_chart(forecast_fig, use_container_width=True)

    st.subheader("Historical weather analytics")

    end = pd.Timestamp.now(tz="UTC").date()
    start = end - pd.Timedelta(days=365 * years)

    history = fetch_json(
        "https://archive-api.open-meteo.com/v1/archive",
        {
            "latitude": lat,
            "longitude": lon,
            "start_date": str(start),
            "end_date": str(end - pd.Timedelta(days=6)),
            "daily": (
                "temperature_2m_max,temperature_2m_min,"
                "temperature_2m_mean,precipitation_sum"
            ),
            "timezone": "auto",
        },
    )

    hist = pd.DataFrame(history["daily"])
    hist["date"] = pd.to_datetime(hist["time"])
    hist = hist.rename(columns={
        "temperature_2m_max": "Maximum °C",
        "temperature_2m_min": "Minimum °C",
        "temperature_2m_mean": "Mean °C",
        "precipitation_sum": "Rainfall mm",
    })

    x, y, z, w = st.columns(4)
    x.metric("Mean maximum", f"{hist['Maximum °C'].mean():.1f} °C")
    y.metric("Mean minimum", f"{hist['Minimum °C'].mean():.1f} °C")
    z.metric("Total precipitation", f"{hist['Rainfall mm'].sum():.1f} mm")
    w.metric("Wet days (>1 mm)", str((hist["Rainfall mm"] > 1).sum()))

    st.subheader("Temperature history")
    fig = go.Figure()
    for col in ["Maximum °C", "Mean °C", "Minimum °C"]:
        fig.add_trace(go.Scatter(
            x=hist["date"], y=hist[col],
            name=col, mode="lines",
        ))
    fig.update_layout(
        template="plotly_dark",
        paper_bgcolor="rgba(0,0,0,0)",
        plot_bgcolor="rgba(0,0,0,0)",
        hovermode="x unified",
    )
    st.plotly_chart(fig, use_container_width=True)
    
    st.subheader("AWS Big Data Analytics")
    st.caption("Processed with Apache Spark • Stored in Hadoop HDFS")

    from pathlib import Path

    processed_dir = Path.home() / "atmosiq" / "data" / "processed"
    monthly_file = processed_dir / "monthly_summary.csv"
    yearly_file = processed_dir / "yearly_summary.csv"

    if monthly_file.exists() and yearly_file.exists():
        monthly_spark = pd.read_csv(monthly_file)
        yearly_spark = pd.read_csv(yearly_file)

        # Remove repeated CSV headers if Spark produced multiple part files.
        monthly_spark["year"] = pd.to_numeric(
            monthly_spark["year"], errors="coerce"
        )
        monthly_spark["month"] = pd.to_numeric(
            monthly_spark["month"], errors="coerce"
        )
        yearly_spark["year"] = pd.to_numeric(
            yearly_spark["year"], errors="coerce"
        )

        monthly_spark = monthly_spark.dropna(subset=["year", "month"])
        yearly_spark = yearly_spark.dropna(subset=["year"])

        if not monthly_spark.empty and not yearly_spark.empty:
            latest = yearly_spark.sort_values("year").iloc[-1]
            hottest = monthly_spark.loc[
                monthly_spark["max_temp_c"].idxmax()
            ]

            k1, k2, k3 = st.columns(3)
            k1.metric(
                "Latest yearly average",
                f"{latest['avg_temp_c']:.2f} °C",
                help=f"Year: {int(latest['year'])}",
            )
            k2.metric(
                "Highest monthly maximum",
                f"{hottest['max_temp_c']:.1f} °C",
                help=(
                    f"{int(hottest['year'])}-"
                    f"{int(hottest['month']):02d}"
                ),
            )
            k3.metric(
                "Years analyzed",
                str(yearly_spark["year"].nunique()),
            )

            left, right = st.columns(2)

            with left:
                st.markdown("#### Monthly temperature trend")
                monthly_spark["period"] = pd.to_datetime(
                    monthly_spark["year"].astype(int).astype(str)
                    + "-"
                    + monthly_spark["month"].astype(int).astype(str)
                    + "-01"
                )
                monthly_spark = monthly_spark.sort_values("period")

                monthly_fig = go.Figure()
                monthly_fig.add_trace(go.Scatter(
                    x=monthly_spark["period"],
                    y=monthly_spark["avg_temp_c"],
                    mode="lines+markers",
                    name="Average",
                    line=dict(color="#83e1ef", width=3),
                ))
                monthly_fig.add_trace(go.Scatter(
                    x=monthly_spark["period"],
                    y=monthly_spark["max_temp_c"],
                    mode="lines",
                    name="Maximum",
                    line=dict(color="#ffad66", width=2),
                ))
                monthly_fig.update_layout(
                    template="plotly_dark",
                    paper_bgcolor="rgba(0,0,0,0)",
                    plot_bgcolor="rgba(0,0,0,0)",
                    yaxis_title="Temperature (°C)",
                    hovermode="x unified",
                )
                st.plotly_chart(monthly_fig, use_container_width=True)

            with right:
                st.markdown("#### Yearly climate trend")
                yearly_spark = yearly_spark.sort_values("year")

                yearly_fig = go.Figure()
                yearly_fig.add_trace(go.Bar(
                    x=yearly_spark["year"].astype(int).astype(str),
                    y=yearly_spark["avg_temp_c"],
                    name="Average temperature",
                    marker_color="#63d2ef",
                ))
                yearly_fig.update_layout(
                    template="plotly_dark",
                    paper_bgcolor="rgba(0,0,0,0)",
                    plot_bgcolor="rgba(0,0,0,0)",
                    yaxis_title="Average temperature (°C)",
                    xaxis_title="Year",
                )
                st.plotly_chart(yearly_fig, use_container_width=True)

            st.markdown("#### Monthly rainfall analysis")
            rainfall_fig = go.Figure()
            rainfall_fig.add_trace(go.Bar(
                x=monthly_spark["period"],
                y=monthly_spark["precipitation_mm"],
                name="Precipitation",
                marker_color="#4287f5",
            ))
            rainfall_fig.update_layout(
                template="plotly_dark",
                paper_bgcolor="rgba(0,0,0,0)",
                plot_bgcolor="rgba(0,0,0,0)",
                xaxis_title="Month",
                yaxis_title="Precipitation (mm)",
            )
            st.plotly_chart(rainfall_fig, use_container_width=True)

            with st.expander("View Spark yearly summary table"):
                st.dataframe(
                    yearly_spark,
                    use_container_width=True,
                    hide_index=True,
                )
        else:
            st.warning(
                "Spark summary files exist, but contain no valid data. "
                "Check the exported CSV files."
            )
    else:
        st.info(
            "Spark results are not available locally yet. "
            "Export the monthly and yearly HDFS summaries to "
            "~/atmosiq/data/processed/."
        )

    st.subheader("Daily records")
    st.dataframe(hist, use_container_width=True, hide_index=True)
    st.download_button(
        "Download historical CSV",
        data=hist.to_csv(index=False).encode("utf-8"),
        file_name="atmosiq_weather_history.csv",
        mime="text/csv",
    )

except requests.RequestException as exc:
    st.error(f"Weather API request failed: {exc}")
