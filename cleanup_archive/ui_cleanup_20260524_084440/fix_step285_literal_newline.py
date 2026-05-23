from pathlib import Path

p = Path("frontend/src/app/client/page.tsx")
s = p.read_text(encoding="utf-8")

s = s.replace("\\n", "")
s = s.replace("\\r", "")

p.write_text(s, encoding="utf-8")

print("STEP_285C_LITERAL_BACKSLASH_NEWLINE_REMOVED")
print("First 5 lines:")
for i, line in enumerate(s.splitlines()[:5], start=1):
    print(f"{i}: {line}")