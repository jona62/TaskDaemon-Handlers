# Publishing the SDKs

The coordinated package version is `0.1.2`. Package preparation and registry publication are separate steps: a successful local build or GitHub source release does not mean a package is available from a language registry.

The [source release](https://github.com/jona62/TaskDaemon-Handlers/releases/tag/v0.1.2) contains the tested distribution artifacts and checksums. Go `v0.1.2` is published and verified through the public module proxy. The Python update and first npm, crates.io, NuGet, and Maven Central uploads still require registry access; PyPI `taskdaemon` 0.1.0 remains available.

| Language | Registry coordinate | Publication route |
| --- | --- | --- |
| Python | PyPI `taskdaemon` | Update the existing project owned by `jonathanmshelia` |
| Node.js | npm `@taskdaemon/handler` | First publication requires ownership of the `@taskdaemon` scope |
| Rust | crates.io `taskdaemon-handler` | First publication requires a verified registry account |
| C# | NuGet `TaskDaemon.Handler` | A trusted-publisher policy or a key permitting new packages |
| Java | Maven Central `io.github.jona62:handler` | Verified GitHub namespace, Portal token, and signing key |
| Go | `github.com/jona62/TaskDaemon-Handlers/go` | Push the matching `go/v0.1.2` module tag |
| C++ | Curated vcpkg `jona62-taskdaemon-handlers` | Upstream review required; local overlay `taskdaemon-handler` is already installable |

## Verify and release the source

The [SDK checks workflow](.github/workflows/sdk-checks.yml) builds and tests all seven languages. It tests installed Python, npm, NuGet, and C++ packages and exports distribution artifacts. Rust verifies its archive with `cargo package`; Java produces binary, source, and Javadoc jars. Maven signing and Portal validation happen during publication.

After checks pass, create the immutable `v0.1.2` and `go/v0.1.2` tags at the verified commit. The publishing workflow rejects branches, mismatched tags, and inconsistent package versions.

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

For Maven Central, sign in to the Portal with the GitHub account `jona62` and verify the `io.github.jona62` namespace. `CENTRAL_USERNAME` and `CENTRAL_PASSWORD` are the Portal-generated publishing token pair. `MAVEN_GPG_KEY` is an exported armored private signing key; its public key must be discoverable by Central. Set `MAVEN_GPG_PASSPHRASE` if the key is protected and `MAVEN_GPG_KEY_FINGERPRINT` when selecting a key from a multi-key export. The Maven GPG plugin uses its BC signer, so the workflow does not need a GPG executable or a persistent keyring. The checked-in [Central settings file](java/central-settings.xml) contains environment references only.

## Publish a selected registry

Once that registry's prerequisites are configured, select the release tag in the [Publish packages workflow](https://github.com/jona62/TaskDaemon-Handlers/actions/workflows/publish-packages.yml). Choose one registry or `all` and version `0.1.2`.

```bash
gh workflow run publish-packages.yml \
  --repo jona62/TaskDaemon-Handlers --ref v0.1.2 \
  -f registry=python -f version=0.1.2
```

Each job rebuilds and verifies its package before uploading. Missing account setup fails the job; it does not queue a later upload. Successful uploads are permanent versioned releases. If an upload times out, check the registry before retrying, because the registry may already have accepted it. The workflow does not suppress duplicate-version errors.

Check the exact released version from the registry, then install it in a fresh consumer. Update SDK and daemon documentation to advertise a registry installation only after this succeeds.

## Go and C++

The Go module needs no separate registry credentials. Verify the `go/v0.1.2` tag through the public module proxy and compile a consumer using the pinned version.

For C++, follow the [vcpkg release preparation](cpp/packaging/README.md). The local overlay works immediately, but a curated-registry listing requires an immutable source archive, checksum, tested port, version database entry, and acceptance of an upstream pull request. Keep the publication status explicit until that review completes.

The tested `jona62-taskdaemon-handlers` 0.1.2 port is [submitted for upstream review](https://github.com/microsoft/vcpkg/pull/54303). It is available from the curated registry after acceptance.

Microsoft's [CLA bot request](https://github.com/microsoft/vcpkg/pull/54303#issuecomment-5991376135) requires the contributor to read the agreement and provide the applicable ownership or employer declaration themselves.

Official registry instructions: [PyPI trusted publishing](https://docs.pypi.org/trusted-publishers/adding-a-publisher/), [npm trusted publishing](https://docs.npmjs.com/trusted-publishers/), [crates.io publishing](https://doc.rust-lang.org/cargo/reference/publishing.html), [NuGet trusted publishing](https://learn.microsoft.com/en-us/nuget/nuget-org/trusted-publishing), [Maven Central namespace registration](https://central.sonatype.org/register/namespace/), [vcpkg port contribution](https://learn.microsoft.com/en-us/vcpkg/contributing/maintainer-guide).
