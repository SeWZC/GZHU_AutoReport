# GZHU自动打卡

## 运行前设置

如果你想要使用这个脚本进行定时打卡，那么你需要有一个能够一直运行的Linux服务器，或者可以每天使用的电脑

### git下载
```shell
git clone https://github.com/SeWZC/GZHU_AutoReport.git
```

### python安装需求：
```sh
python3 -m pip install -r requirements.txt
```

### 配置文件 `config.json`：
```json
{
  "login": [
    {
      "username": "***",
      "password": "***"
    }
  ]
}
```

### 验证码识别：
在文件`auto_report.py`中有一个`get_captcha_code`，将其实现完成即可<br>
可以在[百度云](https://console.bce.baidu.com/ai/#/ai/ocr/app/list)申请，具体如何使用请查看对应接口的说明<br>
如果仅需要测试可以使用`captcha.py`中的代码，请勿用于正式打卡

### 测试
```sh
python3 auto_report.py
```

## 定时打卡
### Linux
使用crontab即可<br>
输入`crontable -e`进入当前用户的定时文件，在最后一行插入一个任务即可<br>
例如（8：25启动）：
```
25 8 * * * python3 代码所在目录/auto_clock.py >> 代码所在目录/log
```
如果有问题可以搜索crontab解决

### 其他可能可以的定时打卡方式
Windows:
可以使用Win的任务计划，选上错过后尽快执行选项。（未实际测试过）<br>
Android:
可以使用类似Tasker、Automate等软件