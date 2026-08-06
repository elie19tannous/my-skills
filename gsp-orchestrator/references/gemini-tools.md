# Gemini CLI Tool Mapping

Skills may reference Claude-style tool names. In Gemini CLI, use these equivalents:

| Skill references | Gemini CLI equivalent |
|-----------------|----------------------|
| `Read` | `read_file` |
| `Write` | `write_file` |
| `Edit` | `replace` |
| `Bash` | `run_shell_command` |
| `Grep` | `grep_search` |
| `Glob` | `glob` |
| `TodoWrite` | `write_todos` |
| `Skill` tool | `activate_skill` |
| `WebSearch` | `google_web_search` |
| `WebFetch` | `web_fetch` |
| `Task` tool | No direct equivalent in Gemini CLI |

## Gemini-specific notes

- Gemini CLI loads `GEMINI.md` at session start for installed extensions.
- Skills still activate on demand via `activate_skill`.
- If a workflow expects subagents, run it in a single session or route to a non-subagent alternative.
