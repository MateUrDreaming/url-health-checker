import json
import urllib.request
import urllib.error
from datetime import datetime


def lambda_handler(event, context):
    """
    Check the health of a single URL

    Input event format:
    {
        "url": "https://example.com",
        "timeout": 10  # optional, defaults to 10 seconds
    }

    Returns:
    {
        "url": "https://example.com",
        "status": "healthy" | "unhealthy",
        "status_code": 200,
        "response_time_ms": 123,
        "error": "error message if failed",
        "checked_at": "2025-10-05T12:00:00Z"
    }
    """

    url = event.get('url')
    timeout = event.get('timeout', 10)

    if not url:
        return {
            'url': 'unknown',
            'status': 'unhealthy',
            'error': 'No URL provided',
            'checked_at': datetime.utcnow().isoformat() + 'Z'
        }

    start_time = datetime.now()

    try:
        # Create request with timeout
        req = urllib.request.Request(
            url,
            headers={'User-Agent': 'AWS-Step-Functions-Health-Checker/1.0'}
        )

        # Make the request
        with urllib.request.urlopen(req, timeout=timeout) as response:
            status_code = response.getcode()
            end_time = datetime.now()
            response_time_ms = int((end_time - start_time).total_seconds() * 1000)

            return {
                'url': url,
                'status': 'healthy' if 200 <= status_code < 400 else 'unhealthy',
                'status_code': status_code,
                'response_time_ms': response_time_ms,
                'checked_at': datetime.utcnow().isoformat() + 'Z'
            }

    except urllib.error.HTTPError as e:
        end_time = datetime.now()
        response_time_ms = int((end_time - start_time).total_seconds() * 1000)

        return {
            'url': url,
            'status': 'unhealthy',
            'status_code': e.code,
            'response_time_ms': response_time_ms,
            'error': f'HTTP Error {e.code}: {e.reason}',
            'checked_at': datetime.utcnow().isoformat() + 'Z'
        }

    except urllib.error.URLError as e:
        return {
            'url': url,
            'status': 'unhealthy',
            'error': f'URL Error: {str(e.reason)}',
            'checked_at': datetime.utcnow().isoformat() + 'Z'
        }

    except Exception as e:
        return {
            'url': url,
            'status': 'unhealthy',
            'error': f'Unexpected error: {str(e)}',
            'checked_at': datetime.utcnow().isoformat() + 'Z'
        }