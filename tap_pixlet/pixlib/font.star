font.HEIGHTS = {
  "tb-8": 8,
  "Dina_r400-6": 10,
  "5x8": 8,
  "6x13": 13,
  "10x20": 20,
  "tom-thumb": 6,
  "CG-pixel-3x5-mono": 5,
  "CG-pixel-4x5-mono": 5,
}

def font.height(font="tb-8"):
  return font.HEIGHTS[font]
