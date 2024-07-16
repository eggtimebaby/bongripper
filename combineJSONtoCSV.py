# analysis.py
import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns
from sqlalchemy import create_engine
from scipy import stats

# Connect to the database
engine = create_engine('postgresql://username:password@localhost/hemp_smoke_db')

# Load data
sessions = pd.read_sql_table('session', engine)
data_points = pd.read_sql_table('data_point', engine)

# Merge sessions and data points
merged_data = pd.merge(data_points, sessions, left_on='session_id', right_on='id')

def plot_opacity_over_time():
    plt.figure(figsize=(12, 6))
    for session_id in merged_data['session_id'].unique():
        session_data = merged_data[merged_data['session_id'] == session_id]
        plt.plot(session_data['timestamp'], session_data['value'], label=f'Session {session_id}')
    plt.title('Opacity Over Time for All Sessions')
    plt.xlabel('Time')
    plt.ylabel('Opacity')
    plt.legend()
    plt.show()

def analyze_session_metrics():
    print(sessions.describe())
    
    plt.figure(figsize=(12, 6))
    sns.boxplot(data=sessions, y='duration')
    plt.title('Distribution of Session Durations')
    plt.show()
    
    plt.figure(figsize=(12, 6))
    sns.scatterplot(data=sessions, x='peak_opacity', y='clearing_time')
    plt.title('Relationship between Peak Opacity and Clearing Time')
    plt.show()

def analyze_opacity_change_patterns():
    sessions['opacity_change_rate_category'] = pd.qcut(sessions['opacity_change_rate'], q=4, labels=['Low', 'Medium-Low', 'Medium-High', 'High'])
    
    plt.figure(figsize=(12, 6))
    sns.boxplot(data=sessions, x='opacity_change_rate_category', y='duration')
    plt.title('Session Duration by Opacity Change Rate Category')
    plt.show()

def identify_anomalies():
    z_scores = stats.zscore(sessions[['duration', 'peak_opacity', 'opacity_change_rate']])
    anomalies = (abs(z_scores) > 3).any(axis=1)
    print("Anomalous sessions:")
    print(sessions[anomalies])

def main():
    plot_opacity_over_time()
    analyze_session_metrics()
    analyze_opacity_change_patterns()
    identify_anomalies()

if __name__ == "__main__":
    main()