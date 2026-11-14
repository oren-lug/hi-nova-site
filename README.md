# hi-nova.com

Nova's public site: the landing page, the privacy policy, an invite-link fallback (404), and `/.well-known/assetlinks.json`, which tells Android that hi-nova.com and the Nova app belong together (invite links open the app; passkeys work).

- Edit `src/` (page bodies and `style.css`), then run `python3 build.py`. It writes `docs/`, which GitHub Pages serves at hi-nova.com.
- The app's signing certificates for `assetlinks.json` are `SIGNING_CERTS` in `build.py`. Add Google Play's app-signing key there once Play Console shows it.
