import requests
from urllib.parse import urlparse

def get_traffic_data(url, api_key):
    print(f"[*] Fetching All Insights from SimilarWeb API for: {url}")
    
    # CRITICAL FIX: Properly parsing domain and removing trailing slashes
    parsed = urlparse(url)
    domain = parsed.netloc if parsed.netloc else parsed.path
    domain = domain.replace('www.', '').strip('/')

    fallback_data = {
        "status": "Demo Mode / Error",
        "global_rank": "N/A", "monthly_visits": "N/A", "bounce_rate": "N/A",
        "pages_per_visit": "N/A", "avg_duration": "N/A", "search_traffic": "N/A",
        "direct_traffic": "N/A", "social_traffic": "N/A", "raw_data": {}
    }

    if not api_key or api_key == "" or api_key == "YOUR_RAPIDAPI_KEY":
        fallback_data["status"] = "API Key Missing"
        return fallback_data

    api_url = "https://similarweb-insights.p.rapidapi.com/all-insights"
    querystring = {"domain": domain}
    headers = {
        "x-rapidapi-key": api_key,
        "x-rapidapi-host": "similarweb-insights.p.rapidapi.com"
    }

    try:
        response = requests.get(api_url, headers=headers, params=querystring, timeout=20)
        
        # Checking for API Rate Limits (Too Many Requests)
        if response.status_code == 429:
            fallback_data["status"] = "API Limit Exceeded"
            return fallback_data
            
        if response.status_code == 200:
            raw_data = response.json()
            
            # Handle standard error messages returned inside 200 OK by API
            if "message" in raw_data and "not found" in raw_data.get("message", "").lower():
                fallback_data["status"] = "Low Traffic Data"
                return fallback_data

            traffic = raw_data.get("Traffic") or {}
            engagement = traffic.get("Engagement") or {}
            sources = traffic.get("Sources") or {}

            # --- BULLETPROOF FORMATTERS (Will not crash on NULL data) ---
            def safe_pct(val):
                try:
                    if val is None or val == "": return "N/A"
                    return f"{float(val) * 100:.1f}%"
                except: return "N/A"

            def safe_time(sec):
                try:
                    if sec is None or sec == "": return "N/A"
                    s = int(float(sec))
                    return f"{s//60:02d}:{s%60:02d}"
                except: return "N/A"

            def safe_rank(val):
                try:
                    if val is None or val == "": return "N/A"
                    return f"#{int(float(val)):,}"
                except: return "N/A"

            def safe_visits(val):
                try:
                    if val is None or val == "": return "N/A"
                    v = float(val)
                    if v >= 1000000: return f"{v/1000000:.1f}M"
                    elif v >= 1000: return f"{v/1000:.1f}K"
                    return str(int(v))
                except: return "N/A"

            def safe_float_str(val):
                try:
                    if val is None or val == "": return "N/A"
                    return f"{float(val):.1f}"
                except: return "N/A"

            rank_val = raw_data.get("GlobalRank", raw_data.get("Rank"))
            visit_val = raw_data.get("EstimatedMonthlyVisits", raw_data.get("Visits"))

            # If all data is completely empty, it means the site is too small for SimilarWeb
            if rank_val is None and visit_val is None and not engagement:
                fallback_data["status"] = "Low Traffic Data"
                return fallback_data

            return {
                "status": "Live Data",
                "global_rank": safe_rank(rank_val),
                "monthly_visits": safe_visits(visit_val),
                "bounce_rate": safe_pct(engagement.get("BounceRate")),
                "pages_per_visit": safe_float_str(engagement.get("PagesPerVisit")),
                "avg_duration": safe_time(engagement.get("TimeOnSite")),
                "search_traffic": safe_pct(sources.get("Search")),
                "direct_traffic": safe_pct(sources.get("Direct")),
                "social_traffic": safe_pct(sources.get("Social")),
                "raw_data": raw_data
            }
        else:
            fallback_data["status"] = f"API Error: {response.status_code}"
            return fallback_data
            
    except Exception as e:
        print(f"[-] Traffic API Exception: {e}")
        fallback_data["status"] = "Connection Failed"
        return fallback_data