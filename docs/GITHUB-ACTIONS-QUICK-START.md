# 🚀 **QUICK START: GITHUB ACTIONS BUILD SYSTEM**

## **One-Line Setup**

Everything is already configured! Just push your changes and GitHub Actions will build automatically.

---

## 🎯 **Three Ways to Trigger Builds**

### **1. Automatic (Just Push Code) ⭐ EASIEST**
```bash
# Push to main or refactoring-testing branch
git push origin main

# Builds start automatically!
# Check GitHub Actions tab to watch progress
```

### **2. Manual (Via GitHub UI)**
1. Go to your repo on GitHub
2. Click **Actions** tab
3. Click **Build Executables**
4. Click **Run workflow** button
5. Watch the magic happen!

### **3. Create a Release (With Version)**
```bash
# Tag a new release
git tag -a v1.0.0 -m "My First Release"

# Push the tag
git push origin v1.0.0

# This triggers:
# ✅ Builds both Linux and Windows
# ✅ Creates GitHub Release
# ✅ Uploads files as release assets
```

---

## 📥 **Download Your Executables**

### **From Artifacts (After Any Build)**
1. **Go to Actions** → Click the workflow
2. **Scroll to bottom** → See Artifacts section
3. **Download** what you need:
   - `SpotifyPlaylistSync-Linux.tar.gz` (Linux)
   - `SpotifyPlaylistSync-Windows.zip` (Windows)

### **From Releases (Tagged Builds)**
1. **Go to Releases** on your repo
2. **Download** the version you want
3. Files available: `.tar.gz` and `.zip`

---

## 🎵 **Using Your Built Executables**

### **Linux**
```bash
# Extract
tar -xzf SpotifyPlaylistSync-Linux.tar.gz
cd SpotifyPlaylistSync-Linux

# Run
./SpotifyPlaylistSync
```

### **Windows**
```cmd
# Extract SpotifyPlaylistSync-Windows.zip

# Run
SpotifyPlaylistSync.exe
```

---

## ✅ **Verify It's Working**

**After you push code:**
1. Go to GitHub **Actions** tab
2. You should see **Build Executables** running
3. Watch for ✅ green checks (success)
4. If you see ❌, click to see error details

**Check status in ~3 minutes for:**
- ✅ Linux build complete
- ✅ Windows build complete
- ✅ Artifacts uploaded

---

## 🔄 **Typical Workflow**

```bash
# 1. Make changes locally
echo "my changes" >> file.py

# 2. Commit changes
git add .
git commit -m "Added new feature"

# 3. Push to GitHub
git push origin main

# ✅ GitHub Actions automatically:
#    • Builds Linux executable
#    • Builds Windows executable
#    • Uploads to artifacts
#    • Ready to download in 3 minutes!

# 4. When ready for release, tag it
git tag -a v1.1.0 -m "Feature release"
git push origin v1.1.0

# ✅ GitHub automatically:
#    • Creates Release page
#    • Uploads both executables
#    • Generates release notes
```

---

## 🎯 **Release Versioning**

Follow semantic versioning:

```bash
# Bug fix (v1.0.0 → v1.0.1)
git tag -a v1.0.1 -m "Fix path handling"

# New features (v1.0.0 → v1.1.0)
git tag -a v1.1.0 -m "Add new sync options"

# Major release (v1.0.0 → v2.0.0)
git tag -a v2.0.0 -m "Complete rewrite"
```

---

## 🚨 **Common Issues**

### "Build Failed"
- Check **Actions** tab for error logs
- Usually: missing dependencies
- Fix: Ensure `config/requirements.txt` exists

### "Can't Find Artifacts"
- Wait 1-2 minutes after build finishes
- Refresh the page
- Look in **Artifacts** section (not files)

### "Release Not Created"
- Releases only trigger on tags starting with `v`
- Example: `v1.0.0` ✅, `version1` ❌
- Both Linux and Windows builds must succeed first

---

## 💡 **Pro Tips**

✅ **Always build before release**
```bash
# Push and let it build
git push origin main

# Wait for success, then tag
git tag -a v1.0.0
git push origin v1.0.0
```

✅ **Check logs to debug**
- Click on failed workflow
- View detailed logs
- Fix issues locally, then repush

✅ **Use GitHub CLI for speed**
```bash
# List recent builds
gh run list --workflow=build-executables.yml

# View latest build details
gh run view $(gh run list -L1 --json databaseId -q '.[0].databaseId')
```

---

## 📊 **What Gets Built**

| Platform | File Format | Size | Notes |
|----------|-------------|------|-------|
| Linux | `.tar.gz` | ~30MB | Portable binary |
| Windows | `.zip` | ~30MB | Portable binary |

Both include:
- ✅ All Python dependencies
- ✅ Spotify API client
- ✅ YouTube downloader
- ✅ Audio processor
- ✅ No Python installation needed!

---

## 🎉 **You're All Set!**

Your CI/CD pipeline is ready. Just:
1. Make changes
2. Push code
3. Get built executables!

No more manual building. GitHub does it all for you! 🚀

---

**Questions?** Check the full documentation in `docs/CI-CD-SETUP.md`