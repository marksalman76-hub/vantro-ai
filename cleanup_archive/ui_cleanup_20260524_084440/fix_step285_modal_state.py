from pathlib import Path

p = Path("frontend/src/app/client/page.tsx")
s = p.read_text(encoding="utf-8")

target = 'const [selectedAgents, setSelectedAgents] = useState<string[]>(['

insert = '''const [showRejectModal, setShowRejectModal] = useState(false);
  const [feedbackText, setFeedbackText] = useState("");

  '''

if "const [showRejectModal, setShowRejectModal]" not in s:
    s = s.replace(target, insert + target)

p.write_text(s, encoding="utf-8")

print("STEP_285D_MODAL_STATE_ADDED")
