"""
Unicode utilities for consistent UTF-8 handling across the application
"""

import os
import sys
import re
import locale

def setup_utf8_environment():
    """Set up UTF-8 environment for the entire application"""
    
    # Set environment variables
    os.environ['PYTHONIOENCODING'] = 'utf-8'
    os.environ['PYTHONUTF8'] = '1'
    
    # Set locale for UTF-8
    if sys.platform == 'win32':
        try:
            locale.setlocale(locale.LC_ALL, 'en_US.UTF-8')
        except:
            try:
                locale.setlocale(locale.LC_ALL, 'C.UTF-8')
            except:
                pass
    else:
        try:
            locale.setlocale(locale.LC_ALL, 'en_US.UTF-8')
        except:
            try:
                locale.setlocale(locale.LC_ALL, 'C.UTF-8')
            except:
                pass

def clean_unicode_text(text):
    """
    Clean problematic Unicode characters from text while preserving UTF-8 compatibility
    """
    if not text:
        return text
    
    # Ensure text is a string
    if not isinstance(text, str):
        text = str(text)
    
    # First, try to encode/decode with UTF-8
    try:
        text = text.encode('utf-8', errors='ignore').decode('utf-8')
    except:
        text = str(text)
    
    # Remove characters that cause charmap issues on Windows
    # Keep basic ASCII plus common UTF-8 characters, remove problematic symbols
    cleaned = re.sub(r'[\x00-\x08\x0B\x0C\x0E-\x1F\x7F]', '', text)  # Remove control chars
    
    # Remove specific problematic Unicode characters that cause charmap issues
    problematic_chars = [
        '\u2705',  # Check mark
        '\U0001f50d', '\U0001f680', '\U0001f917', '\U0001f527', 
        '\U0001f4cc', '\U0001f4b9', '\U0001f4c8', '\U0001f4bc',
        '\u2713', '\u2714', '\u2717', '\u2718',  # Check/cross marks
        '\u2600', '\u2601', '\u2602', '\u2603',  # Weather symbols
        '\u2610', '\u2611', '\u2612', '\u2613',  # Box drawing
        '\u2190', '\u2191', '\u2192', '\u2193',  # Arrows
        '\u2194', '\u2195', '\u2196', '\u2197', '\u2198', '\u2199',  # More arrows
        '\u21a9', '\u21aa', '\u21ab', '\u21ac',  # More arrows
        '\u21b0', '\u21b1', '\u21b2', '\u21b3', '\u21b4', '\u21b5',  # More arrows
        '\u21c4', '\u21c5', '\u21c6',  # Arrows
        '\u21d0', '\u21d1', '\u21d2', '\u21d3', '\u21d4',  # Double arrows
        '\u21e6', '\u21e7', '\u21e8', '\u21e9',  # Triangle arrows
        '\u21ea', '\u21eb', '\u21ec', '\u21ed', '\u21ee', '\u21ef',  # More arrows
        '\u21f2', '\u21f3', '\u21f4', '\u21f5',  # More arrows
        '\u21f6', '\u21f7', '\u21f8', '\u21f9', '\u21fa', '\u21fb', '\u21fc', '\u21fd', '\u21fe', '\u21ff',  # More arrows
        '\u2200', '\u2201', '\u2202', '\u2203', '\u2204', '\u2205', '\u2206', '\u2207', '\u2208', '\u2209', '\u220a', '\u220b', '\u220c', '\u220d', '\u220e', '\u220f',  # Math symbols
        '\u2210', '\u2211', '\u2212', '\u2213', '\u2214', '\u2215', '\u2216', '\u2217', '\u2218', '\u2219', '\u221a', '\u221b', '\u221c', '\u221d', '\u221e', '\u221f',  # Math symbols
        '\u2220', '\u2221', '\u2222', '\u2223', '\u2224', '\u2225', '\u2226', '\u2227', '\u2228', '\u2229', '\u222a', '\u222b', '\u222c', '\u222d', '\u222e', '\u222f',  # Math symbols
        '\u2230', '\u2231', '\u2232', '\u2233', '\u2234', '\u2235', '\u2236', '\u2237', '\u2238', '\u2239', '\u223a', '\u223b', '\u223c', '\u223d', '\u223e', '\u223f',  # Math symbols
        '\u2240', '\u2241', '\u2242', '\u2243', '\u2244', '\u2245', '\u2246', '\u2247', '\u2248', '\u2249', '\u224a', '\u224b', '\u224c', '\u224d', '\u224e', '\u224f',  # Math symbols
        '\u2250', '\u2251', '\u2252', '\u2253', '\u2254', '\u2255', '\u2256', '\u2257', '\u2258', '\u2259', '\u225a', '\u225b', '\u225c', '\u225d', '\u225e', '\u225f',  # Math symbols
        '\u2260', '\u2261', '\u2262', '\u2263', '\u2264', '\u2265', '\u2266', '\u2267', '\u2268', '\u2269', '\u226a', '\u226b', '\u226c', '\u226d', '\u226e', '\u226f',  # Math symbols
        '\u2270', '\u2271', '\u2272', '\u2273', '\u2274', '\u2275', '\u2276', '\u2277', '\u2278', '\u2279', '\u227a', '\u227b', '\u227c', '\u227d', '\u227e', '\u227f',  # Math symbols
        '\u2280', '\u2281', '\u2282', '\u2283', '\u2284', '\u2285', '\u2286', '\u2287', '\u2288', '\u2289', '\u228a', '\u228b', '\u228c', '\u228d', '\u228e', '\u228f',  # Math symbols
        '\u2290', '\u2291', '\u2292', '\u2293', '\u2294', '\u2295', '\u2296', '\u2297', '\u2298', '\u2299', '\u229a', '\u229b', '\u229c', '\u229d', '\u229e', '\u229f',  # Math symbols
        '\u22a0', '\u22a1', '\u22a2', '\u22a3', '\u22a4', '\u22a5', '\u22a6', '\u22a7', '\u22a8', '\u22a9', '\u22aa', '\u22ab', '\u22ac', '\u22ad', '\u22ae', '\u22af',  # Math symbols
        '\u22b0', '\u22b1', '\u22b2', '\u22b3', '\u22b4', '\u22b5', '\u22b6', '\u22b7', '\u22b8', '\u22b9', '\u22ba', '\u22bb', '\u22bc', '\u22bd', '\u22be', '\u22bf',  # Math symbols
        '\u22c0', '\u22c1', '\u22c2', '\u22c3', '\u22c4', '\u22c5', '\u22c6', '\u22c7', '\u22c8', '\u22c9', '\u22ca', '\u22cb', '\u22cc', '\u22cd', '\u22ce', '\u22cf',  # Math symbols
        '\u22d0', '\u22d1', '\u22d2', '\u22d3', '\u22d4', '\u22d5', '\u22d6', '\u22d7', '\u22d8', '\u22d9', '\u22da', '\u22db', '\u22dc', '\u22dd', '\u22de', '\u22df',  # Math symbols
        '\u22e0', '\u22e1', '\u22e2', '\u22e3', '\u22e4', '\u22e5', '\u22e6', '\u22e7', '\u22e8', '\u22e9', '\u22ea', '\u22eb', '\u22ec', '\u22ed', '\u22ee', '\u22ef',  # Math symbols
        '\u22f0', '\u22f1', '\u22f2', '\u22f3', '\u22f4', '\u22f5', '\u22f6', '\u22f7', '\u22f8', '\u22f9', '\u22fa', '\u22fb', '\u22fc', '\u22fd', '\u22fe', '\u22ff',  # Math symbols
        '\u2300', '\u2301', '\u2302', '\u2303', '\u2304', '\u2305', '\u2306', '\u2307', '\u2308', '\u2309', '\u230a', '\u230b', '\u230c', '\u230d', '\u230e', '\u230f',  # Technical symbols
        '\u2310', '\u2311', '\u2312', '\u2313', '\u2314', '\u2315', '\u2316', '\u2317', '\u2318', '\u2319', '\u231a', '\u231b', '\u231c', '\u231d', '\u231e', '\u231f',  # Technical symbols
        '\u2320', '\u2321', '\u2322', '\u2323', '\u2324', '\u2325', '\u2326', '\u2327', '\u2328', '\u2329', '\u232a', '\u232b', '\u232c', '\u232d', '\u232e', '\u232f',  # Technical symbols
        '\u2330', '\u2331', '\u2332', '\u2333', '\u2334', '\u2335', '\u2336', '\u2337', '\u2338', '\u2339', '\u233a', '\u233b', '\u233c', '\u233d', '\u233e', '\u233f',  # Technical symbols
        '\u2340', '\u2341', '\u2342', '\u2343', '\u2344', '\u2345', '\u2346', '\u2347', '\u2348', '\u2349', '\u234a', '\u234b', '\u234c', '\u234d', '\u234e', '\u234f',  # Technical symbols
        '\u2350', '\u2351', '\u2352', '\u2353', '\u2354', '\u2355', '\u2356', '\u2357', '\u2358', '\u2359', '\u235a', '\u235b', '\u235c', '\u235d', '\u235e', '\u235f',  # Technical symbols
        '\u2360', '\u2361', '\u2362', '\u2363', '\u2364', '\u2365', '\u2366', '\u2367', '\u2368', '\u2369', '\u236a', '\u236b', '\u236c', '\u236d', '\u236e', '\u236f',  # Technical symbols
        '\u2370', '\u2371', '\u2372', '\u2373', '\u2374', '\u2375', '\u2376', '\u2377', '\u2378', '\u2379', '\u237a', '\u237b', '\u237c', '\u237d', '\u237e', '\u237f',  # Technical symbols
        '\u2380', '\u2381', '\u2382', '\u2383', '\u2384', '\u2385', '\u2386', '\u2387', '\u2388', '\u2389', '\u238a', '\u238b', '\u238c', '\u238d', '\u238e', '\u238f',  # Technical symbols
        '\u2390', '\u2391', '\u2392', '\u2393', '\u2394', '\u2395', '\u2396', '\u2397', '\u2398', '\u2399', '\u239a', '\u239b', '\u239c', '\u239d', '\u239e', '\u239f',  # Technical symbols
        '\u23a0', '\u23a1', '\u23a2', '\u23a3', '\u23a4', '\u23a5', '\u23a6', '\u23a7', '\u23a8', '\u23a9', '\u23aa', '\u23ab', '\u23ac', '\u23ad', '\u23ae', '\u23af',  # Technical symbols
        '\u23b0', '\u23b1', '\u23b2', '\u23b3', '\u23b4', '\u23b5', '\u23b6', '\u23b7', '\u23b8', '\u23b9', '\u23ba', '\u23bb', '\u23bc', '\u23bd', '\u23be', '\u23bf',  # Technical symbols
        '\u23c0', '\u23c1', '\u23c2', '\u23c3', '\u23c4', '\u23c5', '\u23c6', '\u23c7', '\u23c8', '\u23c9', '\u23ca', '\u23cb', '\u23cc', '\u23cd', '\u23ce', '\u23cf',  # Technical symbols
        '\u23d0', '\u23d1', '\u23d2', '\u23d3', '\u23d4', '\u23d5', '\u23d6', '\u23d7', '\u23d8', '\u23d9', '\u23da', '\u23db', '\u23dc', '\u23dd', '\u23de', '\u23df',  # Technical symbols
        '\u23e0', '\u23e1', '\u23e2', '\u23e3', '\u23e4', '\u23e5', '\u23e6', '\u23e7', '\u23e8', '\u23e9', '\u23ea', '\u23eb', '\u23ec', '\u23ed', '\u23ee', '\u23ef',  # Technical symbols
        '\u23f0', '\u23f1', '\u23f2', '\u23f3', '\u23f4', '\u23f5', '\u23f6', '\u23f7', '\u23f8', '\u23f9', '\u23fa', '\u23fb', '\u23fc', '\u23fd', '\u23fe', '\u23ff',  # Technical symbols
    ]
    
    for char in problematic_chars:
        cleaned = cleaned.replace(char, '')
    
    # Final safety: ensure we can encode to ASCII for Windows charmap compatibility
    try:
        cleaned.encode('ascii', errors='ignore')
    except:
        # If still problematic, force ASCII-only
        cleaned = cleaned.encode('ascii', errors='ignore').decode('ascii')
    
    return cleaned

def safe_print(text):
    """Print text safely with UTF-8 handling"""
    try:
        print(text)
    except UnicodeEncodeError:
        print(clean_unicode_text(str(text)))

def safe_file_read(filepath, encoding='utf-8'):
    """Read file with UTF-8 fallback handling"""
    try:
        with open(filepath, 'r', encoding=encoding) as f:
            return f.read()
    except UnicodeDecodeError:
        try:
            with open(filepath, 'r', encoding='utf-8', errors='ignore') as f:
                return f.read()
        except:
            with open(filepath, 'r', encoding='ascii', errors='ignore') as f:
                return f.read()

def safe_file_write(filepath, content, encoding='utf-8'):
    """Write file with UTF-8 handling"""
    content = clean_unicode_text(content)
    try:
        with open(filepath, 'w', encoding=encoding) as f:
            f.write(content)
    except UnicodeEncodeError:
        with open(filepath, 'w', encoding='ascii', errors='ignore') as f:
            f.write(content)

# Initialize UTF-8 environment when module is imported
setup_utf8_environment()
