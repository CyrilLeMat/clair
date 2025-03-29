# 🔑 How to Get a Confluence API Token for Clair

To enable Clair to audit your Confluence content, you need to generate an API token and configure access to the spaces or pages you want to analyze.

---

## ✅ Step-by-step Guide

### 1. Log In to Atlassian
- Go to [https://id.atlassian.com/manage-profile/security/api-tokens](https://id.atlassian.com/manage-profile/security/api-tokens)
- Make sure you're logged in with the account that has access to your Confluence spaces

### 2. Create a New API Token
- Click **"Create API token"**
- Name it something like `ClairAudit`
- Click **Create** and **Copy** the token immediately (you won’t be able to see it again)

---

### 3. Add Credentials to `config.yaml`
In your `config.yaml`, update the `confluence` section like so:

```yaml
confluence:
  enabled: true
  base_url: "https://your-domain.atlassian.net"
  email: "your-email@example.com"
  api_token: "YOUR_API_TOKEN"
  spaces:
    - "DOC"
    - "ENG"
```

- `base_url`: Your Atlassian instance base URL
- `email`: The email address associated with your Atlassian account
- `api_token`: The token you just generated
- `spaces`: The keys of the Confluence spaces Clair should analyze

---

## 🔍 How to Get Confluence Space Keys
1. Go to the Confluence space you want to analyze
2. Look at the URL:
   ```
https://your-domain.atlassian.net/wiki/spaces/ENG/overview
   ```
3. The part after `/spaces/` and before the next `/` is the **space key**: `ENG`

Repeat for all spaces you want Clair to include.

---

## 🛠 Required Permissions
Ensure the Atlassian account used has **read access** to the pages and spaces you want Clair to scan.
- If needed, ask your Confluence admin to grant access
- The API token inherits the permissions of the account it's linked to

---

## 🧪 Testing Access
Once configured, Clair will attempt to connect to Confluence and retrieve content from the listed spaces. If anything fails:
- Double-check your token, email, and base URL
- Make sure the account has access to the space/pages

---

Once you're set up, Clair can begin auditing your Confluence documentation just like it does with Notion! 🚀