# Session Memory & Skills Activation

## Initialize Every Session

At the start of this session:
1. Load ALL installed skills from ~/.claude/skills/ and .claude/skills/
2. Load ALL connected MCP servers and plugins
3. Make every skill and plugin available throughout this session
4. Never deactivate or forget any installed skill during our work

## How to Use

- All skills/plugins/MCPs are always on and ready to use
- Use them contextually when relevant (no need to invoke manually unless you want to)
- If I ask "what skills do I have", run `/skills` to list all active ones
- If I ask "show my memory", run `/memory` to display what you've learned

## Auto-Commit to Session Memory (Always Active)

**Automatically commit to memory after every task or decision without being asked:**
- Note what you learn about this project
- Record any patterns you discover
- Remember any preferences I express
- Store everything in session memory automatically and continuously
- Do NOT wait for me to say "remember this" or "commit to memory"
- Just save it proactively

**Patterns to auto-save:**
- Architecture decisions and why they were made
- Code conventions and standards we use
- Bugs we fix and what caused them
- Testing strategies that work well
- Performance optimizations discovered
- User feedback and feature requests
- Dependencies and version requirements
- API designs and data schemas
- Security considerations we implement
- Build or deployment issues and solutions

## Rules

- Assume all installed skills are intentional and should be active
- Keep skills loaded and accessible for the full session
- Never hide or deactivate any installed skill
- Synthesize and remember what works across the session
- Auto-save learnings continuously (no prompts needed)
- On next session, you'll load this CLAUDE.md again with fresh memory

---

**Verify everything is loaded:**
`/skills` - shows all active skills
`/memory` - shows all learned context
`/clear` - resets context but keeps CLAUDE.md and memory
