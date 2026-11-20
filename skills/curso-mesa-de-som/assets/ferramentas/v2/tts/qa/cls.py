import sys, os, subprocess, numpy as np, torch
from transformers import Wav2Vec2ForSequenceClassification, Wav2Vec2FeatureExtractor
M = "lgris/portuguese-accent-classifier"
m, fe = Wav2Vec2ForSequenceClassification.from_pretrained(M).eval(), Wav2Vec2FeatureExtractor.from_pretrained(M)
assert m.config.id2label[0] == "pt_br"
for p in sys.argv[1:]:
    a = np.frombuffer(subprocess.run([os.path.expanduser("~/.local/bin/ffmpeg"), "-v", "error", "-i", p, "-ac", "1", "-ar", "16000", "-f", "f32le", "-"], capture_output=True, check=True).stdout, np.float32)
    jan = [a[i:i + 64000] for i in range(0, len(a) - 32000, 64000)]   # janelas de 4 s, sem tirar silencio
    with torch.no_grad():
        ps = [float(m(fe(j, sampling_rate=16000, return_tensors="pt").input_values).logits.softmax(-1)[0, 0]) for j in jan]
    print(f"{p.split('/')[-2]+'/'+p.split('/')[-1]:45s} p(pt_br) media {np.mean(ps):.2f}  min {min(ps):.2f}  janelas BR(>0.5) {sum(x>0.5 for x in ps)}/{len(ps)}  pior {int(np.argmin(ps))*4}-{int(np.argmin(ps))*4+4}s")
