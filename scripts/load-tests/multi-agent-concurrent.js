import http from "k6/http";
import { check, sleep } from "k6";

export const options = {
  thresholds: {
    http_req_failed: ["rate<0.05"],
    http_req_duration: ["p(95)<3000"],
  },
};

export default function () {
  const res = http.get("https://api.trance-formation.com.au/health", {
    timeout: "20s",
  });

  check(res, {
    "backend reachable": (r) => r.status === 200,
    "execution stack enabled": (r) => String(r.body || "").includes('"execution_stack":"enabled"'),
    "owner governance present": (r) => String(r.body || "").includes('"owner_approval_required_for_spend":true'),
  });

  sleep(1);
}
