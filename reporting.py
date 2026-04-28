# Import libraries
import matplotlib.pyplot as plt
import pandas as pd
import storage

def get_glucose_dataframe():
    # Get all glucose readings from database
    readings = storage.get_glucose_readings()

    if len(readings) == 0:
        return None

    # Convert to pandas DataFrame
    df = pd.DataFrame(readings, columns=[
        'id', 'session_id', 'glucose_level',
        'classification', 'recorded_at'
    ])

    # Convert recorded_at to datetime
    df['recorded_at'] = pd.to_datetime(df['recorded_at'])

    return df

def plot_glucose_trend():
    df = get_glucose_dataframe()

    if df is None:
        return None

    # Create the chart
    fig, ax = plt.subplots(figsize=(10, 4))

    ax.plot(
        df['recorded_at'],
        df['glucose_level'],
        marker='o',
        linewidth=2,
        color='#2E75B6',
        markersize=6
    )

    # Add zone reference lines
    ax.axhline(y=70,  color='red',    linestyle='--', alpha=0.5, label='Low threshold (70)')
    ax.axhline(y=126, color='green',  linestyle='--', alpha=0.5, label='Ideal zone start (126)')
    ax.axhline(y=270, color='orange', linestyle='--', alpha=0.5, label='High threshold (270)')

    ax.set_title('Pre-Exercise Glucose Trend')
    ax.set_xlabel('Date and Time')
    ax.set_ylabel('Glucose Level (mg/dL)')
    ax.legend()
    ax.grid(True, alpha=0.3)

    plt.tight_layout()
    return fig

def plot_zone_distribution():
    df = get_glucose_dataframe()

    if df is None:
        return None

    # Count readings per classification
    zone_counts = df['classification'].value_counts()

    # Define colors for each zone
    colors = {
        'Treat Low': 'red',
        'Wait and Recheck': 'orange',
        'Exercise with Caution': 'yellow',
        'Ideal Starting Zone': 'green',
        'Usually Okay': 'blue',
        'Check Ketones First': 'purple'
    }

    bar_colors = [colors.get(zone, 'gray') for zone in zone_counts.index]

    # Create the chart
    fig, ax = plt.subplots(figsize=(10, 4))

    ax.bar(zone_counts.index, zone_counts.values, color=bar_colors)

    ax.set_title('Glucose Zone Distribution')
    ax.set_xlabel('Classification')
    ax.set_ylabel('Number of Readings')
    ax.tick_params(axis='x', rotation=30)

    plt.tight_layout()
    return fig

if __name__ == '__main__':
    import streamlit as st
    storage.create_tables()

    fig1 = plot_glucose_trend()
    fig2 = plot_zone_distribution()

    if fig1 is None:
        print("No glucose data found. Log some readings first.")
    else:
        print("Charts generated successfully.")
        plt.show()