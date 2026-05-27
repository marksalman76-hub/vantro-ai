from pathlib import Path

PAGE = Path("frontend/src/app/client/page.tsx")
text = PAGE.read_text(encoding="utf-8")
lower = text.lower()

print("CLIENT_PORTAL_UX_PASS1_DECLUTTER_RESULTS")
print("page_exists", PAGE.exists())
print("characters", len(text))
print("lines", len(text.splitlines()))
print("soft_border_count", text.count("rgba(15, 23, 42, 0.08)"))
print("soft_shadow_count", text.count("0 18px 55px rgba(15, 23, 42, 0.06)"))
print("backdrop_blur_count", text.count("backdropFilter"))
print("enterprise_ink_count", text.count("#0f172a"))
print("muted_text_count", text.count("#64748b"))

assert PAGE.exists()
assert "execution" in lower
assert "deliverable" in lower
assert "timeline" in lower
assert "workspace" in lower
assert len(text.splitlines()) > 1000
assert text.count("rgba(15, 23, 42, 0.08)") >= 1
assert text.count("0 18px 55px rgba(15, 23, 42, 0.06)") >= 1

print("CLIENT_PORTAL_UX_PASS1_DECLUTTER_OK")
