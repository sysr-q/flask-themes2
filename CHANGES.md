# Changelog

## 2.1.0

Unreleased

- `Themes.init_themes` is renamed to `init_app` like other Flask extensions; the old name still works but warns.
- The module level  `themes_blueprint` is removed and `init_app` now creates the `_themes` blueprint per app.
- Add `refresh()` which clears Jinja's template cache
- `theme_static` and `static_file_url` fall back to the application's static file when the theme does not have it. You can opt out of with `fallback=False`.
- `theme_static` and `static_file_url` pass extra keyword arguments on to `url_for`, so `theme_static('style.css', v=3)` appends `?v=3` for cache busting.
- Themes with an unreadable `info.json` or a mismatching identifier are skipped with a logged warning instead of silently.
- A `THEME_PATHS` string is split on `os.pathsep` instead of `;`.
- `info.json` and `license.txt` are read as UTF-8.
- Requires Flask >= 2.3
