# Dataify Skills for Claude Code

**Unlock the web with AI-powered scraping, search, and structured data extraction**

[![License: MIT](https://img.shields.io/badge/License-MIT-blue.svg)](LICENSE)
[![Skills](https://img.shields.io/badge/Skills-63+-brightgreen.svg)](#skill-catalog)
[![Datasets](https://img.shields.io/badge/Datasets-25+-orange.svg)](#data-sources)
[![MCP Tools](https://img.shields.io/badge/MCP_Tools-25+-purple.svg)](#mcp-server)
[![Platforms](https://img.shields.io/badge/Platforms-25+-red.svg)](#skill-catalog)

[Quick Start](#quick-start) | [Skills](#skill-catalog) | [Agent Onboarding](#agent-onboarding) | [MCP Server](#mcp-server) | [Data Sources](#data-sources) | [Competitive Intelligence](#competitive-intelligence) | [Best Practices](#best-practices) | [Settings](#settings) | [Examples](#examples)

## Overview

This plugin integrates [Dataify](https://dashboard.dataify.com?utm_source=github)'s powerful web infrastructure directly into Claude Code, enabling AI agents to:

- **Scrape any webpage as clean Markdown** — bypassing bot detection, CAPTCHAs, and JavaScript rendering
- **Search Google, Bing, Yandex, DuckDuckGo** with structured JSON results — titles, links, and descriptions ready for processing
- **Extract structured data from 25+ websites** — including Amazon, LinkedIn, Instagram, TikTok, YouTube, Twitter/X, and more
- **Orchestrate 25+ MCP tools** via Dataify's MCP Server — search, scrape, extract structured data from any MCP-compatible AI agent
- **Collect e-commerce intelligence** — product data, pricing, reviews, and seller information from Amazon, eBay, Walmart
- **Perform competitive intelligence** — real-time competitor analysis, price monitoring, review mining, and market landscape mapping
- **Download media files** — YouTube video and audio downloads with transcript extraction

Built on Dataify's [Web Unlocker](https://doc.dataify.com/web-unlocker?utm_source=github), [SERP API](https://doc.dataify.com/serp-api?utm_source=github), and [Web Data API](https://doc.dataify.com/web-data-api?utm_source=github), handling complex web access so your AI agents can focus on what matters.

## Quick Start

### 1. Install

```bash
curl -fsSL https://raw.githubusercontent.com/dataify-server/skills/main/install.sh | bash
```

The installer will clone the repo, prompt for your API token, and configure your shell environment.

### 2. Set Your API Token

```bash
export DATAIFY_API_TOKEN="your-api-token"
```

Get your API token at [Dataify Dashboard](https://dashboard.dataify.com?utm_source=github).

### 3. Try It

```bash
# Search Google
python3 serp-google-search/scripts/google_search.py \
  --params-json '{"q":"AI news"}'

# Unlock any web page
python3 dataify-web-unlocker/scripts/invoke-dataify-web-unlocker.py \
  --url "https://example.com"

# Collect Amazon products
python3 scraper-amazon-product/scripts/submit_amazon_product.py --help
```

## Agent Onboarding

When an AI agent first interacts with Dataify Skills, follow this routing to find the right path:

### Path A: MCP Server (Recommended)

For AI agents using Claude Desktop, Cursor, Windsurf, or any MCP-compatible client — connect via the MCP Server for the most seamless experience.

> Jump to [MCP Server](#mcp-server)

### Path B: Script Execution

For direct script execution and automation — use the Python scripts in each skill directory.

> Jump to [Quick Start](#quick-start)

### Path C: Skills Reference

For browsing available capabilities and finding the right skill for your task.

> Jump to [Skill Catalog](#skill-catalog)

### Path D: REST API

For no-install, direct API integration — call Dataify APIs directly.

> Visit [API Documentation](https://doc.dataify.com?utm_source=github)

## MCP Server

Dataify provides a native **MCP (Model Context Protocol)** server, allowing AI agents like Claude, Cursor, Windsurf, and other MCP-compatible clients to directly call Dataify tools.

### MCP Endpoint

```
https://mcp.dataify.com/mcp?token=YOUR_API_TOKEN&tools=TOOL_LIST
```

### Supported MCP Tools (25)

| Category | Tools | Description |
|----------|-------|-------------|
| **Account** | `user_info` | Query account info and API usage |
| **Web Unlocker** | `web_unlocker` | Scrape any URL as clean content, bypass bot detection |
| **SERP** | `google_serp`, `bing_serp`, `yandex_serp`, `duckduckgo_serp` | Structured search engine results across 4 engines |
| **E-Commerce** | `amazon`, `ebay`, `walmart` | Product data, pricing, reviews, seller info |
| **Social Media** | `facebook`, `instagram`, `tiktok`, `twitter`, `linkedin`, `reddit` | Profiles, posts, comments, followers |
| **Video** | `youtube` | Videos, channels, comments, transcripts, downloads |
| **Search & Maps** | `google` | Google Maps details, reviews, shopping |
| **Travel** | `booking`, `airbnb` | Hotel listings, property data |
| **Jobs & Business** | `indeed`, `glassdoor`, `crunchbase` | Job listings, company profiles, funding data |
| **Developer** | `github`, `google_play_store` | Repository info, app store reviews |
| **Real Estate** | `zillow` | Property listings and data |

### One-line Setup (Recommended)

```bash
curl -fsSL https://raw.githubusercontent.com/dataify-server/skills/main/setup-mcp.sh | bash
```

The script will:
1. Prompt for your API token
2. Let you choose a tool preset (All / Lightweight / Social Media / E-Commerce / Research / Custom)
3. Auto-detect your AI client (Claude Desktop / Cursor / Windsurf)
4. Write the MCP config automatically

You can also pass arguments directly:

```bash
# Specify token and client
bash setup-mcp.sh --token YOUR_TOKEN --client claude

# Load only specific tools
bash setup-mcp.sh --token YOUR_TOKEN --tools "google_serp,amazon,youtube"
```

### Manual Setup

#### Configure in Claude Desktop

Add to your `claude_desktop_config.json`:

```json
{
  "mcpServers": {
    "dataify": {
      "url": "https://mcp.dataify.com/mcp?token=YOUR_API_TOKEN&tools=user_info,web_unlocker,google_serp,yandex_serp,duckduckgo_serp,bing_serp,amazon,youtube,facebook,instagram,reddit,walmart,google,booking,indeed,airbnb,google_play_store,github,tiktok,linkedin,glassdoor,twitter,crunchbase,zillow,ebay"
    }
  }
}
```

#### Configure in Cursor / Windsurf

Go to **Settings > MCP**, click **Add new MCP server**, select type **sse**, and enter the URL above.

### Selective Tool Loading

Load only the tools you need by customizing the `tools` parameter:

```bash
# Only SERP tools
https://mcp.dataify.com/mcp?token=YOUR_API_TOKEN&tools=google_serp,bing_serp,yandex_serp,duckduckgo_serp

# Only social media tools
https://mcp.dataify.com/mcp?token=YOUR_API_TOKEN&tools=facebook,instagram,tiktok,twitter,linkedin,reddit

# Only e-commerce tools
https://mcp.dataify.com/mcp?token=YOUR_API_TOKEN&tools=amazon,ebay,walmart

# Web Unlocker + SERP (lightweight)
https://mcp.dataify.com/mcp?token=YOUR_API_TOKEN&tools=web_unlocker,google_serp
```

## Data Sources

Dataify provides pre-built data extraction for 25+ platforms, accessible via MCP tools, Python scripts, or REST API.

### E-Commerce

| Platform | Data Types | Access |
|----------|-----------|--------|
| **Amazon** | Products, reviews, sellers, global products, product lists | MCP + Scripts |
| **eBay** | Product listings | MCP + Scripts |
| **Walmart** | Product listings | MCP + Scripts |

### Social Media

| Platform | Data Types | Access |
|----------|-----------|--------|
| **Instagram** | Profiles, comments, Reels | MCP + Scripts |
| **Facebook** | Posts, comments, profiles, events | MCP + Scripts |
| **TikTok** | Comments | MCP + Scripts |
| **Twitter/X** | Profiles | MCP + Scripts |
| **LinkedIn** | Company information | MCP + Scripts |
| **Reddit** | Posts, comments | MCP + Scripts |

### Search Engines (SERP)

| Engine | Verticals | Access |
|--------|----------|--------|
| **Google** | Web, AI Mode, Images, Videos, News, Maps, Shopping, Scholar, Finance, Flights, Hotels, Jobs, Lens, Local, Patents, Play, Trends (17) | MCP + Scripts |
| **Bing** | Web, Images, Videos, News, Shopping, Maps (6) | MCP + Scripts |
| **DuckDuckGo** | Web search | MCP + Scripts |
| **Yandex** | Web search | MCP + Scripts |

### Video

| Platform | Data Types | Access |
|----------|-----------|--------|
| **YouTube** | Videos, comments, profiles, transcripts, video download, audio download, video info | MCP + Scripts |

### Travel & Hospitality

| Platform | Data Types | Access |
|----------|-----------|--------|
| **Booking.com** | Hotel listings | MCP + Scripts |
| **Airbnb** | Property listings by search URL | MCP + Scripts |

### Jobs & Business

| Platform | Data Types | Access |
|----------|-----------|--------|
| **Indeed** | Job listings, company info | MCP + Scripts |
| **Glassdoor** | Company profiles | MCP + Scripts |
| **Crunchbase** | Company profiles | MCP + Scripts |

### Developer & Apps

| Platform | Data Types | Access |
|----------|-----------|--------|
| **GitHub** | Repository information | MCP + Scripts |
| **Google Play Store** | App reviews | MCP + Scripts |

### Real Estate

| Platform | Data Types | Access |
|----------|-----------|--------|
| **Zillow** | Property data | MCP |

### Maps & Local

| Platform | Data Types | Access |
|----------|-----------|--------|
| **Google Maps** | Place details, reviews | Scripts |
| **Google Shopping** | Product search by keyword | Scripts |

## Competitive Intelligence

Use Dataify Skills to build real-time competitive intelligence workflows with live web data.

### Competitor Snapshot

Combine multiple skills to build a comprehensive competitor profile:

```bash
# 1. Search for competitor information
python3 serp-google-search/scripts/google_search.py \
  --params-json '{"q":"competitor_name site:crunchbase.com OR site:linkedin.com"}'

# 2. Scrape their website for positioning and pricing
python3 dataify-web-unlocker/scripts/invoke-dataify-web-unlocker.py \
  --url "https://competitor.com/pricing"

# 3. Collect their product reviews on Amazon
python3 scraper-amazon-comment/scripts/submit_amazon_comment.py \
  --asin "B0XXXXXXXX"
```

### Analysis Modules

| Module | Skills Used | Output |
|--------|------------|--------|
| **Competitor Profiling** | Google SERP + Web Unlocker + Crunchbase | Company overview, funding, team, positioning |
| **Price Monitoring** | Amazon + eBay + Walmart + Google Shopping | Cross-platform price comparison |
| **Review Mining** | Amazon Comments + Google Maps Reviews + Instagram | Customer sentiment analysis |
| **Hiring Signal Analysis** | Indeed + Glassdoor + LinkedIn | Strategic intent from job postings |
| **Content & SEO** | Google SERP + Web Unlocker | Search positioning, content strategy |
| **Market Landscape** | Google SERP + Crunchbase | Discover and categorize market players |

### MCP-Powered Analysis

With the MCP Server, AI agents can autonomously chain these tools:

```
User: "Analyze the competitive landscape for [product category]"

Agent workflow:
1. google_serp → Find top competitors
2. web_unlocker → Scrape competitor websites for features & pricing
3. amazon → Collect product data and reviews
4. indeed → Check hiring patterns for strategic signals
5. Synthesize → Generate competitive analysis report
```

## Skill Catalog

### Skills Overview (63)

| Category | Count | Description |
|----------|-------|-------------|
| [Web Unlocker](#web-unlocker) | 1 | Bypass bot detection, scrape any webpage |
| [SERP Skills](#serp-skills) | 25 | Search engine results (Google 17 + Bing 6 + DuckDuckGo + Yandex) |
| [Scraper Skills](#scraper-skills-37) | 37 | Structured data extraction from 20+ platforms |

### Web Unlocker

| Skill | Description |
|-------|-------------|
| [dataify-web-unlocker](dataify-web-unlocker/) | Fetch any web page as clean content, bypassing bot detection, CAPTCHAs, and JavaScript rendering |

### SERP Skills

Structured search engine results across 25 verticals.

#### Google (17)

| Skill | Description |
|-------|-------------|
| [serp-google-search](serp-google-search/) | Google web search results |
| [serp-google-ai-mode](serp-google-ai-mode/) | Google AI Mode search results |
| [serp-google-images](serp-google-images/) | Google Images search |
| [serp-google-videos](serp-google-videos/) | Google Videos search |
| [serp-google-news](serp-google-news/) | Google News search |
| [serp-google-maps](serp-google-maps/) | Google Maps search |
| [serp-google-shopping](serp-google-shopping/) | Google Shopping search and price comparison |
| [serp-google-scholar](serp-google-scholar/) | Google Scholar academic paper search |
| [serp-google-finance](serp-google-finance/) | Google Finance financial data |
| [serp-google-flights](serp-google-flights/) | Google Flights price and itinerary search |
| [serp-google-hotels](serp-google-hotels/) | Google Hotels price and availability search |
| [serp-google-jobs](serp-google-jobs/) | Google Jobs search |
| [serp-google-lens](serp-google-lens/) | Google Lens image search |
| [serp-google-local](serp-google-local/) | Google Local / nearby place search |
| [serp-google-patents](serp-google-patents/) | Google Patents search |
| [serp-google-play](serp-google-play/) | Google Play app store search |
| [serp-google-trends](serp-google-trends/) | Google Trends data |

#### Bing (6)

| Skill | Description |
|-------|-------------|
| [serp-bing-search](serp-bing-search/) | Bing web search |
| [serp-bing-images](serp-bing-images/) | Bing image search |
| [serp-bing-videos](serp-bing-videos/) | Bing video search |
| [serp-bing-news](serp-bing-news/) | Bing news search |
| [serp-bing-shopping](serp-bing-shopping/) | Bing shopping and product search |
| [serp-bing-maps](serp-bing-maps/) | Bing Maps location search |

#### Others (2)

| Skill | Description |
|-------|-------------|
| [serp-duckduckgo-search](serp-duckduckgo-search/) | DuckDuckGo web search |
| [serp-yandex-search](serp-yandex-search/) | Yandex web search |

### Scraper Skills (37)

Structured data extraction from 20+ platforms via async task management.

#### Amazon (5)

| Skill | Description |
|-------|-------------|
| [scraper-amazon-product](scraper-amazon-product/) | Collect Amazon products by ASIN, URL, keyword, category, or Best Sellers |
| [scraper-amazon-comment](scraper-amazon-comment/) | Collect Amazon product reviews |
| [scraper-amazon-global-product](scraper-amazon-global-product/) | Collect Amazon global product information |
| [scraper-amazon-product-list](scraper-amazon-product-list/) | Collect Amazon product listings |
| [scraper-amazon-seller](scraper-amazon-seller/) | Collect Amazon seller information |

#### YouTube (7)

| Skill | Description |
|-------|-------------|
| [scraper-youtube-video-post](scraper-youtube-video-post/) | Collect YouTube videos by URL, keyword, hashtag, or Explore |
| [scraper-youtube-product-by-id](scraper-youtube-product-by-id/) | Collect YouTube video basic information by video ID |
| [scraper-youtube-comment-by-id](scraper-youtube-comment-by-id/) | Collect YouTube comments by video ID |
| [scraper-youtube-profiles](scraper-youtube-profiles/) | Collect YouTube channel profiles by URL or keyword |
| [scraper-youtube-transcript-by-id](scraper-youtube-transcript-by-id/) | Extract YouTube video subtitles/transcripts by video ID |
| [scraper-youtube-video-by-url](scraper-youtube-video-by-url/) | Download YouTube video files by URL |
| [scraper-youtube-audio-by-url](scraper-youtube-audio-by-url/) | Download YouTube audio files by URL |

#### Facebook (4)

| Skill | Description |
|-------|-------------|
| [scraper-facebook-post-by-url](scraper-facebook-post-by-url/) | Collect Facebook posts by URL |
| [scraper-facebook-comment-by-url](scraper-facebook-comment-by-url/) | Collect Facebook post comments by URL |
| [scraper-facebook-profile-by-url](scraper-facebook-profile-by-url/) | Collect Facebook profiles by URL |
| [scraper-facebook-events](scraper-facebook-events/) | Collect Facebook events |

#### Instagram (3)

| Skill | Description |
|-------|-------------|
| [scraper-instagram-profiles](scraper-instagram-profiles/) | Collect Instagram profiles by URL or keyword |
| [scraper-instagram-comment-by-posturl](scraper-instagram-comment-by-posturl/) | Collect Instagram post comments by URL |
| [scraper-instagram-reels](scraper-instagram-reels/) | Collect Instagram Reels information |

#### Google Maps & Shopping (3)

| Skill | Description |
|-------|-------------|
| [scraper-google-map-details](scraper-google-map-details/) | Collect Google Maps place details |
| [scraper-google-maps-reviews](scraper-google-maps-reviews/) | Collect Google Maps reviews |
| [scraper-google-shopping-keywords](scraper-google-shopping-keywords/) | Collect Google Shopping products by keyword |

#### Reddit (2)

| Skill | Description |
|-------|-------------|
| [scraper-reddit-posts](scraper-reddit-posts/) | Collect Reddit posts by URL, keyword, or subreddit |
| [scraper-reddit-comment-by-url](scraper-reddit-comment-by-url/) | Collect Reddit post comments by URL |

#### Indeed (2)

| Skill | Description |
|-------|-------------|
| [scraper-indeed-job-listings](scraper-indeed-job-listings/) | Collect Indeed job listings |
| [scraper-indeed-companies-info](scraper-indeed-companies-info/) | Collect Indeed company information |

#### E-commerce (2)

| Skill | Description |
|-------|-------------|
| [scraper-ebay-products](scraper-ebay-products/) | Collect eBay product information |
| [scraper-walmart-products](scraper-walmart-products/) | Collect Walmart product information |

#### Travel (1)

| Skill | Description |
|-------|-------------|
| [scraper-booking-hotellist](scraper-booking-hotellist/) | Collect Booking.com hotel information |

#### Business & Jobs (3)

| Skill | Description |
|-------|-------------|
| [scraper-crunchbase-company-by-url](scraper-crunchbase-company-by-url/) | Scrape Crunchbase company profiles by URL |
| [scraper-glassdoor-company-by-url](scraper-glassdoor-company-by-url/) | Scrape Glassdoor company profiles by URL |
| [scraper-linkedin-company-information-by-url](scraper-linkedin-company-information-by-url/) | Scrape LinkedIn company information by URL |

#### Social Media (2)

| Skill | Description |
|-------|-------------|
| [scraper-tiktok-comment-by-url](scraper-tiktok-comment-by-url/) | Scrape TikTok comments by URL |
| [scraper-twitter-profile-by-profileurl](scraper-twitter-profile-by-profileurl/) | Scrape X (Twitter) profiles by URL |

#### Developer & Apps (2)

| Skill | Description |
|-------|-------------|
| [scraper-github-repository-by-repo-url](scraper-github-repository-by-repo-url/) | Scrape GitHub repository information by URL |
| [scraper-google-play-store-reviews-by-url](scraper-google-play-store-reviews-by-url/) | Scrape Google Play Store reviews by URL |

#### Real Estate (1)

| Skill | Description |
|-------|-------------|
| [scraper-airbnb-product-by-searchurl](scraper-airbnb-product-by-searchurl/) | Scrape Airbnb property listings by search URL |

## Best Practices

### Web Unlocker

Use the Web Unlocker for any URL that isn't covered by a dedicated skill:

```python
# Scrape any webpage as clean content
python3 dataify-web-unlocker/scripts/invoke-dataify-web-unlocker.py \
  --url "https://example.com/page"
```

**When to use:**
- Target site has no dedicated skill
- You need raw HTML or rendered content
- Site uses JavaScript rendering, CAPTCHAs, or bot detection

### SERP API

Use SERP skills for search engine results with structured JSON output:

```python
# Google search with location targeting
python3 serp-google-search/scripts/google_search.py \
  --params-json '{"q":"AI trends","gl":"us","hl":"en","num":20}'
```

**Best practices:**
- Use `gl` (country) and `hl` (language) for geo-targeted results
- Use `num` to control result count
- Combine with Web Unlocker to scrape the actual pages from search results

### Scraper API

Use Scraper skills for structured data extraction with async task management:

```python
# Submit a batch task, then poll for results
python3 scraper-amazon-product/scripts/submit_amazon_product.py \
  --keyword "wireless headphones" --count 100
```

**Best practices:**
- Submit task first, then poll for completion
- Use for bulk data collection (100+ items)
- Results are delivered as structured JSON

### Skill Selection Guide

| I want to... | Use this |
|--------------|----------|
| Scrape any webpage | `dataify-web-unlocker` |
| Search Google/Bing/etc. | `serp-google-search` / `serp-bing-search` |
| Get Amazon products | `scraper-amazon-product` or MCP `amazon` tool |
| Collect social media data | `scraper-instagram-*` / `scraper-facebook-*` or MCP tool |
| Build a custom scraper | `dataify-web-unlocker` + your parsing logic |
| Run competitive analysis | Combine multiple skills (see [Competitive Intelligence](#competitive-intelligence)) |
| Download YouTube videos | `scraper-youtube-video-by-url` / `scraper-youtube-audio-by-url` |

## Settings

### Environment Variables

| Variable | Required | Description |
|----------|----------|-------------|
| `DATAIFY_API_TOKEN` | Yes | Your Dataify API token ([get one here](https://dashboard.dataify.com?utm_source=github)) |
| `DATAIFY_SKILLS_DIR` | No | Custom install directory (default: `~/.dataify/skills`) |

### API Token Resolution

Skills resolve the API token in this order:

1. `--token` command-line argument
2. `DATAIFY_API_TOKEN` environment variable
3. Prompt user for input

### Skill Structure

Each skill follows a standard layout:

```
skill-name/
├── SKILL.md              # Skill documentation (required)
├── SKILL.zh-CN.md        # Chinese documentation (optional)
├── agents/
│   └── openai.yaml       # OpenAI agent configuration
├── scripts/
│   └── main_script.py    # Execution script
└── references/
    └── api.md            # API reference (optional)
```

## Repository Structure

```
dataify_skills/
├── README.md
├── CONTRIBUTING.md
├── LICENSE
├── install.sh
│
├── dataify-web-unlocker/                          # Web Unlocker
│
├── serp-google-search/                            # SERP — Google (17 verticals)
├── serp-google-ai-mode/
├── serp-google-images/
├── serp-google-videos/
├── serp-google-news/
├── serp-google-maps/
├── serp-google-shopping/
├── serp-google-scholar/
├── serp-google-finance/
├── serp-google-flights/
├── serp-google-hotels/
├── serp-google-jobs/
├── serp-google-lens/
├── serp-google-local/
├── serp-google-patents/
├── serp-google-play/
├── serp-google-trends/
├── serp-bing-search/                              # SERP — Bing (6 verticals)
├── serp-bing-images/
├── serp-bing-videos/
├── serp-bing-news/
├── serp-bing-shopping/
├── serp-bing-maps/
├── serp-duckduckgo-search/                        # SERP — DuckDuckGo
├── serp-yandex-search/                            # SERP — Yandex
│
├── scraper-amazon-product/                        # Scraper — Amazon (5)
├── scraper-amazon-comment/
├── scraper-amazon-global-product/
├── scraper-amazon-product-list/
├── scraper-amazon-seller/
├── scraper-youtube-video-post/                    # Scraper — YouTube (7)
├── scraper-youtube-product-by-id/
├── scraper-youtube-comment-by-id/
├── scraper-youtube-profiles/
├── scraper-youtube-transcript-by-id/
├── scraper-youtube-video-by-url/
├── scraper-youtube-audio-by-url/
├── scraper-facebook-post-by-url/                  # Scraper — Facebook (4)
├── scraper-facebook-comment-by-url/
├── scraper-facebook-profile-by-url/
├── scraper-facebook-events/
├── scraper-instagram-profiles/                    # Scraper — Instagram (3)
├── scraper-instagram-comment-by-posturl/
├── scraper-instagram-reels/
├── scraper-google-map-details/                    # Scraper — Google Maps & Shopping (3)
├── scraper-google-maps-reviews/
├── scraper-google-shopping-keywords/
├── scraper-reddit-posts/                          # Scraper — Reddit (2)
├── scraper-reddit-comment-by-url/
├── scraper-indeed-job-listings/                   # Scraper — Indeed (2)
├── scraper-indeed-companies-info/
├── scraper-ebay-products/                         # Scraper — eBay (1)
├── scraper-walmart-products/                      # Scraper — Walmart (1)
├── scraper-booking-hotellist/                     # Scraper — Booking.com (1)
├── scraper-crunchbase-company-by-url/             # Scraper — Business & Jobs (3)
├── scraper-glassdoor-company-by-url/
├── scraper-linkedin-company-information-by-url/
├── scraper-tiktok-comment-by-url/                 # Scraper — Social Media (2)
├── scraper-twitter-profile-by-profileurl/
├── scraper-github-repository-by-repo-url/         # Scraper — Developer & Apps (2)
├── scraper-google-play-store-reviews-by-url/
└── scraper-airbnb-product-by-searchurl/           # Scraper — Real Estate (1)
```

## Examples

### Example 1: E-commerce Price Comparison

```bash
# Collect product data from multiple platforms
python3 scraper-amazon-product/scripts/submit_amazon_product.py \
  --keyword "wireless earbuds"

python3 scraper-ebay-products/scripts/submit_ebay_products.py \
  --keyword "wireless earbuds"

python3 scraper-walmart-products/scripts/submit_walmart_products.py \
  --keyword "wireless earbuds"
```

### Example 2: Social Media Monitoring

```bash
# Monitor a brand across social platforms
python3 scraper-instagram-profiles/scripts/submit_instagram_profiles.py \
  --url "https://instagram.com/brand_name"

python3 scraper-youtube-profiles/scripts/submit_youtube_profiles.py \
  --url "https://youtube.com/@brand_name"

python3 scraper-reddit-posts/scripts/submit_reddit_posts.py \
  --keyword "brand_name"
```

### Example 3: Job Market Analysis

```bash
# Analyze job market for a specific role
python3 serp-google-jobs/scripts/google_jobs.py \
  --params-json '{"q":"senior AI engineer","gl":"us"}'

python3 scraper-indeed-job-listings/scripts/submit_indeed_job_listings.py \
  --keyword "senior AI engineer"
```

### Example 4: MCP-Powered Research (Claude Desktop)

Once configured, ask Claude directly:

```
"Search Google for the top 10 AI startups in 2025, then scrape each website
 for their product features and pricing. Compile the results into a comparison table."

"Collect all reviews for [product ASIN] on Amazon, analyze sentiment,
 and identify the top 5 customer complaints."

"Find all job postings from [company] on Indeed and LinkedIn,
 then analyze their hiring trends."
```

## Adding a New Skill

See [CONTRIBUTING.md](CONTRIBUTING.md) for detailed guidelines on:

- Skill directory structure and naming conventions
- Writing `SKILL.md` documentation
- Creating `agents/openai.yaml` configurations
- Implementing Python scripts
- Testing and submitting PRs

## License

This project is licensed under the [MIT License](LICENSE).

## Links

- [Dataify Dashboard](https://dashboard.dataify.com?utm_source=github) — Get your API token
- [API Documentation](https://doc.dataify.com?utm_source=github) — Full API reference
- [MCP Server](https://mcp.dataify.com) — Model Context Protocol endpoint for AI agents
