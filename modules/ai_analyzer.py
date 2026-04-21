import google.generativeai as genai
import json
import re

def get_fallback_data():
    # Agar API fail ho jaye toh yeh professional SEO tips show hongi (UI break nahi hoga)
    return [
        {"title": "Improve Loading Speed", "text": "Optimize your Core Web Vitals by deferring unused Javascript and compressing images to modern WebP format.", "icon": "fa-solid fa-bolt"},
        {"title": "Enhance Content Depth", "text": "Ensure your primary pages have sufficient word count and semantic H1/H2 structures for better entity recognition.", "icon": "fa-solid fa-file-lines"},
        {"title": "Optimize Meta Tags", "text": "Write compelling Title tags (30-60 chars) and Meta Descriptions to improve organic search click-through rates.", "icon": "fa-solid fa-heading"},
        {"title": "Image Accessibility", "text": "Add descriptive ALT attributes to all images to assist search engine crawlers and visually impaired users.", "icon": "fa-solid fa-image"}
    ]

def get_ai_suggestions(seo_data, api_key):
    print("[*] Generating AI Strategic Recommendations...")
    try:
        genai.configure(api_key=api_key)
        model = genai.GenerativeModel('gemini-2.5-flash')
        
        prompt = f"""
        Act as an SEO Expert. Review this website data and provide 4 strict actionable tips.
        Format strictly as a JSON array. Do not add any backticks or markdown outside the array.
        [
          {{"title": "String", "text": "String", "icon": "fa-solid fa-check"}}
        ]
        Data: {seo_data}
        """
        
        response = model.generate_content(prompt)
        text = response.text
        
        # Regex se sirf JSON array nikalna, faltu text ignore karna
        match = re.search(r'\[.*\]', text, re.DOTALL)
        if match:
            return json.loads(match.group(0))
        else:
            return get_fallback_data()
            
    except Exception as e:
        print(f"[-] AI Generation Failed (Quota or Network): {e}")
        return get_fallback_data()