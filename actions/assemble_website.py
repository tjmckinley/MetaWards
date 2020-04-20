import metawards
import sys
import os
from distutils import dir_util
import glob

branch = metawards.__branch__
release = metawards.__version__
version = metawards.__version__.split("+")[0]

if version.find("untagged") != -1:
    print("This is an untagged branch")
    version = metawards.__manual_version__

print(f"Build docs for branch {branch} version {version}")

# we will only build docs for the master and devel branches
# (as these are moved into special locations)

if branch not in ["master", "devel", "feature_tutorial"]:
    print(f"We don't assemble the website for branch {branch}")
    sys.exit(0)

os.environ["METAWARDS_VERSION"] = version
os.environ["METAWARDS_BRANCH"] = branch
os.environ["METAWARDS_RELEASE"] = release
os.environ["METAWARDS_REPOSITORY"] = metawards.__repository__
os.environ["METAWARDS_REVISIONID"] = metawards.__revisionid__

if not os.path.exists("./gh-pages"):
    print("You have not checked out the gh-pages branch correctly!")
    sys.exit(-1)

# if this is the master branch, then copy the docs to both the root
# directory of the website, and also to the 'versions/version' directory
if branch == "master":
    dir_util.copy_tree("doc/build/html/", "gh-pages/")
    dir_util.copy_tree("doc/build/html/", f"gh-pages/versions/${version}/")

elif branch == "devel":
    dir_util.copy_tree("doc/build/html/", "gh-pages/versions/devel/")

# now write the versions.json file
versions = {}
versions["latest"] = "/"
versions["development"] = "/versions/devel/"

for version in glob.glob("gh-pages/versions/*"):
    print(version)

