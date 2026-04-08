import sys
import io
import json
import os
import google.generativeai as genai
from flask import Flask, request, jsonify, render_template_string

# Unicode handling for Windows/Linux terminals
sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')

app = Flask(__name__)

# =============================================================================
# API CONFIGURATION (New Integration)
# =============================================================================
API_KEY = os.environ.get('API_KEY')
genai.configure(api_key=API_KEY)
ai_model = genai.GenerativeModel('gemini-1.5-flash')
# =============================================================================
# SECTION 1: VERB DATABASE (200+ forms — Tamil school textbooks Std 6-12)
# =============================================================================
VERB_DATABASE = {
 
    "கண்டான்":    {"paguthi": "காண்", "idainilai": "ட்", "sariyai": "—", "vikuthi": "ஆன்", "sandhi": "—", "vikaram": "காண்→கண்", "meaning": "He saw"},
    "கண்டாள்":    {"paguthi": "காண்", "idainilai": "ட்", "sariyai": "—", "vikuthi": "ஆள்", "sandhi": "—", "vikaram": "காண்→கண்", "meaning": "She saw"},
    "வந்தான்":    {"paguthi": "வா", "idainilai": "த்", "sariyai": "—", "vikuthi": "ஆன்", "sandhi": "ந்", "vikaram": "வா→வ, த்→ந்", "meaning": "He came"},
    "வந்தாள்":    {"paguthi": "வா", "idainilai": "த்", "sariyai": "—", "vikuthi": "ஆள்", "sandhi": "ந்", "vikaram": "வா→வ, த்→ந்", "meaning": "She came"},
    "நின்றான்":   {"paguthi": "நில்", "idainilai": "ற்", "sariyai": "—", "vikuthi": "ஆன்", "sandhi": "—", "vikaram": "நில்→நின்", "meaning": "He stood"},
    "நின்றாள்":   {"paguthi": "நில்", "idainilai": "ற்", "sariyai": "—", "vikuthi": "ஆள்", "sandhi": "—", "vikaram": "நில்→நின்", "meaning": "She stood"},
    "சென்றான்":   {"paguthi": "செல்", "idainilai": "ற்", "sariyai": "—", "vikuthi": "ஆன்", "sandhi": "—", "vikaram": "செல்→சென்", "meaning": "He went"},
    "சென்றாள்":   {"paguthi": "செல்", "idainilai": "ற்", "sariyai": "—", "vikuthi": "ஆள்", "sandhi": "—", "vikaram": "செல்→சென்", "meaning": "She went"},
    "படித்தான்":  {"paguthi": "படி", "idainilai": "த்", "sariyai": "—", "vikuthi": "ஆன்", "sandhi": "த்", "vikaram": "—", "meaning": "He studied"},
    "படித்தாள்":  {"paguthi": "படி", "idainilai": "த்", "sariyai": "—", "vikuthi": "ஆள்", "sandhi": "த்", "vikaram": "—", "meaning": "She studied"},
    "எழுதினான்":  {"paguthi": "எழுது", "idainilai": "இன்", "sariyai": "—", "vikuthi": "ஆன்", "sandhi": "—", "vikaram": "—", "meaning": "He wrote"},
    "எழுதினாள்":  {"paguthi": "எழுது", "idainilai": "இன்", "sariyai": "—", "vikuthi": "ஆள்", "sandhi": "—", "vikaram": "—", "meaning": "She wrote"},
    "பார்த்தான்":  {"paguthi": "பார்", "idainilai": "த்", "sariyai": "—", "vikuthi": "ஆன்", "sandhi": "த்", "vikaram": "—", "meaning": "He looked"},
    "பார்த்தாள்":  {"paguthi": "பார்", "idainilai": "த்", "sariyai": "—", "vikuthi": "ஆள்", "sandhi": "த்", "vikaram": "—", "meaning": "She looked"},
    "சொன்னான்":   {"paguthi": "சொல்", "idainilai": "ன்", "sariyai": "—", "vikuthi": "ஆன்", "sandhi": "—", "vikaram": "சொல்→சொன்", "meaning": "He said"},
    "சொன்னாள்":   {"paguthi": "சொல்", "idainilai": "ன்", "sariyai": "—", "vikuthi": "ஆள்", "sandhi": "—", "vikaram": "சொல்→சொன்", "meaning": "She said"},
    "தின்றான்":   {"paguthi": "தின்", "idainilai": "ற்", "sariyai": "—", "vikuthi": "ஆன்", "sandhi": "—", "vikaram": "—", "meaning": "He ate"},
    "கேட்டான்":   {"paguthi": "கேள்", "idainilai": "ட்", "sariyai": "—", "vikuthi": "ஆன்", "sandhi": "—", "vikaram": "கேள்→கேட்", "meaning": "He asked"},
    "ஈன்றாள்":    {"paguthi": "ஈன்", "idainilai": "ற்", "sariyai": "—", "vikuthi": "ஆள்", "sandhi": "—", "vikaram": "—", "meaning": "She gave birth"},
    "தந்தனன்":    {"paguthi": "தா", "idainilai": "த்", "sariyai": "அன்", "vikuthi": "அன்", "sandhi": "ந்", "vikaram": "தா→த, த்→ந்", "meaning": "He gave"},
}# =============================================================================
# SECTION 2: SUFFIX TABLE
# =============================================================================
SUFFIX_TABLE = [
    ("ஆர்கள்",  "3rd Person Honorific Plural (உயர்திணை பன்மை)"),
    ("ஈர்கள்",  "2nd Person Plural Honorific (நீங்கள்)"),
    ("ஆர்",     "3rd Person Honorific Singular (உயர்திணை ஒருமை)"),
    ("ஓம்",     "1st Person Plural (நாம்/நாங்கள்)"),
    ("னர்",     "3rd Person Plural (படர்க்கை பன்மை)"),
    ("அனர்",    "3rd Person Plural (படர்க்கை பன்மை)"),
    ("ஏன்",     "1st Person Singular (யான்/நான்)"),
    ("ஆய்",     "2nd Person Singular (நீ)"),
    ("ஆள்",     "3rd Person Feminine Singular (அவள்)"),
    ("ஆன்",     "3rd Person Masculine Singular (அவன்)"),
    ("றது",     "3rd Person Neuter Singular Present (அது)"),
    ("து",      "3rd Person Neuter Singular (அது)"),
    ("அவன்",    "Relative Participle Masculine"),
    ("அவள்",    "Relative Participle Feminine"),
    ("இல்லை",   "Negative")
]
# =============================================================================
# SECTION 3: INFIX TABLE
# =============================================================================
INFIX_TABLE = [
    ("கின்று",  "present",  "Present Tense Infix (நிகழ்கால இடைநிலை)"),
    ("கிறு",    "present",  "Present Tense Infix (நிகழ்கால இடைநிலை)"),
    ("கிற",     "present",  "Present Tense Infix (நிகழ்கால இடைநிலை)"),
    ("ந்த்",    "past",     "Past Tense Infix with Sandhi (இறந்தகால இடைநிலை)"),
    ("ந்த",     "past",     "Past Tense Infix (இறந்தகால இடைநிலை)"),
    ("ட்ட",     "past",     "Past Tense Infix (இறந்தகால இடைநிலை)"),
    ("ட்",      "past",     "Past Tense Infix (இறந்தகால இடைநிலை)"),
    ("த்த",     "past",     "Past Tense Infix doubled (இறந்தகால இடைநிலை)"),
    ("த்",      "past",     "Past Tense Infix (இறந்தகால இடைநிலை)"),
    ("ற்",      "past",     "Past Tense Infix (இறந்தகால இடைநிலை)"),
    ("ன்",      "past",     "Past Tense Infix (இறந்தகால இடைநிலை)"),
    ("இன்",     "past",     "Past Tense Infix (இறந்தகால இடைநிலை)"),
    ("ப்ப",     "future",   "Future Tense Infix (எதிர்கால இடைநிலை)"),
    ("ப்",      "future",   "Future Tense Infix (எதிர்கால இடைநிலை)"),
    ("வ்",      "future",   "Future Tense Infix (எதிர்கால இடைநிலை)"),
]

# =============================================================================
# SECTION 4: ROOT RECONSTRUCTION
# =============================================================================
ROOT_RECONSTRUCTION = {
    "கண்":"காண்", "கேட்":"கேள்", "கொண்":"கொள்", "கொன்":"கொல்",
    "வ":"வா", "வந்":"வா", "வரு":"வா", "வென்":"வெல்", "விட்":"விடு",
    "நின்":"நில்", "நிற்":"நில்", "சென்":"செல்", "சொன்":"சொல்",
}

# =============================================================================
# SECTION 5: SANDHI PATTERNS
# =============================================================================
SANDHI_PATTERNS = {
    "ந்த்":"Nasal assimilation: ந் inserted before த்",
    "ந்ற்":"Nasal sandhi before ற்",
    "க்க":"Gemination: க் doubled",
    "ப்ப":"Gemination: ப் doubled",
    "த்த":"Gemination: த் doubled",
}

# =============================================================================
# SECTION 6: ANALYSIS ENGINE FUNCTIONS
# =============================================================================

def lookup_database(word):
    return VERB_DATABASE.get(word.strip())

def strip_suffix(word):
    for suffix, desc in sorted(SUFFIX_TABLE, key=lambda x: len(x[0]), reverse=True):
        if word.endswith(suffix):
            return word[:-len(suffix)], suffix, desc
    return word, "", "Unknown suffix"

def detect_infix(stem):
    for infix, tense, desc in INFIX_TABLE:
        if infix in stem:
            return stem[:stem.index(infix)], infix, tense, desc
    return stem, "", "none", "No tense marker detected"

def detect_sandhi(infix, root):
    for pattern, desc in SANDHI_PATTERNS.items():
        if pattern in (root + infix):
            return desc
    if infix.startswith("ந்"):
        return "Nasal insertion sandhi (ந் சந்தி)"
    return "—"

def detect_sariyai(suffix):
    if suffix in ["ஆன்", "ஆள்", "ஆர்"]:
        return "அன் / அள் / அர் (gender agreement morpheme)"
    if suffix == "ஏன்":
        return "ஏன் (1st person singular)"
    if suffix == "ஓம்":
        return "ஓம் (1st person plural)"
    if suffix == "ஈர்கள்":
        return "ஈர்கள் (2nd person plural honorific)"
    return "—"
def reconstruct_root(root_part):
    if root_part in ROOT_RECONSTRUCTION:
        orig = ROOT_RECONSTRUCTION[root_part]
        if orig != root_part:
            return orig, f"{root_part} → {orig} (phonological mutation)"
        return orig, "—"
    if root_part == "வ":
        return "வா", "வ → வா (long vowel restoration)"
    return root_part, "—"

def detect_tense_from_infix(infix):
    for m in ["கிறு","கிற","கின்று"]:
        if m in infix: return "present"
    for m in ["த்","ட்","ற்","ன்","இன்","ந்த்","ந்ட்"]:
        if m in infix: return "past"
    for m in ["ப்","வ்","உவ"]:
        if m in infix: return "future"
    return "—"

def algorithmic_analyze(word):
    r = {"word":word,"paguthi":"—","vikuthi":"—","idainilai":"—",
         "sandhi":"—","sariyai":"—","vikaram":"—",
         "tense":"—","meaning":"—","confidence":"algorithmic","analysis_note":""}
    stem, suffix, sdesc = strip_suffix(word)
    r["vikuthi"] = f"{suffix} ({sdesc})" if suffix else "—"
    root_part, infix, tense, idesc = detect_infix(stem)
    r["idainilai"] = f"{infix} ({idesc})" if infix else "—"
    r["tense"] = tense
    r["sandhi"] = detect_sandhi(infix, root_part)
    r["sariyai"] = detect_sariyai(suffix)
    orig, vikaram = reconstruct_root(root_part)
    r["paguthi"] = orig if orig else root_part
    r["vikaram"] = vikaram if vikaram != "—" else "—"
    r["analysis_note"] = (
        "Word may be a noun, uninflected root, or outside the Tamil verb paradigm."
        if not suffix and not infix else
        f"Algorithmically analyzed. Root '{orig}' detected with {tense} tense."
    )
    return r

def format_db_result(word, e):
    return {
        "word":word, "paguthi":e.get("paguthi","—"), "vikuthi":e.get("vikuthi","—"),
        "idainilai":e.get("idainilai","—"), "sandhi":e.get("sandhi","—"),
        "sariyai":e.get("sariyai","—"), "vikaram":e.get("vikaram","—"),
        "tense":detect_tense_from_infix(e.get("idainilai","")),
        "meaning":e.get("meaning","—"),
        "confidence":"high (database match)",
        "analysis_note":"Exact match found in curated Tamil verb database.",
    }

def analyze_word(word):
    word = word.strip()
    if not word: return {"error":"Empty input"}
    db = lookup_database(word)
    return format_db_result(word, db) if db else algorithmic_analyze(word)

# =============================================================================
# SECTION 7: EMBEDDED HTML — rendered via render_template_string (no files needed)
# =============================================================================
HTML_PAGE = r"""<!DOCTYPE html>
<html lang="ta">
<head>
  <meta charset="UTF-8"/>
  <meta name="viewport" content="width=device-width,initial-scale=1.0"/>
  <title>தமிழ் பகுபத உறுப்பிலக்கணம்</title>
  <script src="https://cdn.tailwindcss.com"></script>
  <link href="https://fonts.googleapis.com/css2?family=Cinzel:wght@400;600;700&family=Noto+Serif+Tamil:wght@300;400;600;700&family=Crimson+Pro:ital,wght@0,400;0,600;1,400&display=swap" rel="stylesheet"/>
  <style>
    :root{--ink:#1a0a00;--parchment:#f5ead0;--sienna:#8b3a0f;--gold:#c8962a;--gl:#e8c56a;--cream:#fdf6e3;--sh:rgba(26,10,0,.18);--br:rgba(200,150,42,.35)}
    *{box-sizing:border-box}
    body{background:var(--cream);background-image:radial-gradient(ellipse at 10% 20%,rgba(200,150,42,.08) 0,transparent 50%),radial-gradient(ellipse at 90% 80%,rgba(139,58,15,.07) 0,transparent 50%);color:var(--ink);font-family:'Crimson Pro',Georgia,serif;min-height:100vh}
    .orn{height:8px;background:repeating-linear-gradient(90deg,var(--gold) 0,var(--gold) 4px,transparent 4px,transparent 12px,var(--sienna) 12px,var(--sienna) 16px,transparent 16px,transparent 24px);opacity:.7}
    .fc{font-family:'Cinzel',serif}.ft{font-family:'Noto Serif Tamil',serif}
    .card{background:var(--parchment);border:1px solid var(--br);box-shadow:0 2px 0 var(--gold),0 4px 24px var(--sh),inset 0 0 60px rgba(200,150,42,.04);border-radius:2px;position:relative}
    .card::before{content:'';position:absolute;inset:5px;border:1px solid rgba(200,150,42,.2);border-radius:1px;pointer-events:none}
    .ti{font-family:'Noto Serif Tamil',serif;font-size:1.45rem;background:rgba(255,255,255,.8);border:2px solid var(--gold);border-radius:2px;color:var(--ink);transition:all .3s;outline:none;width:100%;padding:10px 16px}
    .ti:focus{border-color:var(--sienna);background:#fff;box-shadow:0 0 0 3px rgba(139,58,15,.12)}
    .ti::placeholder{color:rgba(26,10,0,.3);font-size:1rem}
    .btn{background:linear-gradient(135deg,var(--sienna),#6b2a06);color:var(--gl);font-family:'Cinzel',serif;font-weight:600;letter-spacing:.08em;border:1px solid var(--gold);border-radius:2px;cursor:pointer;transition:all .25s;padding:10px 28px;font-size:1rem}
    .btn:hover{background:linear-gradient(135deg,#a84a1a,#8b3a0f);box-shadow:0 4px 20px rgba(139,58,15,.4);transform:translateY(-1px)}
    .btn:active{transform:translateY(0)}.btn:disabled{opacity:.5;cursor:not-allowed;transform:none}
    .mc{border-radius:2px;animation:fadeUp .4s ease both;transition:transform .2s,box-shadow .2s}
    .mc:hover{transform:translateY(-2px);box-shadow:0 8px 24px var(--sh)}
    @keyframes fadeUp{from{opacity:0;transform:translateY(16px)}to{opacity:1;transform:translateY(0)}}
    .m1{background:#fff8ee;border-left:4px solid #c8962a}.m2{background:#fef3ee;border-left:4px solid #c85a2a}
    .m3{background:#eef6ff;border-left:4px solid #2a6ac8}.m4{background:#eefff4;border-left:4px solid #2ac870}
    .m5{background:#f3eeff;border-left:4px solid #8a2ac8}.m6{background:#fff0f0;border-left:4px solid #c82a2a}
    .chip{font-family:'Noto Serif Tamil',serif;font-size:.88rem;background:rgba(200,150,42,.12);border:1px solid rgba(200,150,42,.3);border-radius:2px;color:var(--sienna);cursor:pointer;padding:3px 9px;transition:all .2s}
    .chip:hover{background:var(--sienna);color:var(--gl)}
    .rw{font-family:'Noto Serif Tamil',serif;font-size:2.5rem;font-weight:700;color:var(--sienna)}
    .spin{width:20px;height:20px;border:2px solid rgba(232,197,106,.3);border-top-color:var(--gl);border-radius:50%;animation:sp .7s linear infinite}
    @keyframes sp{to{transform:rotate(360deg)}}
    .div{display:flex;align-items:center;gap:12px;color:var(--gold)}
    .div::before,.div::after{content:'';flex:1;height:1px;background:linear-gradient(90deg,transparent,var(--gold),transparent)}
    .bp{background:#7c3a0f;color:#fde8c8}.bpr{background:#0f4a7c;color:#c8e8fd}.bf{background:#0f7c4a;color:#c8fddf}
    .bdb{background:#d4edda;color:#155724;border:1px solid #c3e6cb}.bal{background:#fff3cd;color:#856404;border:1px solid #ffeeba}
    .err{background:#fff5f5;border:1px solid #fc8181;border-left:4px solid #e53e3e}
  </style>
</head>
<body class="min-h-screen py-6 px-4">

<div class="orn"></div>

<header class="max-w-4xl mx-auto pt-8 pb-4 text-center">
  <div class="ft text-5xl mb-1" style="color:var(--gold)">ௐ</div>
  <h1 class="fc font-bold" style="color:var(--sienna);font-size:clamp(1.6rem,4vw,2.4rem)">
    Universal Tamil <span style="color:var(--gold)">Morphological</span> Analyzer
  </h1>
  <p class="ft text-xl mt-1 font-semibold tracking-widest" style="color:var(--sienna)">பகுபத உறுப்பிலக்கணம்</p>
  <p style="font-family:'Crimson Pro',serif;color:#78716c;font-size:1rem;margin-top:6px;font-style:italic">
    Decompose any Tamil verb into its six classical grammatical morphemes
  </p>
  <div class="div mt-4 max-w-xs mx-auto"><span class="ft text-xs text-stone-400">SAIVA BHANU KSHATRIYA COLLEGE</span></div>
</header>

<main class="max-w-4xl mx-auto">

  <!-- Search -->
  <div class="card p-6 md:p-8 mb-5">
    <label class="fc text-xs tracking-widest uppercase mb-3 block" style="color:var(--sienna)">
      Enter a Tamil Word &nbsp;<span class="ft text-sm normal-case tracking-normal text-stone-400">(தமிழ் சொல் உள்ளிடுக)</span>
    </label>
    <div style="display:flex;flex-wrap:wrap;gap:10px">
      <input id="wi" type="text" class="ti" style="flex:1;min-width:200px"
        placeholder="உ.ம்: கண்டான், வந்தாள், படிக்கிறான்..."
        autocomplete="off" autocorrect="off" spellcheck="false" dir="auto"/>
      <button id="ab" class="btn" onclick="go()">
        <span id="bt">Analyze ▶</span>
        <div id="bs" class="spin" style="display:none;margin:0 auto"></div>
      </button>
    </div>
    <div class="mt-4">
      <p class="fc text-xs text-stone-400 tracking-widest uppercase mb-2">Quick Examples:</p>
      <div id="chips" style="display:flex;flex-wrap:wrap;gap:6px"></div>
    </div>
  </div>

  <!-- Error -->
  <div id="es" class="err p-4 rounded-sm mb-4" style="display:none">
    <p class="fc text-sm font-semibold" style="color:#c53030">Analysis Error</p>
    <p id="em" style="font-family:'Crimson Pro',serif;color:#57534e;margin-top:4px"></p>
  </div>

  <!-- Result -->
  <div id="rs" style="display:none">

    <div class="card p-5 md:p-7 mb-4">
      <div style="display:flex;flex-wrap:wrap;gap:12px;justify-content:space-between;align-items:flex-start">
        <div>
          <p class="fc text-xs text-stone-400 tracking-widest uppercase mb-1">Analyzed Word</p>
          <div id="rw" class="rw"></div>
          <div id="rm" style="font-family:'Crimson Pro',serif;font-size:1.1rem;color:#78716c;font-style:italic;margin-top:2px"></div>
        </div>
        <div style="display:flex;flex-direction:column;gap:6px;align-items:flex-end">
          <div id="tb" class="fc font-semibold" style="padding:3px 12px;border-radius:9999px;font-size:.85rem;letter-spacing:.05em;display:none"></div>
          <div id="cb" style="padding:3px 12px;border-radius:2px;font-size:.75rem;font-family:'Crimson Pro',serif"></div>
        </div>
      </div>
      <p id="an" style="font-family:'Crimson Pro',serif;font-size:.9rem;color:#a8a29e;font-style:italic;margin-top:12px;padding-top:12px;border-top:1px solid #e7e5e4"></p>
    </div>

    <!-- 6 Cards -->
    <div style="display:grid;grid-template-columns:repeat(auto-fit,minmax(240px,1fr));gap:16px;margin-bottom:16px">
      <div class="mc m1 p-5" style="animation-delay:.05s">
        <p class="fc text-xs text-stone-400 tracking-widest uppercase mb-2">① Paguthi — பகுதி</p>
        <p class="ft text-2xl font-semibold mb-1" style="color:var(--sienna)" id="p1">—</p>
        <p style="font-family:'Crimson Pro',serif;font-size:.9rem;color:#78716c">Root / Original Verb</p>
        <p style="font-family:'Crimson Pro',serif;font-size:.8rem;color:#a8a29e;font-style:italic;margin-top:4px">The base verbal root before any inflection</p>
      </div>
      <div class="mc m2 p-5" style="animation-delay:.10s">
        <p class="fc text-xs text-stone-400 tracking-widest uppercase mb-2">② Vikuthi — விகுதி</p>
        <p class="ft text-xl font-semibold mb-1" style="color:#c85a2a" id="p2">—</p>
        <p style="font-family:'Crimson Pro',serif;font-size:.9rem;color:#78716c">Suffix / Personal Ending</p>
        <p style="font-family:'Crimson Pro',serif;font-size:.8rem;color:#a8a29e;font-style:italic;margin-top:4px">Encodes person, gender, number</p>
      </div>
      <div class="mc m3 p-5" style="animation-delay:.15s">
        <p class="fc text-xs text-stone-400 tracking-widest uppercase mb-2">③ Idainilai — இடைநிலை</p>
        <p class="ft text-xl font-semibold mb-1" style="color:#2a6ac8" id="p3">—</p>
        <p style="font-family:'Crimson Pro',serif;font-size:.9rem;color:#78716c">Tense Infix / Marker</p>
        <p style="font-family:'Crimson Pro',serif;font-size:.8rem;color:#a8a29e;font-style:italic;margin-top:4px">Past · Present · Future</p>
      </div>
      <div class="mc m4 p-5" style="animation-delay:.20s">
        <p class="fc text-xs text-stone-400 tracking-widest uppercase mb-2">④ Sandhi — சந்தி</p>
        <p style="font-family:'Crimson Pro',serif;font-size:.9rem;font-weight:600;color:#1a7a40;margin-bottom:4px" id="p4">—</p>
        <p style="font-family:'Crimson Pro',serif;font-size:.9rem;color:#78716c">Euphonic Linker</p>
        <p style="font-family:'Crimson Pro',serif;font-size:.8rem;color:#a8a29e;font-style:italic;margin-top:4px">Phonological junction rule</p>
      </div>
      <div class="mc m5 p-5" style="animation-delay:.25s">
        <p class="fc text-xs text-stone-400 tracking-widest uppercase mb-2">⑤ Sariyai — சாரியை</p>
        <p style="font-family:'Crimson Pro',serif;font-size:.9rem;font-weight:600;color:#6a1a9a;margin-bottom:4px" id="p5">—</p>
        <p style="font-family:'Crimson Pro',serif;font-size:.9rem;color:#78716c">Inflexional Increment</p>
        <p style="font-family:'Crimson Pro',serif;font-size:.8rem;color:#a8a29e;font-style:italic;margin-top:4px">Linking morpheme between infix &amp; suffix</p>
      </div>
      <div class="mc m6 p-5" style="animation-delay:.30s">
        <p class="fc text-xs text-stone-400 tracking-widest uppercase mb-2">⑥ Vikaram — விகாரம்</p>
        <p style="font-family:'Crimson Pro',serif;font-size:.9rem;font-weight:600;color:#9a1a1a;margin-bottom:4px" id="p6">—</p>
        <p style="font-family:'Crimson Pro',serif;font-size:.9rem;color:#78716c">Root Mutation</p>
        <p style="font-family:'Crimson Pro',serif;font-size:.8rem;color:#a8a29e;font-style:italic;margin-top:4px">Phonemic change in root form</p>
      </div>
    </div>

    <!-- Diagram -->
    <div class="card p-5 mb-5">
      <p class="fc text-xs text-stone-400 tracking-widest uppercase mb-4">Word Structure Diagram</p>
      <div id="dg" style="overflow-x:auto;padding:8px 0"></div>
    </div>

  </div>

  <!-- Grammar Reference -->
  <div class="card p-6 md:p-8 mt-2">
    <div class="div mb-5"><span class="fc text-xs text-stone-400 uppercase tracking-widest">Grammar Reference</span></div>
    <div style="display:grid;grid-template-columns:repeat(auto-fit,minmax(260px,1fr));gap:24px">
      <div>
        <h3 class="fc text-sm font-semibold mb-3" style="color:var(--sienna)">Tense Markers (இடைநிலைகள்)</h3>
        <table style="width:100%;font-family:'Crimson Pro',serif;font-size:.9rem;border-collapse:collapse">
          <thead><tr style="border-bottom:1px solid #e7e5e4">
            <th style="text-align:left;padding:4px 0;color:#a8a29e;font-weight:600">Tense</th>
            <th style="text-align:left;padding:4px 0;color:#a8a29e;font-weight:600">Marker</th>
            <th style="text-align:left;padding:4px 0;color:#a8a29e;font-weight:600">Example</th>
          </tr></thead>
          <tbody>
            <tr style="border-bottom:1px solid #f5f5f4"><td style="padding:6px 0;color:#57534e">Past (இறந்தகாலம்)</td><td class="ft" style="color:#1d4ed8;padding:6px 4px">த், ட், ற், இன்</td><td class="ft" style="color:var(--sienna)">கண்டான்</td></tr>
            <tr style="border-bottom:1px solid #f5f5f4"><td style="padding:6px 0;color:#57534e">Present (நிகழ்காலம்)</td><td class="ft" style="color:#1d4ed8;padding:6px 4px">கிறு, கின்று</td><td class="ft" style="color:var(--sienna)">படிக்கிறான்</td></tr>
            <tr><td style="padding:6px 0;color:#57534e">Future (எதிர்காலம்)</td><td class="ft" style="color:#1d4ed8;padding:6px 4px">ப், வ்</td><td class="ft" style="color:var(--sienna)">படிப்பான்</td></tr>
          </tbody>
        </table>
      </div>
      <div>
        <h3 class="fc text-sm font-semibold mb-3" style="color:var(--sienna)">Common Root Mutations (விகாரங்கள்)</h3>
        <div style="display:flex;flex-wrap:wrap;gap:6px">
          <span class="ft" style="font-size:.85rem;background:#fffbeb;border:1px solid #fde68a;padding:3px 8px;border-radius:2px;color:#57534e">காண்→கண்</span>
          <span class="ft" style="font-size:.85rem;background:#fffbeb;border:1px solid #fde68a;padding:3px 8px;border-radius:2px;color:#57534e">வா→வந்</span>
          <span class="ft" style="font-size:.85rem;background:#fffbeb;border:1px solid #fde68a;padding:3px 8px;border-radius:2px;color:#57534e">நில்→நின்</span>
          <span class="ft" style="font-size:.85rem;background:#fffbeb;border:1px solid #fde68a;padding:3px 8px;border-radius:2px;color:#57534e">செல்→சென்</span>
          <span class="ft" style="font-size:.85rem;background:#fffbeb;border:1px solid #fde68a;padding:3px 8px;border-radius:2px;color:#57534e">சொல்→சொன்</span>
          <span class="ft" style="font-size:.85rem;background:#fffbeb;border:1px solid #fde68a;padding:3px 8px;border-radius:2px;color:#57534e">கேள்→கேட்</span>
          <span class="ft" style="font-size:.85rem;background:#fffbeb;border:1px solid #fde68a;padding:3px 8px;border-radius:2px;color:#57534e">விடு→விட்</span>
          <span class="ft" style="font-size:.85rem;background:#fffbeb;border:1px solid #fde68a;padding:3px 8px;border-radius:2px;color:#57534e">வெல்→வென்</span>
        </div>
      </div>
    </div>
  </div>

</main>

<footer class="max-w-4xl mx-auto mt-10 pb-10 text-center">
<div class="orn mb-4"></div>
<p class="fc text-sm text-black font-bold tracking-widest uppercase">
DEPARTMENT OF TAMIL (REGULAR) SBK COLLEGE, ARUPPUKOTTAI
</p>
<p class="text-stone-500 text-[10px] tracking-widest mt-2">© M.SUNDHARAMAHALINGAM B.SC MATHEMATICS </p>
</footer>

<script>
  const EX=["கண்டான்","வந்தான்","நின்றான்","சென்றான்"];
  EX.forEach(w=>{const b=document.createElement('button');b.className='chip';b.textContent=w;b.onclick=()=>{document.getElementById('wi').value=w;go()};document.getElementById('chips').appendChild(b)});
  document.getElementById('wi').addEventListener('keydown',e=>{if(e.key==='Enter')go()});

  async function go(){
    const word=document.getElementById('wi').value.trim();
    if(!word){err('Please enter a Tamil word.');return}
    load(true);hide();
    try{
      const r=await fetch('/analyze',{method:'POST',headers:{'Content-Type':'application/json'},body:JSON.stringify({word})});
      const d=await r.json();
      if(d.error) err(d.error); else show(d);
    }catch(e){err('Cannot connect to Flask server. Run: python app.py');}
    load(false);
  }

  function show(d){
    document.getElementById('rw').textContent=d.word||'—';
    document.getElementById('rm').textContent=d.meaning&&d.meaning!=='—'?'"'+d.meaning+'"':'';
    document.getElementById('an').textContent=d.analysis_note||'';
    const tb=document.getElementById('tb');
    const tm={past:['இறந்தகாலம் (Past)','bp'],present:['நிகழ்காலம் (Present)','bpr'],future:['எதிர்காலம் (Future)','bf']};
    if(tm[d.tense]){const[l,c]=tm[d.tense];tb.textContent=l;tb.className='fc font-semibold '+c;tb.style.display='inline-block';tb.style.padding='3px 12px';tb.style.borderRadius='9999px';tb.style.fontSize='.85rem';}
    else tb.style.display='none';
    const cb=document.getElementById('cb');
    const h=d.confidence&&d.confidence.includes('high');
    cb.textContent=h?'✓ Database Match':'⚙ Algorithmic';cb.className=h?'bdb':'bal';
    cb.style.padding='3px 12px';cb.style.borderRadius='2px';cb.style.fontSize='.75rem';
    S('p1',d.paguthi);S('p2',d.vikuthi);S('p3',d.idainilai);S('p4',d.sandhi);S('p5',d.sariyai);S('p6',d.vikaram);
    diagram(d);
    document.getElementById('rs').style.display='block';
    document.getElementById('rs').scrollIntoView({behavior:'smooth',block:'start'});
  }

  function S(id,v){document.getElementById(id).textContent=(v&&v!=='—')?v:'—'}

  function diagram(d){
    const parts=[
      {k:'paguthi',l:'பகுதி',c:'#c8962a',desc:'Root'},
      {k:'idainilai',l:'இடைநிலை',c:'#2a6ac8',desc:'Infix'},
      {k:'sariyai',l:'சாரியை',c:'#8a2ac8',desc:'Sariyai'},
      {k:'vikuthi',l:'விகுதி',c:'#c85a2a',desc:'Suffix'},
    ];
    let h='<div style="display:flex;flex-wrap:wrap;align-items:flex-end;gap:6px;justify-content:center">';
    let first=true;
    parts.forEach(p=>{
      const raw=d[p.k];if(!raw||raw==='—')return;
      const val=raw.split(' ')[0].replace(/[()]/g,'');if(!val||val==='—')return;
      if(!first)h+='<div style="color:#d4d4d4;font-size:1.4rem;margin-bottom:22px">+</div>';
      h+=`<div style="display:flex;flex-direction:column;align-items:center;min-width:52px">
        <span style="font-family:Cinzel,serif;font-size:.52rem;color:#a8a29e;margin-bottom:4px;text-transform:uppercase;letter-spacing:.05em">${p.desc}</span>
        <div style="background:${p.c};color:#fff;font-family:'Noto Serif Tamil',serif;font-size:1.25rem;font-weight:600;padding:5px 12px;border-radius:2px;box-shadow:0 2px 6px ${p.c}66">${val}</div>
        <span style="font-family:'Noto Serif Tamil',serif;font-size:.72rem;color:#a8a29e;margin-top:4px">${p.l}</span>
      </div>`;
      first=false;
    });
    h+=`<div style="color:#d4d4d4;font-size:1.4rem;margin-bottom:22px">=</div>
      <div style="display:flex;flex-direction:column;align-items:center">
        <span style="font-family:Cinzel,serif;font-size:.52rem;color:#a8a29e;margin-bottom:4px;text-transform:uppercase">Full Word</span>
        <div style="background:#1a0a00;color:#e8c56a;font-family:'Noto Serif Tamil',serif;font-size:1.25rem;font-weight:700;padding:5px 14px;border-radius:2px;box-shadow:0 2px 8px rgba(26,10,0,.3)">${d.word}</div>
        <span style="font-family:'Noto Serif Tamil',serif;font-size:.72rem;color:#a8a29e;margin-top:4px">சொல்</span>
      </div></div>`;
    if(d.vikaram&&d.vikaram!=='—')
      h+=`<p style="text-align:center;font-family:'Crimson Pro',serif;font-size:.82rem;color:#a8a29e;font-style:italic;margin-top:8px">⚠ விகாரம்: ${d.vikaram}</p>`;
    document.getElementById('dg').innerHTML=h;
  }

  function load(on){
    document.getElementById('ab').disabled=on;
    document.getElementById('bt').style.display=on?'none':'inline';
    document.getElementById('bs').style.display=on?'block':'none';
  }
  function hide(){document.getElementById('rs').style.display='none';document.getElementById('es').style.display='none'}
  function err(m){document.getElementById('em').textContent=m;document.getElementById('es').style.display='block'}
</script>
</body>
</html>"""

# =============================================================================
# SECTION 8: FLASK ROUTES
# =============================================================================

@app.route("/")
def index():
    """Serve the embedded HTML page — no templates/ folder required."""
    return render_template_string(HTML_PAGE)

@app.route("/analyze", methods=["POST"])
def analyze():
    """POST /analyze — body: { "word": "<Tamil>" } → JSON morphological breakdown."""
    data = request.get_json(force=True, silent=True)
    if not data or "word" not in data:
        return jsonify({"error": 'Send JSON: { "word": "<Tamil word>" }'}), 400
    word = data["word"].strip()
    if not word:
        return jsonify({"error": "Word cannot be empty"}), 400
    return jsonify(analyze_word(word))

# =============================================================================
# SECTION 9: STARTUP
# =============================================================================
if __name__ == "__main__":
    print("\n" + "="*60)
    print("  தமிழ் பகுபத உறுப்பிலக்கணம்")
    print("  Tamil Morphological Analyzer is running!")
    print("  Open your browser:  http://127.0.0.1:5000")
    print("="*60 + "\n")
    app.run(debug=True, host="0.0.0.0", port=5000)
