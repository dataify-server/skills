#!/usr/bin/env bash
#
# Dataify Skills - Quick Installer
#
# Usage:
#   curl -fsSL https://raw.githubusercontent.com/nicejingwen/dataify_skills/main/install.sh | bash
#   or
#   bash install.sh
#

set -e

# ── Config ──
REPO_URL="https://github.com/dataify-server/skills.git"
INSTALL_DIR="${DATAIFY_SKILLS_DIR:-$HOME/.dataify/skills}"
DASHBOARD_URL="https://dashboard.dataify.com?utm_source=installer"

# ── Colors ──
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

info()  { echo -e "${BLUE}[INFO]${NC} $1"; }
ok()    { echo -e "${GREEN}[OK]${NC} $1"; }
warn()  { echo -e "${YELLOW}[WARN]${NC} $1"; }
error() { echo -e "${RED}[ERROR]${NC} $1"; exit 1; }

# ── Banner ──
echo ""
echo -e "${BLUE}╔══════════════════════════════════════╗${NC}"
echo -e "${BLUE}║       Dataify Skills Installer       ║${NC}"
echo -e "${BLUE}║      AI Agent Skills for Data        ║${NC}"
echo -e "${BLUE}╚══════════════════════════════════════╝${NC}"
echo ""

# ── Check prerequisites ──
info "Checking prerequisites..."

if ! command -v git &>/dev/null; then
    error "git is not installed. Please install git first."
fi

if ! command -v python3 &>/dev/null; then
    error "python3 is not installed. Please install Python 3.8+ first."
fi

PYTHON_VERSION=$(python3 -c "import sys; print(f'{sys.version_info.major}.{sys.version_info.minor}')")
ok "git found"
ok "python3 found (v${PYTHON_VERSION})"

# ── Clone or update ──
if [ -d "$INSTALL_DIR/.git" ]; then
    info "Existing installation found at $INSTALL_DIR"
    info "Updating to latest version..."
    cd "$INSTALL_DIR"
    if git pull --ff-only origin main 2>/dev/null || git pull --ff-only 2>/dev/null; then
        ok "Updated successfully"
    else
        warn "Could not auto-update. Continuing with existing version."
    fi
else
    info "Installing to $INSTALL_DIR ..."
    mkdir -p "$(dirname "$INSTALL_DIR")"
    git clone "$REPO_URL" "$INSTALL_DIR" 2>/dev/null || error "Failed to clone repository. Check your network connection."
    ok "Cloned successfully"
fi

# ── Count skills ──
SKILL_COUNT=$(find "$INSTALL_DIR" -name "SKILL.md" -not -path "*/.git/*" 2>/dev/null | wc -l | tr -d ' ')
ok "Installed ${SKILL_COUNT} skills"

# ── Setup DATAIFY_API_TOKEN ──
echo ""
if [ -z "$DATAIFY_API_TOKEN" ]; then
    warn "DATAIFY_API_TOKEN is not set."
    echo ""
    echo -e "  To use Dataify skills, you need an API token."
    echo -e "  Get one at: ${BLUE}${DASHBOARD_URL}${NC}"
    echo ""

    read -rp "Enter your API token (or press Enter to skip): " TOKEN_INPUT

    if [ -n "$TOKEN_INPUT" ]; then
        # Detect shell
        SHELL_NAME=$(basename "$SHELL")
        case "$SHELL_NAME" in
            zsh)
                RC_FILE="$HOME/.zshrc"
                ;;
            bash)
                RC_FILE="$HOME/.bashrc"
                ;;
            *)
                RC_FILE="$HOME/.profile"
                ;;
        esac

        # Check if already in RC file
        if grep -q "DATAIFY_API_TOKEN" "$RC_FILE" 2>/dev/null; then
            # Replace existing line
            sed -i.bak "s|^export DATAIFY_API_TOKEN=.*|export DATAIFY_API_TOKEN=\"${TOKEN_INPUT}\"|" "$RC_FILE"
            rm -f "${RC_FILE}.bak"
        else
            echo "" >> "$RC_FILE"
            echo "# Dataify API Token" >> "$RC_FILE"
            echo "export DATAIFY_API_TOKEN=\"${TOKEN_INPUT}\"" >> "$RC_FILE"
        fi

        # Also export for current session
        export DATAIFY_API_TOKEN="$TOKEN_INPUT"
        ok "Token saved to $RC_FILE"
        info "Run 'source $RC_FILE' or open a new terminal to activate."
    else
        info "Skipped. You can set it later:"
        echo -e "  export DATAIFY_API_TOKEN=\"your_token_here\""
    fi
else
    ok "DATAIFY_API_TOKEN is already set"
fi

# ── Add DATAIFY_SKILLS_DIR to environment ──
SHELL_NAME=$(basename "$SHELL")
case "$SHELL_NAME" in
    zsh)  RC_FILE="$HOME/.zshrc" ;;
    bash) RC_FILE="$HOME/.bashrc" ;;
    *)    RC_FILE="$HOME/.profile" ;;
esac

if ! grep -q "DATAIFY_SKILLS_DIR" "$RC_FILE" 2>/dev/null; then
    echo "" >> "$RC_FILE"
    echo "# Dataify Skills directory" >> "$RC_FILE"
    echo "export DATAIFY_SKILLS_DIR=\"${INSTALL_DIR}\"" >> "$RC_FILE"
fi

# ── Done ──
echo ""
echo -e "${GREEN}╔══════════════════════════════════════╗${NC}"
echo -e "${GREEN}║     Installation complete!           ║${NC}"
echo -e "${GREEN}╚══════════════════════════════════════╝${NC}"
echo ""
echo -e "  Skills directory: ${BLUE}${INSTALL_DIR}${NC}"
echo -e "  Total skills:     ${BLUE}${SKILL_COUNT}${NC}"
echo ""
echo -e "  ${YELLOW}Quick start:${NC}"
echo ""
echo -e "  # List all skill categories"
echo -e "  ls \$DATAIFY_SKILLS_DIR"
echo ""
echo -e "  # Run a Google Search"
echo -e "  python3 \$DATAIFY_SKILLS_DIR/skills/serp-google-search/scripts/google_search.py \\"
echo -e "    --params-json '{\"q\":\"AI news\"}'"
echo ""
echo -e "  # Unlock a web page"
echo -e "  python3 \$DATAIFY_SKILLS_DIR/skills/dataify-web-unlocker/scripts/invoke-dataify-web-unlocker.py \\"
echo -e "    --url \"https://example.com\""
echo ""
echo -e "  Dashboard: ${BLUE}${DASHBOARD_URL}${NC}"
echo ""
