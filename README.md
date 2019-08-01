# LickDog

如果你是下面一种情况，欢迎使用。

- 不想错过某个微博的内容
- 想关注某个微博，不被博主发现
- 想关注某个微博，但是在博主的黑名单中
- 学习目的

## 使用

```shell
$ python main.py -h
usage: main.py [-h] -u USER_ID -e EMAIL_TO [-n POLL_COUNT] [-t POLL_INTERVAL]

This is a LickDog.

optional arguments:
  -h, --help        show this help message and exit
  -u USER_ID        Input the target weibo id.
  -e EMAIL_TO       Input the result email to.
  -n POLL_COUNT     Poll number.
  -t POLL_INTERVAL  Poll interval(second).
```

`-u` 和 `-e` 为必须参数。

```shell
$ python main.py -u 2656274875 -e your_receive_email@gmail.com
2019-08-01 07:57:04 - WeiboDog.py[229] - Run - INFO: 开始执行任务(WeiboTask(user_id='2656274875', email_to='your_receive_email@gmail.com'))!
2019-08-01 07:57:06 - EmailDog.py[49] - __SendEmail - INFO: email(New blog from 央视新闻 57分钟前) to (your_receive_email@gmail.com) 发送成功！
2019-08-01 07:57:08 - EmailDog.py[49] - __SendEmail - INFO: email(New blog from 央视新闻 6分钟前) to (your_receive_email@gmail.com) 发送成功！
2019-08-01 07:57:09 - EmailDog.py[49] - __SendEmail - INFO: email(New blog from 央视新闻 27分钟前) to (your_receive_email@gmail.com) 发送成功！
```

效果如下：

![new_blog](/Doc/images/new_blog.png)

(PS:最好将邮件提醒打开)

## 注意点

关键的地方有二：

- 一是user_id的获取
- 二是发送端email帐号

### user_id的获取

打开目标微博，`F12` 调试模式，手机模式，刷新后，地址栏后面会有user_id。

![user_id](/Doc/images/user_id.png)

### 发送端email帐号

发送端email需要设置 **第三方授权码**，网易邮箱的过程如下图所示，在设置中选择客户端授权码。(其他邮箱，自行google)

![email_1](/Doc/images/email_1.png)

拿到授权码后，填充 `Base/config.ini` 中的配置。

```ini
[MAIL]
user = your email
password = your email password
host = your email host
```

(PS: 每个邮箱账户每天发送的邮件次数有限。)
