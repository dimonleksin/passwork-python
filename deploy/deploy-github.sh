#!/bin/bash

# Exit immediately if a command exits with a non-zero status.
set -e

# --- Paths ---
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
SSH_KEY="${SCRIPT_DIR}/keys/github_id_ed25519"

# --- Configuration ---
GIT_USER_NAME="passwork-devops"
GIT_USER_EMAIL="passwork-devops@users.noreply.github.com"
SOURCE_REPO="git@bitbucket.org:passworkteam/passwork-python-connector.git"
TARGET_REPO="git@github.com:passwork-me/passwork-python.git"
SOURCE_BRANCH="main"
TARGET_BRANCH="main"

chmod 600 "${SSH_KEY}"

# --- Argument Parsing ---
VERSION=""
MESSAGE=""

while getopts "v:m:" opt; do
  case ${opt} in
    v )
      VERSION=$OPTARG
      ;;
    m )
      MESSAGE=$OPTARG
      ;;
    \? )
      echo "Invalid option: -$OPTARG" 1>&2
      exit 1
      ;;
    : )
      echo "Invalid option: -$OPTARG requires an argument" 1>&2
      exit 1
      ;;
  esac
done

if [ -z "${MESSAGE}" ]; then
    echo "Usage: $0 -m <message> [-v <version>]"
    exit 1
fi

# --- Main Script ---
echo "Starting release process..."
echo "Version: ${VERSION}"
echo "Commit message: ${MESSAGE}"

# Create a temporary directory for repository clones
WORK_DIR=$(mktemp -d)
echo "Created temporary working directory: ${WORK_DIR}"

# Clone repositories
echo "Cloning source repository: ${SOURCE_REPO} (branch: ${SOURCE_BRANCH})"
git clone --branch "${SOURCE_BRANCH}" "${SOURCE_REPO}" "${WORK_DIR}/source"

echo "Cloning target repository: ${TARGET_REPO} (branch: ${TARGET_BRANCH})"
git clone --branch "${TARGET_BRANCH}" "${TARGET_REPO}" "${WORK_DIR}/target"

# Sync files from source to target
echo "Syncing files from source to target..."
rsync -av --delete --exclude='.git/' --exclude='.github/' "${WORK_DIR}/source/" "${WORK_DIR}/target/"

# Commit and push to target repository
cd "${WORK_DIR}/target"
echo "Preparing to commit changes to the target repository..."

git config user.name "${GIT_USER_NAME}"
git config user.email "${GIT_USER_EMAIL}"

git add .

if git diff-index --quiet HEAD --; then
    echo "No changes to commit in the target repository."
else
    echo "Creating commit in the target repository..."
    git commit -m "${MESSAGE}"
    echo "Pushing changes to the target repository..."
    GIT_SSH_COMMAND="ssh -i ${SSH_KEY} -o IdentitiesOnly=yes -o StrictHostKeyChecking=accept-new" \
      git push origin "${TARGET_BRANCH}"
fi

# Tag the latest commit in the target repository (optional)
if [ -n "${VERSION}" ]; then
echo "Tagging target repository with version ${VERSION}..."
git tag -a "${VERSION}" -m "${VERSION}"
echo "Pushing tag to the target repository..."
GIT_SSH_COMMAND="ssh -i ${SSH_KEY} -o IdentitiesOnly=yes -o StrictHostKeyChecking=accept-new" \
  git push origin "${VERSION}"
else
echo "No version provided; skipping tag in target repository."
fi


# Cleanup
echo "Cleaning up temporary directory..."
rm -rf "${WORK_DIR}"

echo "Script finished successfully!" 