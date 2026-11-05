# Jellybeans Theme Continued

A dark theme for JetBrains IDEs, inspired by [Jellybeans for Vim](https://github.com/nanotech/jellybeans.vim).
Warm, muted syntax colors accompany a matching dark interface and editor color scheme.

This is a maintained continuation of the theme by Zack A. (aurdevv), via
[sefidel/jellybeans-intellij](https://github.com/sefidel/jellybeans-intellij).
It uses a separate plugin ID (`io.github.2chevskii.jellybeans`) from the
[original Marketplace listing](https://plugins.jetbrains.com/plugin/17030-jellybeans-theme).

## Install

Supports IntelliJ Platform 2023.3 and later. Download the release ZIP or build it below,
then choose **Settings → Plugins → ⚙ → Install Plugin from Disk…** and select the ZIP.
In **Settings → Appearance & Behavior → Appearance**, select **Jellybeans**.
The matching editor scheme is **Jellybeans IDEA**.
Disable the original Jellybeans plugin first if installed, to avoid duplicate theme names.

## Build and validate

Use JDK 21 (JDK 17 is the minimum) and Python 3.10 or later. Gradle downloads are
checksum-verified; the wrapper is included, so a system Gradle installation is unnecessary.

```sh
python scripts/validate_theme.py
python -m unittest discover -s scripts
./gradlew buildPlugin verifyPluginStructure verifyPlugin
python scripts/validate_theme.py build/distributions/jellybeans-1.0.0.zip
```

On Windows, use `gradlew.bat` in place of `./gradlew`.
The installable ZIP is written to `build/distributions/`. Plugin Verifier checks
IntelliJ IDEA 2023.3.8 and the latest stable IntelliJ IDEA; reports are under `build/reports/`.
CI runs the same checks on pull requests and pushes to `master`.
Use `./gradlew runIde` to preview the theme in a development IDE.

The theme is resource-only: no executable code or extra runtime dependencies.
Its minimum IDE build is `233`, with no upper bound. Compatibility verification checks
plugin structure and platform compatibility; visually review the theme before releasing.

## Publish

1. Set `pluginVersion` in `gradle.properties` and update the change notes in
   `src/main/resources/META-INF/plugin.xml` and `CHANGELOG.md`.
2. Run the build and validation commands above. Install the ZIP in the oldest supported
   IDE and the latest stable IDE. Review editor highlighting, selection, search, settings,
   tool windows, VCS colors, and disabled controls, including the current UI.
3. Capture genuine IDE screenshots for the Marketplace listing. Include code and IDE chrome;
   avoid mockups. Set the source, issue tracker, MIT license, and Theme category on the listing.
4. For signing, provide `CERTIFICATE_CHAIN`, `PRIVATE_KEY`, and `PRIVATE_KEY_PASSWORD`
   as environment variables and run `./gradlew signPlugin`. Keep credentials outside the repository.
5. [Upload the first release manually](https://plugins.jetbrains.com/docs/intellij/publishing-plugin.html)
   to JetBrains Marketplace using the ZIP in `build/distributions/`. The first release needs
   its own listing; this fork cannot update the original author's listing.
6. For subsequent releases, provide `JETBRAINS_MARKETPLACE_TOKEN` and run `./gradlew publishPlugin`.
   Supply the signing variables as well when signing releases.

Publication and Marketplace review are separate from building this repository.

## Contribute

Report color issues at the [issue tracker](https://github.com/2chevskii/intellij-theme-jellybeans/issues)
with the IDE version, UI mode, language, and a screenshot. Edit the UI palette in
`src/main/resources/themes/jellybeans.theme.json` and editor highlighting in
`src/main/resources/themes/jellybeans.xml`, then run validation.

## License

[MIT](LICENSE). Original copyright © 2021 aurdevv is preserved in the repository and packaged JAR.
