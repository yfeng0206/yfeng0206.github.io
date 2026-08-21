import io, re, glob, os, pathlib

ROOT = str(pathlib.Path(__file__).resolve().parent.parent)
css = io.open(os.path.join(ROOT, "assets", "css", "main.scss"), encoding="utf-8").read()

used = set()
for p in glob.glob(os.path.join(ROOT, "_layouts", "*.html")) + \
         glob.glob(os.path.join(ROOT, "_includes", "*.html")) + \
         glob.glob(os.path.join(ROOT, "_pages", "*.md")) + \
         [os.path.join(ROOT, "index.md")]:
    s = io.open(p, encoding="utf-8").read()
    for m in re.findall(r'class="([^"{}]+)"', s):
        for c in m.split():
            used.add(c)
    # kramdown IAL syntax: {: .btn .btn--primary}
    for m in re.findall(r'\{:\s*([^}]+)\}', s):
        for c in re.findall(r'\.([A-Za-z0-9_\-]+)', m):
            used.add(c)

missing = [c for c in sorted(used) if "." + c not in css]
print("classes referenced:", len(used))
if missing:
    print("MISSING from stylesheet:")
    for c in missing:
        print("   .", c, sep="")
else:
    print("all referenced classes are defined")
