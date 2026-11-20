# Revisao independente de sotaque: CTC de fonemas (wav2vec2 espeak) + janelas de palavra do Whisper + medidas acusticas proprias.
import sys, os, json, subprocess, itertools, re, numpy as np, torch
from transformers import Wav2Vec2FeatureExtractor, Wav2Vec2ForCTC
from huggingface_hub import hf_hub_download
M = "facebook/wav2vec2-xlsr-53-espeak-cv-ft"
fe = Wav2Vec2FeatureExtractor.from_pretrained(M); model = Wav2Vec2ForCTC.from_pretrained(M).eval()
voc = json.load(open(hf_hub_download(M, "vocab.json"))); inv = {v: k for k, v in voc.items()}
FF = os.path.expanduser("~/.local/bin/ffmpeg")
VOW = set("aeiouɐɛɔɨəʊɪyøœɯɤæɑɒʌ")
def isvow(p): return any(c in VOW for c in p)
def load(p, sr):
    r = subprocess.run([FF, "-v", "error", "-i", p, "-ac", "1", "-ar", str(sr), "-f", "f32le", "-"], capture_output=True, check=True).stdout
    return np.frombuffer(r, np.float32).copy()

# marcadores: (palavra, ocorrencia, vogais esperadas, tipo de traco)
TI = ["noite", "gente", "diferente", "ativo", "teste"]           # t+i -> [tʃ] no BR
SCODA = [("está", 0), ("ajustando", 0), ("estúdio", 0), ("depois", 0), ("mesmo", 0), ("teste", 0), ("pois", 0), ("está", 1), ("vamos", 0)]
SCODA_POS = {"pois": -1, "vamos": -1, "depois": -1}               # sibilante final; nas outras, a primeira
VOGAIS = {"noite": 2, "tarde": 2, "gente": 2, "diferente": 4, "ativo": 3, "deixe": 2, "depois": 2, "desligue": 3,
          "verdade": 3, "teste": 2, "simples": 2, "pronto": 2, "equipe": 3, "para": 2, "fazer": 2, "agora": 3,
          "confira": 3, "tempo": 2, "ataque": 3, "mesmo": 2, "estúdio": 4, "ajustando": 4}

def analisa(audio, wj):
    a16 = load(audio, 16000); a = load(audio, 22050)
    with torch.no_grad():
        lp = torch.log_softmax(model(fe(a16, sampling_rate=16000, return_tensors="pt").input_values).logits[0], -1).numpy()
    ids = lp.argmax(-1); fr = 0.02
    words = [(re.sub(r"[^\wà-ü]", "", w["word"].lower()), w["start"], w["end"]) for s in json.load(open(wj))["segments"] for w in s["words"]]
    def win(word, occ=0, pad=0.06):
        hits = [w for w in words if w[0] == word]
        return (hits[occ][1] - pad, hits[occ][2] + pad) if len(hits) > occ else None
    def phones(t0, t1):
        f0, f1 = int(t0 / fr), int(t1 / fr) + 1
        out = []
        for k, g in itertools.groupby(range(f0, min(f1, len(ids))), key=lambda i: ids[i]):
            g = list(g); p = inv[k]
            if p not in ("<pad>", "<s>", "</s>"): out.append((p, g[0] * fr, (g[-1] + 1) * fr))
        return out
    # espectro curto (hop 5 ms, janela 10 ms)
    hop, n = int(0.005 * 22050), int(0.010 * 22050)
    frames = np.lib.stride_tricks.sliding_window_view(a, n)[::hop] * np.hanning(n)
    S = np.abs(np.fft.rfft(frames, 512)) ** 2; f = np.fft.rfftfreq(512, 1 / 22050)
    hf = S[:, (f > 3000)].sum(1) / (S.sum(1) + 1e-12)                      # fracao de energia acima de 3 kHz
    en = 10 * np.log10(S.sum(1) + 1e-12); en -= en.max()
    fric = (hf > 0.6) & (en > -50)
    res = {}
    # (1) palatalizacao: chiado continuo depois do burst do t (procura em [t-30ms, t+180ms])
    for w in TI:
        wi = win(w)
        if not wi: res[f"tʃ {w}"] = None; continue
        ph = [p for p in phones(*wi) if p[0] in ("t", "tʃ", "ts", "θ")]
        if not ph: res[f"tʃ {w}"] = None; continue
        t = ph[-1][1] if w != "ativo" else ph[0][1]                         # ultimo t (te final) / t de ativo
        i0, i1 = int((t - 0.03) / 0.005), int((t + 0.18) / 0.005)
        run, best = 0, 0
        for v in fric[i0:i1]:
            run = run + 1 if v else 0; best = max(best, run)
        pt = np.exp(lp[int((t - 0.04) / fr): int((t + 0.1) / fr) + 1, [voc["tʃ"], voc["ts"]]]).sum(1).max()
        res[f"tʃ {w}"] = (best * 5, round(float(pt), 2))
    # (2) "s" de coda: pico espectral da sibilante (s ~ 6-9 kHz, ʃ ~ 2.5-4.5 kHz)
    for w, occ in SCODA:
        wi = win(w, occ)
        sib = [p for p in phones(*wi) if p[0] in ("s", "z", "ʃ", "ʒ")] if wi else []
        if not sib: res[f"s {w}{occ or ''}"] = None; continue
        p = sib[SCODA_POS.get(w, 0)]
        i0, i1 = int((p[1] - 0.03) / 0.005), int((p[2] + 0.03) / 0.005)
        sel = [i for i in range(i0, min(i1, len(fric))) if fric[i]] or list(range(i0, i1))
        spec = S[sel].mean(0); band = (f > 2000) & (f < 10500)
        res[f"s {w}{occ or ''}"] = int(np.sum(f[band] * spec[band]) / np.sum(spec[band]))  # centroide 2-10.5 kHz
    # (3) reducao vocalica: vogais reconhecidas / esperadas por palavra
    got = exp = 0; falta = []
    for w, e in VOGAIS.items():
        wi = win(w)
        if not wi: continue
        v = sum(isvow(p[0]) for p in phones(wi[0] + 0.03, wi[1] - 0.03)); got += min(v, e); exp += e
        if v < e: falta.append(f"{w}:{v}/{e}")
    res["vogais"] = (got, exp, falta)
    return res

for audio in sys.argv[1:]:
    nome = os.path.splitext(os.path.basename(audio))[0]
    r = analisa(audio, os.path.join(os.path.dirname(audio), "..", "wh", nome + ".json"))
    print("==", nome); print(json.dumps(r, ensure_ascii=False))
