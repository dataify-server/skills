# Dataify capability map

| User need | Capability | Skill pattern | Execution |
| --- | --- | --- | --- |
| General, news, image, video, shopping, travel, jobs, maps, scholarly or patent discovery | Search results | `serp-*` | Synchronous |
| Render or unlock a known webpage | Web content | `dataify-web-unlocker` | Synchronous |
| Marketplace product, seller, price or review records | Structured commerce data | `scraper-amazon-*`, `scraper-ebay-*`, `scraper-walmart-*` | Usually asynchronous |
| Social profiles, posts, comments or media | Structured social data | Matching `scraper-*` platform skill | Usually asynchronous |
| Company, repository, app, job or travel records | Structured vertical data | Matching `scraper-*` skill | Usually asynchronous |
| Check or retrieve a submitted Builder job | Task lifecycle | `dataify-task-operations` | Asynchronous |

Choose by desired output, not merely by keywords. Search discovers links; structured scrapers return platform-specific records; Web Unlocker returns page content.

