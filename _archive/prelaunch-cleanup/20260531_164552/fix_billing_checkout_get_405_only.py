from pathlib import Path
from datetime import datetime

path = Path("frontend/src/app/api/billing-checkout/route.ts")
text = path.read_text(encoding="utf-8")

backup_dir = Path("backups") / ("billing_checkout_get_405_only_before_" + datetime.now().strftime("%Y%m%d_%H%M%S"))
backup_dir.mkdir(parents=True, exist_ok=True)
backup = backup_dir / "route.ts"
backup.write_text(text, encoding="utf-8")

if "export async function GET" not in text:
    text += '''

export async function GET() {
  return Response.json(
    {
      success: false,
      route: "billing-checkout",
      methods: ["POST"],
      beta_checkout_compatibility: true,
      credential_values_exposed: false,
      customer_safe: true
    },
    { status: 405 }
  );
}
'''
else:
    text = text.replace(
        "return NextResponse.json(payload);",
        "return NextResponse.json(payload, { status: 405 });"
    )

path.write_text(text, encoding="utf-8")

print("BILLING_CHECKOUT_GET_405_ONLY_FIXED")
print("Backup:", backup)