#!/usr/bin/env python3

import functools
import os
import sys
import xml.etree.ElementTree as ET

try:
    import git
except ImportError:
    sys.exit("Please install the GitPython package via pip3")

__all__ = [
    "clone_git_repo",
    "RepoEntry",
    "parse_manifest_refs",
    "write_manifest",
]

def clone_git_repo(*, url, path):
    if os.path.isdir(path):
        print("Updating {} repository...".format(path))
        repo = git.Repo(path)
        repo.remote("origin").fetch()
    else:
        print("Downloading {} repository...".format(path))
        repo = git.Repo.clone_from(url, path)

    return repo

@functools.total_ordering
class RepoEntry:
    def __init__(self, name, groups=set()):
        self.name = str(name)
        self.groups = set(groups)

    def __hash__(self):
        return hash(self.name)

    def __eq__(self, other):
        return (self.name, self.groups) == (other.name, other.groups)

    def __lt__(self, other):
        return (self.name, self.groups) < (other.name, other.groups)

def parse_manifest_refs(*, manifest, refs, restrict_remote=None, keep_groups=True):
    repos = {}

    for index, ref in enumerate(refs, 1):
        print("\033[K[{}/{}] Parsing `{}`...".format(index, len(refs), ref), end="\r")

        xml_todo = ["default.xml"]

        # Load the XML
        while len(xml_todo) != 0:
            xml_name = xml_todo.pop(0)

            try:
                manifest_contents = manifest.git.show("{}:{}".format(ref, xml_name))
            except git.exc.GitCommandError as e:
                print("Skipping revision '{}' with non-existing {}".format(ref, xml_name))
                continue
    
            manifest_xml = ET.fromstring(manifest_contents)
    
            for child in manifest_xml:
                if child.tag == "include":
                    xml_todo.append(child.attrib["name"])
                    continue

                # Skip all non-project tags
                if child.tag != "project":
                    continue
    
                if restrict_remote is not None:
                    if "remote" in child.attrib and child.attrib["remote"] != restrict_remote:
                        print(
                            "Skipping project '{}' with non-{} remote '{}'".format(
                                child.attrib["name"], restrict_remote, child.attrib["remote"]
                            )
                        )
                        continue
    
                name = child.attrib["name"].rstrip("/")

                if name not in repos:
                    repos[name] = RepoEntry(name)
                if keep_groups and "groups" in child.attrib:
                    repos[name].groups.update(child.attrib["groups"].split(","))


    return set(repos.values())

def write_manifest(*, filename, repos, remote_name, remote_fetch):
    with open(filename, "w") as file:
        file.write('<?xml version="1.0" encoding="UTF-8"?>\n')
        file.write("<manifest>\n")
        file.write("\n")
        file.write('  <remote  name="' + remote_name + '"\n')
        file.write('           fetch="' + remote_fetch + '" />\n')
        file.write('  <default revision="master"\n')
        file.write('           remote="' + remote_name + '"\n')
        file.write('           sync-j="4" />\n')
        file.write("\n")
        
        for repo in sorted(repos):
            line = 'name="' + repo.name + '"'
        
            # Would we get a path conflict?
            if any(s.name.startswith(repo.name + "/") for s in repos):
                line += ' path="' + repo.name + '.git"'
        
            # Add groups
            if len(repo.groups) > 0:
                line += ' groups="' + ",".join(sorted(repo.groups)) + '"'
        
            file.write("  <project " + line + " />\n")
        
        file.write("</manifest>\n")
