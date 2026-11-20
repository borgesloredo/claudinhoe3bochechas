import sys, subprocess, numpy as np, torch
from transformers import Wav2Vec2FeatureExtractor, Wav2Vec2ForCTC
import json
from huggingface_hub import hf_hub_download
M = "facebook/wav2vec2-xlsr-53-espeak-cv-ft"
fe = Wav2Vec2FeatureExtractor.from_pretrained(M); voc = {v:k for k,v in json.load(open(hf_hub_download(M,"vocab.json"))).items()}; model = Wav2Vec2ForCTC.from_pretrained(M).eval()
def load(p):
    raw = subprocess.run([__import__("os").path.expanduser("~/.local/bin/ffmpeg"), "-v", "error", "-i", p, "-ac", "1", "-ar", "16000", "-f", "f32le", "-"], capture_output=True, check=True).stdout
    return np.frombuffer(raw, np.float32)
for p in sys.argv[1:]:
    a = load(p)
    with torch.no_grad():
        lg = model(fe(a, sampling_rate=16000, return_tensors="pt").input_values).logits[0]
    ids = lg.argmax(-1).tolist()
    print("==", p.split("/")[-1]); import itertools; print(" ".join(voc[i] for i,_ in itertools.groupby(ids) if voc[i] not in ("<pad>","<s>","</s>")))
