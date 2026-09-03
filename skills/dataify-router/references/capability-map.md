# Dataify capability map

| User need | Capability | Skill pattern | Execution |
| --- | --- | --- | --- |
| General, news, image, video, shopping, travel, jobs, maps, scholarly or patent discovery | Search results | `serp-*` | Synchronous |
| Render or unlock a known webpage | Web content | `dataify-web-unlocker` | Synchronous |
| Marketplace product, seller, price or review records | Structured commerce data | `scraper-amazon-*`, `scraper-ebay-*`, `scraper-walmart-*` | Usually asynchronous |
| Social profiles, posts, comments or media | Structured social data | Matching `scraper-*` platform skill | Usually asynchronous |
| Company, repository, app, job or travel records | Structured vertical data | Matching `scraper-*` skill | Usually asynchronous |
| Competitor, pricing, review, hiring, battlecard or market-landscape decision | Competitive intelligence | `dataify-competitive-intelligence` | Multi-source synthesis |
| Comparable offers, channel prices or recurring price changes | Price intelligence | `dataify-price-intelligence` | Multi-source synthesis |
| Cross-source complaints, praise, sentiment or product feedback themes | Review intelligence | `dataify-review-intelligence` | Multi-source synthesis |
| ICP company discovery, qualification and evidence-based ranking | Lead intelligence | `dataify-lead-intelligence` | Multi-source synthesis |
| Cross-source brand mentions, issue detection or reputation monitoring | Brand monitoring | `dataify-brand-monitoring` | Multi-source synthesis |
| Check or retrieve a submitted Builder job | Task lifecycle | `dataify-task-operations` | Asynchronous |

Choose by desired output, not merely by keywords. Search discovers links; structured scrapers return platform-specific records; Web Unlocker returns page content. Route broad competitor strategy to Competitive Intelligence; route price, customer feedback, prospect-company qualification, and brand reputation decisions to their dedicated business Skill. A request for one platform's raw records stays with the platform Skill.
