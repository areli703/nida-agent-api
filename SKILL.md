# Nida OS Agent API

Complete Nida OS Agent API toolkit. Build and manage websites, pages, CRM,
contacts, forms, chatbots, automations, pipelines, email, tasks, and SEO content
entirely through the agent API.

## Quick Start

Get your agent token from the Nida OS dashboard → Agent Settings → API Token.

```bash
export NIDA_BASE_URL="https://www.nida-os.com/api/agent/execute"
export NIDA_AGENT_TOKEN="nid_agent_xxxxx"
export NIDA_WORKSPACE_ID="your-workspace-uuid"
```

## 11 Confirmed Working Modules

1. **website** — sites, chrome, themes
2. **page** — pages, blocks, custom HTML
3. **contact** — CRM contacts
4. **form** — forms (create works, fields via UI)
5. **submission** — form submissions
6. **chatbot** — AI chat widgets
7. **automation** — workflow automations
8. **pipeline** — sales pipelines
9. **email** — email records
10. **task** — todo/tasks
11. **seo_content** — blog posts with full SEO fields

## Key Rules

- Use `id` for single-record ops (NOT `*_id`)
- Omit `per_page` from ALL list endpoints
- `seo_content` requires `params.data` wrapper (only module that does)
- Deletions require admin approval in dashboard
- Never use direct Supabase access

See SKILL.md for complete examples.
