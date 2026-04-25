#!/usr/bin/env bash
# Deploy course/ as a static site to Cloudflare Pages.
#
# Usage:
#   scripts/deploy-cloudflare.sh [project-name]
#   CF_PAGES_PROJECT=foo CF_PAGES_BRANCH=main scripts/deploy-cloudflare.sh
#
# First-time setup:
#   npx wrangler@latest login
#
# Custom domain:
#   Cloudflare dashboard → Pages → <project> → Custom domains → Add.

set -euo pipefail

PROJECT_NAME="${1:-${CF_PAGES_PROJECT:-course-builder}}"
BRANCH="${CF_PAGES_BRANCH:-main}"

ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
COURSE_DIR="${ROOT}/course"
BUNDLE="${COURSE_DIR}/build/bundle.zip"
BUNDLE_STASH="${ROOT}/.deploy-stash-bundle.zip"

if [[ ! -f "${COURSE_DIR}/index.html" ]] || [[ ! -f "${COURSE_DIR}/manifest.json" ]]; then
  echo "course/ does not look like a built course (missing index.html or manifest.json)." >&2
  echo "Run the course-builder pipeline first." >&2
  exit 1
fi

echo "Deploying ${COURSE_DIR}"
echo "  project : ${PROJECT_NAME}"
echo "  branch  : ${BRANCH}"
echo "  size    : $(du -sh "${COURSE_DIR}" | cut -f1)"

restore_bundle() {
  if [[ -f "${BUNDLE_STASH}" ]]; then
    mv "${BUNDLE_STASH}" "${BUNDLE}"
  fi
}
trap restore_bundle EXIT

if [[ -f "${BUNDLE}" ]]; then
  mv "${BUNDLE}" "${BUNDLE_STASH}"
fi

npx --yes wrangler@latest pages deploy "${COURSE_DIR}" \
  --project-name="${PROJECT_NAME}" \
  --branch="${BRANCH}"
