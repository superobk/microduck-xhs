#!/usr/bin/env python3
"""Create a compact preview from the twenty existing technical covers."""
from pathlib import Path
from PIL import Image
root=Path(__file__).resolve().parents[1]
sheet=Image.new('RGB',(1180,1292),'#f7f4ea')
for i in range(20):
    with Image.open(root/'assets/covers'/f'{i+1:02}.png') as im:
        im=im.convert('RGB');im.thumbnail((216,288))
        sheet.paste(im,(20+(i%5)*232,18+(i//5)*322))
sheet.save(root/'assets/cover-contact-sheet.jpg',quality=90)
