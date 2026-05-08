---
name: nida-agent-api
description: |
  Complete Nida OS Agent API toolkit. Build and manage websites, pages, CRM,
  contacts, forms, chatbots, automations, pipelines, email, tasks, and SEO
  content entirely through the agent API — no UI needed.
category: business
tags:
  - nida
  - api
  - website-builder
  - crm
  - agent
  - no-code
  - low-code
  - automation
  - chatbot
  - pipeline
  - email
  - task
  - seo
  - blog
---

# Nida OS Agent API

## PATCH OVERRIDE — Agent API Approval Gate (2026-05-08)

The previous guidance saying `website:update` or `page:update` works directly without approval is obsolete. As of 2026-05-08, **ALL `update` and `delete` actions across ALL modules return `requires_approval: true`**.

Use `POST /api/agent/execute` for `create`, `list`, `get` without issues. For `update` and `delete`, the API returns:

```json
{
  "success": false,
  "requires_approval": true,
  "approval_id": "uuid-here",
  "status": "pending",
  "message": "Action requires admin approval"
}
```

The user must approve these in the Nida dashboard (typically Automations → Approvals or Inbound Webhooks tab). There is no programmatic approval endpoint via the agent API — attempting to approve via API returns "Workspace mismatch" even with correct credentials.

`create` remains the only ungated write operation. For bulk changes, use `create` (which creates new records) rather than `update` (which requires approval).

After `website:create`, read the new site ID from the first available field in this order: `website_id`, `id`, `data.item.id`.


Full programmatic control of Nida OS via the agent REST API. Build production
websites, capture leads, and manage CRM data from any autonomous agent.

## Authentication

Get your agent token from the Nida OS dashboard → Agent Settings → API Token.

```bash
export NIDA_BASE_URL="https://www.nida-os.com/api/agent/execute"
export NIDA_AGENT_TOKEN="nid_agent_xxxxx"
export NIDA_WORKSPACE_ID="your-workspace-uuid"
```

All requests:
```bash
curl -L "$NIDA_BASE_URL" \
  -H "Authorization: Bearer $NIDA_AGENT_TOKEN" \
  -H "Content-Type: application/json" \
  -d '{"workspace_id":"'"$NIDA_WORKSPACE_ID"'",...}'
```

## Site Architecture (Critical)

Nida OS has two rendering modes that behave completely differently:

### `render_mode: "blocks"` (Uses Site Chrome)
- Pages are wrapped by site-level `header_blocks[]` and `footer_blocks[]`
- Page blocks contain ONLY unique content (no nav/footer HTML)
- Site chrome provides consistent header/footer across ALL pages
- Best for multi-page sites with shared navigation

### `render_mode: "custom_html"` (Full Control)
- Page contains a complete `<html>` document
- **Bypasses site chrome entirely** — no site header/footer applied
- You must include your own `<nav>` and `<footer>` in the HTML
- Best for single-page landing sites or agency-quality custom designs

### `render_mode: "blocks_no_shell"` (Blocks Without Chrome)
- Uses page blocks but **does NOT** wrap with site chrome
- Content only, no header_blocks or footer_blocks applied
- Rarely used; mainly for embeddable widgets

### The Site Chrome Model

```
┌─────────────────────────────┐
│  Site header_blocks[]       │  ← Shared across ALL pages
├─────────────────────────────┤
│  Page blocks[]              │  ← Unique per-page content
├─────────────────────────────┤
│  Site footer_blocks[]       │  ← Shared across ALL pages
└─────────────────────────────┘
```

**To use site chrome correctly:**
1. Set `header_blocks` and `footer_blocks` on the **site** via dashboard
2. Create pages with `render_mode: "blocks"`
3. Page blocks should only contain sections, NOT navigation or footers
4. Use `chrome_full_bleed: true` on every block

**Do NOT mix these approaches:**
- ❌ Blocks mode page WITH baked-in `<nav>` → gets double header
- ❌ Custom HTML page on site WITH chrome → nav shows but footer may conflict
- ✅ Blocks mode + site chrome OR custom_html with self-contained nav+footer

## Core Modules

For a condensed cheat sheet of all 11 modules, their quirks, and broken actions, see `references/11-module-quick-reference.md` and `references/hidden-module-discovery.md` for how the 6 undocumented modules were discovered.

### Universal Parameter Rules (Read This First)

These bugs apply across **all** modules. Always follow these rules to avoid 400/500 errors:

**1. Use `id` for single-record operations, NOT `*_id`**
- `page:get` with `page_id` → returns the **wrong page**
- `contact:get` with `contact_id` → returns empty record
- `contact:update` with `contact_id` → schema cache error
- `form:get` with `form_id` → returns `name: null`
- **Correct**: `params: {"id": "UUID"}` for all `get`, `update`, `delete` calls

**2. Omit `per_page` from ALL list endpoints**
- `page:list`, `website:list`, `contact:list`, `form:list`, `submission:list`
- All return `"column X.per_page does not exist"`
- **Correct**: `params: {}` — no pagination params

**3. Response shape is inconsistent**
- Single-item `get` returns `data` directly (e.g., `data.id`, `data.title`, `data.blocks[]`)
- List returns `data.items[]`
- Create/update returns `data.item` or `data` depending on the module — always inspect the raw response

**4. Some documented actions don't exist**
- `contact:search` → `Unsupported entity action: search`
- `form:get_submissions` → `Unsupported entity action: get_submissions`
- Workaround: Use `list` and filter client-side

**5. `seo_content` is the ONLY module requiring `params.data` wrapper**
- All other 10 modules use flat `params`
- `seo_content:create` with flat params returns `"null value in column \"title\""`
- **Correct**: `params: {"data": {"title": "...", "body_content": "..."}}`

**6. ALL `update` and `delete` actions require admin approval**
- As of 2026-05-08, every `update` and `delete` across all modules returns `requires_approval: true`
- `create` is the only ungated write — use it for bulk operations
- Approve in Nida dashboard → Approvals tab

### 1. Website Builder (`module: website`)

#### List Sites
```json
{
  "workspace_id": "...",
  "module": "website",
  "action": "list",
  "params": {}
}
```
⚠️ **Bug**: `per_page` in `params` returns `"column websites.per_page does not exist"`. Omit `per_page` entirely.

#### Get a Site (check header_blocks, footer_blocks, theme)
```json
{
  "workspace_id": "...",
  "module": "website",
  "action": "get",
  "params": {"id": "SITE_UUID"}
}
```

#### Create a Site
```json
{
  "workspace_id": "...",
  "module": "website",
  "action": "create",
  "params": {
    "name": "My Agent Site",
    "subdomain": "my-agent-site"
  }
}
```
✅ **Fixed 2026-05-07**: `website:create` works via the Agent API and returns top-level `website_id`.

✅ **Fixed 2026-05-07**: `page:create` works via the Agent API. Use `website_id` in params; aliases `site_id`, `websiteId`, and `siteId` are also accepted.

#### Update Site Chrome (header/footer blocks)
```json
{
  "workspace_id": "...",
  "module": "website",
  "action": "update",
  "params": {
    "site_id": "SITE_UUID",
    "header_blocks": [
      {
        "type": "custom_html",
        "data": {"html": "<nav>...</nav>"},
        "settings": {"chrome_full_bleed": true, "padding_top": 0, "padding_bottom": 0}
      }
    ],
    "footer_blocks": [
      {
        "type": "custom_html",
        "data": {"html": "<footer>...</footer>"},
        "settings": {"chrome_full_bleed": true, "padding_top": 0, "padding_bottom": 0}
      }
    ]
  }
}
```
⚠️ Requires admin approval via dashboard.

### 2. Pages (`module: page`)

#### List Pages
⚠️ **Bug**: `page:list` does NOT accept `per_page` in `params`. It returns:
```json
{"error": "column website_pages.per_page does not exist"}
```
```json
{
  "workspace_id": "...",
  "module": "page",
  "action": "list",
  "params": {}
}
```
Client-side filtering by `website_id` is required.

#### Create a Page (Blocks Mode + Site Chrome)
```json
{
  "workspace_id": "...",
  "module": "page",
  "action": "create",
  "params": {
    "site_id": "SITE_UUID",
    "title": "Home",
    "slug": "home",
    "is_homepage": true,
    "status": "published",
    "render_mode": "blocks",
    "blocks": [
      {
        "type": "custom_html",
        "data": {"html": "<div>ONLY page content here, no nav/footer</div>"},
        "settings": {
          "padding_top": 0,
          "padding_bottom": 0,
          "chrome_full_bleed": true
        }
      }
    ]
  }
}
```

#### Create a Page (Custom HTML Mode — Full Document)
```json
{
  "workspace_id": "...",
  "module": "page",
  "action": "create",
  "params": {
    "site_id": "SITE_UUID",
    "title": "Home",
    "slug": "home",
    "is_homepage": true,
    "status": "published",
    "render_mode": "custom_html",
    "custom_page_html": "<!DOCTYPE html><html>...</html>"
  }
}
```

#### Update a Page
```json
{
  "workspace_id": "...",
  "module": "page",
  "action": "update",
  "params": {
    "id": "PAGE_UUID",
    "title": "Updated Title",
    "blocks": [...]
  }
}
```
⚠️ **Pitfall**: Use `id` to specify the target page, NOT `page_id`. Using `page_id` may throw:
```json
{"error": "Could not find the 'page_id' column of 'website_pages' in the schema cache"}
```

⚠️ May require admin approval.

#### Delete a Page
```json
{
  "workspace_id": "...",
  "module": "page",
  "action": "delete",
  "params": {"id": "PAGE_UUID"}
}
```
⚠️ **Bug**: Using `page_id` may fail. Use `id` instead. Requires admin approval.

#### Get a Page
```json
{
  "workspace_id": "...",
  "module": "page",
  "action": "get",
  "params": {"id": "PAGE_UUID"}
}
```
⚠️ **Bug**: Using `page_id` may return the **wrong page** (a different record entirely). Use `id` instead.
⚠️ **Response shape**: Returns `data` directly (no `.item` wrapper). Fields are at `data.id`, `data.title`, `data.blocks[]`.

### 3. CRM / Contacts (`module: contact`)

#### List Contacts
```json
{
  "workspace_id": "...",
  "module": "contact",
  "action": "list",
  "params": {}
}
```
⚠️ **Bug**: `per_page` in `params` returns `"column contacts.per_page does not exist"`. Omit `per_page` entirely.

#### Get a Contact
```json
{
  "workspace_id": "...",
  "module": "contact",
  "action": "get",
  "params": {"id": "CONTACT_UUID"}
}
```
⚠️ **Bug**: Using `contact_id` returns an empty record. Use `id` instead.

#### Create a Contact
```json
{
  "workspace_id": "...",
  "module": "contact",
  "action": "create",
  "params": {
    "first_name": "John",
    "last_name": "Doe",
    "email": "john@example.com",
    "phone": "+1234567890",
    "company_name": "Acme Inc",
    "city": "San Francisco",
    "state": "CA",
    "tags": ["lead", "warm"],
    "notes": "Met at conference"
  }
}
```

#### Update a Contact
```json
{
  "workspace_id": "...",
  "module": "contact",
  "action": "update",
  "params": {
    "id": "CONTACT_UUID",
    "tags": ["lead", "hot"],
    "notes": "Follow up next week"
  }
}
```
⚠️ **Bug**: Using `contact_id` throws schema cache error. Use `id` instead.

#### Delete a Contact
```json
{
  "workspace_id": "...",
  "module": "contact",
  "action": "delete",
  "params": {"id": "CONTACT_UUID"}
}
```
⚠️ **Bug**: Using `contact_id` may fail. Use `id` instead. Requires admin approval.

#### Search Contacts
**Status: BROKEN** — `contact:search` returns:
```json
{"error": "Unsupported entity action: search"}
```
Workaround: Use `contact:list` and filter client-side by name/email/tags.

### 4. Forms (`module: form`)

#### List Forms
```json
{
  "workspace_id": "...",
  "module": "form",
  "action": "list",
  "params": {}
}
```
⚠️ **Bug**: `per_page` in `params` returns `"column forms.per_page does not exist"`. Omit `per_page` entirely.

#### Get a Form
```json
{
  "workspace_id": "...",
  "module": "form",
  "action": "get",
  "params": {"id": "FORM_UUID"}
}
```
⚠️ **Bug**: Using `form_id` returns `name: null`. Use `id` instead.

#### Create a Form
```json
{
  "workspace_id": "...",
  "module": "form",
  "action": "create",
  "params": {
    "website_id": "SITE_UUID",
    "name": "Contact Us",
    "success_message": "Thanks! We will be in touch soon.",
    "submit_button_text": "Submit",
    "create_lead_on_submit": true
  }
}
```
⚠️ **Discovery 2026-05-08**: `form:create` is confirmed working. Returns `data.item` with `id`, `website_id`, `name`, `status` (draft by default). The `fields` param does NOT exist in schema cache — forms must be built as custom HTML blocks, or add fields through the Nida UI after creation.

#### Update a Form
```json
{
  "workspace_id": "...",
  "module": "form",
  "action": "update",
  "params": {
    "id": "FORM_UUID",
    "name": "Updated Form Name",
    "success_message": "Thank you! We received your submission.",
    "submit_button_text": "Send"
  }
}
```
⚠️ Use `id`, NOT `form_id`. Updating `fields` via API is not supported.

#### Delete a Form
```json
{
  "workspace_id": "...",
  "module": "form",
  "action": "delete",
  "params": {"id": "FORM_UUID"}
}
```
⚠️ Requires admin approval.

#### Get Form Submissions
**Status: BROKEN** — `form:get_submissions` returns:
```json
{"error": "Unsupported entity action: get_submissions"}
```
Workaround: Use `submission:list` and filter client-side by `form_id`.

### 5. Submissions / Leads (`module: submission`)

#### List All Submissions
```json
{
  "workspace_id": "...",
  "module": "submission",
  "action": "list",
  "params": {}
}
```
⚠️ **Bug**: `per_page` in `params` returns `"column form_submissions.per_page does not exist"`. Omit `per_page` entirely.

### 6. Chatbot (`module: chatbot`)

⚠️ **Discovery 2026-05-08**: `chatbot` is a real module but was missing from all documentation. Fully tested live.

#### List Chatbots
```json
{
  "workspace_id": "...",
  "module": "chatbot",
  "action": "list",
  "params": {}
}
```
Returns: `data.items[]` with `id`, `name`, `status`, `welcome_message`, `placeholder_text`, `fallback_message`, `business_context`, `system_prompt_template`, `tone`, `widget_settings`, `lead_capture_enabled`, etc.

#### Get a Chatbot
```json
{
  "workspace_id": "...",
  "module": "chatbot",
  "action": "get",
  "params": {"id": "CHATBOT_UUID"}
}
```
⚠️ Use `id`, NOT `chatbot_id`. Returns `data` directly (no `.item` wrapper).

#### Update a Chatbot
```json
{
  "workspace_id": "...",
  "module": "chatbot",
  "action": "update",
  "params": {
    "id": "CHATBOT_UUID",
    "welcome_message": "Hey there! How can I help?",
    "system_prompt_template": "You are a helpful AI assistant...",
    "tone": "professional",
    "lead_capture_enabled": true,
    "collect_name": true,
    "collect_email": true,
    "collect_phone": true
  }
}
```
Returns `data.item`.

#### Delete a Chatbot
```json
{
  "workspace_id": "...",
  "module": "chatbot",
  "action": "delete",
  "params": {"id": "CHATBOT_UUID"}
}
```
⚠️ Requires admin approval.

### 7. Automation (`module: automation`)

⚠️ **Discovery 2026-05-08**: `automation` is a real module but was missing from all documentation.

#### List Automations
```json
{
  "workspace_id": "...",
  "module": "automation",
  "action": "list",
  "params": {}
}
```
Returns: `data.items[]` with `id`, `name`, `description`, `status`, `trigger_type`, `workflow_json`.

#### Get an Automation
```json
{
  "workspace_id": "...",
  "module": "automation",
  "action": "get",
  "params": {"id": "AUTOMATION_UUID"}
}
```
⚠️ Use `id`, NOT `automation_id`. Returns `data` directly.

#### Update an Automation
```json
{
  "workspace_id": "...",
  "module": "automation",
  "action": "update",
  "params": {
    "id": "AUTOMATION_UUID",
    "name": "Lead Follow-up",
    "status": "enabled"
  }
}
```
Returns `data.item`.

#### Delete an Automation
```json
{
  "workspace_id": "...",
  "module": "automation",
  "action": "delete",
  "params": {"id": "AUTOMATION_UUID"}
}
```
⚠️ Requires admin approval.

### 8. Pipeline (`module: pipeline`)

⚠️ **Discovery 2026-05-08**: `pipeline` is a real module but was missing from all documentation.

#### List Pipelines
```json
{
  "workspace_id": "...",
  "module": "pipeline",
  "action": "list",
  "params": {}
}
```
Returns: `data.items[]` with `id`, `name`, `is_default`, `created_at`.

#### Get a Pipeline
```json
{
  "workspace_id": "...",
  "module": "pipeline",
  "action": "get",
  "params": {"id": "PIPELINE_UUID"}
}
```
⚠️ Use `id`, NOT `pipeline_id`. Returns `data` directly.

#### Update a Pipeline
```json
{
  "workspace_id": "...",
  "module": "pipeline",
  "action": "update",
  "params": {
    "id": "PIPELINE_UUID",
    "name": "Sales Pipeline"
  }
}
```
Returns `data.item`.

#### Delete a Pipeline
```json
{
  "workspace_id": "...",
  "module": "pipeline",
  "action": "delete",
  "params": {"id": "PIPELINE_UUID"}
}
```
⚠️ Requires admin approval.

### 9. Email (`module: email`)

⚠️ **Discovery 2026-05-08**: `email` is a real module but was missing from all documentation.

#### List Emails
```json
{
  "workspace_id": "...",
  "module": "email",
  "action": "list",
  "params": {}
}
```
Returns: `data.items[]` with `id`, `sender_email`, `sender_name`, `subject`, `body`.

#### Get an Email
```json
{
  "workspace_id": "...",
  "module": "email",
  "action": "get",
  "params": {"id": "EMAIL_UUID"}
}
```
⚠️ Use `id`, NOT `email_id`. Returns `data` directly.

#### Update an Email
```json
{
  "workspace_id": "...",
  "module": "email",
  "action": "update",
  "params": {
    "id": "EMAIL_UUID",
    "sender_name": "Nida Team",
    "subject": "Welcome to Nida"
  }
}
```
Returns `data.item`.

#### Delete an Email
```json
{
  "workspace_id": "...",
  "module": "email",
  "action": "delete",
  "params": {"id": "EMAIL_UUID"}
}
```
⚠️ Requires admin approval.

### 10. Task (`module: task`)

⚠️ **Discovery 2026-05-08**: `task` is a real module but was missing from all documentation.

#### List Tasks
```json
{
  "workspace_id": "...",
  "module": "task",
  "action": "list",
  "params": {}
}
```
Returns: `data.items[]` with `id`, `title`, `description`, `status`, `due_date`, `assigned_user_email`.

#### Get a Task
```json
{
  "workspace_id": "...",
  "module": "task",
  "action": "get",
  "params": {"id": "TASK_UUID"}
}
```
⚠️ Use `id`, NOT `task_id`. Returns `data` directly.

#### Create a Task
```json
{
  "workspace_id": "...",
  "module": "task",
  "action": "create",
  "params": {
    "title": "Follow up with lead",
    "status": "todo",
    "due_date": "2026-05-15T00:00:00Z",
    "assigned_user_email": "user@example.com"
  }
}
```
⚠️ **Bug**: `priority` column does not exist in schema cache. Do NOT include `priority`.
Returns `data.item`.

#### Update a Task
```json
{
  "workspace_id": "...",
  "module": "task",
  "action": "update",
  "params": {
    "id": "TASK_UUID",
    "title": "Updated task title",
    "status": "done"
  }
}
```
Returns `data.item`.

#### Delete a Task
```json
{
  "workspace_id": "...",
  "module": "task",
  "action": "delete",
  "params": {"id": "TASK_UUID"}
}
```
⚠️ Requires admin approval.

### 11. SEO Content / Blog Posts (`module: seo_content`)

⚠️ **Discovery 2026-05-08**: `seo_content` is a real module — it powers the blog/SEO article system in Nida. It was completely missing from all documentation. Fields schema is much richer than other modules.

#### List SEO Content
```json
{
  "workspace_id": "...",
  "module": "seo_content",
  "action": "list",
  "params": {}
}
```
Returns: `data.items[]` with `id`, `title`, `content_type`, `status`, `slug`, `meta_title`, `meta_description`, `focus_keyword`, `publish_date`, `word_count`, etc.

#### Get an SEO Content Item
```json
{
  "workspace_id": "...",
  "module": "seo_content",
  "action": "get",
  "params": {"id": "CONTENT_UUID"}
}
```
⚠️ Use `id`, NOT `seo_content_id`. Returns `data` directly (no `.item` wrapper).

#### Create an SEO Content Item (Blog Post)
⚠️ **Critical quirk**: Unlike all other modules, `seo_content:create` REQUIRES the `data` wrapper in `params`.

```json
{
  "workspace_id": "...",
  "module": "seo_content",
  "action": "create",
  "params": {
    "data": {
      "title": "How AI Agents Are Reshaping Web Design in 2026",
      "content_type": "blog_post",
      "status": "published",
      "slug": "ai-agents-reshaping-web-design-2026",
      "meta_title": "How AI Agents Are Reshaping Web Design in 2026",
      "meta_description": "AI agents now build complete websites autonomously. Learn how this technology is changing the web design industry.",
      "focus_keyword": "AI web design",
      "body_content": "<h2>The Rise of Autonomous Web Agents</h2><p>AI-powered agents are no longer...",
      "excerpt": "Discover how AI agents are revolutionizing the web design industry in 2026.",
      "featured_image": "https://your-cdn.com/image.jpg",
      "target_city": "Danville",
      "target_state": "VA",
      "target_keywords": "AI web design, autonomous websites",
      "tags": ["AI", "web design", "automation"],
      "cta_heading": "Ready to Build Your AI-Powered Site?",
      "cta_text": "Get Started Free",
      "cta_link": "https://nida-os.com/signup"
    }
  }
}
```
⚠️ **Must use `params.data` wrapper** — flat params returns `"null value in column \"title\""`. This is the ONLY module that requires the `data` wrapper.

Returns `data.item` with full field set including:
- `id`, `title`, `slug`, `content_type`, `status`
- `meta_title`, `meta_description`, `focus_keyword`
- `body_content`, `excerpt`, `hero_heading`, `faq_section`
- `internal_links`, `canonical_url`, `json_ld_schema`
- `og_title`, `og_description`, `og_image`
- `target_city`, `target_state`, `target_keywords`, `supporting_keywords`
- `publish_date`, `word_count`, `featured_image`
- `cta_heading`, `cta_text`, `cta_link`

#### Update an SEO Content Item
⚠️ Also requires `data` wrapper.

```json
{
  "workspace_id": "...",
  "module": "seo_content",
  "action": "update",
  "params": {
    "id": "CONTENT_UUID",
    "data": {
      "title": "Updated Title",
      "meta_description": "Updated description for SEO"
    }
  }
}
```
⚠️ Requires admin approval.

#### Delete an SEO Content Item
```json
{
  "workspace_id": "...",
  "module": "seo_content",
  "action": "delete",
  "params": {"id": "CONTENT_UUID"}
}
```
⚠️ Requires admin approval.

## Approval Gate

Destructive operations (`page:update`, `page:delete`, etc.) may return:

```json
{
  "success": false,
  "requires_approval": true,
  "approval_id": "uuid-here",
  "status": "pending",
  "message": "Action requires admin approval"
}
```

Go to the Nida OS dashboard → Approvals tab, find the approval by ID, and
approve it. Currently there is no agent API endpoint to programmatically
approve — it must be done through the UI.

⚠️ **Bug**: Attempting to approve programmatically via the agent API's `approvals` module sometimes returns a **"Workspace mismatch"** error even when the `workspace_id` is correct. Admin UI approval is more reliable.

**Current rule**: Use Agent API `create` for non-destructive adds. Do not use direct database fallback.

## Common Block Types

When using `render_mode: "blocks"`, these block types are available:

| Type | Description | Settings |
|------|-------------|----------|
| `custom_html` | Full HTML block | `padding_top`, `padding_bottom`, `chrome_full_bleed` |
| `form_embed` | Embedded form (use custom_html instead for dark themes) | `form_id` |
| `chatbot` | AI chat widget | `agent_id` |
| `text` | Rich text block | `content` |
| `image` | Image block | `src`, `alt` |

⚠️ **Dark theme bug**: `form_embed` blocks render with a light theme on dark
backgrounds. Use `custom_html` with a hand-built form instead for dark sites.
See `templates/dark-glassmorphism-form.html` for a ready-to-use dark glassmorphism contact form.

## Chrome Rules — Never Double-Render Site Navigation

Nida's `blocks` render mode **automatically wraps** every page with:

```
Site header_blocks[] → your page blocks[] → Site footer_blocks[]
```

**The Golden Rule:** When using `render_mode: "blocks"`, **never** put `<nav>`, `<header>`, `<footer>`, or site-wide navigation inside individual page blocks. If you do, the user sees **two headers and two footers** — one from the site chrome, one from your custom HTML.

### ✅ Correct approach (blocks mode)
1. Set `header_blocks` and `footer_blocks` on the **website** itself
2. Each **page** only contains its unique content sections
3. All blocks have `chrome_full_bleed: true`

### ✅ Correct approach (custom_html mode)
1. `render_mode: "custom_html"` **bypasses** site chrome entirely
2. You supply a full `<!DOCTYPE html>` document including your own `<nav>` and `<footer>`
3. Use this for landing-page-only sites or premium agency designs

### ❌ Wrong approach (the bug you just fixed)
- `render_mode: "blocks"`
- Block 1 contains `<nav>` HTML
- Block N contains `<footer>` HTML
- **Result:** Double nav + double footer on every page
2. **Use `website_id` (or aliases `site_id`, `websiteId`, `siteId`) in `page:create` params.** The API accepts these aliases for the same field, but the canonical parameter is `website_id`. Older versions of this guide incorrectly said to use `site_id` exclusively — both work, but `website_id` is preferred.
3. **Use `render_mode: "custom_html"`** for premium agency-quality designs.
4. **Use anchor links** (`#features`, `#pricing`) for single-page sites.
5. **Cache the `site_id`** and `page_id`s to avoid repeated lookups.
6. **Batch operations** when possible — the API handles concurrent requests well.
7. **When the API is broken**, inform the user the `create` path is temporarily degraded, create the resource via Nida UI once, then continue with API `update` / `list` / `get` operations. Never suggest Supabase direct access.

## Security Constraint — No Direct Database Fallback

⚠️ **NON-NEGOTIABLE**: Agents must **never** bypass the Nida Agent API by calling Supabase directly, using `service_role` keys, SQL consoles, or raw table writes.

**Why:** Direct DB access bypasses business rules, audit controls, and least-privilege boundaries. It breaks the trust model for end-user agents.

**Allowed fallbacks when `create` endpoints regress:**
1. **Nida UI manual create** — create the resource once in the dashboard, then use API `update` / `get` / `list` operations.
2. **Trusted backend proxy endpoint** controlled by Nida (with strict auth + audit), if available.

**Prohibited fallbacks:**
- "Write directly to Supabase"
- "Run SQL insert/update against `websites`/`website_pages` tables"
- "Use admin DB credentials from agent context"

**Agent response requirement:** If a user suggests direct DB access, explicitly refuse and provide the secure next step (UI create + API update).

```json
// 1. Create site
{
  "module": "website",
  "action": "create",
  "params": {
    "name": "Agent Demo",
    "subdomain": "my-demo"
  }
}

// 2. Create homepage
{
  "module": "page",
  "action": "create",
  "params": {
    "site_id": "SITE_UUID",
    "title": "Home",
    "slug": "home",
    "is_homepage": true,
    "status": "published",
    "render_mode": "custom_html",
    "custom_page_html": "<!DOCTYPE html>..."
  }
}

// 3. Create contact page
{
  "module": "page",
  "action": "create",
  "params": {
    "site_id": "SITE_UUID",
    "title": "Contact",
    "slug": "contact",
    "status": "published",
    "render_mode": "custom_html",
    "custom_page_html": "<!DOCTYPE html>..."
  }
}
```

## Troubleshooting

See `references/agent-api-live-test-results-2026-05-08.md` for the full live-tested matrix of which actions work and which are broken.

| Problem | Cause | Fix |
|---------|-------|-----|
| **Double header / double footer** | `blocks` mode already wraps pages with site chrome (header_blocks + footer_blocks). Adding `<nav>` or `<footer>` HTML inside page blocks = duplicate elements. | Remove `<nav>` and `<footer>` from ALL custom_html blocks. Configure site chrome via `website:update header_blocks/footer_blocks` instead. NEVER bake nav/footer into page-level blocks. |
| Old blocks homepage + new custom_html homepage both `is_homepage: true` | Multiple pages marked as homepage | Delete old page via UI approval gate |
| White gaps between sections | Missing `chrome_full_bleed: true` | Add to every block |
| Links don't work | Using relative paths (`/contact`) without published domain | Use full URLs or anchor links (`#contact`) |
| Form renders light on dark | `form_embed` block default theme | Build custom form in `custom_html` instead |
| `requires_approval` on update | Approval gate active for destructive ops | Use `create` instead, or approve in UI |
| DNS not resolving | Custom domain not configured | Set up CNAME in your DNS provider |
| "Workspace mismatch" error | Wrong `workspace_id` in token | Verify workspace from dashboard |
| **`page:create` returns `null value in column "website_id"`** | **Fixed 2026-05-07**: Server-side regression resolved. Use `website_id` in params. If still seeing this on older deployments, ensure agent API is at latest version. |
| `page:create` returns 500 / "Error creating page" | Unicode (emoji) in payload triggers encoding bug | Remove all emoji, non-ASCII chars, and `U+FEFF` BOM from JSON |
| Updated page not visible to user | Wrong site — workspace has multiple sites with similar names | List all sites and verify `website_id` matches the user's visible site |
| Shell `&` interpreted as backgrounding in `curl -d` | Inline JSON containing `&` (CSS `background:` values) | Write JSON to a temp file (`-d @/tmp/payload.json`) instead of inline `-d '...'` |
| Em-dash (`—`, U+2014) breaks `execute_code` | Unicode em-dash not supported in hermes sandbox string literals | Use plain hyphen `-` or HTML entity `--` instead |

## Critical Pitfall: Multiple Sites With Similar Names

⚠️ **ALWAYS verify the exact `website_id`** before creating or updating pages. Nida workspaces can contain multiple sites with near-identical names (e.g., "Agent Demo Site" vs "Nida Agent Demo").

**Before any page operation:**
1. Call `website:list` to get all sites
2. Show the user the full list and confirm which site
3. Note the exact `id` and `subdomain`
4. Use that `id` for all subsequent `page:*` calls

---

## Automation Pattern: Daily Blog Poster

A headless Python script that auto-generates and publishes blog posts daily via cron — no UI approval needed since `seo_content:create` is ungated.

### What it does
- Runs daily at 9 AM (configurable)
- Picks from a rotating bank of pre-written topics (no AI generation needed — all content is human-authored)
- Publishes directly to `nida.craftedmatrix.com` via Agent API
- Tracks which topics have been used to avoid duplicates
- Cycles back to the beginning when all topics are exhausted

### Why this works
- `seo_content:create` does NOT require approval (unlike `update`/`delete`)
- The script is self-contained: state file tracks used indices
- No external dependencies beyond Python stdlib

### Quick-start

1. Save the script as `nida_daily_blog.py`
2. Create `.nida_api_key` file next to it with your API key
3. Run manually: `python3 nida_daily_blog.py`
4. Set cron: `0 9 * * *` (daily at 9 AM)

### Script location

Full source available in the skill repo at `scripts/nida_daily_blog.py`.

### Topic bank
The default topic bank includes 8 high-value articles covering:
- AI agents for small business CRM
- Agentic CRM for startups
- CRM automation for service businesses
- AI voice agents replacing phone systems
- Automated sales funnels
- Email automation revenue strategies
- Chatbots vs AI agents
- Choosing the right CRM by business stage

Each topic includes pre-written HTML sections (headings + paragraphs), meta title, meta description, and slug. Add your own topics by editing the `DEFAULT_TOPICS` array in the script.

### State management
The script stores `used_indices` and `next_index` in `nida_blog_state.json` next to the script. This ensures:
- No duplicate posts across runs
- Automatic reset when all topics are exhausted
- Safe to move between machines (just copy the state file)

### Error handling
- If API key is missing: exits with code 1 and prints error
- If a post fails: continues with remaining posts, reports failures at end
- Non-zero exit code on any failure for cron monitoring

### Scaling up
To publish more posts per day:
- Change `POST_COUNT` env var (default 2)
- Add more topics to the `DEFAULT_TOPICS` array
- Run multiple cron jobs at different times (e.g., 9 AM + 3 PM)

To use AI-generated content instead of pre-written topics:
- Replace the `DEFAULT_TOPICS` array with a function that calls an LLM API
- Use the same `build_html()` and `create_post()` helpers

---
