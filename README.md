# Bing Wallpaper Export

Export Windows Bing / Spotlight lock screen wallpapers from the system cache folder into your Downloads directory, renaming them into an easy-to-browse format:

```
BingWallpaper + YYMMDD + 2-digit sequence + .jpg
```

For example: `feca8fc18a9abd4081c3c5fd4a3304d0089220ac16ce6d298db85a34242ce4c2` becomes `BingWallpaper26091101.jpg`.

Two functionally identical implementations are provided: a **Python** script and a pure **Windows batch** (`.bat`) file. Both resolve all paths at runtime through `%userprofile%`, so nothing is hard-coded to a specific username or drive letter. The same files work for any Windows user.

---

## How It Works (Principle)

Windows 10/11 downloads Bing's daily images ("Windows Spotlight" / lock screen photos) into a hidden cache folder:

```
%userprofile%\AppData\Local\Packages\Microsoft.Windows.ContentDeliveryManager_cw5n1h2txyewy\LocalState\Assets
```

The files in this folder:

- have **no file extension** (they are stored as bare hashed filenames), and
- are actually **JPEG images** despite lacking the `.jpg` suffix.

Because they have no extension, Windows Explorer cannot preview them and most image viewers will not open them. This tool:

1. **Scans** the source folder and selects only regular files with **no extension** (files with any suffix — `.txt`, the script itself, etc. — are ignored).
2. **Sorts** the selected filenames alphabetically so the result is deterministic and reproducible.
3. **Copies** each file (the source is never modified) into the destination folder (`%userprofile%\Downloads` by default).
4. **Renames** each copy to `BingWallpaperYYMMDD##.jpg`, where `YYMMDD` is today's date (two-digit year, month, day) and `##` is a zero-padded sequence starting at `01`.
5. **Avoids overwrites**: before writing each file it scans the destination for that day's prefix and continues numbering after the highest existing sequence. Running the tool twice in one day will not overwrite the first batch — it appends `02`, `03`, ... as needed.

### Portability design

All paths are derived from `%userprofile%` at runtime:

- In Python: `os.path.expandvars("%userprofile%")` (equivalent to `os.path.expanduser("~")`).
- In the batch file: the `%userprofile%` environment variable.

So a copy placed under `C:\Users\Alice`, `D:\Users\Bob`, or any other profile works without editing a single line.

---

## Features

- Cross-user / cross-machine — no hard-coded usernames or drive letters.
- Standard-library only — the Python version needs no third-party packages and no internet access.
- Non-destructive — source files are copied, never moved, renamed, or deleted.
- Deterministic naming — alphabetical sort plus zero-padded sequence.
- Overwrite protection — numbering continues after existing files for the same day.
- Optional custom source and destination directories via arguments.
- Pure-ASCII batch file — safe under any Windows code page (see note below).

---

## Naming Convention

```
BingWallpaper  YYMMDD  ##  .jpg
     |            |     |    |
   fixed      today   seq  extension
              date   (01..)
```

- `YYMMDD` example: `260911` = 2026-09-11.
- `##` is two digits (`01`, `02`, ... `99`). Sequence restarts from `01` on a new date.
- Files are sorted by their original (hash) filename before numbering, so the mapping is stable.

---

## Requirements

- **Python version**: Python 3.x (any modern 3.x; standard library only).
- **Batch version**: Windows with `cmd.exe`. The date is read via `wmic os get localdatetime` and falls back to `powershell -Command "Get-Date -Format yyMMdd"` if `wmic` is unavailable, so it works on editions where `wmic` has been removed.

---

## Usage

### A. Python version (recommended)

Run the script with the default source and destination:

```bash
python export_bing_wallpapers.py
```

Specify a custom source directory:

```bash
python export_bing_wallpapers.py --src "D:\my wallpapers"
```

Specify both a custom source and destination (useful for a dry run into a temporary folder):

```bash
python export_bing_wallpapers.py --src "D:\my wallpapers" --dst "E:\test output"
```

`%userprofile%` variables are also accepted in the arguments.

Example output:

```
feca8fc18a9abd4081c3c5fd4a3304d0089220ac16ce6d298db85a34242ce4c2  ->  BingWallpaper26091101.jpg
...
[DONE] Copied 11 file(s) to: C:\Users\you\Downloads
```

### B. Batch version

Double-click `export_bing_wallpapers.bat`, or run it from a command prompt:

```bat
REM Use default source and destination (paths derived from %userprofile%)
export_bing_wallpapers.bat

REM Custom source (%1) and destination (%2)
export_bing_wallpapers.bat "D:\other source" "E:\other destination"
```

The output and naming are identical to the Python version.

---

## Notes and Troubleshooting

- **The `.bat` file must stay pure ASCII.** On Chinese Windows (GBK code page, 936), `cmd.exe` reads batch files using the local code page. If the file contains UTF-8 Chinese text, the characters are misread as garbage and can be executed as commands, producing errors like `'xxx' is not recognized as an internal or external command`. All comments and messages in the batch file are therefore written in English. If you edit it, keep it ASCII-only, CRLF line endings, and no BOM.
- **Avoid `>` in `echo` lines inside `( )` blocks in batch**, even escaped as `^>` — it can trigger `to: was unexpected at this time.` Use plain wording such as `renamed to` instead.
- **Always build the source path as `"%SRC%\%%F"` in batch**, not `%%~fF`. The `%%~fF` modifier expands a bare filename against the *current working directory*, not the source directory, which makes `copy` fail for every file.
- **Source files are cached wallpapers.** They disappear when Windows rotates/replaces Spotlight assets, so export anything you want to keep before the cache is refreshed.
- **Running twice in one day is safe** — the sequence continues rather than overwriting. If you specifically want to restart at `01`, move the old files out of the destination first or use an empty `--dst` folder.

---

## License

MIT License. See [LICENSE](LICENSE).

## Author

Penicillin508
