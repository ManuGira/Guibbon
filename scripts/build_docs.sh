#!/bin/bash

cd "$(dirname "$0")"
cd ..

source ./.venv/Scripts/activate

# repo must be have no changes
if [[ $(git status --porcelain) ]]; then
  echo "Please stash or commit any local changes before building the docs"
  exit 1
fi

BUILD_DIR=build/docs
BUILD_SITE_DIR=$BUILD_DIR/site

# clean build dir
rm -rf $BUILD_DIR
mkdir -p $BUILD_SITE_DIR

# copy utils script to build dir where it won't be affected by git checkout
cp scripts/build_docs_index.py $BUILD_DIR/build_docs_index.py

# find tags and branches matching version number
git fetch --all --tags --prune
git tag | egrep "v[0-9]+\.[0-9]+\.[0-9]+" > $BUILD_DIR/tag_versions.txt
git branch | egrep "v[0-9]+\.[0-9]+\.[0-9]+-dev" > $BUILD_DIR/dev_versions.txt

# for each tag version, checkout and build doc
cat $BUILD_DIR/tag_versions.txt | while read -r VERSION ; do
  echo "Checkout to tag $VERSION"
  git checkout tags/$VERSION

  echo "Building doc $VERSION"
  BUILD_DST=$BUILD_SITE_DIR/$VERSION
  mkdir -p $BUILD_DST
  mkdocs build --site-dir $BUILD_DST

  echo ""
done

# for each branch version, checkout and build doc
cat $BUILD_DIR/dev_versions.txt | while read -r VERSION ; do
  # remove leading "* " if present
  VERSION="${VERSION//* }"
  echo "Checkout to branch $VERSION"
  git checkout $VERSION

  echo "Building doc $VERSION"
  BUILD_DST=$BUILD_SITE_DIR/$VERSION
  mkdir -p $BUILD_DST
  mkdocs build --site-dir $BUILD_DST

  echo ""
done

# Add a version selector on top of each html page
python $BUILD_DIR/build_docs_index.py $BUILD_DIR/tag_versions.txt $BUILD_DIR/dev_versions.txt $BUILD_SITE_DIR/index.html

