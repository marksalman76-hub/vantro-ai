import { NextResponse } from "next/server";
import { readFile } from "fs/promises";
import path from "path";

const DATA_FILE = path.join(process.cwd(), ".runtime-data", "client-executions.json");

export async function GET() {
  try {
    const raw = await readFile(DATA_FILE, "utf-8");
    const executions = JSON.parse(raw);

    if (!Array.isArray(executions) || executions.length === 0) {
      return NextResponse.json({
        success: true,
        deliverable: null,
      });
    }

    const latest = executions[0];

    return NextResponse.json({
      success: true,
      execution: latest,
      deliverable: latest?.deliverable || null,
    });
  } catch {
    return NextResponse.json({
      success: true,
      deliverable: null,
    });
  }
}
