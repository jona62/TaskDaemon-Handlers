# Publishing the SDKs

The coordinated package version is `0.1.2`. Package preparation and registry publication are separate steps: a successful local build or GitHub source release does not mean a package is available from a language registry.

The [source release](https://github.com/jona62/TaskDaemon-Handlers/releases/tag/v0.1.2) contains the tested distribution artifacts and checksums. Go `v0.1.2`, [npm `@taskdaemon/handler` 0.1.2](https://www.npmjs.com/package/@taskdaemon/handler/v/0.1.2), [crates.io `taskdaemon-handler` 0.1.2](https://crates.io/crates/taskdaemon-handler/0.1.2), [Maven Central `io.github.jona62:handler` 0.1.2](https://repo.maven.apache.org/maven2/io/github/jona62/handler/0.1.2/), and [NuGet `TaskDaemon.Handler` 0.1.2](https://www.nuget.org/packages/TaskDaemon.Handler/0.1.2) are published and verified with isolated consumers. The Python update remains pending; PyPI `taskdaemon` 0.1.0 remains available.

The first npm upload requires a token with publishing access and **Bypass two-factor authentication**. crates.io requires a verified account email. Maven Central requires both its publishing token pair and a PGP signing key. Credentials stored in GitHub do not satisfy these separate registry prerequisites by themselves.

| Language | Registry coordinate | Publication route |
| --- | --- | --- |
| Python | PyPI `taskdaemon` | Update the existing project owned by `jonathanmshelia` |
| Node.js | npm `@taskdaemon/handler` | Published and verified at `0.1.2`, with provenance |
| Rust | crates.io `taskdaemon-handler` | Published and verified at `0.1.2` |
| C# | NuGet `TaskDaemon.Handler` | Published and verified at `0.1.2`, owned by `jonathanmshelia` |
| Java | Maven Central `io.github.jona62:handler` | Published and verified at `0.1.2`, with PGP signatures |
| Go | `github.com/jona62/TaskDaemon-Handlers/go` | Push the matching `go/v0.1.2` module tag |
| C++ | Curated vcpkg `jona62-taskdaemon-handlers` | Upstream review required; local overlay `taskdaemon-handler` is already installable |

## Verify and release the source

The [SDK checks workflow](.github/workflows/sdk-checks.yml) builds and tests all seven languages. It tests installed Python, npm, NuGet, and C++ packages and exports distribution artifacts. Rust verifies its archive with `cargo package`; Java produces binary, source, and Javadoc jars. Maven signing and Portal validation happen during publication.

After checks pass, create the immutable `v0.1.2` and `go/v0.1.2` tags at the verified commit. The publishing workflow always checks out the immutable `v<version>` tag and rejects mismatched source commits and inconsistent package versions. Run the workflow from `main` so publishing fixes can apply without changing released SDK source.

## Configure registry access

All GitHub trusted-publisher configurations use:

- Repository owner: `jona62`
- Repository: `TaskDaemon-Handlers`
- Workflow filename: `publish-packages.yml`

Use the environment listed below when the registry asks for it.

| Registry | GitHub environment | Required setup |
| --- | --- | --- |
| PyPI | `pypi` | Register this trusted publisher on the existing `taskdaemon` project; alternatively set `PYPI_API_TOKEN` |
| npm | `npm` | For the first upload, use an authenticated scope owner or set `NPM_TOKEN`; after the package exists, register this trusted publisher and allow direct `npm publish` |
| crates.io | `crates-io` | For the first upload, set `CRATES_IO_TOKEN`; after owning the crate, configure trusted publishing |
| NuGet | `nuget` | Register a policy allowing new packages and versions for `TaskDaemon.Handler`, then set repository variable `NUGET_USER`; alternatively set `NUGET_API_KEY` |
| Maven Central | `maven-central` | Set `CENTRAL_USERNAME`, `CENTRAL_PASSWORD`, and `MAVEN_GPG_KEY`; add the passphrase/fingerprint variables when needed |

Set secrets in [the SDK repository's Actions settings](https://github.com/jona62/TaskDaemon-Handlers/settings/secrets/actions), or use the interactive CLI without putting secret values in a command:

```bash
gh secret set NPM_TOKEN --repo jona62/TaskDaemon-Handlers
gh secret set CRATES_IO_TOKEN --repo jona62/TaskDaemon-Handlers
```

Do not commit credentials or paste them into issue bodies, release notes, or chat. Repository secrets are available to the workflow's environments unless an environment-specific secret overrides them.

## Obtain the first-upload credentials

Create or sign in to each registry account, then save its publishing credentials in [SDK repository Actions secrets](https://github.com/jona62/TaskDaemon-Handlers/settings/secrets/actions) using **New repository secret** and the exact names below. Use a short expiration for bootstrap tokens. Your account login passwords do not need to be stored in GitHub.

### npm: `NPM_TOKEN`

The account must have permission to publish in the `@taskdaemon` scope. Create or join the `taskdaemon` npm organization if you do not already control it. If that scope belongs to someone else, resolve the scope choice before publishing; do not silently rename the package.

On [npm](https://www.npmjs.com), open the profile menu, **Access Tokens**, then **Generate New Token**. Name it `TaskDaemon first publish`. Under **Packages and scopes**, choose **Read and write (publish and stage)** and restrict it to `@taskdaemon`. For the current unattended GitHub workflow, enable **Bypass two-factor authentication** on this restricted temporary token. Give it a short expiration, generate it, and copy it into `NPM_TOKEN`. Organization-management permissions alone do not grant package publishing permission.

After the first upload, configure the existing package's trusted publisher using the owner/repository/workflow/environment above and explicitly allow direct publishing. This removes the need for a stored npm token. Direct publishing with granular tokens is scheduled to end in January 2027, so treat this token as bootstrap access only.

Official instructions: [token creation](https://docs.npmjs.com/creating-and-viewing-access-tokens/), [organization creation](https://docs.npmjs.com/creating-an-organization/), [token publishing changes](https://docs.npmjs.com/about-access-tokens/).

### crates.io: `CRATES_IO_TOKEN`

Sign in to [crates.io](https://crates.io) with GitHub. In [profile settings](https://crates.io/settings/profile), save an email address and verify it using the registry's email. Open [Create API Token](https://crates.io/settings/tokens/new), name it `TaskDaemon GitHub Actions`, and select **Publish new crates** and **Publish new versions of existing crates**. Restrict the crate pattern to `taskdaemon-handler`; it can match the crate before its first publication. Generate the token and copy its one-time value into `CRATES_IO_TOKEN`.

Official instructions: [Cargo publishing](https://doc.rust-lang.org/cargo/reference/publishing.html); [registry token permissions](https://github.com/rust-lang/crates.io/blob/0ea9b2cc5237d037b7e690d26015bc458cf14d28/svelte/src/lib/utils/token-scopes.ts).

### NuGet: `NUGET_API_KEY`, or trusted publishing

Sign in to [NuGet.org](https://www.nuget.org) or create an account. In the username menu, select **API Keys**, then **Create**. Choose **Push new packages and package versions**, restrict the package glob to `TaskDaemon.Handler`, and set an expiration. Create the key, use **Copy**, and paste it into `NUGET_API_KEY`. Permission to push only new versions is insufficient for the first package.

For a token-free alternative, select **Trusted Publishing** in the username menu and add a GitHub policy with owner `jona62`, repository `TaskDaemon-Handlers`, workflow `publish-packages.yml`, environment `nuget`, new-package and new-version scopes, and package glob `TaskDaemon.Handler`. Save the NuGet profile username as the GitHub repository **variable** `NUGET_USER`, rather than as a secret or an email address.

Official instructions: [scoped API keys](https://learn.microsoft.com/en-us/nuget/nuget-org/scoped-api-keys), [trusted publishing](https://learn.microsoft.com/en-us/nuget/nuget-org/trusted-publishing).

### Maven Central: token pair and signing key

Sign in to [Central](https://central.sonatype.com) with the account that owns the publishing token. Confirm that `io.github.jona62` appears as verified in **View Namespaces**. Different sign-in methods create separate Central accounts, even with the same email. GitHub sign-in as `jona62` normally provisions this namespace automatically; contact Central support if it is missing. For an email or Google account, register `io.github.jona62`, create the temporary public repository `jona62/VERIFICATION_KEY` using the assigned key, and complete verification before uploading. Open [User Tokens](https://central.sonatype.com/usertoken), select **Generate User Token**, and enter a display name and expiration. Save its generated username as `CENTRAL_USERNAME` and its generated password as `CENTRAL_PASSWORD`; these are the publishing token pair, not the account's login/password.

The separate signing key is generated locally. With GnuPG installed, create a passphrase-protected RSA signing key and list its fingerprint:

```bash
gpg --quick-generate-key "Jonathan James <YOUR_PUBLIC_EMAIL>" rsa3072 sign 2y
gpg --list-secret-keys --fingerprint
```

Use the name/email you intend to associate publicly with the release. Set the full fingerprint from that output, publish only the public key, and stream the protected private-key export directly into GitHub's secret store:

```bash
TASKDAEMON_SIGNING_FINGERPRINT='YOUR_FULL_FINGERPRINT'
gpg --keyserver hkps://keyserver.ubuntu.com --send-keys "$TASKDAEMON_SIGNING_FINGERPRINT"
gpg --armor --export-secret-keys "$TASKDAEMON_SIGNING_FINGERPRINT" |
  gh secret set MAVEN_GPG_KEY --repo jona62/TaskDaemon-Handlers
gh secret set MAVEN_GPG_PASSPHRASE --repo jona62/TaskDaemon-Handlers
```

The last command prompts for the key passphrase. Keep the original GnuPG key and its revocation certificate backed up; the pipeline does not write a private-key file into the repository. If selecting among multiple exported keys, also set `MAVEN_GPG_KEY_FINGERPRINT` to the full fingerprint. Check that a fresh keyring can retrieve the public key by its long key ID before uploading; keyserver propagation can temporarily prevent Central from validating signatures.

Official instructions: [Portal tokens](https://central.sonatype.org/publish/generate-portal-token/), [namespace registration](https://central.sonatype.org/register/namespace/), [Central signing requirements](https://central.sonatype.org/publish/requirements/gpg/), [GnuPG key generation](https://www.gnupg.org/documentation/manuals/gnupg/OpenPGP-Key-Management.html).

The Maven GPG plugin uses its BC signer, so the workflow does not need a GPG executable or a persistent keyring. The checked-in [Central settings file](java/central-settings.xml) contains environment references only.

## Publish a selected registry

Once that registry's prerequisites are configured, select `main` in the [Publish packages workflow](https://github.com/jona62/TaskDaemon-Handlers/actions/workflows/publish-packages.yml). Choose one registry or `all` and version `0.1.2`. The workflow builds the selected version's immutable release tag rather than the branch's SDK source.

```bash
gh workflow run publish-packages.yml \
  --repo jona62/TaskDaemon-Handlers --ref main \
  -f registry=python -f version=0.1.2
```

Each job rebuilds and verifies its package before uploading. Missing account setup fails the job; it does not queue a later upload. Successful uploads are permanent versioned releases. If an upload times out, check the registry before retrying, because the registry may already have accepted it. The workflow does not suppress duplicate-version errors.

Check the exact released version from the registry, then install it in a fresh consumer. Update SDK and daemon documentation to advertise a registry installation only after this succeeds.

## Go and C++

The Go module needs no separate registry credentials. Verify the `go/v0.1.2` tag through the public module proxy and compile a consumer using the pinned version.

For C++, follow the [vcpkg release preparation](cpp/packaging/README.md). The local overlay works immediately, but a curated-registry listing requires an immutable source archive, checksum, tested port, version database entry, and acceptance of an upstream pull request. Keep the publication status explicit until that review completes.

The tested `jona62-taskdaemon-handlers` 0.1.2 port is [submitted for upstream review](https://github.com/microsoft/vcpkg/pull/54303). It is available from the curated registry after acceptance.

Microsoft's [CLA bot request on the pull request](https://github.com/microsoft/vcpkg/pull/54303) requires the contributor to read the agreement and provide the applicable ownership or employer declaration themselves.

Official registry instructions: [PyPI trusted publishing](https://docs.pypi.org/trusted-publishers/adding-a-publisher/), [npm trusted publishing](https://docs.npmjs.com/trusted-publishers/), [crates.io publishing](https://doc.rust-lang.org/cargo/reference/publishing.html), [NuGet trusted publishing](https://learn.microsoft.com/en-us/nuget/nuget-org/trusted-publishing), [Maven Central namespace registration](https://central.sonatype.org/register/namespace/), [vcpkg port contribution](https://learn.microsoft.com/en-us/vcpkg/contributing/maintainer-guide).
