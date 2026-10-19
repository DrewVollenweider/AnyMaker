# Google Drive archives

Updated 2026-09-29. This synchronizes editor projects without changing native-export compatibility conclusions.

## Workflow

1. Choose Archives on the left, name it, Save current vehicle.
2. Overwrite updates that local archive from current project, preserving name/ID/cloud identity and updating timestamp after confirmation.
3. The row's upload-cloud icon synchronizes that saved archive. First use opens Google account/authorization. After edits, overwrite/save a new archive before uploading.
4. Find/create root `anymaker-builder-vehicles`, storing `name.anymaker.json`. Stable archive identity updates the same cloud file; confirm before overwriting.
5. Sync from Google Drive paginates names/update times/sizes; full bytes are requested only on Download to local archives.
6. Validated download enters local manual archives, available for loading/subgrid import, without replacing current project. Repeated download confirms local-copy overwrite.
7. Disconnect Google clears page authorization, attempts revocation, clears cloud list without deleting archives. Refresh requires login again; disconnect/refresh allows account switching.

Buttons trigger synchronization; no scheduled uploads or automatic multidevice merge. Confirmed overwrite replaces the entire file without atomic multidevice conflict resolution. After interruption, retry searches stable identity again; duplicate identities cause explicit errors, never arbitrary overwrite selection.

## One-time Google configuration

No actual OAuth Client ID or secret is committed. Maintainers must:

1. Enable Google Drive API in a Google Cloud project.
2. Configure Auth Platform branding/audience/data access, test users or publication as appropriate.
3. Create a Web application OAuth client.
4. Register exact Authorized JavaScript origins (scheme/domain/necessary port, no path), e.g. `https://username.github.io`, not `https://username.github.io/anymaker-builder/`.
5. For local debugging register supported `http://localhost` plus actual port, e.g. `http://localhost:5173`. Mock tests at 127.0.0.1 do not prove real OAuth configuration there.
6. Request/register `https://www.googleapis.com/auth/drive.file`. Browser token mode needs no backend/client secret. Never place secrets/access/refresh tokens in source/templates/page settings.
7. Configure Client ID either by copying `.env.example` to local `.env.local`, setting public `VITE_GOOGLE_CLIENT_ID`, rebuilding (recommended; users then click login directly and site config overrides old browser settings), or, without site config, saving a Web OAuth ID in Google login settings, persisted per browser/site path.

Google login cannot discover this app's Client ID: GIS requires precreated `client_id`; authorization returns an access token only.

Self-hosted CSP must permit GIS script/login frames/popups/API connections. If setting Cross-Origin-Opener-Policy, follow official GIS popup compatibility guidance. First authorization must follow a user click. Configured sites preload SDK without blocking editor startup.

`drive.file` permits app-created/approved files, not all Drive. Same account/OAuth app can synchronize across devices; a different app does not automatically access old private files. An existing unapproved same-name folder may lead to a separate app-owned folder. Lists include only app-marked archive JSON, never unrelated-file downloads.

## Data and validation

Outer format `anymaker-builder-archive` v1 stores `id/name/savedAt/document`; inner `anymaker-web-project` schema is unchanged.

- `src/editor/google-drive-auth.js`: user-triggered tokens, expiration/denial/closed popup; tokens memory-only.
- `src/editor/google-drive.js`: Drive v3 queries/folders/pagination, metadata versus lazy bytes, resumable upload, HTTP categories.
- `src/editor/drive-archive-format.js`: outer/bounded-stream validation, reject dangerous JSON keys, invoke project migration/validation.
- `src/editor/google-drive-ui.js`: config/login/list/upload/download; localization `src/locales/google-drive-en.js`.
- `src/editor/archive-store.js`: atomic IndexedDB cloud identity prevents autosave during upload causing later duplicates.

Limits: **16 MiB actual UTF-8** per project, including streamed reads; 1 MiB per metadata response; 2000 list entries; reject repeated page tokens/incomplete search. Downloads require cloud markers, matching outer ID, project validation; failures do not write IndexedDB. Render names with textContent.

Upload session URIs require fixed Google HTTPS origin/Drive paths, with redirects disabled to avoid sending Authorization elsewhere. API timeout 60 seconds. A 401 clears login; user click reauthenticates. No background popups/endless retry.

Autosave has fixed local ID but first sync assigns device-specific cloud ID. Downloaded copies retain source cloud ID and update source on later upload. Local deletion is local-only. Upload is not game-load acceptance.

## Validation and limits

Actual 2026-09-28: 242 unit tests, 98 editor cases, four Drive browser cases passed. Four Drive cases reran after UI changes, screenshot inspected. Build passed with >500 kB warning.

2026-09-29 compact UI: 242 unit, four Drive, three affected editor cases/build passed. At 240px, archive/subgrid controls remain one line with untruncated labels. Full editor run had three failures from omitted subgrid heading/summary; fixed and reran those three, not all 98.

- `npm test` includes `tests/google-drive.test.js`: scopes, expiry/late callbacks, config allowlist, validation/bytes, pagination/folders, repeat updates, session URLs/errors.
- `npm run test:browser:drive`: real page/IndexedDB with mocked GIS/HTTP; buttons/gestures, upload/update, lazy download, corrupt archive isolation, disconnect/login, localization/preferences, concurrent identity saves.
- Editor: `npm run test:browser:editor`; routine: `npm run check`.
- **Unverified**: real OAuth project/account upload/download, deployed origin/CSP/popup policy. Requires real Web Client ID and user login; mocks do not replace service acceptance.

## Official references

Read on 2026-09-28 (historical research, not a new current-service check):

- [GIS token model](https://developers.google.com/identity/oauth2/web/guides/use-token-model): click-triggered short-lived tokens, REST/CORS, reauthorization on expiry.
- [GIS JavaScript reference](https://developers.google.com/identity/oauth2/web/reference/js-reference): initTokenClient, requestAccessToken, scope/error_callback/revoke.
- [Client IDs](https://developers.google.com/identity/oauth2/web/guides/get-google-api-clientid): web clients/authorized origins.
- [Drive scopes](https://developers.google.com/workspace/drive/api/guides/api-specific-auth): drive.file access.
- [Uploads](https://developers.google.com/workspace/drive/api/guides/manage-uploads): resumable initialization/Location/PUT/PATCH.
- [Folders](https://developers.google.com/workspace/drive/api/guides/folder): MIME/root/parents.
- [Search](https://developers.google.com/workspace/drive/api/guides/search-files): q/appProperties/nextPageToken.
- [Custom properties](https://developers.google.com/workspace/drive/api/guides/properties): combined key/value ≤124 bytes; archiveId limited to 115 ASCII characters.
