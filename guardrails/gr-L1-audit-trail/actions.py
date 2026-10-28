"""gr-L1-audit-trail: Persistence action for audit record logging."""
import json
import time
import uuid
import re
import logging
from nemoguardrails.actions import action

logger = logging.getLogger("gr-L1-audit-trail")

PII_PATTERNS = {
    "email": (r'\b[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Z|a-z]{2,}\b', "[EMAIL]"),
    "phone": (r'\b(?:\+?1[-.\s]?)?(?:\(?\d{3}\)?[-.\s]?)?\d{3}[-.\s]?\d{4}\b', "[PHONE]"),
    "ssn": (r'\b\d{3}-\d{2}-\d{4}\b', "[SSN]"),
    "credit_card": (r'\b(?:\d{4}[-\s]?){3}\d{4}\b', "[CC]"),
}


def _mask_pii(params: dict) -> dict:
    """Mask PII patterns in parameter values."""
    masked = {}
    for key, value in params.items():
        if isinstance(value, str):
            masked_value = value
            for _, (pattern, replacement) in PII_PATTERNS.items():
                masked_value = re.sub(pattern, replacement, masked_value)
            masked[key] = masked_value
        else:
            masked[key] = value
    return masked


@action()
async def persist_audit_record(output: str) -> bool:
    """Persist structured audit record. Called after validation passes."""
    try:
        data = json.loads(output) if isinstance(output, str) else output

        params = data.get("input_summary", {}).get("parameters", {})
        masked_params = _mask_pii(params)

        audit_record = {
            "audit_id": f"audit-{uuid.uuid4()}",
            "timestamp": time.strftime("%Y-%m-%dT%H:%M:%S.000Z", time.gmtime()),
            "agent_id": data.get("agent_id"),
            "agent_version": data.get("agent_version"),
            "execution_id": data.get("execution_id"),
            "input_source": data.get("input_summary", {}).get("source"),
            "source_agent_id": data.get("input_summary", {}).get("source_agent_id"),
            "input_parameters_masked": masked_params,
            "output_type": data.get("output", {}).get("type"),
            "output_item_count": len(data.get("output", {}).get("items", [])),
            "output_artifact_count": len(data.get("output", {}).get("artifacts", [])),
            "schema_version": data.get("output", {}).get("schema_version"),
            "status": "success" if data.get("output", {}).get("items") or data.get("output", {}).get("artifacts") else "empty",
        }

        # --- PERSISTENCE (uncomment one for production) ---

        # Option 1: AWS DynamoDB
        # import boto3
        # dynamodb = boto3.resource('dynamodb')
        # table = dynamodb.Table('agent-audit-trail')
        # table.put_item(Item=audit_record)

        # Option 2: AWS S3
        # import boto3
        # s3 = boto3.client('s3')
        # key = f"audit/{audit_record['agent_id']}/{audit_record['execution_id']}.json"
        # s3.put_object(Bucket='agent-audit-bucket', Key=key, Body=json.dumps(audit_record))

        # Option 3: AWS CloudWatch Logs
        # import boto3
        # logs = boto3.client('logs')
        # logs.put_log_events(logGroupName='/agent-factory/audit', logStreamName=audit_record['agent_id'], logEvents=[{'timestamp': int(time.time()*1000), 'message': json.dumps(audit_record)}])

        # Option 4: PostgreSQL
        # import asyncpg
        # conn = await asyncpg.connect(dsn='postgresql://...')
        # await conn.execute('INSERT INTO audit_trail (data) VALUES ($1)', json.dumps(audit_record))

        # Default: log to stdout (dev/testing)
        logger.info(f"AUDIT: {json.dumps(audit_record)}")
        return True

    except (json.JSONDecodeError, TypeError) as e:
        logger.error(f"AUDIT FAILURE: {e}")
        return False
