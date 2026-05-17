"""
Data mining and ML for analyzing blocking patterns
"""
import pandas as pd
import numpy as np
from sklearn.ensemble import RandomForestClassifier
from sklearn.model_selection import train_test_split
from typing import List, Dict
import logging

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


class BlockingPatternAnalyzer:
    """Analyze blocking patterns using machine learning"""
    
    def __init__(self):
        self.model = RandomForestClassifier(n_estimators=100, random_state=42)
        self.feature_names = [
            'response_time',
            'status_code',
            'dns_resolution_time',
            'tcp_handshake_time',
            'ssl_handshake_time',
            'ttl_value',
            'packet_loss_rate'
        ]
    
    def extract_features(self, connection_data: Dict) -> np.ndarray:
        """Extract features from connection attempt data"""
        features = []
        
        for feature in self.feature_names:
            features.append(connection_data.get(feature, 0))
        
        return np.array(features).reshape(1, -1)
    
    def train_model(self, historical_data: pd.DataFrame):
        """Train model on historical blocking data"""
        logger.info("Training blocking pattern detection model...")
        
        X = historical_data[self.feature_names]
        y = historical_data['is_blocked']
        
        X_train, X_test, y_train, y_test = train_test_split(
            X, y, test_size=0.2, random_state=42
        )
        
        self.model.fit(X_train, y_train)
        
        accuracy = self.model.score(X_test, y_test)
        logger.info(f"Model accuracy: {accuracy:.2%}")
        
        # Feature importance
        importance = dict(zip(self.feature_names, self.model.feature_importances_))
        logger.info(f"Feature importance: {importance}")
        
        return accuracy
    
    def predict_blocking(self, connection_data: Dict) -> Dict:
        """Predict if connection attempt will be blocked"""
        features = self.extract_features(connection_data)
        
        prediction = self.model.predict(features)[0]
        probability = self.model.predict_proba(features)[0]
        
        return {
            'is_blocked': bool(prediction),
            'confidence': float(max(probability)),
            'block_probability': float(probability[1])
        }
    
    def analyze_blocking_patterns(self, data: pd.DataFrame) -> Dict:
        """Analyze patterns in blocking behavior"""
        analysis = {
            'total_attempts': len(data),
            'blocked_count': int(data['is_blocked'].sum()),
            'block_rate': float(data['is_blocked'].mean()),
            'avg_response_time_blocked': float(data[data['is_blocked'] == 1]['response_time'].mean()),
            'avg_response_time_allowed': float(data[data['is_blocked'] == 0]['response_time'].mean()),
            'common_block_indicators': {}
        }
        
        # Identify common patterns in blocked requests
        blocked_data = data[data['is_blocked'] == 1]
        
        for feature in self.feature_names:
            if feature in blocked_data.columns:
                analysis['common_block_indicators'][feature] = {
                    'mean': float(blocked_data[feature].mean()),
                    'std': float(blocked_data[feature].std()),
                    'median': float(blocked_data[feature].median())
                }
        
        return analysis
    
    def generate_evasion_strategy(self, blocking_pattern: Dict) -> List[str]:
        """Generate evasion strategies based on detected patterns"""
        strategies = []
        
        # Analyze which features indicate blocking
        if blocking_pattern.get('dns_resolution_time', 0) > 5:
            strategies.append("Use alternative DNS servers (DoH/DoT)")
        
        if blocking_pattern.get('status_code') in [403, 451]:
            strategies.append("Use HTTP proxy or VPN")
        
        if blocking_pattern.get('tcp_handshake_time', 0) > 10:
            strategies.append("Try TCP obfuscation or domain fronting")
        
        if blocking_pattern.get('packet_loss_rate', 0) > 0.3:
            strategies.append("Use UDP-based protocols (QUIC, WireGuard)")
        
        if not strategies:
            strategies.append("Use Tor or multi-hop proxy")
        
        return strategies


def create_sample_dataset(n_samples: int = 1000) -> pd.DataFrame:
    """Create sample dataset for testing"""
    np.random.seed(42)
    
    data = {
        'response_time': np.random.exponential(2, n_samples),
        'status_code': np.random.choice([200, 403, 404, 451, 500], n_samples),
        'dns_resolution_time': np.random.exponential(1, n_samples),
        'tcp_handshake_time': np.random.exponential(1.5, n_samples),
        'ssl_handshake_time': np.random.exponential(2, n_samples),
        'ttl_value': np.random.randint(30, 128, n_samples),
        'packet_loss_rate': np.random.beta(1, 10, n_samples),
    }
    
    # Create blocking label based on patterns
    df = pd.DataFrame(data)
    df['is_blocked'] = (
        (df['response_time'] > 5) |
        (df['status_code'].isin([403, 451])) |
        (df['dns_resolution_time'] > 3)
    ).astype(int)
    
    return df


if __name__ == "__main__":
    # Demo
    analyzer = BlockingPatternAnalyzer()
    
    # Create and train on sample data
    sample_data = create_sample_dataset(1000)
    analyzer.train_model(sample_data)
    
    # Analyze patterns
    patterns = analyzer.analyze_blocking_patterns(sample_data)
    print("\n=== Blocking Pattern Analysis ===")
    print(f"Block rate: {patterns['block_rate']:.2%}")
    
    # Test prediction
    test_connection = {
        'response_time': 6.5,
        'status_code': 403,
        'dns_resolution_time': 2.0,
        'tcp_handshake_time': 1.5,
        'ssl_handshake_time': 2.0,
        'ttl_value': 64,
        'packet_loss_rate': 0.1
    }
    
    prediction = analyzer.predict_blocking(test_connection)
    print(f"\n=== Prediction ===")
    print(f"Will be blocked: {prediction['is_blocked']}")
    print(f"Confidence: {prediction['confidence']:.2%}")
    
    # Generate evasion strategies
    strategies = analyzer.generate_evasion_strategy(test_connection)
    print(f"\n=== Recommended Evasion Strategies ===")
    for i, strategy in enumerate(strategies, 1):
        print(f"{i}. {strategy}")
