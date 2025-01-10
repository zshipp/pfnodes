# AWS Resource Monitoring

## Overview
This document outlines the steps taken to monitor ACN resource usage, investigate December’s data transfer, and implement budget alerts in AWS.

---

## 1. CloudWatch Dashboard Setup

1. **Dashboard Creation**  
   - Created a new dashboard named **ACN_Resource_Monitoring**.
   - Added a metric widget for **EstimatedCharges** from `AWS/Billing` in the **us-east-1** region, ensuring *Receive Billing Alerts* was enabled in Billing Preferences.

2. **Metric Configuration**  
   - Currently tracking **EstimatedCharges** for USD to monitor overall AWS costs.
   - Adjusted alert thresholds to notify via email when costs exceed the defined budget (see “Budget & Alerts”).

---

## 2. December Usage Investigation

1. **Data Transfer Review**  
   - Inspected December’s NetworkIn/Out metrics (EC2 and RDS) and found no abnormal spikes.
   - Cost Explorer and standard usage logs did not indicate excessive usage or anomalies.

2. **Conclusion**  
   - December’s usage appeared within expected limits, the previous limits were set too low, and there were no significant cost outliers.

---

## 3. Budget & Alerts

1. **AWS Budget Configuration**  
   - Set a small monthly budget for overall AWS costs.
   - Configured an email notification to trigger if the budget threshold is exceeded.

2. **Alert Threshold**  
   - The alert is triggered when costs approach or exceed the budget amount, rather than a percentage threshold.

---

## 4. Next Steps

- Continue to monitor both the **EstimatedCharges** and any relevant usage metrics in **ACN_Resource_Monitoring**.
- Update the budget threshold or alerts as necessary when usage patterns change.
- If new services are added under ACN, add relevant metrics (CPU, Network, RDS usage, etc.) to the dashboard.

---

## 5. Summary

- **ACN_Resource_Monitoring** dashboard now monitors estimated AWS charges.
- December data transfer and resource usage were within normal range.
- Budget alerts are set to send notifications upon reaching the set cost threshold.
- This setup should fulfill the task requirements for AWS resource monitoring and cost management.

