# AtmosIQ - Weather Intelligence

An end-to-end Big Data and Cloud Computing project for historical weather analytics using AWS, Hadoop, Apache Spark, Streamlit and Plotly.

## Project Overview

AtmosIQ collects historical weather data for Nagpur, stores it in Amazon S3 and Hadoop HDFS, processes it using PySpark, and presents interactive weather insights through a Streamlit dashboard.

## Technologies Used

- AWS EC2 - Cloud computing
- Amazon S3 - Cloud object storage
- Hadoop 3.4.2 - HDFS
- Apache Spark / PySpark 3.5.7 - Big Data processing
- Python - Data processing
- Streamlit - Dashboard
- Plotly - Interactive visualizations
- Pandas - Data analysis
- Open-Meteo API - Weather data

## Architecture

Open-Meteo API -> Amazon S3 -> Hadoop HDFS -> PySpark -> Streamlit Dashboard

## Dataset

- Location: Nagpur, Maharashtra, India
- Period: 2021-2025
- Records: 1,826 daily records
- Parameters: Maximum temperature, minimum temperature, mean temperature, precipitation and rain.

## Main Features

- Live weather information
- Seven-day weather forecast
- Historical temperature analysis
- Monthly and yearly temperature summaries
- Hottest and coldest days
- Precipitation analysis
- Interactive Plotly charts
- Historical CSV download

## Project Structure

```text
AtmosIQ/
├── app/
│   └── streamlit_app.py
├── data/
│   └── processed/
├── weather_analysis.py
├── requirements.txt
├── README.md
└── .gitignore  
Data Source
https://open-meteo.com/
