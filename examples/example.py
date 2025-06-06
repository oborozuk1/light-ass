from light_ass import *

ass_text = r"""
[Script Info]
PlayResX: 1920
PlayResY: 1080

[V4+ Styles]
Format: Name, Fontname, Fontsize, PrimaryColour, SecondaryColour, OutlineColour, BackColour, Bold, Italic, Underline, StrikeOut, ScaleX, ScaleY, Spacing, Angle, BorderStyle, Outline, Shadow, Alignment, MarginL, MarginR, MarginV, Encoding
Style: OPJP,FOT-BabyPop Std EB,74,&H003493EF,&H000000FF,&H00FFFFFF,&H14202020,0,0,0,0,100,100,0,0,1,3,0,2,30,30,20,1

[Events]
Format: Layer, Start, End, Style, Name, MarginL, MarginR, MarginV, Effect, Text
Dialogue: 0,0:02:43.14,0:02:45.02,OPJP,,0,0,0,,{\fad(0,500)\t(1,20,\clip(1,2,3,4))}どこへゆこう？
Dialogue: 0,0:03:45.98,0:03:49.75,OPJP,,0,0,0,,Lucky Lucky　まだまだ旅は続く

[Fonts]
fontname: FOT-BabyPop Std EB
data here
"""

doc = Subtitle.from_string(ass_text, drop_unknown_sections=False)

print(doc.styles["OPJP"].color1)  # &H003493EF

parsed = doc.events[0].parse_tags()
print(parsed)
print(tag_parser.join_tags(parsed, skip_comment=True))

# print(doc.to_string())

text = r"{\move(2,3,4,5)\t(1,2,\fs50)}"
parsed = tag_parser.parse_tags(text)
print(parsed[1])
print(parsed[1].is_line_tag)
