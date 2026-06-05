# Dataify Amazon Product 中文版

## 采集模式

| Mode | Use for | Builder `spider_id` |
| --- | --- | --- |
| `asin` | Collect product details by ASIN. Amazon product URLs can be accepted and converted to ASINs. | `amazon_product_by-asin` |
| `url` | Collect product details by one or more Amazon product URLs and a zip code. | `amazon_product_by-url` |
| `keyword` | Collect Amazon keyword search results. | `amazon_product_by-keywords` |
| `category-url` | Collect Amazon category listing results from a category URL. | `amazon_product_by-category-url` |
| `best-sellers-url` | Collect Amazon Best Sellers listing results from a Best Sellers URL. | `amazon_product_by-best-sellers` |

## API TOKEN 处理

使用 `DATAIFY_API_TOKEN` 作为长期保存的 token 名称。

- 如果用户在请求中提供了 token，则使用该 token。
- 如果未提供 token，先检查环境变量中是否已保存 `DATAIFY_API_TOKEN`。
- 如果本地已保存 `DATAIFY_API_TOKEN`，则直接使用。
- 如果没有可用的 token，提示用户前往 [Dataify](https://dashboard.dataify.com?utm_source=skill) 获取 API TOKEN。
- 没有 token 不要调用 Builder 接口。

## 设置 DATAIFY_API_TOKEN

推荐使用永久环境变量，而不是只在当前终端临时设置。

Windows PowerShell，当前用户永久设置：

```powershell
[Environment]::SetEnvironmentVariable("DATAIFY_API_TOKEN", "your_token_here", "User")
```

然后重新打开 PowerShell。如果当前会话也要立即生效，再执行：

```powershell
$env:DATAIFY_API_TOKEN = "your_token_here"
```

macOS 或 Linux，bash 永久设置：

```bash
echo 'export DATAIFY_API_TOKEN="your_token_here"' >> ~/.bashrc
source ~/.bashrc
```

macOS 或 Linux，zsh 永久设置：

```bash
echo 'export DATAIFY_API_TOKEN="your_token_here"' >> ~/.zshrc
source ~/.zshrc
```
## 核心工作流程

1. 从用户请求中识别采集模式。
2. 提交前，以 Markdown 表格展示必填参数、可选参数和默认值。
3. 询问用户是否需要修改参数。
4. 规范化并验证最终参数值。
5. 获取 Dataify token（用户提供或已保存的 `DATAIFY_API_TOKEN`）。
6. 如果没有 token，提示用户前往 [Dataify](https://dashboard.dataify.com?utm_source=skill) 获取。
7. 提交 Builder 请求创建任务。
8. 从响应中读取 `data.task_id`。
9. 提交成功后停止，告诉用户前往 [Dataify](https://dashboard.dataify.com?utm_source=skill) 查看或管理结果。

## 参数清单

### ASIN

| Field | Required | Default | Notes |
| --- | --- | --- | --- |
| `asin` | Yes | No default | One or more ASINs. Amazon product URLs can be accepted and converted to ASINs. |
| `file_name` | No | `{{TasksID}}` | Builder form field. Can be changed by the user. |

Submit multiple ASINs as an array of objects, for example `[{"asin":"B0BZYCJK89"}]`.

### Product URL

| Field | Required | Default | Notes |
| --- | --- | --- | --- |
| `url` | Yes | No default | One or more complete Amazon product URLs. |
| `zip_code` | Yes | No default | Zip code used for each Amazon URL, for example `94107`. |
| `file_name` | No | `{{TasksID}}` | Builder form field. Can be changed by the user. |

Submit multiple URLs as an array of objects, for example `[{"url":"https://www.amazon.com/.../dp/B0BRXPR726","zip_code":"94107"}]`.

### Keyword

| Field | Required | Default | Notes |
| --- | --- | --- | --- |
| `keyword` | Yes | No default | Amazon search keyword. |
| `page_turning` | No | `2` | Integer greater than or equal to `1`. |
| `lowest_price` | No | `10` | Lowest price filter. |
| `highest_price` | No | `50` | Highest price filter. |
| `file_name` | No | `{{TasksID}}` | Builder form field. Can be changed by the user. |

Require `lowest_price <= highest_price`.

### Category URL

| Field | Required | Default | Notes |
| --- | --- | --- | --- |
| `url` | Yes | No default | Amazon category URL. |
| `page_turning` | Yes | No default | Integer greater than or equal to `1`. |
| `sort_by` | No | `Best Sellers` | Dropdown-style option. |
| `file_name` | No | `{{TasksID}}` | Builder form field. Can be changed by the user. |

Show all `sort_by` options as a Markdown table with both `Label` and `Value` columns before asking the user to choose.

| Label | Value |
| --- | --- |
| `Best Sellers` | `Best Sellers` |
| `Newest Arrivals` | `Newest Arrivals` |
| `Avg. Customer Review` | `Avg. Customer Review` |
| `Price: High to Low` | `Price: High to Low` |
| `Price: Low to High` | `Price: Low to High` |
| `Featured` | `Featured` |

Accepted `sort_by` display values and submitted values:

- best sellers or `Best Sellers` -> `Best Sellers`
- newest arrivals or `Newest Arrivals` -> `Newest Arrivals`
- average customer review or `Avg. Customer Review` -> `Avg. Customer Review`
- price high to low or `Price: High to Low` -> `Price: High to Low`
- price low to high or `Price: Low to High` -> `Price: Low to High`
- featured recommendations or `Featured` -> `Featured`

### Best Sellers URL

| Field | Required | Default | Notes |
| --- | --- | --- | --- |
| `url` | Yes | No default | Amazon Best Sellers category URL. |
| `page_turning` | Yes | No default | Integer greater than or equal to `1`. |
| `file_name` | No | `{{TasksID}}` | Builder form field. Can be changed by the user. |

## 脚本用法

使用 Python 运行：

```bash
python3 scripts/submit_amazon_product.py --help
```

## 注意事项

- 提交成功后不要下载结果文件，告诉用户前往 [Dataify](https://dashboard.dataify.com?utm_source=skill) 查看。
- 始终以 Markdown 表格展示参数确认，不要使用纯文本或项目列表。
- 如果用户已经提供了部分参数，在表格中显示这些值，只询问是否修改剩余参数。
