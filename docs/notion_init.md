# 🔑 How to Get a Notion API Key for Clair

To enable Clair to audit your Notion workspace, you need to generate a Notion API integration token and connect it to the database(s) you want to analyze.

---

## ✅ Step-by-step Guide

### 1. Go to the Notion Developers Portal
- Navigate to [https://www.notion.com/my-integrations](https://www.notion.com/my-integrations)
- Click **"+ New integration"**

### 2. Create a New Integration
- Give your integration a name, e.g. `ClairAudit`
- Choose your **workspace**
- Under **Capabilities**, enable:
  - ✅ Read content
  - ✅ Read user information (optional)
- Click **Submit**

### 3. Copy the Integration Token
- Once the integration is created, you’ll see a **"Internal Integration Token"**
- Copy it and paste it into your `config.yaml` under the `notion` section:

```yaml
notion:
  enabled: true
  integration_token: "YOUR_NOTION_TOKEN"
  database_ids:
    - "your-database-id"
```

---

### 4. Share Databases with Your Integration
- Open Notion and navigate to the database you want Clair to access
- Click **Share** in the top-right corner
- Type the name of your integration (e.g. `ClairAudit`) and grant access
- Repeat this for each database you want to analyze

---

## 🧪 How to Get a Database ID

To get the `database_id`:
1. Open the database in Notion
2. Copy the URL — it looks like:

```
https://www.notion.so/yourworkspace/Name-of-DB-a1b2c3d4e5f67890123456789abcdef0
```

3. Extract the last part (after the last slash, ignoring query params):
```
a1b2c3d4e5f67890123456789abcdef0 → your `database_id`
```

---

## 🧠 Tips
- Your integration **won’t see any content** unless it’s explicitly shared to it.
- Make sure all relevant **pages and subpages** are inside the shared database.
- You can test API access using [Notion SDK](https://github.com/ramnes/notion-sdk-py) or Clair's future `--dry-run` mode.

---

Once you’ve added your token and database ID(s) to `config.yaml`, you’re ready to start auditing Notion content with Clair! 🚀
