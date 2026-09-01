#!/usr/bin/env bash
#
# Dataify Skills - Batch Publish to ClawHub
#
# Usage:
#   bash publish.sh                          # Publish all skills
#   bash publish.sh --version 1.1.0          # Specify version
#   bash publish.sh --dry-run                # Preview without uploading
#   bash publish.sh --filter "amazon"        # Only publish matching skills
#

set -euo pipefail

# ── Colors ──
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m'

ok()    { echo -e "${GREEN}[OK]${NC} $1"; }
fail()  { echo -e "${RED}[FAIL]${NC} $1"; }
info()  { echo -e "${BLUE}[INFO]${NC} $1"; }
warn()  { echo -e "${YELLOW}[WARN]${NC} $1"; }

# ── Parse arguments ──
VERSION=""
CHANGELOG=""
DRY_RUN=""
FILTER=""
EXCLUDE=""

while [[ $# -gt 0 ]]; do
    case $1 in
        --version)   VERSION="$2"; shift 2 ;;
        --changelog) CHANGELOG="$2"; shift 2 ;;
        --dry-run)   DRY_RUN="--dry-run"; shift ;;
        --filter)    FILTER="$2"; shift 2 ;;
        --exclude)   EXCLUDE="$2"; shift 2 ;;
        --help)
            echo "Usage: bash publish.sh [OPTIONS]"
            echo ""
            echo "Options:"
            echo "  --version VERSION      Version to publish (e.g., 1.1.0)"
            echo "  --changelog TEXT       Changelog message"
            echo "  --dry-run              Preview publish plan without uploading"
            echo "  --filter PATTERN       Only publish skills matching pattern"
            echo "  --exclude PATTERN      Skip skills matching pattern"
            echo "  --help                 Show this help"
            echo ""
            echo "Examples:"
            echo "  bash publish.sh --version 1.1.0 --changelog 'Update docs'"
            echo "  bash publish.sh --dry-run"
            echo "  bash publish.sh --filter amazon --version 1.1.0"
            exit 0
            ;;
        *) warn "Unknown option: $1"; shift ;;
    esac
done

# ── Pre-flight checks ──
if ! command -v clawhub &>/dev/null; then
    fail "clawhub CLI not installed. Run: npm i -g clawhub"
    exit 1
fi

clawhub whoami &>/dev/null || { fail "Not logged in. Run: clawhub login"; exit 1; }

# ── Prompt for version if not provided ──
if [ -z "$VERSION" ]; then
    read -rp "Enter version to publish (e.g., 1.1.0): " VERSION
    if [ -z "$VERSION" ]; then
        fail "Version is required"
        exit 1
    fi
fi

if [ -z "$CHANGELOG" ]; then
    read -rp "Enter changelog (or press Enter to skip): " CHANGELOG
fi

# ── Slug mapping ──
# ClawHub slugs use "dataify-" prefix, local dirs use "scraper-"/"serp-" prefix
get_slug() {
    local dir_name="$1"
    case "$dir_name" in
        dataify-*)             echo "$dir_name" ;;
        serp-*)                echo "dataify-${dir_name#serp-}" ;;
        scraper-*)             echo "dataify-${dir_name#scraper-}" ;;
        *)                     echo "dataify-${dir_name}" ;;
    esac
}

# ── Banner ──
echo ""
echo -e "${BLUE}╔══════════════════════════════════════════╗${NC}"
echo -e "${BLUE}║    Dataify Skills → ClawHub Publisher     ║${NC}"
echo -e "${BLUE}╚══════════════════════════════════════════╝${NC}"
echo ""
info "Version:   ${VERSION}"
info "Changelog: ${CHANGELOG:-"(none)"}"
[ -n "$DRY_RUN" ] && warn "DRY RUN mode — no actual uploads"
[ -n "$FILTER" ] && info "Filter:    *${FILTER}*"
[ -n "$EXCLUDE" ] && info "Exclude:   *${EXCLUDE}*"
echo ""

# ── Publish loop ──
SKILLS_DIR="$(cd "$(dirname "$0")" && pwd)/skills"

# ClawHub reads ignore files from each published skill directory, not from the
# repository root. Fail closed if local Python caches could leak into a package.
if find "$SKILLS_DIR" -type f \( -name '*.pyc' -o -name '*.pyo' \) -print -quit | grep -q . || \
   find "$SKILLS_DIR" -type d -name '__pycache__' -print -quit | grep -q .; then
    fail "Python cache files found under skills/. Remove __pycache__ directories before publishing."
    exit 1
fi

TOTAL=0
SUCCESS=0
SKIPPED=0
FAILED=0

for skill_dir in "$SKILLS_DIR"/*/; do
    [ ! -f "${skill_dir}SKILL.md" ] && continue

    dir_name=$(basename "$skill_dir")

    # Apply filter
    if [ -n "$FILTER" ] && [[ "$dir_name" != *"$FILTER"* ]]; then
        continue
    fi
    if [ -n "$EXCLUDE" ] && [[ "$dir_name" == *"$EXCLUDE"* ]]; then
        continue
    fi

    TOTAL=$((TOTAL + 1))
    slug=$(get_slug "$dir_name")

    # Extract name from SKILL.md frontmatter
    name=$(grep '^name:' "${skill_dir}SKILL.md" 2>/dev/null | head -1 | sed 's/^name: *//')
    if [ -z "$name" ]; then
        name="$slug"
    fi

    # Execute
    echo -e "${BLUE}[$TOTAL]${NC} ${dir_name} → ${slug}"

    if [ -n "$DRY_RUN" ]; then
        echo "  clawhub skill publish <skill-dir> --slug $slug --name $name --version $VERSION"
        SUCCESS=$((SUCCESS + 1))
    else
        publish_args=(skill publish "$skill_dir" --slug "$slug" --name "$name" --version "$VERSION")
        [ -n "$CHANGELOG" ] && publish_args+=(--changelog "$CHANGELOG")
    fi

    if [ -z "$DRY_RUN" ] && output=$(clawhub "${publish_args[@]}" 2>&1); then
        echo "$output" | tail -1
        SUCCESS=$((SUCCESS + 1))
    elif [ -z "$DRY_RUN" ]; then
        echo "$output" >&2
        FAILED=$((FAILED + 1))
        fail "  Failed: $slug"
    fi
done

# ── Summary ──
echo ""
echo -e "${GREEN}╔══════════════════════════════════════════╗${NC}"
echo -e "${GREEN}║           Publish Complete                ║${NC}"
echo -e "${GREEN}╚══════════════════════════════════════════╝${NC}"
echo ""
echo -e "  Total:     ${BLUE}${TOTAL}${NC}"
echo -e "  Success:   ${GREEN}${SUCCESS}${NC}"
echo -e "  Failed:    ${RED}${FAILED}${NC}"
echo -e "  Version:   ${BLUE}${VERSION}${NC}"
echo ""

[ "$FAILED" -eq 0 ]
