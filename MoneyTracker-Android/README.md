# My Money Tracker — Android

Private offline money ledger. Records are stored in Android WebView local storage on this phone. No network permissions are requested. Use Export backup before uninstalling or clearing app data.

## Build using GitHub (no Android Studio needed)

1. Create a **private** GitHub repository (e.g. `money-tracker-android`).
2. Upload **the contents of this folder** to the repository root, including `.github/workflows/build-apk.yml` (hidden `.github` folder). You can use GitHub's **Add file → Upload files** or push using git.
3. Open **Actions → Build Android APK → Run workflow**. A push to main may also start it automatically.
4. Wait for the green check. Open the completed run, and download **MoneyTracker-APK** under Artifacts.
5. Extract the downloaded ZIP on your Android phone and tap `app-debug.apk`. Approve **Install unknown apps** for your file manager if Android asks.

The debug APK is signed automatically for installation. Keep this APK for reinstalling. Uninstalling deletes app-local records; export a backup first.
