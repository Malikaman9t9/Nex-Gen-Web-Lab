import requests
from bs4 import BeautifulSoup
from urllib.parse import urlparse, urljoin
import time
import urllib3

# Disable SSL warnings for strict sites
urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)

def get_basic_onpage(url):
    print(f"[*] Extracting advanced SEO factors for: {url}")
    try:
        # Premium Headers to bypass basic bot protection
        headers = {
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36',
            'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,image/apng,*/*;q=0.8',
            'Accept-Language': 'en-US,en;q=0.9',
            'Connection': 'keep-alive'
        }
        
        start_time = time.time()
        # verify=False prevents crashes on sites with slight SSL issues
        response = requests.get(url, headers=headers, timeout=15, verify=False)
        response_time = round(time.time() - start_time, 2)
        
        if response.status_code == 200:
            html_text = response.text
            html_size_kb = round(len(response.content) / 1024, 2)
            soup = BeautifulSoup(html_text, 'html.parser')
            
            title_tag = soup.find('title')
            title = title_tag.text.strip() if title_tag else "Missing Title"
            
            meta_desc_tag = soup.find('meta', attrs={'name': 'description'})
            description = meta_desc_tag['content'] if meta_desc_tag else "Missing"
            
            h1_tags = [h1.text.strip() for h1 in soup.find_all('h1')]
            h2_count = len(soup.find_all('h2'))
            h3_count = len(soup.find_all('h3'))
            
            images = soup.find_all('img')
            missing_alt = [img['src'] for img in images if not img.get('alt')]
            
            domain = urlparse(url).netloc
            links = soup.find_all('a', href=True)
            internal_links = [link['href'] for link in links if domain in link['href'] or link['href'].startswith('/')]
            external_links = [link['href'] for link in links if domain not in link['href'] and link['href'].startswith('http')]
            
            canonical_tag = soup.find('link', rel='canonical')
            canonical = canonical_tag['href'] if canonical_tag else "Missing"
            
            robots_tag = soup.find('meta', attrs={'name': 'robots'})
            robots = robots_tag['content'].lower() if robots_tag else "index, follow"
            has_noindex = "Yes" if "noindex" in robots else "No"
            
            html_tag = soup.find('html')
            lang = html_tag.get('lang') if html_tag and html_tag.get('lang') else "Missing"
            
            og_title = soup.find('meta', attrs={'property': 'og:title'})
            og_title_content = og_title['content'] if og_title else "Missing"
            
            text_content = soup.get_text(separator=' ')
            word_count = len(text_content.split())
            
            schema = soup.find('script', type='application/ld+json')
            schema_status = "Found" if schema else "Missing"
            
            is_https = "Yes" if url.startswith("https") else "No"
            
            css_files = [link['href'] for link in soup.find_all('link', rel='stylesheet') if link.get('href')]
            js_files = [script['src'] for script in soup.find_all('script') if script.get('src')]
            unminified_css = sum(1 for css in css_files if '.min.css' not in css)
            unminified_js = sum(1 for js in js_files if '.min.js' not in js)
            
            dir_listing_secured = "Yes"
            try:
                test_dir = urljoin(url, '/wp-includes/')
                dir_resp = requests.get(test_dir, headers=headers, timeout=5, verify=False)
                if "Index of" in dir_resp.text:
                    dir_listing_secured = "No"
            except:
                pass
                
            return {
                'title': title, 'title_count': len(title) if title != "Missing Title" else 0,
                'description': description, 'desc_count': len(description) if description != "Missing" else 0,
                'h1': h1_tags if h1_tags else ["Missing"], 'h2_count': h2_count, 'h3_count': h3_count,
                'total_images': len(images), 'missing_alt': len(missing_alt),
                'internal_links': len(internal_links), 'external_links': len(external_links),
                'canonical': canonical, 'meta_robots': robots, 'has_noindex': has_noindex,
                'lang': lang, 'og_title': og_title_content,
                'word_count': word_count, 'schema': schema_status, 'is_https': is_https,
                'response_time': response_time, 'html_size_kb': html_size_kb,
                'unminified_css': unminified_css, 'unminified_js': unminified_js,
                'dir_listing_secured': dir_listing_secured
            }
        else:
            return None
    except Exception as e:
        print(f"[-] Scraping Failed: {e}")
        return None