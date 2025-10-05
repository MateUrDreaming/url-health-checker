import json


def lambda_handler(event, context):
    """
    Check if any URLs in the results are unhealthy

    Input:
    {
        "results": [
            {"status": "healthy", ...},
            {"status": "unhealthy", ...}
        ]
    }

    Returns:
    {
        "has_unhealthy": true/false
    }
    """

    results = event.get('results', [])

    has_unhealthy = any(
        result.get('status') == 'unhealthy'
        for result in results
    )

    return {
        'has_unhealthy': has_unhealthy
    }