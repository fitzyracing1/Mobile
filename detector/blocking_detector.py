"""
Detect web blocking attempts through pattern analysis
"""
import requests
import socket
from typing import Dict, List, Tuple
import time
import logging

try:
    import dns.resolver
    DNS_AVAILABLE = True
except ImportError:
    DNS_AVAILABLE = False
    logging.warning("dnspython not installed - DNS detection disabled")

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


class BlockingDetector:
    """Detects various types of web blocking"""
    
    def __init__(self):
        self.test_urls = [
            "https://www.youtube.com",
            "https://www.google.com",
            "https://www.bbc.com"
        ]
        self.dns_servers = [
            "8.8.8.8",  # Google
            "1.1.1.1",  # Cloudflare
            "208.67.222.222"  # OpenDNS
        ]
    
    def detect_dns_blocking(self, domain: str) -> Dict:
        """Detect DNS-based blocking"""
        if not DNS_AVAILABLE:
            return {'error': 'dnspython not installed - run: pip install dnspython'}
        
        results = {}
        
        for dns_server in self.dns_servers:
            try:
                resolver = dns.resolver.Resolver()
                resolver.nameservers = [dns_server]
                answer = resolver.resolve(domain, 'A')
                results[dns_server] = {
                    'blocked': False,
                    'ips': [str(rdata) for rdata in answer]
                }
            except Exception as e:
                results[dns_server] = {
                    'blocked': True,
                    'error': str(e)
                }
        
        return results
    
    def detect_http_blocking(self, url: str) -> Dict:
        """Detect HTTP/HTTPS blocking or tampering"""
        result = {
            'url': url,
            'accessible': False,
            'status_code': None,
            'response_time': None,
            'content_modified': False
        }
        
        try:
            start = time.time()
            response = requests.get(url, timeout=10)
            result['response_time'] = time.time() - start
            result['status_code'] = response.status_code
            result['accessible'] = 200 <= response.status_code < 300
            
            # Check for censorship page indicators
            content_lower = response.text.lower()
            censorship_keywords = ['blocked', 'restricted', 'forbidden', 'censored']
            result['content_modified'] = any(kw in content_lower for kw in censorship_keywords)
            
        except requests.exceptions.Timeout:
            result['error'] = 'Timeout - possible throttling'
        except requests.exceptions.ConnectionError:
            result['error'] = 'Connection blocked'
        except Exception as e:
            result['error'] = str(e)
        
        return result
    
    def detect_ip_blocking(self, host: str, port: int = 443) -> Dict:
        """Detect IP-based blocking"""
        result = {
            'host': host,
            'port': port,
            'blocked': False
        }
        
        try:
            sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            sock.settimeout(5)
            sock.connect((host, port))
            sock.close()
            result['blocked'] = False
        except socket.timeout:
            result['blocked'] = True
            result['reason'] = 'Timeout'
        except socket.error as e:
            result['blocked'] = True
            result['reason'] = str(e)
        
        return result
    
    def comprehensive_scan(self) -> Dict:
        """Run all detection methods"""
        logger.info("Starting comprehensive blocking detection...")
        
        scan_results = {
            'timestamp': time.time(),
            'dns_blocking': {},
            'http_blocking': [],
            'ip_blocking': []
        }
        
        # DNS tests
        if DNS_AVAILABLE:
            for url in self.test_urls:
                domain = url.split('//')[-1].split('/')[0]
                scan_results['dns_blocking'][domain] = self.detect_dns_blocking(domain)
        else:
            scan_results['dns_blocking'] = {'note': 'DNS detection skipped - dnspython not installed'}
        
        # HTTP tests
        for url in self.test_urls:
            scan_results['http_blocking'].append(self.detect_http_blocking(url))
        
        # IP tests
        for url in self.test_urls:
            domain = url.split('//')[-1].split('/')[0]
            scan_results['ip_blocking'].append(
                self.detect_ip_blocking(domain, 443)
            )
        
        return scan_results


if __name__ == "__main__":
    detector = BlockingDetector()
    results = detector.comprehensive_scan()
    
    print("\n=== Blocking Detection Results ===")
    for method, data in results.items():
        if method != 'timestamp':
            print(f"\n{method.upper()}:")
            print(data)
