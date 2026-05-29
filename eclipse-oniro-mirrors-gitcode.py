#!/usr/bin/env python3

import os
import re
import sys
import xml.etree.ElementTree as ET
from common import *


def groups_for_repo(repo, extra=[]):
    groups = set(extra)

    # Not really intended as a group for syncing, but maybe useful for other cronjobs.
    # List of repositories taken from mirror_large_repos.yml.
    if repo.name in [
        "developtools_profiler",
        "developtools_smartperf_host",
        "device_board_hihope",
        "device_soc_rockchip",
        "docs",
        "global_i18n",
        "kernel_linux_5.10",
        "kernel_linux_6.6",
        "multimedia_audio_framework",
        "multimedia_av_codec",
        "third_party_mindspore",
        "third_party_rust_rust",
        "third_party_vk-gl-cts",
        "update_updater",
        "xts_acts",
    ]:
        groups.add("mirror:large")

    return sorted(groups)


# Clone (or update) the repositories
openharmony_manifest = clone_git_repo(
    url="https://gitcode.com/openharmony/manifest.git", path="openharmony_manifest"
)

openharmony_refs = [
    # From mirror-repo-list-generator.sh
    "origin/OpenHarmony-3.2-Release",
    "origin/OpenHarmony-4.0-Release",
    "origin/OpenHarmony-4.1-Release",
    "origin/OpenHarmony-5.0.0-Release",
    "origin/OpenHarmony-5.0.2-Release",
    "origin/OpenHarmony-5.0.3-Release",
    "origin/OpenHarmony-5.1.0-Release",
    # From mirror_gitcode.yml
    "origin/master",
]
# Look for repo names in each ref
openharmony_repos = parse_manifest_refs(
    manifest=openharmony_manifest, refs=openharmony_refs, restrict_remote="gitcode"
)

# Always add the manifest so one can sync from this mirror
openharmony_repos.add(RepoEntry("manifest"))

# Generate groups for all repositories
for repo in openharmony_repos:
    repo.groups.update(groups_for_repo(repo))

write_manifest(
    filename="eclipse-oniro-mirrors-gitcode.xml",
    repos=openharmony_repos,
    remote_name="gitcode",
    remote_fetch="https://gitcode.com/openharmony/",
)
