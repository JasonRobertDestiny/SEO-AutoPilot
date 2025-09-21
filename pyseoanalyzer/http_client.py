import urllib3
from urllib3.exceptions import HTTPError
import time


class Http:
    """HTTP client wrapper using urllib3"""
    
    def __init__(self):
        self.http = urllib3.PoolManager(
            timeout=urllib3.Timeout(connect=10.0, read=30.0),
            headers={
                'User-Agent': 'Python-SEO-Analyzer/2025.4.3 (https://github.com/sethblack/python-seo-analyzer)',
                'Cache-Control': 'no-cache, no-store, must-revalidate',
                'Pragma': 'no-cache',
                'Expires': '0'
            },
            cert_reqs='CERT_REQUIRED',
            ca_certs=None
        )
    
    def get(self, url):
        """Perform HTTP GET request with improved compatibility"""
        try:
            # Use more standard headers that are less likely to be blocked
            headers = {
                'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,*/*;q=0.8',
                'Accept-Language': 'en-US,en;q=0.5',
                'Accept-Encoding': 'gzip, deflate',
                'Connection': 'keep-alive',
                'Upgrade-Insecure-Requests': '1',
            }
            
            response = self.http.request('GET', url, headers=headers)
            return response
        except Exception as e:
            # Fallback: try with minimal headers if the first request fails
            try:
                headers = {
                    'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8',
                }
                response = self.http.request('GET', url, headers=headers)
                return response
            except Exception as fallback_e:
                raise HTTPError(f"HTTP request failed: {e}, fallback also failed: {fallback_e}")


# Thread-safe singleton instance
http = Http()