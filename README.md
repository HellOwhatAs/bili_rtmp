# bili-rtmp

Get the rtmp address and code of bili even you do not have 50+ fans.  
[《哔哩哔哩第三方开播权限排查指南》](https://www.bilibili.com/blackboard/activity-pSrb2KQb6G.html)

## Setup
```
pip install -r requirements.txt
```
and (Edge and its) webdriver for selenium

## Usage
### 1. Login
```
python main.py login
```
login to bilibili.com in selenium  
Start the live (开始直播) and then stop the live (结束直播) in “Web在线直播”  
when `startLive.pkl` and `stopLive.pkl` appears you can close the login program (press any key)

### 2. Start Live
```
python main.py start
```
this print the rtmp `addr` and `code` in the terminal

### 3. Stop Live
```
python main.py stop
```
