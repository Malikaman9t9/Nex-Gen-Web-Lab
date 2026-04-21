import asyncio
import aiohttp

async def fetch_strategy_data(session, url, strategy, api_key):
    base_url = "https://www.googleapis.com/pagespeedonline/v5/runPagespeed"
    
    params = {
        'url': url,
        'strategy': strategy,
        'key': api_key,
        'category': ['performance', 'accessibility', 'best-practices', 'seo']
    }
    
    # Default fallback data structure
    fallback_data = {
        'performance':0, 'accessibility':0, 'best-practices':0, 'seo':0,
        'metrics': {
            'fcp': {'value':'N/A', 'score':0}, 'lcp': {'value':'N/A', 'score':0},
            'tbt': {'value':'N/A', 'score':0}, 'cls': {'value':'N/A', 'score':0},
            'si': {'value':'N/A', 'score':0}
        }
    }
    
    try:
        async with session.get(base_url, params=params) as response:
            if response.status == 200:
                data = await response.json()
                cats = data.get('lighthouseResult', {}).get('categories', {})
                audits = data.get('lighthouseResult', {}).get('audits', {})
                
                def get_audit(key):
                    return {
                        'value': audits.get(key, {}).get('displayValue', 'N/A'),
                        'score': audits.get(key, {}).get('score', 0)
                    }

                return strategy, {
                    'performance': int(cats.get('performance', {}).get('score', 0) * 100),
                    'accessibility': int(cats.get('accessibility', {}).get('score', 0) * 100),
                    'best-practices': int(cats.get('best-practices', {}).get('score', 0) * 100),
                    'seo': int(cats.get('seo', {}).get('score', 0) * 100),
                    'metrics': {
                        'fcp': get_audit('first-contentful-paint'),
                        'lcp': get_audit('largest-contentful-paint'),
                        'tbt': get_audit('total-blocking-time'),
                        'cls': get_audit('cumulative-layout-shift'),
                        'si': get_audit('speed-index')
                    }
                }
            else:
                return strategy, fallback_data
    except Exception as e:
        print(f"[-] Speed API Error for {strategy}: {e}")
        return strategy, fallback_data

async def run_speed_test(url, api_key):
    async with aiohttp.ClientSession() as session:
        tasks = [
            fetch_strategy_data(session, url, 'mobile', api_key),
            fetch_strategy_data(session, url, 'desktop', api_key)
        ]
        results = await asyncio.gather(*tasks)
        return {k: v for k, v in results}

def check_speed(url, api_key):
    print(f"[*] Analyzing Deep Core Web Vitals for: {url}")
    return asyncio.run(run_speed_test(url, api_key))