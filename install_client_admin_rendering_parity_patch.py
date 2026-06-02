from pathlib import Path

p = Path("frontend/src/app/client/page.tsx")

text = p.read_text(encoding="utf-8")

# -------------------------------------------------------------------
# 1. Add richer deliverable extraction helpers
# -------------------------------------------------------------------

anchor = 'function formatOutput(value: unknown): string {'

inject = '''
function extractRichDeliverable(payload: any) {
  if (!payload) return null;

  const execution =
    payload.execution ||
    payload.result ||
    payload.data ||
    payload;

  const adapter =
    execution.adapter_result ||
    execution.execution?.adapter_result ||
    execution.output ||
    {};

  const provider =
    execution.provider_execution ||
    execution.output?.provider_execution ||
    {};

  const mediaPack =
    execution.media_pack ||
    adapter.media_pack ||
    {};

  return {
    adapter,
    provider,
    mediaPack,
    preview_url:
      execution.preview_url ||
      adapter.preview_url ||
      mediaPack.preview_url ||
      null,

    generated_files:
      execution.generated_files ||
      adapter.generated_files ||
      mediaPack.generated_files ||
      [],

    generation_jobs:
      execution.generation_jobs ||
      adapter.generation_jobs ||
      mediaPack.generation_jobs ||
      [],

    voiceover_script:
      execution.voiceover_script ||
      adapter.voiceover_script ||
      null,

    avatar_prompt:
      execution.avatar_prompt ||
      adapter.avatar_prompt ||
      null,

    video_prompt:
      execution.video_prompt ||
      adapter.video_prompt ||
      null,

    supports_audio:
      execution.supports_audio ||
      adapter.supports_audio ||
      false,

    supports_video:
      execution.supports_video ||
      adapter.supports_video ||
      false,

    llm_content:
      execution?.provider_execution?.generated_content ||
      execution?.output?.provider_execution?.generated_content ||
      execution?.output?.content ||
      null,
  };
}

'''

if inject not in text:
    text = text.replace(anchor, inject + "\n" + anchor, 1)

# -------------------------------------------------------------------
# 2. Add state
# -------------------------------------------------------------------

old_state = 'const [liveDeliverable, setLiveDeliverable] = useState<any>(null);'

new_state = '''
const [liveDeliverable, setLiveDeliverable] = useState<any>(null);
const [richDeliverable, setRichDeliverable] = useState<any>(null);
'''

text = text.replace(old_state, new_state)

# -------------------------------------------------------------------
# 3. Populate rich deliverable after execution
# -------------------------------------------------------------------

old_exec = 'setLiveDeliverable(data);'

new_exec = '''
setLiveDeliverable(data);
setRichDeliverable(extractRichDeliverable(data));
'''

text = text.replace(old_exec, new_exec)

# -------------------------------------------------------------------
# 4. Add rendering block before closing main content
# -------------------------------------------------------------------

marker = '''
              </div>
            )}
'''

render_block = '''
              </div>

              {richDeliverable && (
                <div className="mt-6 rounded-2xl border border-white/10 bg-black/30 p-6">
                  <div className="mb-4 flex items-center justify-between">
                    <div>
                      <h3 className="text-xl font-semibold text-white">
                        Premium Generated Deliverable
                      </h3>

                      <p className="text-sm text-neutral-400">
                        Governed live execution output
                      </p>
                    </div>

                    <div className="rounded-full bg-emerald-500/20 px-3 py-1 text-xs text-emerald-300">
                      LIVE AI OUTPUT
                    </div>
                  </div>

                  {richDeliverable.preview_url && (
                    <div className="mb-6 overflow-hidden rounded-xl border border-white/10">
                      <img
                        src={richDeliverable.preview_url}
                        alt="Generated Preview"
                        className="w-full"
                      />
                    </div>
                  )}

                  {richDeliverable.generation_jobs?.length > 0 && (
                    <div className="mb-6">
                      <h4 className="mb-2 text-sm font-semibold uppercase tracking-wide text-neutral-300">
                        Media Generation Jobs
                      </h4>

                      <div className="grid gap-3 md:grid-cols-3">
                        {richDeliverable.generation_jobs.map((job: any, idx: number) => (
                          <div
                            key={idx}
                            className="rounded-xl border border-white/10 bg-white/5 p-3"
                          >
                            <div className="text-sm font-medium text-white">
                              {job.job_type || "generation"}
                            </div>

                            <div className="mt-1 text-xs text-neutral-400">
                              {job.status || "queued"}
                            </div>
                          </div>
                        ))}
                      </div>
                    </div>
                  )}

                  {richDeliverable.voiceover_script && (
                    <div className="mb-6 rounded-xl border border-white/10 bg-white/5 p-4">
                      <div className="mb-2 text-sm font-semibold text-neutral-300">
                        Voiceover Script
                      </div>

                      <div className="whitespace-pre-wrap text-sm text-neutral-200">
                        {richDeliverable.voiceover_script}
                      </div>
                    </div>
                  )}

                  {richDeliverable.video_prompt && (
                    <div className="mb-6 rounded-xl border border-white/10 bg-white/5 p-4">
                      <div className="mb-2 text-sm font-semibold text-neutral-300">
                        Video Direction
                      </div>

                      <div className="whitespace-pre-wrap text-sm text-neutral-200">
                        {richDeliverable.video_prompt}
                      </div>
                    </div>
                  )}

                  {richDeliverable.avatar_prompt && (
                    <div className="mb-6 rounded-xl border border-white/10 bg-white/5 p-4">
                      <div className="mb-2 text-sm font-semibold text-neutral-300">
                        Avatar Direction
                      </div>

                      <div className="whitespace-pre-wrap text-sm text-neutral-200">
                        {richDeliverable.avatar_prompt}
                      </div>
                    </div>
                  )}

                  {richDeliverable.llm_content && (
                    <div className="rounded-xl border border-white/10 bg-white/5 p-4">
                      <div className="mb-2 text-sm font-semibold text-neutral-300">
                        Premium Strategic Output
                      </div>

                      <div className="max-h-[600px] overflow-auto whitespace-pre-wrap text-sm text-neutral-200">
                        {richDeliverable.llm_content}
                      </div>
                    </div>
                  )}
                </div>
              )}
            )}
'''

text = text.replace(marker, render_block, 1)

p.write_text(text, encoding="utf-8")

print("CLIENT_ADMIN_RENDERING_PARITY_PATCH_INSTALLED")