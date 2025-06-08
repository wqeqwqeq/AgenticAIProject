# 🔍 Search Engine Redirect Bookmarklet

A JavaScript bookmarklet that captures your current search query from any supported search engine and redirects it to an alternative search engine. Perfect for comparing search results across different platforms!

## 🚀 Features

- **Multi-Engine Support**: Works with Google, Bing, Yahoo, DuckDuckGo, and Baidu
- **Automatic Query Extraction**: Intelligently extracts search queries from different URL formats
- **One-Click Redirection**: Opens alternative search results in a new tab
- **URL Encoding**: Properly handles special characters and spaces in search queries

## 📋 Installation

### Method 1: Using the Demo Page
1. Open `demo.html` in your browser
2. Click the "📋 Copy Bookmarklet" button
3. Create a new bookmark in your browser
4. Paste the copied code as the bookmark URL
5. Name it something like "Search Redirect"

### Method 2: Manual Installation
1. Copy the code from `bookmarklet-minified.js`
2. Create a new bookmark in your browser
3. Paste the code as the bookmark URL
4. Save the bookmark

## 🔄 Supported Search Engine Redirects

| From | To |
|------|-----|
| Google | Baidu |
| Bing | Google |
| Yahoo | DuckDuckGo |
| DuckDuckGo | Google |
| Baidu | Google |

## 🛠️ How It Works

1. **URL Detection**: The bookmarklet detects which search engine you're currently on
2. **Query Extraction**: It extracts the search query using the appropriate URL parameter:
   - Google: `q` parameter
   - Bing: `q` parameter  
   - Yahoo: `p` parameter
   - DuckDuckGo: `q` parameter
   - Baidu: `wd` parameter
3. **URL Construction**: Builds a new search URL for the alternative engine
4. **Redirection**: Opens the new search in a new browser tab

## 💡 Usage Example

**Scenario**: You're browsing Google search results for "javascript tutorials"
- **Current URL**: `https://www.google.com/search?q=javascript+tutorials`
- **Click bookmarklet**
- **Opens**: `https://www.baidu.com/s?wd=javascript+tutorials`

## 📁 Project Files

- `search-redirect-bookmarklet.js` - Readable version of the bookmarklet code
- `bookmarklet-minified.js` - Minified version for actual use
- `demo.html` - Interactive demo page with installation instructions
- `README.md` - This documentation file

## 🔧 Customization

To modify which search engines redirect to which alternatives, edit the `alternativeEngines` object in the source code:

```javascript
const alternativeEngines = {
    'Google': 'https://www.baidu.com/s?wd=',
    'Bing': 'https://www.google.com/search?q=',
    'Yahoo': 'https://duckduckgo.com/?q=',
    'DuckDuckGo': 'https://www.google.com/search?q=',
    'Baidu': 'https://www.google.com/search?q='
};
```

## ⚠️ Browser Compatibility

This bookmarklet works in all modern browsers that support:
- ES6 JavaScript features
- `URL` constructor
- `URLSearchParams`

## 🤝 Contributing

Feel free to submit issues and enhancement requests! To add support for additional search engines:

1. Add the search engine to the `searchEngines` object with its URL pattern and query parameter
2. Add a corresponding entry in the `alternativeEngines` object
3. Test with actual search URLs from that engine

## 📜 License

This project is open source and available under the MIT License. 