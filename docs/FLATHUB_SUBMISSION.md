# Flathub Submission Notes

Current status as of 2026-04-29:

- GitHub repository: `MrMiYaGi68/Matrix-Calculator`
- Release asset checked: `v1.0.0 / matrix_calculator-1.0.0.tar.gz`
- Flatpak manifest updated to use `io.qt.PySide.BaseApp`
- Flatpak manifest SHA currently matches the published release tarball
- AppStream metadata validates locally

Validation results:

- `appstreamcli validate --no-net io.github.MrMiYaGi68.MatrixCalculator.metainfo.xml`
  passes
- `flatpak-builder-lint manifest io.github.MrMiYaGi68.MatrixCalculator.json`
  reports:
  - `appid-url-not-reachable`
  - `runtime-update-available-to-org.kde.Platform-6.10` (warning)

Why the linter fails:

- The Flatpak ID `io.github.MrMiYaGi68.MatrixCalculator` maps to
  `https://github.com/mrmiyagi68/matrixcalculator`
- The actual upstream repository is
  `https://github.com/MrMiYaGi68/Matrix-Calculator`
- Because of that mismatch, Flathub's URL reachability check fails

Pragmatic submission path:

1. Submit the app to Flathub with the current ID.
2. Add or request an exception for `appid-url-not-reachable`.
3. Mention that the upstream GitHub repository is
   `MrMiYaGi68/Matrix-Calculator` and the mismatch is caused by the hyphenated
   repository name.

Cleaner future path:

1. Rename the Flatpak ID to a GitHub-mappable form such as
   `io.github.mrmiyagi68.matrix_calculator`
2. Rename the Flatpak metadata files accordingly
3. Rebuild `dist/matrix_calculator-1.0.0.tar.gz`
4. Replace the GitHub release asset
5. Update the manifest SHA to the new tarball checksum

Important:

- Flathub builds from the release tarball, not from the `main` branch alone.
- If metadata filenames or contents change upstream, the release tarball must be
  rebuilt and re-uploaded before the Flathub manifest should be pointed at it.
