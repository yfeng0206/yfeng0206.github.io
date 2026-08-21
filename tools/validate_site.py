import os, io, re, glob, sys, pathlib
import yaml

ROOT = str(pathlib.Path(__file__).resolve().parent.parent)
errors = []

def fm_of(path):
    t = io.open(path, encoding="utf-8").read()
    if not t.startswith("---"):
        errors.append(f"{os.path.relpath(path,ROOT)}: missing front matter"); return None, t
    end = t.find("\n---", 3)
    if end == -1:
        errors.append(f"{os.path.relpath(path,ROOT)}: unterminated front matter"); return None, t
    try:
        return yaml.safe_load(t[3:end]) or {}, t[end+4:]
    except Exception as e:
        errors.append(f"{os.path.relpath(path,ROOT)}: YAML error: {e}"); return None, t[end+4:]

layouts = {os.path.splitext(f)[0] for f in os.listdir(os.path.join(ROOT,"_layouts"))}
includes = set(os.listdir(os.path.join(ROOT,"_includes")))

permalinks = {"/", "/404.html"}
docs = []

for p in glob.glob(os.path.join(ROOT,"_pages","*.md")) + [os.path.join(ROOT,"index.md")]:
    fm, body = fm_of(p); docs.append((p,fm,body))
    if fm and fm.get("permalink"): permalinks.add(fm["permalink"])
for coll, base in (("_research","/research/"), ("_projects","/projects/")):
    for p in glob.glob(os.path.join(ROOT,coll,"*.md")):
        fm, body = fm_of(p); docs.append((p,fm,body))
        permalinks.add(base + os.path.basename(p)[:-3] + "/")
for p in glob.glob(os.path.join(ROOT,"_posts","*.md")):
    fm, body = fm_of(p); docs.append((p,fm,body))
    m = re.match(r"^\d{4}-\d{2}-\d{2}-(.+)\.md$", os.path.basename(p))
    if m: permalinks.add("/writing/" + m.group(1) + "/")
    else: errors.append(f"bad post filename {p}")

for p,fm,body in docs:
    if fm:
        for r in (fm.get("redirect_from") or []): permalinks.add(r)

for p, fm, body in docs:
    rel = os.path.relpath(p, ROOT)
    if fm is None: continue
    lay = fm.get("layout")
    if not lay:
        lay = "post" if "_posts" in p else ("work" if ("_research" in p or "_projects" in p) else "page")
    if lay not in layouts: errors.append(f"{rel}: layout '{lay}' missing")
    if not fm.get("title"): errors.append(f"{rel}: missing title")
    for img in re.findall(r"!\[[^\]]*\]\((/assets/[^)\s]+)\)", body):
        if not os.path.exists(os.path.join(ROOT, img.lstrip("/").replace("/",os.sep))):
            errors.append(f"{rel}: missing image {img}")
    for key in ("teaser","image"):
        v = fm.get(key)
        if v and v.startswith("/assets") and not os.path.exists(os.path.join(ROOT, v.lstrip("/").replace("/",os.sep))):
            errors.append(f"{rel}: missing {key} {v}")
    for link in re.findall(r"\]\((/[^)\s]*)\)", body):
        base = link.split("#")[0]
        if base.startswith("/assets/"):
            if not os.path.exists(os.path.join(ROOT, base.lstrip("/").replace("/",os.sep))):
                errors.append(f"{rel}: missing asset {base}")
        elif base and base not in permalinks:
            errors.append(f"{rel}: dead internal link {link}")
    if "/portfolio/" in body: errors.append(f"{rel}: still references /portfolio/ in body")

for lp in glob.glob(os.path.join(ROOT,"_layouts","*.html")) + glob.glob(os.path.join(ROOT,"_includes","*.html")):
    t = io.open(lp, encoding="utf-8").read(); rel = os.path.relpath(lp, ROOT)
    if t.count("{%") != t.count("%}"): errors.append(f"{rel}: unbalanced liquid tags")
    if t.count("{{") != t.count("}}"): errors.append(f"{rel}: unbalanced liquid output")
    for inc in re.findall(r"{%-?\s*include\s+([A-Za-z0-9_\-./]+)", t):
        if inc not in includes: errors.append(f"{rel}: include '{inc}' missing")
    o = len(re.findall(r"{%-?\s*(if|for|unless|case)\b", t))
    c = len(re.findall(r"{%-?\s*end(if|for|unless|case)\b", t))
    if o != c: errors.append(f"{rel}: {o} opens vs {c} closes")

for dp in glob.glob(os.path.join(ROOT,"_data","*.yml")):
    try: yaml.safe_load(io.open(dp,encoding="utf-8").read())
    except Exception as e: errors.append(f"_data/{os.path.basename(dp)}: {e}")

nav = yaml.safe_load(io.open(os.path.join(ROOT,"_data","navigation.yml"),encoding="utf-8").read())
for item in nav["main"]:
    if item["url"] not in permalinks:
        errors.append(f"navigation: {item['title']} -> {item['url']} unresolved")

for f in ("assets/favicon.ico","assets/images/avatar.png","assets/images/favicon-32.png",
          "assets/images/favicon-180.png","assets/images/sel-oct.jpg"):
    if not os.path.exists(os.path.join(ROOT, f.replace("/",os.sep))):
        errors.append(f"missing asset {f}")

print("nav:", " | ".join(i["title"] for i in nav["main"]))
print(f"permalinks: {len(permalinks)}")
if errors:
    print("\nERRORS:"); [print("  -",e) for e in errors]; sys.exit(1)
print("\nAll structural checks passed.")
