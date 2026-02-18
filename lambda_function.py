import boto3
import time
import json

def lambda_handler(event, context):
    ec2 = boto3.client('ec2')
    sns = boto3.client('sns')
    
    # --- CONFIGURATION ---
    TOPIC_ARN = 'arn:aws:sns:us-east-1:123456789:SecurityAlerts'
    CHECK_INTERVAL = 5  # Check every 5 seconds
    RUNTIME_LIMIT = 880 # Run for 14 mins 40 seconds (leave buffer for 15m timeout)
    # ---------------------

    start_time = time.time()
    print("Guard Dog Started: Monitoring Security Groups every 5 seconds...")

    # THE INFINITE LOOP
    while (time.time() - start_time) < RUNTIME_LIMIT:
        try:
            # 1. Scan ALL Security Groups
            response = ec2.describe_security_groups()
            
            for sg in response['SecurityGroups']:
                sg_id = sg['GroupId']
                
                # Check Inbound Rules
                for permission in sg.get('IpPermissions', []):
                    # Check for 0.0.0.0/0 on Port 22
                    is_open_to_world = False
                    for ip_range in permission.get('IpRanges', []):
                        if ip_range.get('CidrIp') == '0.0.0.0/0':
                            is_open_to_world = True
                    
                    if (permission.get('FromPort') == 22) and is_open_to_world:
                        print(f"VIOLATION FOUND: {sg_id}. REMEDIATING IMMEDIATELY...")
                        
                        # Fix it
                        ec2.revoke_security_group_ingress(
                            GroupId=sg_id,
                            IpPermissions=[permission]
                        )
                        
                        # Notify
                        sns.publish(
                            TopicArn=TOPIC_ARN,
                            Message=f"Guard Dog Alert: Instantly removed SSH (0.0.0.0/0) from {sg_id}",
                            Subject="Immediate Auto-Remediation"
                        )
            
            # Sleep before next check
            time.sleep(CHECK_INTERVAL)
            
        except Exception as e:
            print(f"Error in loop: {e}")
            time.sleep(CHECK_INTERVAL) # Sleep even if error to avoid crash loop

    return "Guard Dog Shift Ended. Restarting..."
