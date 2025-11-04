# 🚀 **GITHUB ACTIONS CI/CD SETUP**

## **Automated Build System for Linux & Windows**

This project now includes GitHub Actions workflows that automatically build distributable executables for both Linux and Windows.

---

## 📋 **WORKFLOW: build-executables.yml**

### **What It Does**

1. **Builds Linux Executable** (Ubuntu latest)
   - Python 3.12 environment
   - PyInstaller compilation
   - Creates `.tar.gz` package

2. **Builds Windows Executable** (Windows latest)
   - Python 3.12 environment
   - PyInstaller compilation
   - Creates `.zip` package

3. **Creates Releases** (on tag push)
   - Combines Linux and Windows builds
   - Creates GitHub Release
   - Uploads both executables

---

## 🎯 **TRIGGERS**

The workflow runs automatically on:

| Trigger | Branch | Action |
|---------|--------|--------|
| **Push** | `main` | Build Linux & Windows |
| **Push** | `refactoring-testing` | Build Linux & Windows |
| **Pull Request** | `main` | Build Linux & Windows |
| **Manual** | Any | `workflow_dispatch` |
| **Tag Push** | Any | Create Release + Upload |

---

## 🔧 **SETUP REQUIREMENTS**

### **1. No Additional Setup Needed!**
The workflow is self-contained and requires:
- ✅ Python 3.12 (provided by GitHub)
- ✅ pip (auto-installed)
- ✅ PyInstaller (auto-installed)

### **2. Secrets (Optional)**
The workflow uses `GITHUB_TOKEN` which is automatically provided by GitHub.

---

## 📦 **OUTPUT ARTIFACTS**

### **After Each Build**
Artifacts are stored for 30 days:

**Linux Build:**
- `SpotifyPlaylistSync-Linux/` - Folder with executable
- `SpotifyPlaylistSync-Linux.tar.gz` - Compressed package

**Windows Build:**
- `SpotifyPlaylistSync-Windows/` - Folder with executable
- `SpotifyPlaylistSync-Windows.zip` - Compressed package

### **How to Download**
1. Go to GitHub Actions tab
2. Click on the workflow run
3. Click "Artifacts" section
4. Download the package you need

---

## 🏷️ **CREATING RELEASES**

### **Automatic Release on Tag**

```bash
# Create a tag
git tag -a v1.0.0 -m "Release version 1.0.0"

# Push the tag to GitHub
git push origin v1.0.0
```

This automatically:
1. ✅ Builds Linux executable
2. ✅ Builds Windows executable
3. ✅ Creates GitHub Release
4. ✅ Uploads both executables as release assets
5. ✅ Generates release notes

### **Manual Release**

You can also create releases manually in GitHub UI:
1. Go to Releases
2. Click "Create new release"
3. Select tag and fill in details

---

## 🔍 **WORKFLOW FILE LOCATION**

```
.github/
└── workflows/
    └── build-executables.yml
```

---

## 📊 **WORKFLOW STRUCTURE**

```yaml
build-linux
  ├── Checkout code
  ├── Setup Python 3.12
  ├── Cache dependencies
  ├── Install requirements
  ├── Build with PyInstaller
  ├── Create .tar.gz package
  └── Upload artifacts

build-windows
  ├── Checkout code
  ├── Setup Python 3.12
  ├── Cache dependencies
  ├── Install requirements
  ├── Build with PyInstaller
  ├── Create .zip package
  └── Upload artifacts

create-release (on tag)
  ├── Download Linux artifacts
  ├── Download Windows artifacts
  ├── Create GitHub Release
  └── Upload release assets
```

---

## 🚀 **MANUAL BUILD EXECUTION**

### **Via GitHub UI (Recommended)**

1. Go to **Actions** tab
2. Click **Build Executables** on the left
3. Click **Run workflow**
4. Select branch
5. Click **Run workflow** button
6. Wait for builds to complete
7. Download artifacts

### **Via Command Line**

```bash
# Trigger workflow via GitHub CLI
gh workflow run build-executables.yml -r main

# View workflow status
gh workflow view build-executables.yml

# List recent runs
gh run list --workflow=build-executables.yml
```

---

## 📋 **MONITORING BUILDS**

### **View Real-Time Output**

1. Go to **Actions** tab
2. Click on the running workflow
3. Click on the job (build-linux or build-windows)
4. View live logs

### **Check Build Status**

```bash
# View workflow status
gh workflow view build-executables.yml

# View latest run
gh run list --workflow=build-executables.yml --limit=1
```

---

## 🐛 **TROUBLESHOOTING**

### **Build Fails**

1. **Check logs**: Click workflow → job → scroll down for errors
2. **Common issues**:
   - Missing `config/requirements.txt` - ensure file exists
   - Python version mismatch - we use Python 3.12
   - Virtual environment issues - cleared automatically

### **Artifacts Not Showing**

- Wait 30 seconds after build completes
- Refresh page
- Check artifact retention settings (set to 30 days)

### **Release Not Created**

- Only triggers on tag push (starts with `v`)
- Ensure both Linux and Windows builds passed first

---

## 💡 **BEST PRACTICES**

### **1. Use Semantic Versioning**
```bash
git tag -a v1.0.0 -m "Initial release"
git tag -a v1.0.1 -m "Bug fix"
git tag -a v1.1.0 -m "New features"
git tag -a v2.0.0 -m "Major release"
```

### **2. Test Before Release**
- Always test builds locally first
- Ensure all tests pass
- Review changes before tagging

### **3. Update Documentation**
- Update CHANGELOG.md before tagging
- Add release notes in GitHub UI
- Document breaking changes

### **4. Monitor Build Times**
- Linux builds: ~2-3 minutes
- Windows builds: ~2-3 minutes
- Release creation: ~30 seconds

---

## 🎯 **NEXT STEPS**

1. **Commit the workflow file**
   ```bash
   git add .github/workflows/build-executables.yml
   git commit -m "Add GitHub Actions CI/CD workflow"
   git push origin main
   ```

2. **Create your first release**
   ```bash
   git tag -a v1.0.0 -m "First production release"
   git push origin v1.0.0
   ```

3. **Download from GitHub**
   - Go to Releases page
   - Download SpotifyPlaylistSync-Linux.tar.gz
   - Download SpotifyPlaylistSync-Windows.zip

---

## 📚 **RESOURCES**

- [GitHub Actions Documentation](https://docs.github.com/en/actions)
- [PyInstaller Documentation](https://pyinstaller.org/)
- [GitHub CLI Reference](https://cli.github.com/manual/)
- [Semantic Versioning](https://semver.org/)

---

**✅ Your CI/CD pipeline is now fully automated and production-ready!**