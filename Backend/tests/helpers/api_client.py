"""
API Client for AI Customer Support Widget Testing
Provides a simple interface for making HTTP requests to the API
"""

import requests
from typing import Dict, Any, Optional
import json


class APIClient:
    """HTTP client for API testing"""

    def __init__(self, base_url: str = "http://localhost:8000", timeout: int = 30):
        self.base_url = base_url.rstrip('/')
        self.timeout = timeout
        self.session = requests.Session()
        self.session.headers.update({
            'Content-Type': 'application/json',
            'Accept': 'application/json'
        })

    def post(self, endpoint: str, data: Dict[str, Any], headers: Optional[Dict[str, str]] = None) -> Dict[str, Any]:
        url = f"{self.base_url}{endpoint}"
        try:
            response = self.session.post(url, json=data, headers=headers, timeout=self.timeout)
            try:
                response_data = response.json()
            except json.JSONDecodeError:
                response_data = {"text": response.text, "error": "Failed to parse JSON response"}

            if isinstance(response_data, list):
                response_data = {"_items": response_data}

            response_data['_status_code'] = response.status_code
            response_data['_headers'] = dict(response.headers)
            return response_data

        except requests.exceptions.Timeout:
            return {"_status_code": 408, "error": "Request timeout", "timeout": self.timeout}
        except requests.exceptions.ConnectionError as e:
            return {"_status_code": 503, "error": f"Connection error: {str(e)}"}
        except Exception as e:
            return {"_status_code": 500, "error": f"Request failed: {str(e)}"}

    def get(self, endpoint: str, params: Optional[Dict[str, Any]] = None, headers: Optional[Dict[str, str]] = None) -> Dict[str, Any]:
        url = f"{self.base_url}{endpoint}"
        try:
            response = self.session.get(url, params=params, headers=headers, timeout=self.timeout)
            try:
                response_data = response.json()
            except json.JSONDecodeError:
                response_data = {"text": response.text, "error": "Failed to parse JSON response"}

            if isinstance(response_data, list):
                response_data = {"_items": response_data}

            response_data['_status_code'] = response.status_code
            response_data['_headers'] = dict(response.headers)
            return response_data

        except requests.exceptions.Timeout:
            return {"_status_code": 408, "error": "Request timeout", "timeout": self.timeout}
        except requests.exceptions.ConnectionError as e:
            return {"_status_code": 503, "error": f"Connection error: {str(e)}"}
        except Exception as e:
            return {"_status_code": 500, "error": f"Request failed: {str(e)}"}

    def put(self, endpoint: str, data: Dict[str, Any], headers: Optional[Dict[str, str]] = None) -> Dict[str, Any]:
        url = f"{self.base_url}{endpoint}"
        try:
            response = self.session.put(url, json=data, headers=headers, timeout=self.timeout)
            try:
                response_data = response.json()
            except json.JSONDecodeError:
                response_data = {"text": response.text, "error": "Failed to parse JSON response"}

            if isinstance(response_data, list):
                response_data = {"_items": response_data}

            response_data['_status_code'] = response.status_code
            response_data['_headers'] = dict(response.headers)
            return response_data

        except requests.exceptions.Timeout:
            return {"_status_code": 408, "error": "Request timeout", "timeout": self.timeout}
        except requests.exceptions.ConnectionError as e:
            return {"_status_code": 503, "error": f"Connection error: {str(e)}"}
        except Exception as e:
            return {"_status_code": 500, "error": f"Request failed: {str(e)}"}

    def delete(self, endpoint: str, headers: Optional[Dict[str, str]] = None) -> Dict[str, Any]:
        url = f"{self.base_url}{endpoint}"
        try:
            response = self.session.delete(url, headers=headers, timeout=self.timeout)
            try:
                response_data = response.json()
            except json.JSONDecodeError:
                response_data = {"text": response.text}

            response_data['_status_code'] = response.status_code
            return response_data

        except Exception as e:
            return {"_status_code": 500, "error": f"Request failed: {str(e)}"}

    def set_auth_token(self, token: str):
        self.session.headers.update({'Authorization': f'Bearer {token}'})

    def clear_auth_token(self):
        self.session.headers.pop('Authorization', None)

    def close(self):
        self.session.close()
