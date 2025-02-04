# light-ass
A lightweight library for handling Advanced SubStation Alpha (ASS) subtitles.

## Features
- Parse ASS subtitles effortlessly
- Check the validity of field types
- Parse ASS override tags (partial)

## Installation
```
pip install light-ass
```

## Usage
```python
import light_ass

document = light_ass.load("example.ass")
print(document.info)
print(document.styles)
print(document.events)
```

## TODO
- Support for more sections
- More methods for ASS shapes
- ASS minifier
- Support for VSFilterMod tags

## License
MIT License
