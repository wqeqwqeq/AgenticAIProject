javascript:(function(){
    // Get current URL
    const currentUrl = window.location.href;
    const url = new URL(currentUrl);
    const hostname = url.hostname.toLowerCase();
    
    // Define search engines and their query parameters
    const searchEngines = {
        // Google
        'www.google.com': { param: 'q', name: 'Google' },
        'google.com': { param: 'q', name: 'Google' },
        
        // Bing
        'www.bing.com': { param: 'q', name: 'Bing' },
        'bing.com': { param: 'q', name: 'Bing' },
        
        // Yahoo
        'search.yahoo.com': { param: 'p', name: 'Yahoo' },
        'yahoo.com': { param: 'p', name: 'Yahoo' },
        
        // DuckDuckGo
        'duckduckgo.com': { param: 'q', name: 'DuckDuckGo' },
        
        // Baidu
        'www.baidu.com': { param: 'wd', name: 'Baidu' },
        'baidu.com': { param: 'wd', name: 'Baidu' }
    };
    
    // Alternative search engines to redirect to
    const alternativeEngines = {
        'Google': 'https://www.baidu.com/s?wd=',
        'Bing': 'https://www.google.com/search?q=',
        'Yahoo': 'https://duckduckgo.com/?q=',
        'DuckDuckGo': 'https://www.google.com/search?q=',
        'Baidu': 'https://www.google.com/search?q='
    };
    
    // Check if current site is a supported search engine
    let currentEngine = null;
    let queryParam = null;
    
    for (const [domain, config] of Object.entries(searchEngines)) {
        if (hostname.includes(domain.replace('www.', '')) || hostname === domain) {
            currentEngine = config.name;
            queryParam = config.param;
            break;
        }
    }
    
    if (!currentEngine) {
        alert('This bookmarklet only works on supported search engines (Google, Bing, Yahoo, DuckDuckGo, Baidu)');
        return;
    }
    
    // Extract the search query
    const searchQuery = url.searchParams.get(queryParam);
    
    if (!searchQuery) {
        alert('No search query found in the current URL');
        return;
    }
    
    // Get alternative search engine URL
    const alternativeUrl = alternativeEngines[currentEngine];
    
    if (!alternativeUrl) {
        alert('No alternative search engine configured for ' + currentEngine);
        return;
    }
    
    // Construct the new URL with the extracted query
    const newUrl = alternativeUrl + encodeURIComponent(searchQuery);
    
    // Open the new URL
    window.open(newUrl, '_blank');
    
})(); 