#!/usr/bin/env bash
#
# Dataify Skills - Universal Installer
#
# Install skills into Claude Code, Codex (OpenAI), OpenClaw, or configure MCP Server.
#
# Usage:
#   curl -fsSL https://raw.githubusercontent.com/dataify-server/skills/main/install.sh | bash
#   bash install.sh
#   bash install.sh --target claude-code
#   bash install.sh --target codex
#   bash install.sh --target openclaw
#   bash install.sh --target all
#   bash install.sh --target claude-code --skills "serp-google-search,scraper-amazon-product"
#   bash install.sh --token YOUR_TOKEN
#   bash install.sh --uninstall --target claude-code
#

set -e

# ── Config ──
REPO_URL="https://github.com/dataify-server/skills.git"
INSTALL_DIR="${DATAIFY_SKILLS_DIR:-$HOME/.dataify/skills}"
DASHBOARD_URL="https://dashboard.dataify.com?utm_source=installer"
SKILL_PREFIX="dataify-"

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
TARGET=""
SKILLS_FILTER=""
TOKEN=""
UNINSTALL=false

while [[ $# -gt 0 ]]; do
    case $1 in
        --target)    TARGET="$2"; shift 2 ;;
        --skills)    SKILLS_FILTER="$2"; shift 2 ;;
        --token)     TOKEN="$2"; shift 2 ;;
        --uninstall) UNINSTALL=true; shift ;;
        --help)
            echo "Usage: bash install.sh [OPTIONS]"
            echo ""
            echo "Options:"
            echo "  --target TARGET      Target tool: claude-code, codex, openclaw, all (default: auto-detect)"
            echo "  --skills SKILLS      Comma-separated skill names to install (default: all)"
            echo "  --token TOKEN        Dataify API token (optional, can set later)"
            echo "  --uninstall          Remove installed skills from target tool"
            echo "  --help               Show this help message"
            echo ""
            echo "Examples:"
            echo "  bash install.sh                                    # Interactive, auto-detect tools"
            echo "  bash install.sh --target claude-code               # Install to Claude Code only"
            echo "  bash install.sh --target all                       # Install to all detected tools"
            echo "  bash install.sh --target codex --token abc123      # Install to Codex with token"
            echo "  bash install.sh --uninstall --target claude-code   # Remove from Claude Code"
            exit 0
            ;;
        *) warn "Unknown option: $1"; shift ;;
    esac
done

# ── Banner ──
echo ""
echo -e "${BLUE}╔══════════════════════════════════════════╗${NC}"
echo -e "${BLUE}║      Dataify Skills Installer            ║${NC}"
echo -e "${BLUE}║  63+ Skills · 3 Tools · Cross-Platform   ║${NC}"
echo -e "${BLUE}╚══════════════════════════════════════════╝${NC}"
echo ""

# ── Tool paths ──
get_claude_code_skills_dir() {
    echo "$HOME/.claude/skills"
}

get_openclaw_skills_dir() {
    echo "$HOME/.openclaw/skills"
}

get_codex_dir() {
    echo "$HOME/.codex"
}

# ── Detect installed tools ──
detect_tools() {
    local found=()
    # Claude Code
    if command -v claude &>/dev/null || [ -d "$HOME/.claude" ]; then
        found+=("claude-code")
    fi
    # Codex
    if command -v codex &>/dev/null || [ -d "$HOME/.codex" ]; then
        found+=("codex")
    fi
    # OpenClaw
    if command -v openclaw &>/dev/null || [ -d "$HOME/.openclaw" ]; then
        found+=("openclaw")
    fi
    echo "${found[@]}"
}

# ── Get list of skills to install ──
get_skill_dirs() {
    local skills_root="$INSTALL_DIR/skills"
    if [ -n "$SKILLS_FILTER" ]; then
        IFS=',' read -ra SKILL_NAMES <<< "$SKILLS_FILTER"
        for name in "${SKILL_NAMES[@]}"; do
            name=$(echo "$name" | xargs)  # trim whitespace
            local dir="$skills_root/$name"
            if [ -d "$dir" ] && [ -f "$dir/SKILL.md" ]; then
                echo "$dir"
            else
                warn "Skill not found: $name"
            fi
        done
    else
        find "$skills_root" -maxdepth 2 -name "SKILL.md" -not -path "*/.git/*" 2>/dev/null | while read -r f; do
            dirname "$f"
        done
    fi
}

# ── Uninstall ──
uninstall_claude_code() {
    local target_dir
    target_dir="$(get_claude_code_skills_dir)"
    local count=0
    if [ -d "$target_dir" ]; then
        for link in "$target_dir"/${SKILL_PREFIX}*; do
            if [ -L "$link" ]; then
                rm "$link"
                count=$((count + 1))
            fi
        done
    fi
    ok "Claude Code: removed $count skills from $target_dir"
}

uninstall_openclaw() {
    local target_dir
    target_dir="$(get_openclaw_skills_dir)"
    local count=0
    if [ -d "$target_dir" ]; then
        for link in "$target_dir"/${SKILL_PREFIX}*; do
            if [ -L "$link" ]; then
                rm "$link"
                count=$((count + 1))
            fi
        done
    fi
    ok "OpenClaw: removed $count skills from $target_dir"
}

uninstall_codex() {
    local codex_dir
    codex_dir="$(get_codex_dir)"
    local agents_file="$codex_dir/AGENTS.md"
    if [ -f "$agents_file" ]; then
        # Remove the Dataify section from AGENTS.md
        if grep -q "<!-- DATAIFY_SKILLS_START -->" "$agents_file" 2>/dev/null; then
            sed -i.bak '/<!-- DATAIFY_SKILLS_START -->/,/<!-- DATAIFY_SKILLS_END -->/d' "$agents_file"
            rm -f "${agents_file}.bak"
            # Remove file if empty after cleanup
            if [ ! -s "$agents_file" ] || ! grep -q '[^[:space:]]' "$agents_file" 2>/dev/null; then
                rm -f "$agents_file"
            fi
            ok "Codex: removed Dataify section from $agents_file"
        else
            info "Codex: no Dataify section found in $agents_file"
        fi
    else
        info "Codex: no AGENTS.md found"
    fi
}

if [ "$UNINSTALL" = true ]; then
    case "$TARGET" in
        claude-code) uninstall_claude_code ;;
        codex)       uninstall_codex ;;
        openclaw)    uninstall_openclaw ;;
        all)
            uninstall_claude_code
            uninstall_codex
            uninstall_openclaw
            ;;
        "")
            error "Please specify --target for uninstall (claude-code, codex, openclaw, all)"
            ;;
        *)
            error "Unknown target: $TARGET"
            ;;
    esac
    echo ""
    ok "Uninstall complete."
    exit 0
fi

# ── Phase 1: Clone or update repository ──
info "Phase 1: Downloading skills..."

if ! command -v git &>/dev/null; then
    error "git is not installed. Please install git first."
fi

if [ -d "$INSTALL_DIR/.git" ]; then
    info "Existing installation found, updating..."
    cd "$INSTALL_DIR"
    git pull --ff-only origin main 2>/dev/null || git pull --ff-only 2>/dev/null || warn "Could not auto-update. Using existing version."
    cd - > /dev/null
    ok "Updated successfully"
else
    info "Cloning to $INSTALL_DIR ..."
    mkdir -p "$(dirname "$INSTALL_DIR")"
    git clone "$REPO_URL" "$INSTALL_DIR" 2>/dev/null || error "Failed to clone repository. Check your network connection."
    ok "Cloned successfully"
fi

SKILL_COUNT=$(find "$INSTALL_DIR/skills" -maxdepth 2 -name "SKILL.md" -not -path "*/.git/*" 2>/dev/null | wc -l | tr -d ' ')
ok "Found ${SKILL_COUNT} skills"
echo ""

# ── Phase 2: Install to target tools ──
info "Phase 2: Installing skills to tools..."

# --- Claude Code & OpenClaw: symlink skill directories ---
install_symlinks() {
    local tool_name="$1"
    local target_dir="$2"
    local count=0

    mkdir -p "$target_dir"

    while IFS= read -r skill_dir; do
        [ -z "$skill_dir" ] && continue
        local skill_name
        skill_name=$(basename "$skill_dir")
        # Avoid double prefix (e.g., dataify-dataify-web-unlocker)
        local link_name
        if [[ "$skill_name" == ${SKILL_PREFIX}* ]]; then
            link_name="$skill_name"
        else
            link_name="${SKILL_PREFIX}${skill_name}"
        fi
        local link_path="$target_dir/$link_name"

        # Remove existing symlink if present
        if [ -L "$link_path" ]; then
            rm "$link_path"
        elif [ -e "$link_path" ]; then
            warn "$tool_name: $link_name already exists (not a symlink), skipping"
            continue
        fi

        ln -s "$skill_dir" "$link_path"
        count=$((count + 1))
    done < <(get_skill_dirs)

    ok "$tool_name: $count skills linked -> $target_dir"
}

install_claude_code() {
    local target_dir
    target_dir="$(get_claude_code_skills_dir)"
    install_symlinks "Claude Code" "$target_dir"
}

install_openclaw() {
    local target_dir
    target_dir="$(get_openclaw_skills_dir)"
    install_symlinks "OpenClaw" "$target_dir"
}

# --- Codex: generate AGENTS.md index ---
install_codex() {
    local codex_dir
    codex_dir="$(get_codex_dir)"
    local agents_file="$codex_dir/AGENTS.md"

    mkdir -p "$codex_dir"

    # Build skill index content
    local content=""
    content+="<!-- DATAIFY_SKILLS_START -->\n"
    content+="# Dataify Skills\n\n"
    content+="You have access to Dataify data collection skills for web scraping, search, and structured data extraction.\n\n"
    content+="**Setup:** Set \`DATAIFY_API_TOKEN\` environment variable before using any skill.\n"
    content+="Get your token at: https://dashboard.dataify.com\n\n"
    content+="## Available Skills\n\n"
    content+="| Skill | Description | Script |\n"
    content+="|-------|-------------|--------|\n"

    while IFS= read -r skill_dir; do
        [ -z "$skill_dir" ] && continue
        local skill_name
        skill_name=$(basename "$skill_dir")

        # Extract description from SKILL.md frontmatter (handles BOM and quoted values)
        local description=""
        if [ -f "$skill_dir/SKILL.md" ]; then
            description=$(tr -d '\357\273\277' < "$skill_dir/SKILL.md" | grep -m1 '^description:' | sed 's/^description: *//; s/^"//; s/"$//')
        fi
        [ -z "$description" ] && description="$skill_name"
        # Truncate long descriptions
        if [ ${#description} -gt 80 ]; then
            description="${description:0:77}..."
        fi

        # Find main script
        local main_script=""
        if [ -d "$skill_dir/scripts" ]; then
            main_script=$(find "$skill_dir/scripts" -maxdepth 1 -name "*.py" ! -name "preview_params.py" ! -name "__pycache__" 2>/dev/null | head -1)
            if [ -z "$main_script" ]; then
                main_script=$(find "$skill_dir/scripts" -maxdepth 1 -name "*.py" 2>/dev/null | head -1)
            fi
        fi

        if [ -n "$main_script" ]; then
            content+="| ${skill_name} | ${description} | \`python3 ${main_script}\` |\n"
        else
            content+="| ${skill_name} | ${description} | See SKILL.md |\n"
        fi
    done < <(get_skill_dirs)

    content+="\n## Usage\n\n"
    content+="For detailed instructions on any skill, read its SKILL.md:\n"
    content+="\`\`\`bash\n"
    content+="cat ${INSTALL_DIR}/skills/<skill-name>/SKILL.md\n"
    content+="\`\`\`\n"
    content+="<!-- DATAIFY_SKILLS_END -->\n"

    # Write or merge into AGENTS.md
    if [ -f "$agents_file" ]; then
        # Remove existing Dataify section if present
        if grep -q "<!-- DATAIFY_SKILLS_START -->" "$agents_file" 2>/dev/null; then
            sed -i.bak '/<!-- DATAIFY_SKILLS_START -->/,/<!-- DATAIFY_SKILLS_END -->/d' "$agents_file"
            rm -f "${agents_file}.bak"
        fi
        # Append
        echo "" >> "$agents_file"
        echo -e "$content" >> "$agents_file"
        ok "Codex: updated $agents_file"
    else
        echo -e "$content" > "$agents_file"
        ok "Codex: created $agents_file"
    fi
}

# --- Select and run installation ---
run_install() {
    local targets=("$@")
    for t in "${targets[@]}"; do
        case "$t" in
            claude-code) install_claude_code ;;
            codex)       install_codex ;;
            openclaw)    install_openclaw ;;
            *)           warn "Unknown target: $t" ;;
        esac
    done
}

if [ -n "$TARGET" ]; then
    if [ "$TARGET" = "all" ]; then
        run_install "claude-code" "codex" "openclaw"
    else
        run_install "$TARGET"
    fi
else
    # Auto-detect and interactive
    DETECTED=($(detect_tools))

    if [ ${#DETECTED[@]} -eq 0 ]; then
        echo -e "  No tools auto-detected. Select target:"
        echo ""
        echo -e "  ${CYAN}1)${NC} Claude Code"
        echo -e "  ${CYAN}2)${NC} Codex (OpenAI)"
        echo -e "  ${CYAN}3)${NC} OpenClaw"
        echo -e "  ${CYAN}4)${NC} All"
        echo ""
        read -rp "  Choose [1-4]: " CHOICE
        case "$CHOICE" in
            1) run_install "claude-code" ;;
            2) run_install "codex" ;;
            3) run_install "openclaw" ;;
            4) run_install "claude-code" "codex" "openclaw" ;;
            *) run_install "claude-code" "codex" "openclaw" ;;
        esac
    else
        echo -e "  Detected tools:"
        for t in "${DETECTED[@]}"; do
            echo -e "    ${GREEN}✓${NC} $t"
        done
        echo ""
        read -rp "  Install to all detected tools? [Y/n]: " CONFIRM
        if [ "$CONFIRM" = "n" ] || [ "$CONFIRM" = "N" ]; then
            echo ""
            echo -e "  ${CYAN}1)${NC} Claude Code"
            echo -e "  ${CYAN}2)${NC} Codex (OpenAI)"
            echo -e "  ${CYAN}3)${NC} OpenClaw"
            echo -e "  ${CYAN}4)${NC} All"
            echo ""
            read -rp "  Choose [1-4]: " CHOICE
            case "$CHOICE" in
                1) run_install "claude-code" ;;
                2) run_install "codex" ;;
                3) run_install "openclaw" ;;
                4) run_install "claude-code" "codex" "openclaw" ;;
                *) run_install "${DETECTED[@]}" ;;
            esac
        else
            run_install "${DETECTED[@]}"
        fi
    fi
fi

# ── Save token if provided ──
if [ -n "$TOKEN" ]; then
    SHELL_NAME=$(basename "$SHELL")
    case "$SHELL_NAME" in
        zsh)  RC_FILE="$HOME/.zshrc" ;;
        bash) RC_FILE="$HOME/.bashrc" ;;
        *)    RC_FILE="$HOME/.profile" ;;
    esac

    if grep -q "DATAIFY_API_TOKEN" "$RC_FILE" 2>/dev/null; then
        sed -i.bak "s|^export DATAIFY_API_TOKEN=.*|export DATAIFY_API_TOKEN=\"${TOKEN}\"|" "$RC_FILE"
        rm -f "${RC_FILE}.bak"
    else
        echo "" >> "$RC_FILE"
        echo "# Dataify API Token" >> "$RC_FILE"
        echo "export DATAIFY_API_TOKEN=\"${TOKEN}\"" >> "$RC_FILE"
    fi
    ok "Token saved to $RC_FILE"
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

# ── Phase 3: Done ──
echo ""
echo -e "${GREEN}╔══════════════════════════════════════════╗${NC}"
echo -e "${GREEN}║       Installation Complete!              ║${NC}"
echo -e "${GREEN}╚══════════════════════════════════════════╝${NC}"
echo ""
echo -e "  Skills directory: ${BLUE}${INSTALL_DIR}${NC}"
echo -e "  Total skills:     ${BLUE}${SKILL_COUNT}${NC}"
echo ""
echo -e "  ${BOLD}Usage:${NC}"
echo -e "    Claude Code  ${CYAN}/dataify-serp-google-search${NC}"
echo -e "    OpenClaw     ${CYAN}/dataify-serp-google-search${NC}"
echo -e "    Codex        ${CYAN}Skills auto-loaded from ~/.codex/AGENTS.md${NC}"
echo ""
echo -e "  ${BOLD}To use skills, set your API token:${NC}"
echo -e "    export DATAIFY_API_TOKEN=\"your-token\""
echo -e "    Get one at: ${BLUE}${DASHBOARD_URL}${NC}"
echo ""
echo -e "  ${BOLD}Other commands:${NC}"
echo -e "    Update:    ${CYAN}bash install.sh${NC}"
echo -e "    Uninstall: ${CYAN}bash install.sh --uninstall --target all${NC}"
echo -e "    MCP setup: ${CYAN}bash setup-mcp.sh${NC}"
echo ""
