import csv
from collections import defaultdict
from datetime import datetime, timedelta

# File paths
ENGAGEMENT_LOG = 'engagement_log.csv'
DAILY_REPORT = 'daily_report.csv'

# Load the log of engagements
def load_engagement_log():
    data = []
    with open(ENGAGEMENT_LOG, mode="r") as file:
        reader = csv.DictReader(file)
        for row in reader:
            data.append(row)
    return data

# Aggregate data by member and hour
def analyze_engagement(data):
    member_engagement = defaultdict(int)    # Engagement count per member
    hourly_engagement = defaultdict(int)    # Engagement count per hour

    for entry in data:
        member = entry["Member ID"]
        timestamp = datetime.strptime(entry["Timestamp"], "%Y-%m-%d %H:%M:%S")
        hour = timestamp.replace(minute=0, second=0, microsecond=0)

        member_engagement[member] += 1
        hourly_engagement[hour] += 1

    # Identify peak hour
    peak_hour = max(hourly_engagement, key=hourly_engagement.get)
    
    return member_engagement, hourly_engagement, peak_hour

# Write the daily report
def generate_daily_report(member_engagement, hourly_engagement, peak_hour):
    with open(DAILY_REPORT, mode="w", newline="") as file:
        writer = csv.writer(file)
        writer.writerow(["Metric", "Value"])
        writer.writerow(["Total Unique Members Engaged", len(member_engagement)])
        writer.writerow(["Hourly Peak Engagement", peak_hour.strftime("%Y-%m-%d %H:%M:%S")])
        
        writer.writerow(["", ""])  # Blank row for separation
        writer.writerow(["Hourly Engagement Breakdown"])
        for hour, count in sorted(hourly_engagement.items()):
            writer.writerow([hour.strftime("%Y-%m-%d %H:%M:%S"), count])
        
        writer.writerow(["", ""])  # Blank row for separation
        writer.writerow(["Member Engagement Breakdown"])
        for member, count in member_engagement.items():
            writer.writerow([member, count])

    print("Daily report generated:", DAILY_REPORT)

# Main function to run daily analysis and reporting
def run_daily_engagement_tracker():
    data = load_engagement_log()
    member_engagement, hourly_engagement, peak_hour = analyze_engagement(data)
    generate_daily_report(member_engagement, hourly_engagement, peak_hour)

# Execute daily tracker
if __name__ == "__main__":
    run_daily_engagement_tracker()
