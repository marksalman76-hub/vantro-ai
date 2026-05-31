import http from "k6/http";
import { sleep, check } from "k6";

export const options = {
  vus: 10,
  duration: "1m",
  thresholds: {
    http_req_failed: ["rate<0.05"],
    http_req_duration: ["p(95)<1500"]
  }
};

export default function () {
  const res = http.get("https://api.trance-formation.com.au/health");
  check(res, {
    "safe concurrency health status 200": (r) => r.status === 200
  });
  sleep(1);
}
