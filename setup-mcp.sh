#!/usr/bin/env bash
#
# Dataify MCP - Quick Setup for AI Agents
#
# Automatically configure Dataify MCP Server for Claude Desktop, Cursor, or Windsurf.
#
# Usage:
#   curl -fsSL https://raw.githubusercontent.com/dataify-server/skills/main/setup-mcp.sh | bash
#   or
#   bash setup-mcp.sh
#   bash setup-mcp.sh --tools "google_serp,amazon,youtube"
#

set -e

# ── Config ──
MCP_BASE_URL="https://mcp.dataify.com/mcp"
DASHBOARD_URL="https://dashboard.dataify.com?utm_source=mcp-setup"
ALL_TOOLS="user_info,web_unlocker,google_serp,yandex_serp,duckduckgo_serp,bing_serp,amazon,youtube,facebook,instagram,reddit,walmart,google,booking,indeed,airbnb,google_play_store,github,tiktok,linkedin,glassdoor,twitter,crunchbase,zillow,ebay"

# ── Colors ──
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
CYAN='\033[0;36m'
BOLD='\033[1m'
NC='\033[0m'

info()  { echo -e "${BLUE}[INFO]${NC} $1"; }
ok()    { echo -e "${GREEN}[OK]${NC} $1"; }
warn()  { echo -e "${YELLOW}[WARN]${NC} $1"; }
error() { echo -e "${RED}[ERROR]${NC} $1"; exit 1; }

# ── Parse arguments ──
TOKEN=""
CLIENT=""
TOOLS=""

while [[ $# -gt 0 ]]; do
    case $1 in
        --client) CLIENT="$2"; shift 2 ;;
        --tools)  TOOLS="$2"; shift 2 ;;
        --help)
            echo "Usage: bash setup-mcp.sh [OPTIONS]"
            echo ""
            echo "Options:"
            echo "  --client CLIENT  Target client: claude, cursor, windsurf (default: auto-detect)"
            echo "  --tools TOOLS    Comma-separated tool list (default: all 25 tools)"
            echo "  --help           Show this help message"
            echo ""
            echo "Examples:"
            echo "  bash setup-mcp.sh"
            echo "  DATAIFY_API_TOKEN=... bash setup-mcp.sh --client claude"
            echo "  bash setup-mcp.sh --tools \"google_serp,amazon,youtube\""
            exit 0
            ;;
        *) warn "Unknown option: $1"; shift ;;
    esac
done

# ── Banner ──
echo ""
echo -e "${BLUE}╔══════════════════════════════════════════╗${NC}"
echo -e "${BLUE}║      Dataify MCP Server Setup            ║${NC}"
echo -e "${BLUE}║  25 Tools · 25+ Platforms · AI Agents    ║${NC}"
echo -e "${BLUE}╚══════════════════════════════════════════╝${NC}"
echo ""

# ── Step 1: Get API Token ──
if [ -z "$TOKEN" ]; then
    # Try environment variable
    if [ -n "$DATAIFY_API_TOKEN" ]; then
        TOKEN="$DATAIFY_API_TOKEN"
        ok "Using token from DATAIFY_API_TOKEN environment variable"
    else
        echo -e "  Get your API token at: ${BLUE}${DASHBOARD_URL}${NC}"
        echo ""
        read -rp "  Enter your Dataify API token: " TOKEN
        echo ""
        if [ -z "$TOKEN" ]; then
            error "API token is required. Get one at ${DASHBOARD_URL}"
        fi
    fi
fi
ok "API token received"

# ── Step 2: Select tools ──
if [ -z "$TOOLS" ]; then
    echo ""
    echo -e "${BOLD}Select tool preset:${NC}"
    echo ""
    echo -e "  ${CYAN}1)${NC} All tools (25 tools - recommended)"
    echo -e "  ${CYAN}2)${NC} Lightweight (web_unlocker + SERP only)"
    echo -e "  ${CYAN}3)${NC} Social Media (facebook, instagram, tiktok, twitter, linkedin, reddit, youtube)"
    echo -e "  ${CYAN}4)${NC} E-Commerce (amazon, ebay, walmart + google_serp)"
    echo -e "  ${CYAN}5)${NC} Research (google_serp, web_unlocker, github, crunchbase, indeed)"
    echo -e "  ${CYAN}6)${NC} Custom (enter your own tool list)"
    echo ""
    read -rp "  Choose [1-6] (default: 1): " PRESET

    case "${PRESET:-1}" in
        1) TOOLS="$ALL_TOOLS" ;;
        2) TOOLS="user_info,web_unlocker,google_serp,bing_serp,yandex_serp,duckduckgo_serp" ;;
        3) TOOLS="user_info,facebook,instagram,tiktok,twitter,linkedin,reddit,youtube" ;;
        4) TOOLS="user_info,amazon,ebay,walmart,google_serp,web_unlocker" ;;
        5) TOOLS="user_info,google_serp,web_unlocker,github,crunchbase,indeed,glassdoor" ;;
        6)
            echo ""
            echo -e "  Available tools:"
            echo -e "  ${CYAN}user_info, web_unlocker, google_serp, bing_serp, yandex_serp, duckduckgo_serp,${NC}"
            echo -e "  ${CYAN}amazon, ebay, walmart, facebook, instagram, tiktok, twitter, linkedin,${NC}"
            echo -e "  ${CYAN}reddit, youtube, google, booking, indeed, airbnb, google_play_store,${NC}"
            echo -e "  ${CYAN}github, glassdoor, crunchbase, zillow${NC}"
            echo ""
            read -rp "  Enter tools (comma-separated): " TOOLS
            if [ -z "$TOOLS" ]; then
                TOOLS="$ALL_TOOLS"
                warn "No tools entered, using all tools"
            fi
            ;;
        *) TOOLS="$ALL_TOOLS" ;;
    esac
fi

TOOL_COUNT=$(echo "$TOOLS" | tr ',' '\n' | wc -l | tr -d ' ')
ok "Selected ${TOOL_COUNT} tools"

# ── Build MCP URL ──
MCP_URL="${MCP_BASE_URL}?token=${TOKEN}&tools=${TOOLS}"

# ── Step 3: Detect or select client ──
detect_clients() {
    local found=()
    # Claude Desktop
    if [ -d "$HOME/Library/Application Support/Claude" ] 2>/dev/null || \
       [ -d "$HOME/.config/claude" ] 2>/dev/null; then
        found+=("claude")
    fi
    # Cursor
    if [ -d "$HOME/Library/Application Support/Cursor" ] 2>/dev/null || \
       [ -d "$HOME/.config/Cursor" ] 2>/dev/null; then
        found+=("cursor")
    fi
    # Windsurf
    if [ -d "$HOME/Library/Application Support/Windsurf" ] 2>/dev/null || \
       [ -d "$HOME/.config/Windsurf" ] 2>/dev/null; then
        found+=("windsurf")
    fi
    echo "${found[@]}"
}

if [ -z "$CLIENT" ]; then
    DETECTED=($(detect_clients))

    if [ ${#DETECTED[@]} -eq 0 ]; then
        echo ""
        echo -e "${BOLD}No AI client auto-detected. Select target:${NC}"
        echo ""
        echo -e "  ${CYAN}1)${NC} Claude Desktop"
        echo -e "  ${CYAN}2)${NC} Cursor"
        echo -e "  ${CYAN}3)${NC} Windsurf"
        echo -e "  ${CYAN}4)${NC} Print config only (manual setup)"
        echo ""
        read -rp "  Choose [1-4]: " CLIENT_CHOICE
        case "$CLIENT_CHOICE" in
            1) CLIENT="claude" ;;
            2) CLIENT="cursor" ;;
            3) CLIENT="windsurf" ;;
            4) CLIENT="print" ;;
            *) CLIENT="print" ;;
        esac
    elif [ ${#DETECTED[@]} -eq 1 ]; then
        CLIENT="${DETECTED[0]}"
        ok "Auto-detected: ${CLIENT}"
    else
        echo ""
        echo -e "${BOLD}Multiple clients detected:${NC}"
        echo ""
        local i=1
        for c in "${DETECTED[@]}"; do
            echo -e "  ${CYAN}${i})${NC} ${c}"
            i=$((i+1))
        done
        echo -e "  ${CYAN}${i})${NC} All detected clients"
        echo ""
        read -rp "  Choose [1-${i}]: " CLIENT_CHOICE

        if [ "$CLIENT_CHOICE" = "$i" ]; then
            CLIENT="all"
        elif [ "$CLIENT_CHOICE" -ge 1 ] 2>/dev/null && [ "$CLIENT_CHOICE" -le ${#DETECTED[@]} ]; then
            CLIENT="${DETECTED[$((CLIENT_CHOICE-1))]}"
        else
            CLIENT="all"
        fi
    fi
fi

# ── Step 4: Write config ──
MCP_JSON=$(cat <<EOF
{
  "mcpServers": {
    "dataify": {
      "url": "${MCP_URL}"
    }
  }
}
EOF
)

write_config() {
    local client="$1"
    local config_file=""
    local config_dir=""

    case "$client" in
        claude)
            if [ "$(uname)" = "Darwin" ]; then
                config_dir="$HOME/Library/Application Support/Claude"
            else
                config_dir="$HOME/.config/claude"
            fi
            config_file="${config_dir}/claude_desktop_config.json"
            ;;
        cursor)
            if [ "$(uname)" = "Darwin" ]; then
                config_dir="$HOME/Library/Application Support/Cursor/User"
            else
                config_dir="$HOME/.config/Cursor/User"
            fi
            config_file="${config_dir}/mcp.json"
            ;;
        windsurf)
            if [ "$(uname)" = "Darwin" ]; then
                config_dir="$HOME/Library/Application Support/Windsurf/User"
            else
                config_dir="$HOME/.config/Windsurf/User"
            fi
            config_file="${config_dir}/mcp.json"
            ;;
    esac

    if [ -z "$config_file" ]; then
        return 1
    fi

    mkdir -p "$config_dir"

    if [ -f "$config_file" ]; then
        # Check if dataify is already configured
        if grep -q '"dataify"' "$config_file" 2>/dev/null; then
            warn "${client}: config already contains 'dataify' entry"
            read -rp "  Overwrite existing dataify config? [y/N]: " OVERWRITE
            if [ "$OVERWRITE" != "y" ] && [ "$OVERWRITE" != "Y" ]; then
                info "${client}: skipped"
                return 0
            fi
        fi

        # Merge into existing config using python3
        if command -v python3 &>/dev/null; then
            python3 -c "
import json, sys
try:
    with open('${config_file}', 'r') as f:
        config = json.load(f)
except (json.JSONDecodeError, FileNotFoundError):
    config = {}

if 'mcpServers' not in config:
    config['mcpServers'] = {}

config['mcpServers']['dataify'] = {'url': '${MCP_URL}'}

with open('${config_file}', 'w') as f:
    json.dump(config, f, indent=2)
    f.write('\n')
" 2>/dev/null
            ok "${client}: config updated → ${config_file}"
        else
            echo "$MCP_JSON" > "$config_file"
            ok "${client}: config written → ${config_file}"
        fi
    else
        echo "$MCP_JSON" > "$config_file"
        ok "${client}: config created → ${config_file}"
    fi
}

echo ""
if [ "$CLIENT" = "print" ]; then
    info "Add the following to your AI client's MCP config:"
    echo ""
    echo "$MCP_JSON"
    echo ""
elif [ "$CLIENT" = "all" ]; then
    for c in "${DETECTED[@]}"; do
        write_config "$c"
    done
else
    write_config "$CLIENT"
fi

# ── Done ──
echo ""
echo -e "${GREEN}╔══════════════════════════════════════════╗${NC}"
echo -e "${GREEN}║        MCP Setup Complete!                ║${NC}"
echo -e "${GREEN}╚══════════════════════════════════════════╝${NC}"
echo ""
echo -e "  MCP URL:    ${BLUE}${MCP_BASE_URL}?token=****&tools=${TOOLS}${NC}"
echo -e "  Tools:      ${BLUE}${TOOL_COUNT} tools loaded${NC}"
echo -e "  Client:     ${BLUE}${CLIENT}${NC}"
echo ""
echo -e "  ${YELLOW}Next steps:${NC}"
echo ""
echo -e "  1. Restart your AI client (${CLIENT})"
echo -e "  2. Ask your AI agent:"
echo -e "     ${CYAN}\"Search Google for AI news\"${NC}"
echo -e "     ${CYAN}\"Scrape https://example.com\"${NC}"
echo -e "     ${CYAN}\"Collect Amazon product reviews for ASIN B0XXXXXXXX\"${NC}"
echo ""
echo -e "  Dashboard:  ${BLUE}${DASHBOARD_URL}${NC}"
echo ""
