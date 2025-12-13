# 🚀 GitHub Setup Guide - TallyConnect

## स्टेप-बाय-स्टेप मार्गदर्शन

---

## Step 1: GitHub Repository तयार करा (2 minutes)

### 1.1 GitHub वर जा
- Link: https://github.com/new
- किंवा: GitHub.com → Login → Top-right "+" → "New repository"

### 1.2 Repository Details भरा
```
Repository name: TallyConnect
Description: Modern Tally Sync Platform - Professional data synchronization tool

☑️ Private (Recommended - फक्त तुम्हाला दिसेल)
☐ Public (कोणीही पाहू शकेल)

❌ Don't check these:
   ☐ Add a README file
   ☐ Add .gitignore
   ☐ Choose a license
```

### 1.3 Create Repository
- **"Create repository"** button क्लिक करा
- नवीन page उघडेल - **तिथे URL दिसेल**
- Example: `https://github.com/pramit123/TallyConnect`

---

## Step 2: Personal Access Token तयार करा (One-time setup)

### 2.1 Token Generation Page वर जा
Link: https://github.com/settings/tokens/new

किंवा Manual:
1. GitHub → Profile Picture (Top-right)
2. Settings
3. (Scroll down) Developer settings
4. Personal access tokens → Tokens (classic)
5. "Generate new token" → "Generate new token (classic)"

### 2.2 Token Settings
```
Note: TallyConnect Access Token
Expiration: No expiration (किंवा 90 days)

Select Scopes (permissions):
☑️ repo (Full control of private repositories)
   ☑️ repo:status
   ☑️ repo_deployment
   ☑️ public_repo
   ☑️ repo:invite
```

### 2.3 Generate & Copy
1. Scroll down → **"Generate token"** button
2. 🟢 **Token दिसेल** (ghp_xxxxxxxxxxxxxxxxxxxx)
3. ⚠️ **IMPORTANT:** Token COPY करून safe जागी save करा
4. ⚠️ हा token **फक्त एकदा** दिसतो - पुन्हा मिळणार नाही!

Example token:
```
ghp_1234567890abcdefghijklmnopqrstuvwxyz
```

---

## Step 3: Code Push करा

### 3.1 Script Edit करा

1. **File उघडा:** `github_push.bat`
2. **Line 9** वर तुमचे GitHub username टाका:
   ```batch
   set GITHUB_USER=YOUR_USERNAME
   ```
   
   Example:
   ```batch
   set GITHUB_USER=pramit123
   ```

3. **Save करा** (Ctrl+S)

### 3.2 Script चालवा

1. **Double-click** `github_push.bat`
2. Terminal उघडेल
3. **Login prompt:**
   ```
   Username: [तुमचे GitHub username टाका]
   Password: [Token paste करा - NOT password!]
   ```

4. **Enter** दाबा

### 3.3 Success!
```
SUCCESS! Code pushed to GitHub
Repository URL: https://github.com/pramit123/TallyConnect
```

---

## ⚠️ Troubleshooting

### Problem 1: "Authentication failed"
**Solution:**
- Password ऐवजी **Personal Access Token** वापरा
- Token regenerate करा: https://github.com/settings/tokens/new

### Problem 2: "Repository not found"
**Solution:**
- `github_push.bat` मध्ये username check करा
- GitHub वर repository create केले आहे का ते verify करा

### Problem 3: "Permission denied"
**Solution:**
- Token च्या permissions check करा
- `repo` scope select केले आहे का ते verify करा

### Problem 4: "Remote origin already exists"
**Solution:**
Already handled in script! Script automatic remove करून नवीन add करेल.

---

## 🎯 After Push - काय करू शकता:

### 1. Repository पाहा
```
https://github.com/YOUR_USERNAME/TallyConnect
```

### 2. Settings Configure करा
- Settings → General → Features
- ☑️ Issues (bug tracking)
- ☑️ Projects (project management)
- ☑️ Wiki (documentation)

### 3. Branch Protection (Recommended)
- Settings → Branches
- Add rule → Branch name: `main`
- ☑️ Require pull request reviews before merging
- ☑️ Require status checks to pass

### 4. Collaborators Add करा (Optional)
- Settings → Collaborators
- "Add people" → Enter username/email

### 5. README Badge Add करा
```markdown
![Version](https://img.shields.io/badge/version-5.6-blue)
![Python](https://img.shields.io/badge/python-3.13-green)
![License](https://img.shields.io/badge/license-Proprietary-red)
```

---

## 📝 Future Commits

### नवीन changes push करायचे:

```bash
# Changes stage करा
git add .

# Commit करा
git commit -m "Your commit message"

# Push करा
git push
```

किंवा simple batch file बनवा:
```batch
@echo off
git add .
git commit -m "%1"
git push
```

Save as: `quick_push.bat`

Use: `quick_push.bat "Fixed bug in sync logic"`

---

## 🔐 Security Best Practices

1. ✅ **Private repository** वापरा (sensitive code)
2. ✅ **Token secure ठेवा** (password manager मध्ये)
3. ✅ **Token periodically rotate करा** (90 days)
4. ✅ **.gitignore** verify करा (DB files ignore होतात का)
5. ❌ **Token code मध्ये hardcode नका**
6. ❌ **Token screenshot/email नका करू**

---

## 📞 Need Help?

### GitHub Resources:
- Docs: https://docs.github.com
- Support: https://support.github.com
- Community: https://github.community

### Common Links:
- Create Token: https://github.com/settings/tokens/new
- Your Repositories: https://github.com?tab=repositories
- Your Profile: https://github.com/YOUR_USERNAME

---

**Happy Coding! 🚀**

