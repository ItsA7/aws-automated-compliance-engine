# Continuous Cloud Compliance Engine

## Overview
Constructed a serverless DevSecOps tool designed to enforce security compliance in real-time. It acts as a "Guard Dog" for AWS Security Groups, automatically detecting and remediating overly permissive rules (e.g., SSH open to 0.0.0.0/0) to prevent unauthorized access.

## Architecture
* **Compute:** AWS Lambda (Python 3.9) running in a "Guard Dog" polling loop.
* **Trigger:** Amazon EventBridge Scheduler (runs every 15 minutes).
* **Notification:** Amazon SNS (alerts security team upon remediation).
* **Permissions:** IAM Role with least-privilege access (`ec2:Describe*`, `ec2:Revoke*`, `sns:Publish`).

## Architecture Diagram

```mermaid
    graph TD
        %% Nodes
        Trigger([🕒 15-Min Scheduler]) -->|Wake Up| Lambda[⚡ Lambda Guard Dog]
    
        subgraph "Execution Loop"
            Lambda -->|1. Scan| API{AWS API}
            API -->|2. Return Rules| Lambda
            Lambda -->|3. Check Logic| Decision{Any Open SSH?}
        end
    
        Decision -- No --> Sleep([💤 Sleep / End])
        Decision -- Yes --> Fix[🛡️ Revoke Rule]
    
        Fix -->|Success| Notify[📢 SNS Alert]
        Notify --> Email[@ SecOps Team]

        %% Styling
        classDef aws fill:#FF9900,stroke:#232F3E,color:white,stroke-width:2px;
        classDef sec fill:#D13212,stroke:#5A1005,color:white,stroke-width:2px;
        classDef safe fill:#1D8102,stroke:#0E3F01,color:white,stroke-width:2px;

        class Lambda,API,Notify aws;
        class Fix,Decision sec;
        class Trigger,Sleep,Email safe;
```

## How It Works
1.  **Scheduled Execution:** EventBridge wakes up the Lambda function every 15 minutes.
2.  **Continuous Polling:** The function enters a "Guard Dog" loop, scanning all Security Groups in the region every 5 seconds.
3.  **Detection logic:**
    * Iterates through every Inbound Rule.
    * Checks for `0.0.0.0/0` (Anywhere) on sensitive ports (Port 22, 3389).
4.  **Auto-Remediation:** If a violation is found, the script **immediately revokes** the rule via the Boto3 SDK.
5.  **Alerting:** An SNS notification is sent to the SecOps team with the specific Security Group ID and violation details.

## Key Benefits
* **Zero-Touch Security:** Eliminates manual auditing of security groups.
* **Near Real-Time Remediation:** Reduces Mean Time to Remediate (MTTR) from hours/days to **<5 seconds**.
* **Audit Readiness:** Ensures continuous compliance with **SOC 2** and **ISO 27001** network access policies.
* **Cost Efficiency:** Uses AWS Lambda's lightweight execution model, costing <$1/month.

## Deployment
1.  **Clone the Repo:**
    ```bash
    git clone [https://github.com/yourusername/aws-compliance-engine.git](https://github.com/yourusername/aws-compliance-engine.git)
    ```
2.  **Deploy Lambda:** Upload `lambda_function.py` to AWS Lambda.
3.  **Configure Environment:**
    * Set `TOPIC_ARN` in the script to your SNS Topic.
    * Increase Lambda Timeout to **15 minutes**.
4.  **Set Scheduler:** Create an EventBridge Schedule to run every 15 minutes.

## Future Scope
* Add support for "Allowed IP Lists" (Whitelisting).
* Integrate with Slack/Microsoft Teams for chat alerts.
* Expand scanning to include S3 Bucket Policies.
