Custom fork of [shotgunsoftware/tk-multi-loader2](https://github.com/shotgunsoftware/tk-multi-loader2). Use by editing
[tk-config-default2:env/includes/app_locations.yml](https://github.com/shotgunsoftware/tk-config-default2/blob/master/env/includes/app_locations.yml)
to:

```yaml
apps.tk-multi-loader2.location:
  type: git
  path: https://github.com/Treehouse-Digital/tk-multi-loader2.git
  version: 1.25.4-th.1.0.0
```

## Developing

This is currently used as a submodule within a bigger git repo, which should have been
cloned down via

```bash
git clone --recurse-submodule ...
```

### Syncing with SG

Then `cd` into this repo and add [shotgunsoftware/tk-multi-loader2](https://github.com/shotgunsoftware/tk-multi-loader2)
as the `upstream` remote, which we'll then use as pull only (one-time setup):

```bash
cd /path/to/tk-multi-loader2
git remote add upstream git@github.com:shotgunsoftware/tk-multi-loader2.git
git remote set-url --push upstream PUSH-NOT-ALLOWED
git remote update
```

Afterwards, merge-and-squash our changes onto latest version tag, suppose new
SG/upstream version tag `v1.2.3` appears, before tagging and pushing both SG's tag,
our updated `master` and our Rez-compatible tag back to our fork (origin)

```bash
git checkout -B master origin/master  # Force sync with our GitHub fork
git merge --squash v1.2.3 && git commit --no-edit
git tag 1.2.3-th.1.0.0  # Rez-compatible version number
git push origin master v1.2.3 1.2.3-th.1.0.0  # Push branch, SG tag and our tag
```

Optionally, then go to https://github.com/Treehouse-Digital/tk-multi-loader2/releases/new and
create a new release with the `1.2.3-th.1.0.0` tag.

### Additional changes

Each change should branch off SG's `v#.#.#` tag as per above. The branch should be
named `th-#.#.#` i.e. `th-0.23.2` when branching off SG `v0.23.2`.

`master` branch should point to the latest tip of `th-#.#.#` where possible.

Any additional changes can then be made and pushed to the `th-#.#.#` branch
(and `master` if latest) and released as using sem-ver version numbering after a
`-th.` segment. Be sure to update the changelog below.
 
## Changelog

These track the only functional differences between SG/upstream and our own fork.

### Added

- `publish_fields` settings for additional entity fields to fetch.


----

[![VFX Platform](https://img.shields.io/badge/vfxplatform-2025%20%7C%202024%20%7C%202023%20%7C%202022-blue.svg)](http://www.vfxplatform.com/)
[![Python](https://img.shields.io/badge/python-3.11%20%7C%203.10%20%7C%203.9-blue.svg)](https://www.python.org/)
[![Build Status](https://dev.azure.com/shotgun-ecosystem/Toolkit/_apis/build/status/Apps/tk-multi-loader2?branchName=master)](https://dev.azure.com/shotgun-ecosystem/Toolkit/_build/latest?definitionId=73&branchName=master)
[![codecov](https://codecov.io/gh/shotgunsoftware/tk-multi-loader2/branch/master/graph/badge.svg)](https://codecov.io/gh/shotgunsoftware/tk-multi-loader2)
[![Code style: black](https://img.shields.io/badge/code%20style-black-000000.svg)](https://github.com/psf/black)
[![Linting](https://img.shields.io/badge/PEP8%20by-Hound%20CI-a873d1.svg)](https://houndci.com)

## Documentation
This repository is a part of the Flow Production Tracking Toolkit.

- For more information about this app and for release notes, *see the wiki section*.
- For general information and documentation, click here: https://help.autodesk.com/view/SGDEV/ENU/?contextId=SA_INTEGRATIONS_USER_GUIDE
- For information about Flow Production Tracking in general, click here: https://www.autodesk.com/products/flow-production-tracking/overview

## Using this app in your Setup
All the apps that are part of our standard app suite are pushed to our App Store.
This is where you typically go if you want to install an app into a project you are
working on. For an overview of all the Apps and Engines in the Toolkit App Store,
click here: https://help.autodesk.com/view/SGDEV/ENU/?contextId=PC_TOOLKIT_APPS

## Have a Question?
Don't hesitate to contact us at https://www.autodesk.com/support
