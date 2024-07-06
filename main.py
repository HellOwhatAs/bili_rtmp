from selenium import webdriver
import pickle, os, requests, json, pprint
from selenium.webdriver.edge.options import Options
from selenium.webdriver.edge.service import Service

from mitmproxy import http
from mitmproxy.tools.main import mitmdump
import multiprocessing, argparse

COOKIES = 'cookies.pkl'
START_LIVE = "startLive"
STOP_LIVE = "stopLive"

def request(flow: http.HTTPFlow) -> None:
    if flow.request.method == "POST":
        for symbol in (START_LIVE, STOP_LIVE):
            if symbol in flow.request.url:
                with open(f"{symbol}.pkl", "wb") as f:
                    pickle.dump(flow.request, f)
        with open('network_requests.txt', 'a') as f:
            f.write(f'{flow.request.method} {flow.request.url}\n')

def startLive():
    fp = f"{START_LIVE}.pkl"
    if not os.path.exists(fp): raise "Please login first"
    with open(fp, 'rb') as f:
        start_request: http.Request = pickle.load(f)

    headers = dict(start_request.headers)
    headers['cookie'] = ' '.join(f'{k}={v};' for k, v in start_request.cookies.items())

    resp = requests.post(
        start_request.url,
        data={i[:i.find('=')]: i[i.find('=')+1:] for i in start_request.content.decode().split('&')},
        headers=headers
    )

    if resp.status_code == 200:
        rtmp = json.loads(resp.content)['data']['rtmp']
        pprint.pprint({k: rtmp[k] for k in ('addr', 'code')})
    else: raise resp

def stopLive():
    with open(f"{STOP_LIVE}.pkl", 'rb') as f:
        stop_request: http.Request = pickle.load(f)

    headers = dict(stop_request.headers)
    headers['cookie'] = ' '.join(f'{k}={v};' for k, v in stop_request.cookies.items())

    resp = requests.post(
        stop_request.url,
        data={i[:i.find('=')]: i[i.find('=')+1:] for i in stop_request.content.decode().split('&')},
        headers=headers
    )

    if resp.status_code == 200:
        print("Live stopped")
    else: raise resp

class Driver(webdriver.Edge):
    def __init__(self, options: Options = None, service: Service = None, keep_alive: bool = True) -> None:
        super().__init__(options, service, keep_alive)
    
    def save_cookies(self, path):
        with open(path, 'wb') as file:
            pickle.dump(self.get_cookies(), file)

    def load_cookies(self, path):
        with open(path, 'rb') as file:
            cookies = pickle.load(file)
            for cookie in cookies:
                self.add_cookie(cookie)

    def login(self):
        self.get('https://bilibili.com/')
        input("[Press any key after Login]")
        self.get("https://live.bilibili.com/p/html/web-hime/index.html")
        self.save_cookies(COOKIES)

if __name__ == "__main__":

    parser = argparse.ArgumentParser(description="a tool for bilibili live code")
    subparsers = parser.add_subparsers(dest="command")
    parser_login = subparsers.add_parser("login", help="login via selenium")
    parser_login.add_argument("-p", "--port", type=int, default=8080, help="port of mitmproxy")
    parser_start = subparsers.add_parser("start", help="start live")
    parser_stop = subparsers.add_parser("stop", help="stop live")

    args = parser.parse_args()
    if args.command == "start": startLive()
    elif args.command == "stop": stopLive()
    elif args.command == "login":
        PORT = str(args.port)
        multiprocessing.Process(target=mitmdump, args=(['-s', __file__, "-p", PORT],)).start()

        options = webdriver.EdgeOptions()
        options.add_argument(f'--proxy-server=http://127.0.0.1:{PORT}')
        options.add_argument('--ignore-certificate-errors')
        browser = Driver(options=options)

        if not os.path.exists(COOKIES):
            browser.login()
        else:
            browser.get("https://live.bilibili.com/p/html/web-hime/index.html")
            browser.load_cookies(COOKIES)
            browser.refresh()
        
        input('[Press any key after "开始直播" and "结束直播"]')
        browser.quit()
    else: parser.print_help()