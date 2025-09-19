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
        """Perform HTTP GET request with cache-busting headers"""
        try:
            # Add timestamp to URL to prevent caching issues
            cache_buster = f"?_t={int(time.time() * 1000)}"
            if '?' in url:
                url_with_cache_buster = f"{url}&_t={int(time.time() * 1000)}"
            else:
                url_with_cache_buster = f"{url}{cache_buster}"
            
            # Additional cache-busting headers per request
            headers = {
                'Cache-Control': 'no-cache, no-store, must-revalidate, max-age=0',
                'Pragma': 'no-cache',
                'Expires': '0',
                'If-Modified-Since': 'Thu, 01 Jan 1970 00:00:00 GMT',
                'If-None-Match': '*'
            }
            
            response = self.http.request('GET', url_with_cache_buster, headers=headers)
            return response
        except Exception as e:
            # Fallback: try original URL without cache buster if the modified URL fails
            try:
                headers = {
                    'Cache-Control': 'no-cache, no-store, must-revalidate, max-age=0',
                    'Pragma': 'no-cache',
                    'Expires': '0'
                }
                response = self.http.request('GET', url, headers=headers)
                return response
            except Exception as fallback_e:
                raise HTTPError(f"HTTP request failed: {e}, fallback also failed: {fallback_e}")


# Thread-safe singleton instance
http = Http()