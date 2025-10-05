# URL Health Checker with AWS Step Functions

A serverless application that checks the health of multiple URLs in parallel using AWS Step Functions and Lambda. Perfect for monitoring website availability and API endpoints.

## Architecture



## Features

- Parallel Processing: Check up to 10 URLs simultaneously
- Error Handling: Automatic retries with exponential backoff
- Alerting: Email notifications when URLs are down
- Detailed Metrics: Response time, status codes, timestamps
- Serverless: No servers to manage, pay only for what you use

## Prerequisites

- AWS Account
- AWS CLI configured with credentials
- AWS SAM CLI installed ([installation guide](https://docs.aws.amazon.com/serverless-application-model/latest/developerguide/install-sam-cli.html))
- Python 3.11+ (for local testing)

## Quick Start

### 1. Clone and Setup

```bash
mkdir url-health-checker && cd url-health-checker
mkdir src statemachine
```

### 2. Deploy

```bash
sam build

sam deploy --guided
```

Follow the prompts and confirm the SNS subscription email.

### 3. Test It

```bash
aws stepfunctions start-execution \
  --state-machine-arn <ARN-from-output> \
  --input '{
    "urls": [
      {"url": "https://aws.amazon.com"},
      {"url": "https://google.com"},
      {"url": "https://github.com"},
      {"url": "https://this-will-fail.invalid"}
    ]
  }'
```

## Input Format

```json
{
  "urls": [
    {
      "url": "https://example.com",
      "timeout": 10
    },
    {
      "url": "https://api.example.com/health"
    }
  ]
}
```

## Output Format

```json
{
  "total_urls": 3,
  "results": [
    {
      "url": "https://aws.amazon.com",
      "status": "healthy",
      "status_code": 200,
      "response_time_ms": 145,
      "checked_at": "2025-10-05T12:00:00Z"
    },
    {
      "url": "https://broken-site.com",
      "status": "unhealthy",
      "error": "HTTP Error 404: Not Found",
      "checked_at": "2025-10-05T12:00:01Z"
    }
  ]
}
```

## Use Cases

- Website Monitoring: Check if your websites are accessible
- API Health Checks: Monitor REST API endpoints
- Multi-Region Testing: Test availability from different AWS regions
- Scheduled Monitoring: Combine with EventBridge for regular checks
- Integration Testing: Verify deployments across environments

## Customization

### Change Concurrency Limit

Edit `state-machine.json`:
```json
"MaxConcurrency": 20
```

### Add Scheduled Execution

Add to `template.yaml`:
```yaml
  ScheduledCheck:
    Type: AWS::Events::Rule
    Properties:
      ScheduleExpression: rate(5 minutes)
      Targets:
        - Arn: !Ref UrlHealthCheckerStateMachine
          RoleArn: !GetAtt EventBridgeRole.Arn
          Input: |
            {
              "urls": [
                {"url": "https://your-site.com"}
              ]
            }
```

### Store Results in DynamoDB

Add a new state after `AggregateResults`:
```json
"SaveResults": {
  "Type": "Task",
  "Resource": "arn:aws:states:::dynamodb:putItem",
  "Parameters": {
    "TableName": "url-health-results",
    "Item": {
      "execution_id": {"S.$": "$.summary.execution_id"},
      "results": {"S.$": "States.JsonToString($.results)"}
    }
  }
}
```

## Cost Estimate

For 100 checks per day:
- Step Functions: ~$0.03/month
- Lambda: ~$0.01/month
- SNS: ~$0.01/month

**Total: Approximately $0.05/month**

## Local Testing

Test the Lambda function locally:

```bash
cd src && pip install -r requirements.txt

python3 -c "
from check_url import lambda_handler
result = lambda_handler({'url': 'https://aws.amazon.com'}, None)
print(result)
"
```

## Monitoring

View execution results:
1. Go to AWS Step Functions Console
2. Click on `url-health-checker` state machine
3. View recent executions and their results

Check logs:
```bash
aws logs tail /aws/stepfunctions/url-health-checker --follow
```

## Cleanup

```bash
sam delete
```

## Contributing

Feel free to submit issues and enhancement requests!

## License

MIT License - feel free to use this in your projects.

## Learn More

- [AWS Step Functions](https://aws.amazon.com/step-functions/)
- [AWS SAM Documentation](https://docs.aws.amazon.com/serverless-application-model/)
- [Step Functions Best Practices](https://docs.aws.amazon.com/step-functions/latest/dg/best-practices.html)
