# 企业微信Webhook发送指南

## Webhook地址
```
https://qyapi.weixin.qq.com/cgi-bin/webhook/send?key=d3ed6660-1f33-47cc-83dd-84423fc7f8ac
```

## Python发送
```python
import requests

url = "https://qyapi.weixin.qq.com/cgi-bin/webhook/send?key=d3ed6660-1f33-47cc-83dd-84423fc7f8ac"
data = {
    "msgtype": "text",
    "text": {
        "content": "你好，这是一条测试消息"
    }
}
requests.post(url, json=data)
```

## curl发送
```bash
curl -X POST \
'https://qyapi.weixin.qq.com/cgi-bin/webhook/send?key=d3ed6660-1f33-47cc-83dd-84423fc7f8ac' \
-H 'Content-Type: application/json' \
-d '{"msgtype":"text","text":{"content":"Hello World!"}}'
```

## PHP发送
```php
$url = "https://qyapi.weixin.qq.com/cgi-bin/webhook/send?key=d3ed6660-1f33-47cc-83dd-84423fc7f8ac";
$data = json_encode([
    "msgtype" => "text",
    "text" => ["content" => "PHP发送的消息"]
]);

$ch = curl_init();
curl_setopt($ch, CURLOPT_URL, $url);
curl_setopt($ch, CURLOPT_POST, 1);
curl_setopt($ch, CURLOPT_POSTFIELDS, $data);
curl_setopt($ch, CURLOPT_HTTPHEADER, ['Content-Type: application/json']);
curl_exec($ch);
curl_close($ch);
```

## Markdown消息
```python
data = {
    "msgtype": "markdown",
    "markdown": {
        "content": "## 标题\n**重要通知**\n- 任务完成\n- 状态正常"
    }
}
```

## @所有人
```python
data = {
    "msgtype": "text",
    "text": {
        "content": "重要通知",
        "mentioned_list": ["@all"]
    }
}
```

## 注意
- 每分钟最多20条消息
- 文本最长4096字节
- 必须使用UTF-8编码