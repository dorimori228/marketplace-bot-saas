# AI Learning System for Facebook Marketplace Bot

## Overview

The AI Learning System is an intelligent component that learns from your listing data to generate better title and description variations for each relist. It uses Cursor AI API to analyze patterns in your successful listings and create more effective variations.

## Features

### 🤖 AI-Powered Variations
- **Intelligent Title Generation**: Learns from your successful titles to create better variations
- **Smart Description Optimization**: Analyzes your description patterns to generate engaging variations
- **Pattern Recognition**: Identifies what works best for your specific account and products
- **Continuous Learning**: Improves over time as it learns from more listings

### 📊 Learning Analytics
- **Account-Specific Analysis**: Each account has its own learning profile
- **Success Pattern Recognition**: Identifies what makes listings successful
- **Performance Metrics**: Tracks which variations perform best
- **Global Insights**: Cross-account learning for better results

### 🔄 Fallback System
- **Traditional Variations**: Falls back to existing variation system if AI fails
- **Reliable Operation**: Always generates variations, even without AI
- **Error Handling**: Graceful degradation when AI services are unavailable

## Setup Instructions

### 1. Get Cursor AI API Key

1. Go to [Cursor Dashboard](https://cursor.com/dashboard/integrations)
2. Navigate to the API Keys section
3. Create a new API key
4. Copy the key for configuration

### 2. Configure the System

Run the setup script:

```bash
python setup_ai_learning.py
```

Or set the environment variable manually:

```bash
export CURSOR_API_KEY=your_api_key_here
```

### 3. Initialize Learning Data

The system will automatically:
- Create learning data structure
- Analyze existing listings
- Set up account-specific learning profiles

## How It Works

### Learning Process

1. **Data Collection**: Analyzes all your existing listings
2. **Pattern Recognition**: Identifies successful patterns in titles and descriptions
3. **AI Training**: Uses Cursor AI to learn from your data
4. **Variation Generation**: Creates intelligent variations for new listings

### AI Analysis

The system analyzes:
- **Title Patterns**: Length, word count, emoji usage, number usage
- **Description Patterns**: Length, structure, bullet points, emoji usage
- **Category Distribution**: What categories work best
- **Price Patterns**: Successful price ranges
- **Success Metrics**: Which variations perform best

### Variation Generation

When creating variations, the AI:
1. **Analyzes Original Content**: Understands the core product information
2. **Applies Learned Patterns**: Uses successful patterns from your account
3. **Generates Multiple Options**: Creates several variations to choose from
4. **Selects Best Option**: Picks the most effective variation

## API Endpoints

### Analyze Account Listings
```http
POST /account/{account_name}/ai_analyze
```
Analyzes all listings for an account to learn patterns.

### Get AI Insights
```http
GET /account/{account_name}/ai_insights
```
Retrieves learning insights for a specific account.

### Global AI Insights
```http
GET /ai_global_insights
```
Retrieves global learning insights across all accounts.

## Configuration

### Environment Variables

```bash
# Required: Cursor AI API Key
CURSOR_API_KEY=your_api_key_here

# Optional: Learning data directory
AI_LEARNING_BASE_DIR=accounts
```

### Learning Data Structure

```
accounts/
├── ai_learning_data.json          # Global learning data
├── account1/
│   ├── listings.db               # Account listings
│   └── originals/                # Original content storage
└── account2/
    ├── listings.db
    └── originals/
```

## Usage Examples

### Basic Usage

The AI learning system is automatically integrated into the bot. When you create or relist items, it will:

1. **Analyze Your Data**: Learn from your existing listings
2. **Generate Variations**: Create intelligent title and description variations
3. **Apply Learning**: Use patterns that have worked for your account

### Manual Analysis

```python
from ai_learning_system import AILearningSystem

# Initialize AI system
ai_system = AILearningSystem()

# Analyze account listings
result = ai_system.analyze_account_listings('your_account')
if result['success']:
    print(f"Analyzed {result['analysis']['total_listings']} listings")

# Generate AI variations
title_result = ai_system.generate_ai_title_variation('your_account', 'Original Title')
if title_result['success']:
    print(f"AI Generated: {title_result['variation']}")
```

### Training on Success

```python
# Train on successful listings
successful_listings = [
    {'title': 'Successful Title 1', 'description': 'Successful Description 1'},
    {'title': 'Successful Title 2', 'description': 'Successful Description 2'}
]

ai_system.train_on_successful_listings('your_account', successful_listings)
```

## Benefits

### 🎯 Improved Performance
- **Higher Engagement**: AI-generated variations are more engaging
- **Better SEO**: Optimized for Facebook Marketplace search
- **Reduced Duplicates**: More unique variations reduce duplicate detection

### 📈 Continuous Improvement
- **Learning from Success**: Gets better with each successful listing
- **Account-Specific**: Tailored to your specific products and audience
- **Pattern Recognition**: Identifies what works best for your niche

### ⚡ Efficiency
- **Automated Learning**: No manual configuration required
- **Intelligent Fallbacks**: Always works, even without AI
- **Seamless Integration**: Works with existing bot functionality

## Troubleshooting

### Common Issues

1. **API Key Not Working**
   - Verify your Cursor API key is correct
   - Check if the key has proper permissions
   - Ensure the key is set in environment variables

2. **Learning Data Not Updating**
   - Check file permissions in the accounts directory
   - Verify the AI learning data file is writable
   - Restart the bot to reinitialize learning

3. **AI Variations Not Generated**
   - Check if the AI system has enough data to learn from
   - Verify the Cursor API is accessible
   - Check the fallback system is working

### Debug Mode

Enable debug logging to see AI learning activity:

```python
import logging
logging.basicConfig(level=logging.DEBUG)
```

## Advanced Configuration

### Custom Learning Parameters

```python
# Initialize with custom parameters
ai_system = AILearningSystem(
    cursor_api_key='your_key',
    base_dir='custom_accounts_dir'
)
```

### Learning Data Management

```python
# Get learning insights
insights = ai_system.get_learning_insights('account_name')
print(f"Total listings analyzed: {insights['total_listings']}")

# Global insights
global_insights = ai_system.get_learning_insights()
print(f"Total accounts: {global_insights['total_accounts']}")
```

## Performance Optimization

### Data Management
- **Regular Cleanup**: Remove old learning data periodically
- **Account Separation**: Each account has isolated learning data
- **Efficient Storage**: Compressed learning data for better performance

### API Usage
- **Rate Limiting**: Respects Cursor API rate limits
- **Caching**: Caches learning data to reduce API calls
- **Fallback Strategy**: Uses traditional variations when AI is unavailable

## Security

### Data Privacy
- **Local Storage**: All learning data stored locally
- **No External Sharing**: Data never sent to external services except Cursor AI
- **Account Isolation**: Each account's data is separate

### API Security
- **Secure Storage**: API keys stored securely
- **Environment Variables**: Sensitive data in environment variables
- **Access Control**: Proper file permissions for learning data

## Support

### Getting Help
1. Check the troubleshooting section above
2. Review the bot logs for AI learning activity
3. Verify your Cursor API key is working
4. Test the system with the setup script

### Monitoring
- **Learning Progress**: Check AI learning data file for updates
- **API Usage**: Monitor Cursor API usage in your dashboard
- **Performance**: Track variation quality and success rates

## Future Enhancements

### Planned Features
- **Advanced Analytics**: More detailed learning insights
- **A/B Testing**: Compare AI vs traditional variations
- **Custom Models**: Account-specific AI models
- **Performance Tracking**: Success rate monitoring

### Integration Opportunities
- **External APIs**: Integration with other AI services
- **Custom Learning**: User-defined learning parameters
- **Advanced Analytics**: Detailed performance metrics
- **Multi-Language**: Support for different languages

---

**Note**: The AI Learning System is designed to work seamlessly with your existing bot setup. It enhances the variation generation process while maintaining full compatibility with the traditional system.
