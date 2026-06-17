from __future__ import annotations

from pathlib import Path


ROOT = Path(__file__).resolve().parent


def read(path: Path) -> str:
    if not path.exists():
        return ""
    return path.read_text(encoding="utf-8", errors="ignore")


def require(condition: bool, message: str) -> None:
    if not condition:
        raise AssertionError(message)


def frontend_sources() -> dict[str, str]:
    root = ROOT / "frontend" / "src"
    files: dict[str, str] = {}
    for path in root.rglob("*"):
        if path.is_file() and path.suffix in {".ts", ".tsx", ".js", ".jsx"}:
            files[str(path.relative_to(ROOT)).replace("\\", "/")] = read(path)
    return files


def next_bundle_sources() -> dict[str, str]:
    root = ROOT / "frontend" / ".next"
    if not root.exists():
        return {}
    files: dict[str, str] = {}
    for path in root.rglob("*"):
        if path.is_file() and path.suffix in {".js", ".html"}:
            files[str(path.relative_to(ROOT)).replace("\\", "/")] = read(path)
    return files


def main() -> int:
    component_path = ROOT / "frontend" / "src" / "components" / "UniversalCompleteMediaRunAgentPanel.tsx"
    component = read(component_path)
    sources = frontend_sources()

    old_heading_hits = [
        path for path, text in sources.items() if "Generated media script packet" in text
    ]
    require(
        not old_heading_hits,
        f"Old Complete Media heading is still present in frontend source: {old_heading_hits}",
    )

    require(
        "Generated media plan" in component,
        "Complete Media popup must render the clean Generated media plan heading.",
    )
    require(
        "Complete media popup UX v3" in component,
        "Admin-only Complete Media UX v3 marker is missing.",
    )
    require(
        "Portal payload provider check:" in component,
        "Admin portal payload provider check line is missing.",
    )
    require(
        'video_provider: "auto"' in component
        and 'audio_provider: "auto"' in component
        and 'provider_router_mode: "category_readiness"' in component,
        "Complete Media popup must request provider selection through the category router.",
    )
    require(
        'video_provider: "runway"' not in component
        and 'audio_provider: "elevenlabs"' not in component,
        "Complete Media popup must not hardcode a Runway + ElevenLabs provider pair.",
    )
    require(
        "friendlyMediaStatus" in component and "friendlyProviderFailureMessage" in component,
        "Portal must map backend/provider statuses into friendly user-facing copy.",
    )
    require(
        "Media job ${jobId} status: ${status}" not in component
        and "Provider attempts:" not in component,
        "Raw backend/provider status strings must not be promoted into the main portal status message.",
    )
    require(
        "friendlyMediaStatus(popupMediaJobStatus)" in component,
        "The visible Status row must use the friendly media status mapper.",
    )
    require(
        "data-complete-media-provider-diagnostics-toggle" in component
        and "Show provider diagnostics" in component
        and "providerDiagnosticsOpen ? (" in component,
        "Provider diagnostics must be behind an explicit admin diagnostics expander.",
    )
    require(
        "data-complete-media-provider-diagnostics-summary" in component
        and "Visual generation needs attention" in component,
        "Provider failures must show a clean default summary before diagnostics.",
    )
    require(
        "Provider called:" in component
        and "Runway called:" not in component,
        "Provider diagnostics must be vendor-neutral in the default admin UI.",
    )
    require(
        "JSON.stringify(preflightResult.media_script_packet, null, 2)" in component
        and "technicalScriptPacketOpen ? (" in component
        and component.find("technicalScriptPacketOpen ? (") < component.find("JSON.stringify(preflightResult.media_script_packet, null, 2)"),
        "Script packet JSON must only render behind the admin technical script toggle.",
    )
    require(
        "return JSON.stringify(value, null, 2)" not in component,
        "Default final output rendering must not stringify raw objects into the portal.",
    )

    admin_page = sources.get("frontend/src/app/admin/page.tsx", "")
    client_page = sources.get("frontend/src/app/client/page.tsx", "")
    require(
        "<UniversalCompleteMediaRunAgentPanel" in admin_page
        and "<UniversalCompleteMediaRunAgentPanel" in client_page,
        "Admin and client portals must both use the canonical Complete Media popup component.",
    )

    bundles = next_bundle_sources()
    if bundles:
        stale_bundle_hits = [
            path for path, text in bundles.items() if "Generated media script packet" in text
        ]
        require(
            not stale_bundle_hits,
            f"Built portal bundle still contains the old Complete Media heading: {stale_bundle_hits}",
        )
        require(
            any("Complete media popup UX v3" in text for text in bundles.values()),
            "Built portal bundle does not contain the Complete Media UX v3 marker.",
        )
        require(
            any("Generated media plan" in text for text in bundles.values()),
            "Built portal bundle does not contain the clean Generated media plan heading.",
        )

    print("Complete Media portal renderer verification passed.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
