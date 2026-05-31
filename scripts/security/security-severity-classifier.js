console.log("SECURITY_SEVERITY_CLASSIFIER_READY");

const severities = [
  "LOW",
  "MEDIUM",
  "HIGH",
  "CRITICAL"
];

console.log({
  supported_severities: severities,
  runtime_ready: true
});
