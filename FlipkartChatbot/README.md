# Customer Support Chatbot 🛍️

A modern, AI-powered customer support chatbot for e-commerce platforms built with Streamlit and Groq AI. This intelligent assistant helps customers with order tracking, product information, returns, refunds, and more.

## 🌟 Features

- **Multi-language Support** - Supports both English and Hindi (Devanagari script)
- **Order Tracking** - Real-time order status and tracking information
- **Product Recommendations** - Smart product suggestions with ratings and reviews
- **Voice Features** - Text-to-speech responses for accessibility
- **Streaming Responses** - Real-time AI response generation
- **Interactive UI** - Modern gradient design with smooth animations
- **Smart Context Memory** - Maintains conversation context across interactions

## 📋 Prerequisites

- Python 3.8 or higher
- Groq API Key (free from [Groq Console](https://console.groq.com/))

## 🚀 Installation & Setup

### 1. Clone the Repository
```bash
git clone <your-repository-url>
cd FlipkartChatbot
```

### 3. Install Dependencies
```bash
pip install -r requirements.txt
```

### 4. Set Up Environment Variables
Create a [`.env`](ecommerce-chatbot/.env) file in the root directory:
```env
GROQ_API_KEY=your_groq_api_key_here
```

### 5. Verify Data Files
Ensure the following data files are present in the [`data/`](ecommerce-chatbot/data) directory:
- [`products.json`](ecommerce-chatbot/data/products.json) - Product catalog
- [`orders.json`](ecommerce-chatbot/data/orders.json) - Sample order data

## 🏃‍♂️ Running the Application

### Start the Streamlit App
```bash
streamlit run app.py
python chatbot.py
```

The application will open in your default browser at `http://localhost:8501`

### Alternative Port (if 8501 is busy)
```bash
streamlit run app.py --server.port 8502
```

## 📁 Project Structure

```
ecommerce-chatbot/
├── app.py               # Streamlit application
├── chatbot.py.py        # Main file that renders HTML
├── config.py            # Configuration settings
├── prompts.py           # AI prompts and templates
├── requirements.txt     # Python dependencies
├── .env                 # Environment variables (API keys)
├── .gitignore           # Git ignore rules
├── data/
│   ├── products.json    # Product catalog data
│   └── orders.json      # Sample order data
└── __pycache__/         # Python cache files
```

## 🔧 Configuration

### Environment Variables
Edit [`.env`](ecommerce-chatbot/.env) file:
```env
GROQ_API_KEY=your_groq_api_key_here
```

### AI Model Settings
Modify [`config.py`](ecommerce-chatbot/config.py) to change the AI model:
```python
GROQ_MODEL_NAME = "llama3-8b-8192"  # Default model
# Other options: "mixtral-8x7b-32768", "llama3-70b-8192"
```

### Customizing Prompts
Edit [`prompts.py`](ecommerce-chatbot/prompts.py) to customize:
- System prompts for AI behavior
- Language-specific responses
- Quick action templates


## 📊 Data Management

### Adding New Products
Edit [`data/products.json`](ecommerce-chatbot/data/products.json):
```json
{
  "id": "PROD009",
  "name": "New Product",
  "category": "Category",
  "price": 99.99,
  "description": "Product description",
  "features": ["Feature 1", "Feature 2"],
  "in_stock": true,
  "rating": 4.5,
  "reviews_count": 100
}
```

### Adding New Orders
Edit [`data/orders.json`](ecommerce-chatbot/data/orders.json) with similar structure as existing orders.

## 🤝 Contributing

1. Fork the repository
2. Create a feature branch
3. Make your changes
4. Test thoroughly
5. Submit a pull request

## 📝 License

This project is for educational/demonstration purposes. Please ensure compliance with your organization's policies before commercial use.

---

**Happy Coding! 🎉**

For more information about the underlying technologies:
- [Streamlit Documentation](https://docs.streamlit.io/)
- [Groq API Documentation](https://console.groq.com/docs)
