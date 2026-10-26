"""Original schematic illustrations for Part 1. No third-party image assets."""
from pathlib import Path

OUT = Path(__file__).resolve().parents[2] / "frontend/public/toeic/images"
OUT.mkdir(parents=True, exist_ok=True)

def person(x, y, pose="walk", color="#28776c"):
    arms = 'M0 57 L-32 86 M0 57 L30 84' if pose == "carry" else 'M0 55 L-25 80 M0 55 L25 65'
    legs = 'M0 105 L-22 155 M0 105 L25 150' if pose == "walk" else 'M0 105 L-12 155 M0 105 L15 155'
    return f'<g transform="translate({x} {y})"><circle cx="0" cy="15" r="17" fill="#ba805d"/><path d="M0 38 V105" stroke="{color}" stroke-width="28"/><path d="{arms}" stroke="{color}" stroke-width="14" fill="none"/><path d="{legs}" stroke="#344d5a" stroke-width="14" fill="none"/></g>'

scenes = {
 "carrying": person(300,95,"carry") + '<rect x="265" y="165" width="70" height="55" fill="#bc9466" stroke="#725c42"/><path d="M300 165 V220 M265 185 H335" stroke="#725c42"/>',
 "typing": '<rect x="230" y="180" width="220" height="15" fill="#ae8e6b"/><path d="M245 195 V275 M435 195 V275" stroke="#6b604f" stroke-width="12"/><rect x="340" y="110" width="90" height="60" rx="5" fill="#425b64"/><rect x="348" y="118" width="74" height="44" fill="#b7dad4"/><path d="M385 170 V180" stroke="#425b64" stroke-width="8"/><rect x="285" y="173" width="45" height="7" fill="#425b64"/><circle cx="235" cy="95" r="18" fill="#ba805d"/><path d="M235 116 V205 L280 215 V270 M235 135 L275 169 L310 174" fill="none" stroke="#28776c" stroke-width="18"/><path d="M210 150 V225 H265 M220 225 V275" stroke="#344d5a" fill="none" stroke-width="10"/>',
 "watering": person(240,100,"carry") + '<path d="M310 247 L320 282 H370 L380 247Z" fill="#b96b49"/><path d="M345 246 V200 M345 225 Q310 190 320 220 M345 220 Q380 180 369 217" stroke="#43815c" stroke-width="9" fill="none"/><path d="M260 160 H300 V190 H260Z M300 170 L320 185 L312 192" fill="#557fa5" stroke="#315776" stroke-width="3"/><path d="M320 191 L330 211 M326 190 L340 210 M331 190 L348 205" stroke="#6faecc" stroke-width="3"/>',
 "bicycle": '<rect x="125" y="55" width="380" height="165" fill="#e1dbd0"/><path d="M125 110 H505 M125 165 H505 M230 55 V110 M400 55 V110 M320 110 V165 M230 165 V220 M400 165 V220" stroke="#c7bfb0" stroke-width="2"/><g fill="none" stroke-width="6"><circle cx="235" cy="235" r="45" stroke="#364d56"/><circle cx="405" cy="235" r="45" stroke="#364d56"/><path d="M235 235 L280 160 L325 235Z M280 160 H370 L325 235 M370 160 L405 235 M370 160 L360 140 H390 M280 160 L275 140 H300" stroke="#28776c"/></g>',
 "shelves": '<g stroke="#475d67" stroke-width="10"><path d="M140 65 V285 M460 65 V285 M140 130 H460 M140 200 H460 M140 270 H460"/></g>' + ''.join(f'<rect x="{x}" y="{y}" width="{w}" height="{h}" fill="#bd966b" stroke="#806647" stroke-width="2"/><path d="M{x+w//2} {y} V{y+h}" stroke="#806647"/>' for x,y,w,h in [(160,80,70,45),(255,90,65,35),(355,75,80,50),(165,150,90,45),(295,145,60,50),(375,155,60,40),(165,220,55,45),(245,225,85,40),(365,220,70,45)]),
 "table": '<ellipse cx="300" cy="180" rx="125" ry="60" fill="#ad8e69" stroke="#7b674e" stroke-width="4"/><path d="M220 205 V265 M380 205 V265" stroke="#7b674e" stroke-width="10"/>' + ''.join(f'<g transform="translate({x} {y})"><rect width="50" height="40" rx="5" fill="#47756f"/><path d="M5 40 V70 M45 40 V70" stroke="#385b57" stroke-width="6"/></g>' for x,y in [(205,80),(345,80),(165,195),(390,195)]),
 "ladder": '<rect x="340" y="40" width="130" height="245" fill="#dbd6cc"/><g stroke="#977347" stroke-width="9"><path d="M185 280 L340 65 M230 280 L380 65"/>' + ''.join(f'<path d="M{195+int(i*19)} {265-i*27} L{240+int(i*18)} {265-i*27}"/>' for i in range(7)) + '</g>',
 "walking": '<path d="M100 300 L235 80 H370 L520 300" fill="#ded4bd"/>' + person(255,100) + person(370,115,color="#5c6e9a") + '<path d="M40 250 Q90 200 130 250 M470 240 Q540 180 590 240" stroke="#8eac83" stroke-width="20" fill="none"/>'
}
for name, body in scenes.items():
    (OUT / f"{name}.svg").write_text(f'<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 640 330"><rect width="640" height="330" rx="18" fill="#f4f0e7"/><path d="M30 285 H610" stroke="#c8c3b6" stroke-width="3"/>{body}</svg>', encoding="utf-8")
print(f"Wrote {len(scenes)} original illustrations")
