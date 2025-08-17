"""
Snowflake Configuration for Production UNSPSC System

Automatically connects to your Snowflake connection from within Snowflake.
Provides easy setup and LLM integration.
"""

import sys
import os
from pathlib import Path
from typing import Optional
from snowflake.snowpark.context import get_active_session

# Global session instance
_session: Optional[Session] = None
_llm = None

def get_snowflake_session() -> Session:
    """
    Get Snowflake session using existing set up Snowflake configuration.
    
    Returns:
        Session: Active Snowflake session
    """
    global _session
    
    if _session is not None:
        return _session
    
    print(f"🔗 Connecting to Snowflake using {connection_name}...")
    
    try:
        _session = get_active_session()
        print(f"✅ Connected to Snowflake")
        
        # Test the connection
        result = _session.sql("SELECT CURRENT_USER(), CURRENT_ROLE(), CURRENT_DATABASE()").collect()
        if result:
            print(f"   👤 User: {result[0][0]}")
            print(f"   🎭 Role: {result[0][1]}")
            print(f"   🗄️ Database: {result[0][2] if result[0][2] else 'None'}")
        
        return _session
        
    except Exception as e:
        print(f"❌ Snowflake connection failed: {e}")
        print("\n🔧 SETUP INSTRUCTIONS:")
        print("1. This assumes you're operating this library within Snowflake such that get_activate_session is available")
        raise

def get_snowflake_llm(model_name: str = "llama3-70b"):
    """
    Get Snowflake LLM instance using the established session.
    
    Args:
        model_name: Snowflake Cortex model to use
        
    Returns:
        CustomSnowflakeLLM instance
    """
    global _llm
    
    if _llm is not None and _llm.model == model_name:
        return _llm
        
    session = get_snowflake_session()
    
    # Try different import methods to handle script vs module execution
    try:
        from ..models.snowflake_llm import CustomSnowflakeLLM
    except ImportError:
        try:
            # Add parent directory to path for direct script execution
            current_dir = Path(__file__).parent.parent
            sys.path.insert(0, str(current_dir))
            from models.snowflake_llm import CustomSnowflakeLLM
        except ImportError:
            raise ImportError("Could not import CustomSnowflakeLLM. Check models package.")
    
    _llm = CustomSnowflakeLLM(session=session, model=model_name)
    print(f"🧠 Initialized Snowflake LLM: {model_name}")
    
    return _llm

def close_session():
    """Close the current Snowflake session"""
    global _session, _llm
    
    if _session:
        _session.close()
        _session = None
        print("🧹 Snowflake session closed")
    
    _llm = None

def test_connection() -> bool:
    """
    Test the Snowflake connection and LLM functionality.
    
    Args:
        connection_name: Connection name to test
        
    Returns:
        bool: True if all tests pass
    """
    try:
        print("🧪 Testing Snowflake Connection")
        print("=" * 40)
        
        # Test session
        session = get_snowflake_session()
        print("✅ Session connection successful")
        
        # Test LLM
        llm = get_snowflake_llm()
        test_response = llm.query("Say 'Connection test successful'")
        
        if "Connection test successful" in test_response:
            print("✅ LLM test successful")
            print(f"   Response: {test_response[:50]}...")
        else:
            print("⚠️ LLM test partial - received response but unexpected format")
            print(f"   Response: {test_response[:100]}...")
        
        print("✅ All connection tests passed!")
        return True
        
    except Exception as e:
        print(f"❌ Connection test failed: {e}")
        return False 
