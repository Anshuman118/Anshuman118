<div align="center">

### <code>Anshuman118@github ~ $ ./contributions.sh</code>

<img src="./contrib-heatmap.svg" width="860" alt="Animated contribution heatmap" />

<br><br>

### <code>Anshuman118@github ~ $ whoami</code>

<table>
  <tr>
    <td valign="top">
      <img src="./avi-ascii.svg" width="370" alt="Animated ASCII portrait" />
    </td>
    <td valign="top">
      <img src="./info-card.svg" width="490" alt="Animated neofetch profile card" />
    </td>
  </tr>
</table>

<br>

### <code>Anshuman118@github ~ $ cat stack.txt</code>

<pre>
Python • C++ • Java • JavaScript • Git • GitHub
</pre>

### <code>Anshuman118@github ~ $ exit</code>

</div>

---

## Customize

This profile is intentionally built from local, self-contained SVGs rather than third-party
GitHub-stat widgets. The repository follows the requested terminal/neofetch architecture:
the README embeds generated SVGs with `<img>`, while SVG SMIL animations handle the visual
effects.

### Configuration

Replace these placeholders before pushing:

- `Anshuman118` — your GitHub username.
- `YOUR_NAME` — your display name.
- `YOUR_ROLE` — your role.
- `CURRENT_FOCUS` — what you are working on now.
- `PREVIOUS_EXPERIENCE` — previous experience.
- `YOUR_HIGHLIGHTS` / the `HIGHLIGHTS` value — projects, achievements, etc.
- `PORTRAIT SOURCE` — your local source image.
- Colors — edit the constants at the top of the SVG generator scripts.
- SVG widths — edit the README `<img width="...">` values.
- Animation speed — change the `begin`/`dur` values in the SVG generator scripts.

### Where to edit

| What you want to change | Edit |
|---|---|
| Username | `README.md`, `.github/workflows/update-profile-art.yml`, and `--username` when fetching |
| Name / role / focus / experience / stack | `scripts/make_info_card.py` |
| Portrait | Supply a new source photo to `scripts/prep_photo.py` |
| Portrait colors / grid | `scripts/make_ascii_svg.py` |
| Heatmap colors / dimensions | `scripts/render_heatmap_svg.py` |
| Animation speed | `scripts/make_ascii_svg.py`, `scripts/make_info_card.py`, `scripts/render_heatmap_svg.py` |
| Heatmap data | `data/contributions.json` is generated automatically |

### Local setup

macOS/Linux:

```bash
python3 -m venv .venv
source .venv/bin/activate
python -m pip install -r scripts/requirements.txt
```

Windows PowerShell:

```powershell
py -3.11 -m venv .venv
.venv\Scripts\Activate.ps1
python -m pip install -r scripts\requirements.txt
```

Windows Command Prompt:

```bat
py -3.11 -m venv .venv
.venv\Scripts\activate.bat
python -m pip install -r scripts\requirements.txt
```

### Generate everything

Place your portrait in the repository root, then run:

```bash
python scripts/prep_photo.py source-photo.jpg
python scripts/make_ascii_svg.py
python scripts/make_info_card.py
python scripts/fetch_contributions.py --username Anshuman118
python scripts/render_heatmap_svg.py
```

For a static info-card preview:

```bash
STATIC=1 python scripts/make_info_card.py
```

Windows PowerShell:

```powershell
$env:STATIC="1"
python scripts/make_info_card.py
Remove-Item Env:STATIC
```

### Preview locally

The generated SVGs are standalone files. Open `avi-ascii.svg`, `info-card.svg`, and
`contrib-heatmap.svg` directly in a modern browser, or serve the directory:

```bash
python -m http.server 8000
```

Then open `http://localhost:8000/`.

### Create the GitHub profile repository

A GitHub profile repository must have the exact same name as the GitHub username. With GitHub CLI:

```bash
gh repo create YAnshuman118 --public --clone
cd Anshuman118
mkdir -p scripts data .github/workflows
```

Copy this project into that repository, replace the placeholders, generate the SVGs/data,
then commit:

```bash
git add .
git commit -m "build animated profile README"
git push
```

GitHub renders the profile repository's `README.md` at the top of the matching user's profile.

### Daily contribution refresh

`.github/workflows/update-profile-art.yml` runs daily at `06:17 UTC`, and also supports
`workflow_dispatch`. It only regenerates:

- `data/contributions.json`
- `contrib-heatmap.svg`

The portrait and info card stay unchanged until you regenerate them manually.

The workflow uses the repository's built-in Actions write permission to commit generated files;
it does not require you to create or store a personal access token.

### Design constraints

- No JavaScript.
- No external CSS.
- No `<script>` tags.
- No third-party GitHub statistics service.
- No GitHub GraphQL API.
- No personal access token.
- Contribution data comes from GitHub's public contribution-calendar HTML.
- Animation lives inside standalone SVG files.
- Animations are one-shot and freeze at their final state.
- The README uses `<img>` and a table for predictable GitHub rendering.

### Important note

GitHub can change its contribution-calendar HTML. The scraper deliberately has a fallback
for common `data-date` markup changes and fails with a useful message rather than silently
writing incorrect data. If GitHub changes the page structure substantially, update
`scripts/fetch_contributions.py`.

### Setup checklist

- [ ] Create the profile repository with the exact username.
- [ ] Replace every `Anshuman118`.
- [ ] Replace `YOUR_NAME`, `YOUR_ROLE`, and the profile values in `make_info_card.py`.
- [ ] Put your portrait at `source-photo.jpg` or pass another path to `prep_photo.py`.
- [ ] Install the local dependencies.
- [ ] Generate the portrait SVG, info card, contribution JSON, and heatmap.
- [ ] Open the SVGs locally and verify them.
- [ ] Push to GitHub.
- [ ] Run the workflow manually once from the Actions tab.
