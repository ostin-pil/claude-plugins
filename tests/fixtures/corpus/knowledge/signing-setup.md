# Code-signing setup for Untype

## Why stable signing

macOS TCC (the permission database behind Accessibility / Input Monitoring / Mic / Speech prompts) keys grants on a bundle's designated requirement, which includes the code-signing identity's SHA1 + subject. Ad-hoc signatures , what `swift build` produces by default, change every build, so TCC sees each rebuild as a different app and drops the previously-granted permissions. Manual testing then needs the Accessibility toggle re-enabled after every recompile, which is an intolerable inner loop.

`bin/build.sh` fixes this by re-signing `Build/Untype.app` with a stable local self-signed identity (`Untype Dev`) after each `swift build`. The identity SHA is stable across rebuilds, so TCC keeps the grants attached.

## One-time setup

1. **Create the certificate.** Open Keychain Access to Certificate Assistant to Create a Certificate. Set:
   - Name: `Untype Dev`
   - Identity Type: `Self Signed Root`
   - Certificate Type: `Code Signing`

   Leave everything else at defaults. The cert lands in the `login` keychain.

2. **Trust the certificate for code signing.** Certificate Assistant does NOT set trust automatically, this is the step that trips people up. In Keychain Access to `login` to Certificates, double-click the new `Untype Dev` entry, expand the **Trust** disclosure, and set **Code Signing** to **Always Trust**. Close the window and enter your login password when prompted.

   Without this step `security find-identity -v -p codesigning` reports zero valid identities (the identity exists but fails trust evaluation with `CSSMERR_TP_NOT_TRUSTED`) and `codesign` refuses to use the cert.

3. **Verify.** Run:

   ```sh
   security find-identity -v -p codesigning
   ```

   You should see exactly one valid `Untype Dev` identity. If you see more than one, you created the cert multiple times, delete the duplicates in Keychain Access so the output is unambiguous.

After that, `./bin/build.sh` builds and signs the bundle and TCC grants survive rebuilds.

## Troubleshooting

`bin/build.sh` distinguishes two failure modes:

- **"not found in login keychain"**, the `Untype Dev` cert doesn't exist at all. Run step 1 above.
- **"exists but is not trusted for Code Signing"**, the cert is present but no trust record. Run step 2 above.

If `codesign` itself fails mid-build (after the gate passes), check `codesign -dv Build/Untype.app` to inspect the current signature; the expected output contains `Authority=Untype Dev` and `Identifier=com.untype.app`.

## Cross-references

- `bin/build.sh`, the script that enforces this setup.
- `CLAUDE.md` to **Build & Run to 1. App Bundle**, short pointer to this doc.
- `knowledge/session-21-followups.md` §1, historical context on why the stable-signing workflow replaced the old `swift build && cp` dance.
