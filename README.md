# bili-rtmp

Get the rtmp address (服务器) and code (推流码) of bili (B站) even if you do not have 50+ fans (≥50粉).  
演示视频：[bili-rtmp 视频使用流程](https://www.bilibili.com/video/BV1VRhme8ECp)
## Setup
```
pip install -r requirements.txt
```
and Edge browser

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
