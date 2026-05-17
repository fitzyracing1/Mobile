"""
Belarus Freedom - Main Application
Anti-censorship toolkit for internet freedom
"""
import argparse
import sys
from detector.blocking_detector import BlockingDetector
from data_mining.pattern_analyzer import BlockingPatternAnalyzer, create_sample_dataset
from circumvention.proxy_manager import ProxyManager, DomainFronting, TorConnector
from youtube_access.youtube_unblock import YouTubeUnblocker
import logging

logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)


def detect_blocking():
    """Run blocking detection"""
    print("\n" + "="*60)
    print("BLOCKING DETECTION")
    print("="*60)
    
    detector = BlockingDetector()
    results = detector.comprehensive_scan()
    
    # Analyze results
    blocked_count = sum(
        1 for test in results['http_blocking'] 
        if not test.get('accessible', False)
    )
    
    print(f"\nScanned {len(results['http_blocking'])} URLs")
    print(f"Blocked: {blocked_count}")
    print(f"Accessible: {len(results['http_blocking']) - blocked_count}")
    
    # Show details
    print("\nDetailed Results:")
    for test in results['http_blocking']:
        status = "✗ BLOCKED" if not test.get('accessible') else "✓ Accessible"
        print(f"  {test['url']}: {status}")
        if 'error' in test:
            print(f"    Error: {test['error']}")
    
    return results


def analyze_patterns():
    """Run pattern analysis"""
    print("\n" + "="*60)
    print("PATTERN ANALYSIS & MACHINE LEARNING")
    print("="*60)
    
    analyzer = BlockingPatternAnalyzer()
    
    # Create sample dataset
    print("\nGenerating training data...")
    data = create_sample_dataset(1000)
    
    # Train model
    accuracy = analyzer.train_model(data)
    print(f"Model trained with {accuracy:.2%} accuracy")
    
    # Analyze patterns
    patterns = analyzer.analyze_blocking_patterns(data)
    print(f"\nBlock rate in dataset: {patterns['block_rate']:.2%}")
    
    # Generate strategies
    test_pattern = {
        'response_time': 6.5,
        'status_code': 403,
        'dns_resolution_time': 3.0
    }
    
    strategies = analyzer.generate_evasion_strategy(test_pattern)
    print("\nRecommended Evasion Strategies:")
    for i, strategy in enumerate(strategies, 1):
        print(f"  {i}. {strategy}")
    
    return analyzer


def setup_circumvention():
    """Setup circumvention tools"""
    print("\n" + "="*60)
    print("CIRCUMVENTION SETUP")
    print("="*60)
    
    # Proxy Manager
    print("\n1. Proxy Configuration:")
    manager = ProxyManager()
    manager.add_socks5_proxy("127.0.0.1", 9050)  # Tor default
    print(f"   Configured {len(manager.proxies)} proxy(ies)")
    
    # Domain Fronting
    print("\n2. Domain Fronting:")
    fronting = DomainFronting()
    example = fronting.create_fronted_request("blocked-site.com", "cloudflare.com")
    print(f"   {example['description']}")
    
    # Tor
    print("\n3. Tor Network:")
    tor = TorConnector()
    print(f"   Tor SOCKS proxy: localhost:{tor.tor_port}")
    print("   Note: Requires Tor to be running locally")
    
    return manager


def unblock_youtube(url: str = None):
    """Unblock YouTube access"""
    print("\n" + "="*60)
    print("YOUTUBE UNBLOCKING")
    print("="*60)
    
    unblocker = YouTubeUnblocker()
    
    if url:
        print(f"\nConverting: {url}")
        alternatives = unblocker.get_invidious_url(url)
        print("\nInvidious Alternatives:")
        for alt in alternatives:
            print(f"  • {alt}")
    
    # Test instances
    print("\nTesting Invidious instances...")
    results = unblocker.test_invidious_access()
    accessible = [r for r in results if r['accessible']]
    
    print(f"\nAccessible instances: {len(accessible)}/{len(results)}")
    for r in accessible:
        print(f"  ✓ {r['instance']} ({r['response_time']:.2f}s)")
    
    # Show recommendations
    suggestions = unblocker.get_proxy_suggestions_for_youtube()
    print("\nRecommended Protocols:")
    for protocol in suggestions['recommended_vpn_protocols']:
        print(f"  • {protocol}")
    
    return unblocker


def main():
    parser = argparse.ArgumentParser(
        description='Belarus Freedom - Anti-Censorship Toolkit'
    )
    parser.add_argument(
        '--detect',
        action='store_true',
        help='Run blocking detection'
    )
    parser.add_argument(
        '--analyze',
        action='store_true',
        help='Run pattern analysis'
    )
    parser.add_argument(
        '--circumvent',
        action='store_true',
        help='Setup circumvention tools'
    )
    parser.add_argument(
        '--youtube',
        nargs='?',
        const=True,
        help='Unblock YouTube (optionally provide URL)'
    )
    parser.add_argument(
        '--all',
        action='store_true',
        help='Run all modules'
    )
    
    args = parser.parse_args()
    
    # Run requested modules
    if args.all or (not any([args.detect, args.analyze, args.circumvent, args.youtube])):
        print("\n" + "="*60)
        print("BELARUS FREEDOM - ANTI-CENSORSHIP TOOLKIT")
        print("="*60)
        detect_blocking()
        analyze_patterns()
        setup_circumvention()
        unblock_youtube()
    else:
        if args.detect:
            detect_blocking()
        
        if args.analyze:
            analyze_patterns()
        
        if args.circumvent:
            setup_circumvention()
        
        if args.youtube:
            url = args.youtube if isinstance(args.youtube, str) else None
            unblock_youtube(url)
    
    print("\n" + "="*60)
    print("Complete! Stay free and safe.")
    print("="*60 + "\n")


if __name__ == "__main__":
    main()
