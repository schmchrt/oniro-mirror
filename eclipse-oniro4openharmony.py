#!/usr/bin/env python3

import os
import re
import sys
import xml.etree.ElementTree as ET
from common import *


def groups_for_repo(repo, extra=[]):
    groups = set(extra)

    return sorted(groups)


# Clone (or update) the repositories
oniro_manifest = clone_git_repo(
    url="https://github.com/eclipse-oniro4openharmony/manifest.git",
    path="oniro_manifest",
)

# For oniro-original projects we cover all repositories referenced by release branches or master
oniro_refs = [
    ref.name
    for ref in oniro_manifest.remote().refs
    if re.match(r"origin/OpenHarmony-.*-Release", ref.name)
] + ["origin/master"]

# Look for repo names in each ref
oniro_repos = parse_manifest_refs(
    manifest=oniro_manifest,
    refs=oniro_refs,
    restrict_remote="oniro4openharmony",
    restrict_remote_noisy=False,
)

# Always add the manifest so one can sync from this mirror
oniro_repos.add(RepoEntry("manifest"))

# Generate groups for all repositories
for repo in oniro_repos:
    repo.groups.update(groups_for_repo(repo))

write_manifest(
    filename="eclipse-oniro4openharmony.xml",
    repos=oniro_repos,
    remote_name="oniro4openharmony",
    remote_fetch="https://github.com/eclipse-oniro4openharmony/",
)
