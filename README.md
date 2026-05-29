# oniro-mirror

A collection of scripts and XML files for mirroring OpenHarmony, Oniro, and related repositories.

## Configurations

The following configurations are available:

| Manifest                            | Source URL                                      | Additional Compatible URLs                  | Description                                               |
|:-----------------------------------:|:-----------------------------------------------:|:-------------------------------------------:|:---------------------------------------------------------:|
| `eclipse-oniro-mirrors-gitcode.xml` | `https://gitcode.com/openharmony/`              | `https://github.com/eclipse-oniro-mirrors/` | Selective mirror of upstream OpenHarmony repositories.    |
| `eclipse-oniro4openharmony.xml`     | `https://github.com/eclipse-oniro4openharmony/` |                                             | Selective mirror of Oniro repositories.                   |

## Initialization

To initialize a mirror locally, use the following invocation of `repo init` with one of the manifest names from the table above.

```
repo init -u https://github.com/schmchrt/oniro-mirror -m <manifest> --mirror
```

As an example, initializing a mirror with the `eclipse-oniro-mirrors-gitcode` configuration would look like the following:

```
repo init -u https://github.com/schmchrt/oniro-mirror -m eclipse-oniro-mirrors-gitcode.xml --mirror
```

Be aware that `repo init --mirror` follows the usual initialization semantics, the current working directory will be the base directory.
Make sure to have created and moved into a new directory beforehand.

## Usage

Mirrors can be used either as a reference for local copying of objects (while still fetching the most current objects from the remote) or as the primary remote.

In the following examples it is assumed that a mirror has already been established at `/path/to/mirror/of/eclipse-oniro-mirrors` and that it is fully synchronized.

### Mirror as reference

With an existing mirror the `--reference` option can be used during `repo init` of a normal worktree to register the reference.

```
repo init -u https://github.com/eclipse-oniro4openharmony/manifest.git -b OpenHarmony-6.1-Release -m oniro.xml --no-repo-verify --reference=/path/to/mirror/of/eclipse-oniro-mirrors
```

Internally, this will cause every repository that is being fetched to look up the matching path in the referenced mirror first.
If the path exists, it will be registered as an alternate source of Git objects using `.git/objects/info/alternates` and objects will be referenced from there instead of being fetched over network.
Do note that the referenced objects are not copied or hard-linked into the worktree, so moving or deleting the mirror directory will break any worktrees that depend on the reference.

### Mirror as primary remote

With a fully synchronized mirror it is also possible to use it as a primary remote for cloning a new worktree.
This will create a fully independent (no-reference) worktree and the mirror is used to fetch and update projects going forward.

#### Projects with a relative `fetch` path

If a project is using a relative `fetch` path for its remote (i.e. the repository URLs are determined in relation to the path of the manifest repository) then it is sufficient to provide a mirror path as the manifest URL.

```
repo init -u /path/to/mirror/of/eclipse-oniro-mirrors/manifest.git -b master -m default.xml --no-repo-verify
```

**Note:** As `eclipse-oniro-mirrors` is a mirror of upstream OpenHarmony repositories, this command would create a worktree for upstream OpenHarmony, not Oniro.

**Note:** As neither OpenHarmony nor Oniro make use of relative `fetch` paths, this will not take full advantage of the mirror without also using the following approach.

#### Projects without a relative `fetch` path

If a project does not utilize relative `fetch` paths (Oniro and OpenHarmony included), then it is necessary to register the replacement repositories in the Git configuration.
This will automatically redirect a repository access that matches a certain URL prefix to a different URL prefix using the `insteadOf` configuration system.

To enable this behavior, the following pattern should be appended to your users `.gitconfig`:

```
[url "/path/to/mirror/of/eclipse-oniro-mirrors"]
    insteadOf = https://github.com/eclipse-oniro-mirrors
    insteadOf = https://gitcode.com/openharmony
```

As shown above, this configuration can also cover additional compatible URLs that point to equivalent repositories to replace both.

**Note:** The replacement will happen as long as the section in the configuration is present and not commented-out.
The replacement will happen while pulling and pushing, it will happen when trying to use `repo sync` when updating the mirror itself, and it will also happen if the local mirror does not have a certain repository.
Notably, it also does not have a fallback if the local mirror does not have a certain repository, for example in the event of an incomplete mirror manifest.
