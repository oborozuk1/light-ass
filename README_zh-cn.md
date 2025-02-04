# light-ass
处理 ASS 字幕的轻量级的库

## 特性
- 轻松解析 ASS 字幕
- 检查字段类型的有效性
- 解析 ASS 覆盖标签（部分）

## 安装
```
pip install light-ass
```

## 用法
```python
import light_ass

document = light_ass.load("example.ass")
print(document.info)
print(document.styles)
print(document.events)
```

## TODO
- 支持更多部分（section)
- 增加处理 ASS 形状的方法
- 压缩 ASS
- 支持 VSFilterMod 标签

## 开源许可
MIT License
