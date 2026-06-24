# Soundproject One-Click Installer Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Wrap the existing PyInstaller build into a single `Soundproject-Setup-1.0.0.exe` (built with Inno Setup) that installs the app, silently installs the bundled ViGEmBus driver, and shows a GPLv3 license page — so a stranger can download one file, click through it once, plug in the hardware, and have a working app.

**Architecture:** Packaging-only change, no application code touched. A new `Python/packaging/installer.iss` Inno Setup script wraps the existing `dist/Soundproject/` PyInstaller output, chain-installing the ViGEmBus MSI that `vgamepad` already bundles inside it. A new `LICENSE` file (verbatim GPLv3 text) at the repo root is referenced by the installer's license page.

**Tech Stack:** Inno Setup 6 (`ISCC.exe` compiler), PyInstaller (existing), Windows `msiexec`.

Spec: [`Docs/superpowers/specs/2026-06-24-soundproject-installer-design.md`](../specs/2026-06-24-soundproject-installer-design.md)

---

### Task 1: Add the GPLv3 LICENSE file

**Files:**
- Create: `LICENSE` (repo root)

- [ ] **Step 1: Download the canonical GPLv3 text verbatim**

Use a direct HTTP download (not a tool that might summarize/reformat text) so the file is byte-for-byte the official text:

```bash
curl -fsSL -o LICENSE https://www.gnu.org/licenses/gpl-3.0.txt
```

- [ ] **Step 2: Verify it downloaded correctly**

```bash
wc -c LICENSE && head -3 LICENSE && tail -5 LICENSE
```

Expected: size around 35,000 bytes (a few hundred either way is fine; under ~5,000 means something went wrong, e.g. an HTML error page got saved instead). First lines show:
```
                    GNU GENERAL PUBLIC LICENSE
                       Version 3, 29 June 2007
```
Last lines show the "How to Apply These Terms to Your New Programs" section ending in `END OF TERMS AND CONDITIONS` followed by the appendix text.

- [ ] **Step 3: Commit**

```bash
git add LICENSE
git commit -m "Add GPLv3 LICENSE"
```

---

### Task 2: Install the Inno Setup compiler (one-time dev-machine setup)

This installs a regular free dev tool (not a driver) via Windows' own trusted package manager. It's a one-time setup on whichever machine builds releases — end users who just run the resulting `Setup.exe` never need this.

**Files:** none (environment setup only)

- [ ] **Step 1: Install via winget**

```bash
winget install --id JRSoftware.InnoSetup --silent
```

Expected: exits 0, reports `Successfully installed`.

- [ ] **Step 2: Verify ISCC.exe is present**

```bash
"/c/Program Files (x86)/Inno Setup 6/ISCC.exe" /?
```

Expected: prints Inno Setup Compiler version/usage banner. If winget installed it somewhere else, find it with:

```bash
find "/c/Program Files (x86)/Inno Setup 6" "/c/Program Files/Inno Setup 6" -maxdepth 1 -iname "ISCC.exe" 2>/dev/null
```

No commit (nothing in the repo changes).

---

### Task 3: Rebuild the PyInstaller app bundle inside this worktree

Worktrees don't inherit gitignored build output from the main checkout, so `Python/dist/` doesn't exist here yet. The installer script in Task 4 packages whatever is in `Python/dist/Soundproject/`, so that has to exist first.

**Files:** none tracked (produces gitignored `Python/dist/`, `Python/build/`)

- [ ] **Step 1: Build it**

```bash
cd Python
python packaging/make_icon.py
pyinstaller packaging/soundproject.spec
```

- [ ] **Step 2: Verify the build output and the bundled driver MSI are both present**

```bash
ls dist/Soundproject/Soundproject.exe
find dist/Soundproject/_internal/vgamepad/win/vigem/install/x64 -iname "*.msi"
```

Expected: both commands print a path, no "No such file" errors.

No commit (build output is gitignored).

---

### Task 4: Write and compile the Inno Setup installer script

**Files:**
- Create: `Python/packaging/installer.iss`

- [ ] **Step 1: Write the script**

```ini
#define MyAppName "Soundproject"
#define MyAppVersion "1.0.0"
#define MyAppPublisher "Soundproject"
#define MyAppExeName "Soundproject.exe"

[Setup]
AppId={{0BB34128-C518-4090-8889-54B996BEF7A3}
AppName={#MyAppName}
AppVersion={#MyAppVersion}
AppPublisher={#MyAppPublisher}
DefaultDirName={autopf}\{#MyAppName}
DefaultGroupName={#MyAppName}
DisableProgramGroupPage=yes
LicenseFile=..\..\LICENSE
OutputDir=..\dist
OutputBaseFilename=Soundproject-Setup-{#MyAppVersion}
Compression=lzma
SolidCompression=yes
WizardStyle=modern
ArchitecturesAllowed=x64compatible
ArchitecturesInstallIn64BitMode=x64compatible
PrivilegesRequired=admin
SetupIconFile=icon.ico
UninstallDisplayIcon={app}\{#MyAppExeName}

[Languages]
Name: "english"; MessagesFile: "compiler:Default.isl"

[Tasks]
Name: "desktopicon"; Description: "Create a &desktop icon"; GroupDescription: "Additional icons:"

[Files]
Source: "..\dist\Soundproject\*"; DestDir: "{app}"; Flags: ignoreversion recursesubdirs createallsubdirs

[Icons]
Name: "{group}\{#MyAppName}"; Filename: "{app}\{#MyAppExeName}"
Name: "{group}\Uninstall {#MyAppName}"; Filename: "{uninstallexe}"
Name: "{autodesktop}\{#MyAppName}"; Filename: "{app}\{#MyAppExeName}"; Tasks: desktopicon

[Run]
Filename: "{sys}\msiexec.exe"; Parameters: "/i ""{app}\_internal\vgamepad\win\vigem\install\x64\ViGEmBusSetup_x64.msi"" /quiet /norestart"; StatusMsg: "Installing ViGEmBus driver..."; Flags: waituntilterminated
Filename: "{app}\{#MyAppExeName}"; Description: "Launch {#MyAppName}"; Flags: nowait postinstall skipifsilent
```

Notes for whoever implements this:
- `AppId` is a fixed, already-generated GUID — keep it identical in every future version so Windows treats upgrades as upgrades, not a second parallel install. Do not regenerate it.
- `{sys}\msiexec.exe` plus `ArchitecturesInstallIn64BitMode=x64compatible` resolves to the real `System32\msiexec.exe`, not the WOW64 redirected one.
- `AppPublisher` is set to "Soundproject" (the project itself) rather than a personal name — change this single line if a different publisher string is wanted, nothing else depends on it.

- [ ] **Step 2: Compile it**

```bash
cd Python
"/c/Program Files (x86)/Inno Setup 6/ISCC.exe" packaging/installer.iss
```

- [ ] **Step 3: Verify the output**

```bash
ls -la dist/Soundproject-Setup-1.0.0.exe
```

Expected: compiler output ends with `Successful compile (0 errors, 0 warnings)` (warnings about missing translations are fine if any appear; 0 errors is the hard requirement), and the file exists, several MB+ in size.

- [ ] **Step 4: Commit**

```bash
git add packaging/installer.iss
git commit -m "Add Inno Setup installer script"
```

(`dist/Soundproject-Setup-1.0.0.exe` itself is a build artifact under the already-gitignored `Python/dist/` — it does not get committed.)

---

### Task 5: Update the README

**Files:**
- Modify: `Python/README.md`

- [ ] **Step 1: Add a License line and the installer build step**

In the `## Build the standalone .exe` section, add a new `## Build the installer` section right after it, plus a `## License` section at the end of the file. Concretely, change this:

```markdown
## Build the standalone .exe

```
pip install -r requirements-dev.txt
python packaging/make_icon.py
pyinstaller packaging/soundproject.spec
```

The build lands in `dist/Soundproject/Soundproject.exe`.
```

to this:

```markdown
## Build the standalone .exe

```
pip install -r requirements-dev.txt
python packaging/make_icon.py
pyinstaller packaging/soundproject.spec
```

The build lands in `dist/Soundproject/Soundproject.exe`.

## Build the installer

Requires the free [Inno Setup](https://jrsoftware.org/isinfo.php) compiler (one-time
dev-machine install: `winget install --id JRSoftware.InnoSetup`). Run after the steps
above, from `Python/`:

```
"C:\Program Files (x86)\Inno Setup 6\ISCC.exe" packaging\installer.iss
```

Produces `dist\Soundproject-Setup-1.0.0.exe` — a single file that installs the app,
shortcuts, and the ViGEmBus driver in one click. This is what to hand to anyone who
isn't building from source.
```

Then add at the very end of the file:

```markdown
## License

GPLv3 — see [LICENSE](../LICENSE).
```

- [ ] **Step 2: Caveat the manual ViGEmBus section for installer users**

The existing `## One-time external dependency` section (right after the new `## Build the installer` section) still applies to anyone running from source or the plain `.exe` — but is now redundant/confusing for anyone who used the new installer. Add one sentence to the top of that section:

```markdown
## One-time external dependency

If you used `Soundproject-Setup-*.exe`, this is already handled — skip this section.

Gamepad button presses require the [ViGEmBus driver](https://github.com/nefarius/ViGEmBus)
to be installed once on the machine. It can't be bundled into the .exe (it's
```

(i.e. insert the new sentence, keep the rest of the existing paragraph unchanged.)

- [ ] **Step 3: Verify**

```bash
grep -n "Inno Setup\|License\|already handled" README.md
```

Expected: shows the new lines added in Steps 1 and 2.

- [ ] **Step 4: Commit**

```bash
git add README.md
git commit -m "Document the installer build step and GPLv3 license"
```

---

### Task 6: Verify the installer end-to-end

This is manual/behavioral verification — there's no pytest-style unit test for an installer wizard. ViGEmBus is already installed on this dev machine (installed manually earlier), so the driver-install step will be observed as a fast no-op here rather than a true clean-machine first-install; that's expected and is noted as a known gap in the spec's verification plan.

**Files:** none

- [ ] **Step 1: Run the installer**

Launch `Python\dist\Soundproject-Setup-1.0.0.exe` (e.g. via computer-use or by hand). Click through it.

Expected, in order: License Agreement page showing real GPLv3 text with Next disabled until "I accept" is selected → install location page → "Create a desktop icon" checkbox page → a single UAC prompt → install progress → Finish page with "Launch Soundproject" checked.

- [ ] **Step 2: Confirm the app installed correctly**

```powershell
Get-Item "C:\Program Files\Soundproject\Soundproject.exe"
Get-Service ViGEmBus | Select-Object Status, StartType
```

Expected: the exe exists; `ViGEmBus` shows `Running` / `System` (same as before — confirming the chained install didn't break anything).

- [ ] **Step 3: Confirm the Start Menu shortcut launches the app**

Open Start Menu, find "Soundproject", launch it, confirm the Carbon Red GUI window opens (same check as the earlier source-run verification).

- [ ] **Step 4: Uninstall and confirm clean removal**

Uninstall via Settings → Apps → Soundproject → Uninstall (this runs the uninstaller Inno Setup generated automatically; no separate tool needed):

```powershell
Get-Item "C:\Program Files\Soundproject" -ErrorAction SilentlyContinue
Get-Service ViGEmBus | Select-Object Status
```

Run the uninstall from Windows Settings first, then re-run the two commands above. Expected: the `Soundproject` directory check now fails (`ErrorAction SilentlyContinue` just suppresses the error, absence is the pass condition), and `ViGEmBus` is still `Running` — confirming uninstall didn't touch the shared driver, per the design decision to leave it installed.

No commit (verification only). If any step fails, stop and report — don't move on to merging a broken installer.
