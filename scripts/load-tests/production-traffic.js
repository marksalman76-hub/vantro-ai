import http from "k6/http";
import { check, sleep } from "k6";

export const options = {
  thresholds: {
    http_req_failed: ["rate<0.05"],
    http_req_duration: ["p(95)<2000"],
  },
};

export default function () {
  const res = http.get("https://api.trance-formation.com.au/health", {
    timeout: "20s",
  });

  check(res, {
    "health status is 200": (r) => r.status === 200,
    "health body confirms running": (r) => String(r.body || "").includes('"status":"running"'),
  });

  sleep(1);
}
