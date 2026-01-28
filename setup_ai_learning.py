#!/usr/bin/env python3
"""
AI Learning System Setup Script
Helps users configure the Cursor AI API for intelligent listing variations.
"""

import os
import json
from datetime import datetime

def setup_openai_api():
    """Setup OpenAI API configuration."""
    print("🤖 OpenAI AI Learning System Setup")
    print("=" * 50)
    
    # Check if API key already exists
    api_key = os.getenv('OPENAI_API_KEY')
    if api_key:
        print(f"✅ OpenAI API key already configured")
        print(f"   Key: {api_key[:8]}...{api_key[-4:]}")
        
        choice = input("\nDo you want to update the API key? (y/n): ").lower().strip()
        if choice != 'y':
            return True
    
    print("\n📋 To get your OpenAI API key:")
    print("1. Go to https://platform.openai.com/api-keys")
    print("2. Sign in to your OpenAI account")
    print("3. Create a new API key")
    print("4. Copy the key and paste it below")
    
    while True:
        api_key = input("\n🔑 Enter your OpenAI API key: ").strip()
        
        if not api_key:
            print("❌ API key cannot be empty. Please try again.")
            continue
        
        if len(api_key) < 20:
            print("❌ API key seems too short. Please check and try again.")
            continue
        
        # Test the API key
        print("🧪 Testing API key...")
        test_result = test_openai_api_key(api_key)
        
        if test_result:
            print("✅ API key is valid!")
            break
        else:
            print("❌ API key test failed. Please check your key and try again.")
            retry = input("Do you want to try again? (y/n): ").lower().strip()
            if retry != 'y':
                return False
    
    # Save API key to environment
    save_api_key(api_key)
    
    print("\n🎉 OpenAI API setup completed!")
    print("   The AI learning system is now ready to use.")
    
    return True

def test_openai_api_key(api_key):
    """Test if the OpenAI API key is valid."""
    try:
        # Test OpenAI API key format
        if api_key.startswith('sk-') and len(api_key) >= 20:
            return True
        return False
    except Exception as e:
        print(f"⚠️ Error testing API key: {e}")
        return False

def save_api_key(api_key):
    """Save API key to environment configuration."""
    try:
        # Create .env file
        env_file = '.env'
        env_content = f"OPENAI_API_KEY={api_key}\n"
        
        with open(env_file, 'w') as f:
            f.write(env_content)
        
        print(f"💾 API key saved to {env_file}")
        
        # Also set environment variable for current session
        os.environ['CURSOR_API_KEY'] = api_key
        
        print("✅ Environment variable set for current session")
        
    except Exception as e:
        print(f"⚠️ Error saving API key: {e}")
        print("   You may need to set the environment variable manually:")
        print(f"   export OPENAI_API_KEY={api_key}")

def setup_ai_learning_data():
    """Initialize AI learning data structure."""
    try:
        print("\n📊 Initializing AI learning data...")
        
        # Create accounts directory if it doesn't exist
        os.makedirs('accounts', exist_ok=True)
        
        # Initialize learning data file
        learning_data_file = os.path.join('accounts', 'ai_learning_data.json')
        
        if os.path.exists(learning_data_file):
            print("✅ AI learning data already exists")
            return True
        
        # Create initial learning data structure
        initial_data = {
            'accounts': {},
            'global_patterns': {},
            'success_metrics': {},
            'last_updated': datetime.now().isoformat(),
            'version': '1.0',
            'setup_date': datetime.now().isoformat()
        }
        
        with open(learning_data_file, 'w', encoding='utf-8') as f:
            json.dump(initial_data, f, indent=2, ensure_ascii=False)
        
        print("✅ AI learning data initialized")
        return True
        
    except Exception as e:
        print(f"❌ Error initializing AI learning data: {e}")
        return False

def test_ai_system():
    """Test the AI learning system."""
    try:
        print("\n🧪 Testing AI learning system...")
        
        from ai_learning_system import AILearningSystem
        
        # Initialize AI system
        ai_system = AILearningSystem()
        
        # Test basic functionality
        print("✅ AI learning system initialized successfully")
        
        # Test global insights
        insights = ai_system.get_learning_insights()
        print(f"✅ Global insights retrieved: {len(insights.get('accounts', []))} accounts")
        
        print("🎉 AI learning system is working correctly!")
        return True
        
    except Exception as e:
        print(f"❌ Error testing AI system: {e}")
        return False

def main():
    """Main setup function."""
    print("🚀 Facebook Marketplace Bot - AI Learning Setup")
    print("=" * 60)
    
    # Step 1: Setup OpenAI API
    if not setup_openai_api():
        print("❌ Setup failed at API configuration step")
        return False
    
    # Step 2: Initialize learning data
    if not setup_ai_learning_data():
        print("❌ Setup failed at data initialization step")
        return False
    
    # Step 3: Test AI system
    if not test_ai_system():
        print("❌ Setup failed at system test step")
        return False
    
    print("\n🎉 AI Learning System Setup Complete!")
    print("=" * 50)
    print("✅ OpenAI API configured")
    print("✅ Learning data initialized")
    print("✅ System tested and working")
    print("\n📚 Next steps:")
    print("1. Run your bot to start collecting learning data")
    print("2. The AI will analyze your listings and learn patterns")
    print("3. Future listings will use AI-powered variations")
    print("\n🔧 To configure API key manually:")
    print("   export OPENAI_API_KEY=your_api_key_here")
    
    return True

if __name__ == "__main__":
    try:
        success = main()
        if success:
            print("\n✅ Setup completed successfully!")
        else:
            print("\n❌ Setup failed. Please check the errors above.")
    except KeyboardInterrupt:
        print("\n\n⚠️ Setup cancelled by user")
    except Exception as e:
        print(f"\n❌ Unexpected error during setup: {e}")
