import pickle, os, requests, json, pprint
# ifEdge
from selenium.webdriver import Edge as Driver
from selenium.webdriver.edge.options import Options
from selenium.webdriver.edge.service import Service
from webdriver_manager.microsoft import EdgeChromiumDriverManager as DriverManager
# fi
from mitmproxy import http
from mitmproxy.tools.main import mitmdump
import multiprocessing, argparse
from typing import Literal

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

def live(command: Literal["start", "stop"]):
    fp = f"{START_LIVE if command == 'start' else STOP_LIVE}.pkl"
    if not os.path.exists(fp): raise "Please login first"
    with open(fp, 'rb') as f:
        request: http.Request = pickle.load(f)

    headers = dict(request.headers)
    headers['cookie'] = ' '.join(f'{k}={v};' for k, v in request.cookies.items())

    resp = requests.post(
        request.url,
        data={i[:i.find('=')]: i[i.find('=')+1:] for i in request.content.decode().split('&')},
        headers=headers
    )

    if resp.status_code == 200:
        if command == "start":
            rtmp = json.loads(resp.content)['data']['rtmp']
            pprint.pprint({k: rtmp[k] for k in ('addr', 'code')})
        else:
            print("Live stopped")
    else: raise resp

class MyDriver(Driver):
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
        input("[Press Enter after Login]")
        self.get("https://live.bilibili.com/p/html/web-hime/index.html")
        self.save_cookies(COOKIES)

if __name__ == "__main__":

    parser = argparse.ArgumentParser(description="Get the rtmp address (服务器) and code (推流码) of bili (B站) even if you do not have 50+ fans (≥50粉).")
    subparsers = parser.add_subparsers(dest="command")
    parser_login = subparsers.add_parser("login", help="Login to bili via selenium, generating `cookies.pkl`, `startLive.pkl`, and `stopLive.pkl`")
    parser_login.add_argument("-p", "--port", type=int, default=8080, help="port of mitmproxy")
    parser_start = subparsers.add_parser("start", help="Start live, printing `addr` (服务器) and `code` (推流码)")
    parser_stop = subparsers.add_parser("stop", help="Stop live")

    args = parser.parse_args()
    if args.command == "start": live("start")
    elif args.command == "stop": live("stop")
    elif args.command == "login":
        PORT = str(args.port)
        multiprocessing.Process(target=mitmdump, args=(['-s', __file__, "-p", PORT, '-q'],), daemon=True).start()

        options = Options()
        options.add_argument(f'--proxy-server=http://127.0.0.1:{PORT}')
        options.add_argument('--ignore-certificate-errors')
        options.add_experimental_option("excludeSwitches", ["enable-logging"])
        browser = MyDriver(options=options, service=Service(DriverManager().install()))

        if not os.path.exists(COOKIES):
            browser.login()
        else:
            browser.get("https://live.bilibili.com/p/html/web-hime/index.html")
            browser.load_cookies(COOKIES)
            browser.refresh()
        
        input('[Press Enter after "开始直播" and "结束直播"]')
        browser.quit()
    else: parser.print_help()