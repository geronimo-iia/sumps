import os
import sys

from git import Repo
from msgspec import Struct

from sumps.lang import singleton
from sumps.lang.registry import Dictionary


@singleton
class MiniFS:
    root: str
    etc: str
    lib: str
    tmp: str
    datat: str

    def __init__(self, root: str = os.getcwd()):
        self.root = root
        for path in ["etc", "lib", "tmp", "data"]:
            target = os.path.join(root, path)
            setattr(self, path, target)
            os.makedirs(target, exist_ok=True)


class Library(Struct):
    name: str
    package: str
    source: str | None = None


class Libraries(Dictionary[Library]):
    def __init__(self):
        pass


def init_libraries():
    pass


def init_local_storage():
    os.makedirs(os.path.join(os.getcwd(), "etc"))  # configuration files and some system databases.
    os.makedirs(os.path.join(os.getcwd(), "lib"))
    os.makedirs(os.path.join(os.getcwd(), "tmp"))

    sumps_path = os.path.join(os.getcwd(), "lib", "sumps")
    if os.path.exists(sumps_path):
        repo = Repo.init(sumps_path)
        if repo.is_dirty():
            repo.index.checkout(repo.untracked_files)
    else:
        repo = Repo.clone_from("https://github.com/geronimo-iia/sumps.git", sumps_path)

    sys.path.append(os.path.join(sumps_path, "sumps"))


def get_repo():
    return Repo.init(os.getcwd())

    # repo = Repo.clone_from(repo_url, os.getcwd())
    # origin = empty_repo.create_remote("origin", repo.remotes.origin.url)
    # origin.exists()
    # origin.fetch()  # Ensure we actually have data. fetch() returns useful information.


# empty_repo.create_head("master", origin.refs.master)  # Create local branch "master" from remote "master".
# empty_repo.heads.master.set_tracking_branch(origin.refs.master)  # Set local "master" to track remote "master.
# empty_repo.heads.master.checkout()  # Check out local "master" to working tree.
# pr empty_repo.create_head("master", origin.refs.master).set_tracking_branch(origin.refs.master).checkout()
# Push and pull behaves similarly to `git push|pull`.
# origin.pull()
# origin.push()  # Attempt push, ignore errors.
# origin.push().raise_if_error()  # Push and raise error if it fails.


def get_latest_commit_tree(repo):
    return repo.head.commit.tree


def print_files_from_git(root, level=0):
    for entry in root:
        print(f"{'-' * 4 * level}| {entry.path}, {entry.type}")
        if entry.type == "tree":
            print_files_from_git(entry, level + 1)


# $ git add <file>
# see repo.untracked_files repo.is_dirty()  # Check the dirty state.
# add_file = [update_file]  # relative path from git root
# repo.index.add(add_file)  # notice the add function requires a list of paths
# repo.index.commit("Update to file2")

# repo.index.diff(None)  # Compares staging area to working directory.
# for d in diffs:
#    print(d.a_path)
