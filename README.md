# Dataify Skills

[![License: MIT](https://img.shields.io/badge/License-MIT-blue.svg)](LICENSE)
[![Skills](https://img.shields.io/badge/Skills-79+-brightgreen.svg)](#skill-catalog)
[![Platforms](https://img.shields.io/badge/Platforms-15+-orange.svg)](#skill-catalog)

AI agent skills for [Dataify](https://dashboard.dataify.com?utm_source=github) — enabling AI agents to scrape, search, and extract structured data from 15+ platforms with 79+ ready-to-use skills.

## Features

- **79+ Pre-built Skills** — covering e-commerce, social media, search engines, job boards, and more
- **SERP API** — structured search results from Google, Bing, DuckDuckGo, Yandex across 25+ verticals
- **Web Unlocker** — bypass bot detection, CAPTCHAs, and JavaScript rendering
- **Builder API** — submit large-scale data collection tasks with async task management
- **Multi-language Docs** — English & Chinese documentation

## Installation

### One-line Install (macOS / Linux)

```bash
curl -fsSL https://raw.githubusercontent.com/dataify-server/skills/main/install.sh | bash
```

The installer will:
1. Clone the repo to `~/.dataify/skills`
2. Prompt you to enter your API token
3. Save `DATAIFY_API_TOKEN` and `DATAIFY_SKILLS_DIR` to your shell profile

### Manual Install

```bash
git clone https://github.com/dataify-server/skills.git
cd dataify_skills
export DATAIFY_API_TOKEN="YOUR_TOKEN"
```

Get your API Token at [Dataify Dashboard](https://dashboard.dataify.com?utm_source=github).

## Quick Start

### Google Search

```bash
python3 serp-skills/google/dataify-google-search/scripts/google_search.py \
  --params-json '{"q":"AI news"}'
```

### Web Unlocker

```bash
python3 dataify-web-unlocker/scripts/invoke-dataify-web-unlocker.py \
  --url "https://example.com"
```

### Amazon Product Collection

```bash
python3 amazon-skills/dataify-amazon-product/scripts/submit_amazon_product.py --help
```

## Skill Structure

Each skill contains:
- `SKILL.md` — Documentation and usage instructions (English)
- `SKILL.zh-CN.md` — Chinese documentation
- `agents/openai.yaml` — OpenAI agent configuration
- `scripts/` — Python execution scripts

Refer to the individual skill's `SKILL.md` for detailed parameters and examples.

## Repository Structure

```
dataify_skills/
├── README.md
├── dataify-web-unlocker/          # Web Unlocker
├── dataify-builder-skills/        # Generic Builder scrapers (8 skills)
├── serp-skills/                   # Search Engine Results (25 skills)
│   ├── google/                    #   Google (17 verticals)
│   ├── bing/                      #   Bing (6 verticals)
│   ├── duckduckgo/                #   DuckDuckGo
│   └── yandex/                    #   Yandex
├── amazon-skills/                 # Amazon (5 skills)
├── youtube-skills/                # YouTube (7 skills)
├── facebook-skills/               # Facebook (4 skills)
├── instagram-skills/              # Instagram (3 skills)
├── google-skills/                 # Google Maps & Shopping (3 skills)
├── reddit-skills/                 # Reddit (2 skills)
├── indeed-skills/                 # Indeed (2 skills)
├── ebay-skills/                   # eBay (1 skill)
├── walmart-skills/                # Walmart (1 skill)
└── booking-skills/                # Booking.com (1 skill)
```

## Skill Catalog

### Web Unlocker

| Skill | Description |
|-------|-------------|
| [dataify-web-unlocker](dataify-web-unlocker/) | Fetch web pages through Dataify Web Unlocker API, bypassing bot detection and CAPTCHAs |

### Builder Skills

General-purpose scrapers for popular platforms.

| Skill | Description |
|-------|-------------|
| [dataify-airbnb-product-by-searchurl](dataify-builder-skills/dataify-airbnb-product-by-searchurl/) | Scrape Airbnb product listings by search URL |
| [dataify-crunchbase-company-by-url](dataify-builder-skills/dataify-crunchbase-company-by-url/) | Scrape Crunchbase company profiles by URL |
| [dataify-github-repository-by-repo-url](dataify-builder-skills/dataify-github-repository-by-repo-url/) | Scrape GitHub repository information by URL |
| [dataify-glassdoor-company-by-url](dataify-builder-skills/dataify-glassdoor-company-by-url/) | Scrape Glassdoor company profiles by URL |
| [dataify-google-play-store-reviews-by-url](dataify-builder-skills/dataify-google-play-store-reviews-by-url/) | Scrape Google Play Store reviews by URL |
| [dataify-linkedin-company-information-by-url](dataify-builder-skills/dataify-linkedin-company-information-by-url/) | Scrape LinkedIn company information by URL |
| [dataify-tiktok-comment-by-url](dataify-builder-skills/dataify-tiktok-comment-by-url/) | Scrape TikTok comments by URL |
| [dataify-twitter-profile-by-profileurl](dataify-builder-skills/dataify-twitter-profile-by-profileurl/) | Scrape X (Twitter) profiles by URL |

### SERP Skills — Google (17)

| Skill | Description |
|-------|-------------|
| [dataify-google-search](serp-skills/google/dataify-google-search/) | Google web search results |
| [dataify-google-ai-mode](serp-skills/google/dataify-google-ai-mode/) | Google AI Mode search results |
| [dataify-google-images](serp-skills/google/dataify-google-images/) | Google Images search |
| [dataify-google-videos](serp-skills/google/dataify-google-videos/) | Google Videos search |
| [dataify-google-news](serp-skills/google/dataify-google-news/) | Google News search |
| [dataify-google-maps](serp-skills/google/dataify-google-maps/) | Google Maps search |
| [dataify-google-shopping](serp-skills/google/dataify-google-shopping/) | Google Shopping search and price comparison |
| [dataify-google-scholar](serp-skills/google/dataify-google-scholar/) | Google Scholar academic paper search |
| [dataify-google-finance](serp-skills/google/dataify-google-finance/) | Google Finance financial data |
| [dataify-google-flights](serp-skills/google/dataify-google-flights/) | Google Flights price and itinerary search |
| [dataify-google-hotels](serp-skills/google/dataify-google-hotels/) | Google Hotels price and availability search |
| [dataify-google-jobs](serp-skills/google/dataify-google-jobs/) | Google Jobs search |
| [dataify-google-lens](serp-skills/google/dataify-google-lens/) | Google Lens image search |
| [dataify-google-local](serp-skills/google/dataify-google-local/) | Google Local / nearby place search |
| [dataify-google-patents](serp-skills/google/dataify-google-patents/) | Google Patents search |
| [dataify-google-play](serp-skills/google/dataify-google-play/) | Google Play app store search |
| [dataify-google-trends](serp-skills/google/dataify-google-trends/) | Google Trends data |

### SERP Skills — Bing (6)

| Skill | Description |
|-------|-------------|
| [dataify-bing-search](serp-skills/bing/dataify-bing-search/) | Bing web search |
| [dataify-bing-images](serp-skills/bing/dataify-bing-images/) | Bing image search |
| [dataify-bing-videos](serp-skills/bing/dataify-bing-videos/) | Bing video search |
| [dataify-bing-news](serp-skills/bing/dataify-bing-news/) | Bing news search |
| [dataify-bing-shopping](serp-skills/bing/dataify-bing-shopping/) | Bing shopping and product search |
| [dataify-bing-maps](serp-skills/bing/dataify-bing-maps/) | Bing Maps location search |

### SERP Skills — Others (2)

| Skill | Description |
|-------|-------------|
| [dataify-duckduckgo-search](serp-skills/duckduckgo/dataify-duckduckgo-search/) | DuckDuckGo web search |
| [dataify-yandex-search](serp-skills/yandex/dataify-yandex-search/) | Yandex web search |

### Amazon Skills (5)

| Skill | Description |
|-------|-------------|
| [dataify-amazon-product](amazon-skills/dataify-amazon-product/) | Collect Amazon products by ASIN, URL, keyword, category, or Best Sellers |
| [dataify-amazon-comment](amazon-skills/dataify-amazon-comment/) | Collect Amazon product reviews |
| [dataify-amazon-global-product](amazon-skills/dataify-amazon-global-product/) | Collect Amazon global product information |
| [dataify-amazon-product-list](amazon-skills/dataify-amazon-product-list/) | Collect Amazon product listings |
| [dataify-amazon-seller](amazon-skills/dataify-amazon-seller/) | Collect Amazon seller information |

### YouTube Skills (7)

| Skill | Description |
|-------|-------------|
| [dataify-youtube-video-post](youtube-skills/dataify-youtube-video-post/) | Collect YouTube videos by URL, keyword, hashtag, or Explore |
| [dataify-youtube-product-by-id](youtube-skills/dataify-youtube-product-by-id/) | Collect YouTube video basic information by video ID |
| [dataify-youtube-comment-by-id](youtube-skills/dataify-youtube-comment-by-id/) | Collect YouTube comments by video ID |
| [dataify-youtube-profiles](youtube-skills/dataify-youtube-profiles/) | Collect YouTube channel profiles by URL or keyword |
| [dataify-youtube-transcript-by-id](youtube-skills/dataify-youtube-transcript-by-id/) | Extract YouTube video subtitles/transcripts by video ID |
| [dataify-youtube-video-by-url](youtube-skills/dataify-youtube-video-by-url/) | Download YouTube video files by URL |
| [dataify-youtube-audio-by-url](youtube-skills/dataify-youtube-audio-by-url/) | Download YouTube audio files by URL |

### Facebook Skills (4)

| Skill | Description |
|-------|-------------|
| [dataify-facebook-post-by-url](facebook-skills/dataify-facebook-post-by-url/) | Collect Facebook posts by URL |
| [dataify-facebook-comment-by-url](facebook-skills/dataify-facebook-comment-by-url/) | Collect Facebook post comments by URL |
| [dataify-facebook-profile-by-url](facebook-skills/dataify-facebook-profile-by-url/) | Collect Facebook profiles by URL |
| [dataify-facebook-events](facebook-skills/dataify-facebook-events/) | Collect Facebook events |

### Instagram Skills (3)

| Skill | Description |
|-------|-------------|
| [dataify-instagram-profiles](instagram-skills/dataify-instagram-profiles/) | Collect Instagram profiles by URL or keyword |
| [dataify-instagram-comment-by-posturl](instagram-skills/dataify-instagram-comment-by-posturl/) | Collect Instagram post comments by URL |
| [dataify-instagram-reels](instagram-skills/dataify-instagram-reels/) | Collect Instagram Reels information |

### Google Maps & Shopping Skills (3)

| Skill | Description |
|-------|-------------|
| [dataify-google-map-details](google-skills/dataify-google-map-details/) | Collect Google Maps place details |
| [dataify-google-maps-reviews](google-skills/dataify-google-maps-reviews/) | Collect Google Maps reviews |
| [dataify-google-shopping-keywords](google-skills/dataify-google-shopping-keywords/) | Collect Google Shopping products by keyword |

### Reddit Skills (2)

| Skill | Description |
|-------|-------------|
| [dataify-reddit-posts](reddit-skills/dataify-reddit-posts/) | Collect Reddit posts by URL, keyword, or subreddit |
| [dataify-reddit-comment-by-url](reddit-skills/dataify-reddit-comment-by-url/) | Collect Reddit post comments by URL |

### Indeed Skills (2)

| Skill | Description |
|-------|-------------|
| [dataify-indeed-job-listings](indeed-skills/dataify-indeed-job-listings/) | Collect Indeed job listings |
| [dataify-indeed-companies-info](indeed-skills/dataify-indeed-companies-info/) | Collect Indeed company information |

### E-commerce Skills (2)

| Skill | Description |
|-------|-------------|
| [dataify-ebay-products](ebay-skills/dataify-ebay-products/) | Collect eBay product information |
| [dataify-walmart-products](walmart-skills/dataify-walmart-products/) | Collect Walmart product information |

### Travel Skills (1)

| Skill | Description |
|-------|-------------|
| [dataify-booking-hotellist](booking-skills/dataify-booking-hotellist/) | Collect Booking.com hotel information |

## Adding a New Skill

Each skill follows a standard structure:

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

### Steps

1. Create a new directory under the appropriate category
2. Write `SKILL.md` with frontmatter (`name`, `description`), workflow, and parameters
3. Add `agents/openai.yaml` with tool definitions and JSON schema
4. Implement the execution script in `scripts/`
5. Test the skill end-to-end
6. Submit a Pull Request

## License

This project is licensed under the [MIT License](LICENSE).

## Links

- [Dataify Dashboard](https://dashboard.dataify.com?utm_source=github)
- [API Documentation](https://docs.dataify.com?utm_source=github)
