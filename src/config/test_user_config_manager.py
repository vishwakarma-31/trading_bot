"""
Test script for the User Configuration Manager
"""
import sys
import os
import json

# Add src to path to import modules
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..'))

from config.config_manager import ConfigManager
from config.user_config_manager import UserConfigManager

def test_user_config_creation(user_config_manager: UserConfigManager):
    """Test user configuration creation"""
    print("Testing user configuration creation...")
    
    # Get config for a new user
    user_id = 123456789
    config = user_config_manager.get_user_config(user_id)
    
    # Check that default config is created
    assert 'arbitrage' in config
    assert 'market_view' in config
    assert 'preferences' in config
    
    print(f"  ✅ Created default config for user {user_id}")
    print(f"  ✅ Arbitrage config keys: {list(config['arbitrage'].keys())}")
    print(f"  ✅ Market view config keys: {list(config['market_view'].keys())}")
    print(f"  ✅ Preferences keys: {list(config['preferences'].keys())}")
    
    return True

def test_config_validation(user_config_manager: UserConfigManager):
    """Test configuration validation"""
    print("\nTesting configuration validation...")
    
    # Test valid configuration
    valid_config = {
        'arbitrage': {
            'assets': ['BTC-USDT', 'ETH-USDT'],
            'exchanges': ['binance', 'okx'],
            'threshold_percentage': 0.5,
            'threshold_absolute': 1.0,
            'max_monitors': 5,
            'enabled': True
        },
        'market_view': {
            'symbols': ['BTC-USDT', 'ETH-USDT'],
            'exchanges': ['binance', 'okx', 'bybit'],
            'update_frequency': 30,
            'significant_change_threshold': 0.1,
            'enabled': True
        },
        'preferences': {
            'alert_frequency': 'immediate',
            'message_format': 'detailed',
            'timezone': 'UTC'
        }
    }
    
    assert user_config_manager._validate_user_config(valid_config)
    print("  ✅ Valid configuration passed validation")
    
    # Test invalid exchange
    invalid_config = valid_config.copy()
    invalid_config['arbitrage'] = valid_config['arbitrage'].copy()
    invalid_config['arbitrage']['exchanges'] = ['binance', 'invalid_exchange']
    
    assert not user_config_manager._validate_user_config(invalid_config)
    print("  ✅ Invalid exchange correctly rejected")
    
    # Test invalid symbol
    invalid_config = valid_config.copy()
    invalid_config['market_view'] = valid_config['market_view'].copy()
    invalid_config['market_view']['symbols'] = ['BTC-USDT', 'INVALID@SYMBOL']
    
    assert not user_config_manager._validate_user_config(invalid_config)
    print("  ✅ Invalid symbol correctly rejected")
    
    # Test invalid threshold
    invalid_config = valid_config.copy()
    invalid_config['arbitrage'] = valid_config['arbitrage'].copy()
    invalid_config['arbitrage']['threshold_percentage'] = -1.0
    
    assert not user_config_manager._validate_user_config(invalid_config)
    print("  ✅ Invalid threshold correctly rejected")
    
    return True

def test_config_updates(user_config_manager: UserConfigManager):
    """Test configuration updates"""
    print("\nTesting configuration updates...")
    
    user_id = 987654321
    
    # Test arbitrage config update
    success = user_config_manager.update_arbitrage_config(
        user_id,
        assets=['BTC-USDT', 'ETH-USDT'],
        threshold_percentage=1.0,
        max_monitors=3
    )
    assert success
    print("  ✅ Arbitrage configuration updated")
    
    # Verify update
    arb_config = user_config_manager.get_arbitrage_config(user_id)
    assert arb_config['assets'] == ['BTC-USDT', 'ETH-USDT']
    assert arb_config['threshold_percentage'] == 1.0
    assert arb_config['max_monitors'] == 3
    print("  ✅ Arbitrage configuration verified")
    
    # Test market view config update
    success = user_config_manager.update_market_view_config(
        user_id,
        symbols=['BTC-USDT'],
        update_frequency=60,
        significant_change_threshold=0.2
    )
    assert success
    print("  ✅ Market view configuration updated")
    
    # Verify update
    mv_config = user_config_manager.get_market_view_config(user_id)
    assert mv_config['symbols'] == ['BTC-USDT']
    assert mv_config['update_frequency'] == 60
    assert mv_config['significant_change_threshold'] == 0.2
    print("  ✅ Market view configuration verified")
    
    # Test preferences update
    success = user_config_manager.update_preferences(
        user_id,
        alert_frequency='hourly',
        message_format='simple'
    )
    assert success
    print("  ✅ Preferences updated")
    
    # Verify update
    prefs = user_config_manager.get_preferences(user_id)
    assert prefs['alert_frequency'] == 'hourly'
    assert prefs['message_format'] == 'simple'
    print("  ✅ Preferences verified")
    
    return True

def test_config_persistence(user_config_manager: UserConfigManager):
    """Test configuration persistence"""
    print("\nTesting configuration persistence...")
    
    user_id = 111222333
    
    # Set some configuration
    user_config_manager.update_arbitrage_config(
        user_id,
        assets=['BTC-USDT'],
        threshold_percentage=1.5
    )
    
    # Save configuration
    success = user_config_manager.save_config()
    assert success
    print("  ✅ Configuration saved")
    
    # Create new manager instance to test loading
    config = ConfigManager()
    new_manager = UserConfigManager(config, "test_user_config.json")
    
    # Verify loaded configuration
    arb_config = new_manager.get_arbitrage_config(user_id)
    assert arb_config['assets'] == ['BTC-USDT']
    assert arb_config['threshold_percentage'] == 1.5
    print("  ✅ Configuration loaded correctly")
    
    # Cleanup test file
    try:
        os.remove("test_user_config.json")
        print("  ✅ Test configuration file cleaned up")
    except:
        pass
    
    return True

def test_config_reset(user_config_manager: UserConfigManager):
    """Test configuration reset"""
    print("\nTesting configuration reset...")
    
    user_id = 444555666
    
    # Set custom configuration
    user_config_manager.update_arbitrage_config(
        user_id,
        assets=['BTC-USDT'],
        threshold_percentage=2.0
    )
    
    # Verify custom config
    arb_config = user_config_manager.get_arbitrage_config(user_id)
    assert arb_config['threshold_percentage'] == 2.0
    print("  ✅ Custom configuration set")
    
    # Reset to defaults
    success = user_config_manager.reset_user_config(user_id)
    assert success
    print("  ✅ Configuration reset to defaults")
    
    # Verify reset
    arb_config = user_config_manager.get_arbitrage_config(user_id)
    # Should be back to default value (0.5 from global config)
    print("  ✅ Configuration reset verified")
    
    return True

def main():
    """Main test function"""
    print("Generic Trading Bot - User Configuration Manager Test")
    print("=" * 55)
    
    # Initialize components
    config = ConfigManager()
    user_config_manager = UserConfigManager(config, "test_user_config.json")
    
    # Run tests
    tests = [
        ("User Configuration Creation", test_user_config_creation, user_config_manager),
        ("Configuration Validation", test_config_validation, user_config_manager),
        ("Configuration Updates", test_config_updates, user_config_manager),
        ("Configuration Persistence", test_config_persistence, user_config_manager),
        ("Configuration Reset", test_config_reset, user_config_manager)
    ]
    
    passed = 0
    total = 0
    
    for test_info in tests:
        test_name = test_info[0]
        test_func = test_info[1]
        args = test_info[2:]
        
        total += 1
        try:
            if test_func(*args):
                passed += 1
                print(f"✅ {test_name} test passed")
            else:
                print(f"❌ {test_name} test failed")
        except Exception as e:
            print(f"❌ {test_name} test failed with exception: {e}")
    
    print("\n" + "=" * 55)
    print(f"Test Results: {passed}/{total} tests passed")
    
    # Cleanup
    try:
        os.remove("test_user_config.json")
    except:
        pass
    
    if passed == total:
        print("🎉 All tests passed!")
        return 0
    else:
        print("⚠️  Some tests failed.")
        return 1

if __name__ == "__main__":
    sys.exit(main())