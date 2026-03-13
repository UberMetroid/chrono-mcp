#!/usr/bin/env python3
"""
Extract Radical Dreamers dialog - properly handle 0x81 separator
"""

from pathlib import Path
import json

BASE_DIR = Path("/home/jeryd/Code/Chrono_Series")
ROM_PATH = BASE_DIR / "Radical Dreamers" / "BS Radical Dreamers - Le Tresor Interdit (Japan) [T-En by Demiforce v1.4] [n].sfc"
DATA_DIR = BASE_DIR / "data"

rom = open(ROM_PATH, 'rb').read()

# 0x81 = separator between words (shown as @ in hex)
# Normal ASCII = readable text

def decode_rd_text(data):
    results = []
    current_word = []
    current_sentence = []
    
    for b in data:
        if 0x20 <= b <= 0x7E:
            current_word.append(chr(b))
        elif b == 0x81:
            # End of word
            if current_word:
                word = ''.join(current_word)
                if len(word) > 1 or (word.isalpha()):
                    current_sentence.append(word)
                current_word = []
        else:
            # End of sentence/phrase
            if current_sentence and len(current_sentence) >= 2:
                text = ' '.join(current_sentence)
                if len(text) > 5:
                    results.append(text)
            current_word = []
            current_sentence = []
    
    # Don't forget last one
    if current_sentence and len(current_sentence) >= 2:
        text = ' '.join(current_sentence)
        if len(text) > 5:
            results.append(text)
    
    return results

texts = decode_rd_text(rom)
print(f"Found {len(texts)} text segments")

# Filter for English
common = {'the','a','an','is','are','was','were','to','of','and','or','but','in','on','at','for','with','i','you','he','she','it','we','they','my','your','his','her','its','our','their','this','that','what','where','when','why','how','who','can','will','would','could','should','do','does','did','have','has','had','go','come','see','know','think','say','tell','ask','get','give','make','look','want','need','feel','become','leave','put','keep','let','begin','seem','help','show','hear','play','run','move','live','believe','hold','bring','happen','write','provide','sit','stand','lose','pay','meet','include','continue','set','learn','change','lead','understand','watch','follow','stop','create','speak','read','allow','add','spend','grow','open','walk','win','offer','remember','love','consider','appear','buy','wait','serve','die','send','expect','build','stay','fall','cut','reach','kill','remain','suggest','raise','pass','sell','require','report','decide','pull','kid','magil','gil','natsume','radical','dreamer','dreamers','chrono','time','gate','treasure','castle','king','queen','princess','guard','stone','power','mystic','night','world','end','death','life','friend','enemy','fight','battle','save','load','game','start','begin','menu','select','cancel','ok','yes','no','all','some','any','every','much','many','more','most','few','little','big','small','great','good','bad','new','old','first','last','long','short','high','low','right','left','up','down','out','about','into','over','under','again','also','just','only','even','still','ever','never','then','there','here','now','once','away','before','after','while','because','if','unless','until','since','during','through','between','among','about','against','without','within','behind','beyond','like','unlike','near','far','very','too','quite','rather','so','than','such','these','those'}

meaningful = []
for t in texts:
    words = t.lower().split()
    valid = [w for w in words if w in common or (len(w) > 3 and w.isalpha())]
    if len(valid) >= 1:
        meaningful.append(t)

# Dedupe
seen = set()
unique = []
for text in meaningful:
    if text not in seen:
        seen.add(text)
        unique.append(text)

print(f"Unique: {len(unique)}")

with open(DATA_DIR / "radical_dreamers_dialog.json", 'w') as f:
    json.dump(unique[:3000], f, indent=2)

print("Saved")
print("\nSample:")
for line in unique[:30]:
    print(f"  {line}")
