# srapi-py

A Python client for the [speedrun.com REST API v1](https://github.com/speedruncomorg/api/tree/master/version1).

Inspired by the Go client [sgt-kabukiman/srapi](https://github.com/sgt-kabukiman/srapi).

---

## Features

- Full coverage of the speedrun.com API v1 — games, runs, users, categories, levels, leaderboards, series, variables, and more
- Lazy pagination — `Collection` objects iterate across all pages automatically
- Embedded resources — request related data in a single API call via `embed=`
- Lazy loading — resource methods (e.g. `run.game()`) use embedded data when available and fall back to a network call
- Authentication support for notifications, profile, and run submission
- Clean dataclass-based models with type hints throughout
- Single dependency: [`requests`](https://docs.python-requests.org/)

---

## Installation

**From source (development):**

```bash
git clone https://github.com/xS2RT/srapi-py.git
cd srapi-py
pip install -e .
```

**Requirements:** Python 3.8+, `requests >= 2.28.0`

---

## Quick Start

```python
import srapi

client = srapi.Client()

game = client.game("eldenring")
categories = list(client.game_categories(game.id))

# Categories: Any%, Defeat Consort, Two Gods, All Remembrances, ...
# Each category has subcategories (Zips, Unrestricted, Restricted, Glitchless)
# implemented as variables in the API.

any_pct = next(c for c in categories if c.name == "Any%")

# Find the subcategory variable and its value IDs
variables  = list(client.category_variables(any_pct.id))
subcat_var = next(v for v in variables if "Subcategor" in v.name)
glitchless = next(v for v in subcat_var.values.values() if v.label == "Glitchless")

# Fetch the Any% Glitchless leaderboard — top 5
lb = client.leaderboard(
    game.id,
    any_pct.id,
    top=5,
    variables={subcat_var.id: glitchless.id},
)
for entry in lb.runs:
    print(f"#{entry.place} {entry.run.times.primary}")

# Iterate all verified Any% Glitchless runs (auto-paginates)
for run in client.runs(game=game.id, category=any_pct.id, status="verified"):
    if run.values.get(subcat_var.id) == glitchless.id:
        print(run.date, run.times.primary)
```

---

## Usage

### Creating a client

```python
import srapi

# Anonymous — works for all public endpoints
client = srapi.Client()

# Authenticated — required for profile, notifications, run submission
client = srapi.Client(api_key="your_api_key_here")

# Custom User-Agent
client = srapi.Client(user_agent="my-tool/1.0")
```

Your API key is on your speedrun.com profile under **Settings → API Key**.

---

### Games

```python
# Fetch by ID or abbreviation
game = client.game("eldenring")
game = client.game("nd28z0ed")

# List games with filters
for game in client.games(platform="n64", released=1996):
    print(game.name)

# Fetch with embedded categories and levels (saves extra requests)
game = client.game("eldenring", embed=["categories", "levels"])
cats = game.categories()   # uses embedded data — no network call

# Related data
categories = client.game_categories(game.id)
levels     = client.game_levels(game.id)
variables  = client.game_variables(game.id)
records    = client.game_records(game.id, top=3)
derived    = client.game_derived_games(game.id)
```

---

### Runs

```python
# Fetch a single run
run = client.run("run_id")

# Filter runs
for run in client.runs(game="nd28z0ed", status="verified", sort_by="date", direction="desc"):
    print(run.date, run.times.primary)

# Other filters: user, guest, examiner, level, category, platform, region, emulated
for run in client.runs(user="user_id", game="nd28z0ed"):
    print(run.times.primary)

# Embed related data to avoid extra requests
run = client.run("run_id", embed=["game", "category", "players"])
game     = run.game()      # uses embedded data
category = run.category()  # uses embedded data

# Run times
print(run.times.primary)          # Duration object
print(run.times.primary.seconds)  # float seconds
print(run.times.realtime)
print(run.times.ingame)

# Submit a run (requires API key)
new_run = client.submit_run(
    category="category_id",
    times={"realtime": "PT3M42S"},
    platform="platform_id",
    video="https://youtu.be/...",
    variables={"var_id": "value_id"},
)

# Moderator actions (requires API key + moderator role)
client.update_run_status("run_id", "verified")
client.update_run_status("run_id", "rejected", reason="No video proof")
client.delete_run("run_id")
```

---

### Users

```python
# Fetch by ID or username
user = client.user("S2RT")
print(user.name, user.role, user.twitch)

# Search users
for user in client.users(name="S2R"):
    print(user.name)

# Personal bests
pbs = client.user_personal_bests(user.id, game="nd28z0ed")
for pb in pbs:
    print(f"#{pb.place} {pb.run.times.primary}")
```

---

### Categories & Levels

```python
category = client.category("category_id")

# Variables and records
variables = client.category_variables(category.id)
records   = client.category_records(category.id, top=5)

# Or call methods directly on the object
variables = category.variables()
records   = category.records(top=5)

level = client.level("level_id")
cats  = level.categories()
vars_ = level.variables()
recs  = level.records(top=3)
```

---

### Leaderboards

```python
# Full-game leaderboard (all subcategories mixed)
lb = client.leaderboard(game="nd28z0ed", category="02qr00pk", top=10)

# Filter to a specific subcategory — e.g. Any% Zips
# Variable id="7891zr5n", Zips value id="10vmz22l"
lb = client.leaderboard(
    game="nd28z0ed",
    category="02qr00pk",
    top=10,
    variables={"7891zr5n": "10vmz22l"},
)

for entry in lb.runs:
    print(f"#{entry.place} {entry.run.times.primary}")

# Individual level leaderboard
lb = client.level_leaderboard(
    game="game_id",
    level="level_id",
    category="category_id",
    top=5,
)
```

---

### Subcategories

On speedrun.com, what appears in the UI as subcategory tabs — for example **Zips | Unrestricted | Restricted | Glitchless** under Elden Ring's Any% — are implemented in the API as **variables** on a category. There is no separate subcategory endpoint; you work with them through the variables system.

```python
game     = client.game("eldenring")
any_pct  = next(c for c in client.game_categories(game.id) if c.name == "Any%")

# Fetch the category's variables
variables = list(client.category_variables(any_pct.id))

# Elden Ring Any% variables:
#   "Version"             — patch version (1.04, 1.07, ...)
#   "Route"               — Wrong Warp, Death's Poker, Bloodhound's Fang, ...
#   "Any% - Subcategories"— Zips, Unrestricted, Restricted, Glitchless

subcat_var = next(v for v in variables if "Subcategor" in v.name)
print(subcat_var.name)
# Any% - Subcategories

for value_id, value in subcat_var.values.items():
    print(value_id, value.label)
# 10vmz22l  Zips
# rqv5por1  Unrestricted
# 5le7rzm1  Restricted
# qj740p3q  Glitchless

# Look up a specific subcategory value by label
zips = next(v for v in subcat_var.values.values() if v.label == "Zips")

# Leaderboard for Any% Zips
lb = client.leaderboard(
    game.id,
    any_pct.id,
    top=10,
    variables={subcat_var.id: zips.id},
)

# Filter runs to a specific subcategory
for run in client.runs(game=game.id, category=any_pct.id, status="verified"):
    if run.values.get(subcat_var.id) == zips.id:
        print(run.times.primary)

# The same pattern applies to every category:
# Defeat Consort, Two Gods, All Remembrances, etc. each have their own
for cat in client.game_categories(game.id):
    cat_vars = list(client.category_variables(cat.id))
    sub = next((v for v in cat_vars if "Subcategor" in v.name), None)
    if sub:
        labels = [v.label for v in sub.values.values()]
        print(f"{cat.name}: {labels}")
# Any%: ['Zips', 'Unrestricted', 'Restricted', 'Glitchless']
# Defeat Consort: ['Unrestricted', 'Restricted', 'Glitchless']
# Two Gods: ['Unrestricted', 'Restricted', 'Glitchless']
# ...
```

---

### Series

```python
series = client.series("mario")
for game in series.games():
    print(game.name)

for series in client.series_list(name="zelda"):
    print(series.name)
```

---

### Notifications & Profile

Both require an API key.

```python
client = srapi.Client(api_key="your_key")

me = client.profile()
print(me.name, me.role)

for notif in client.notifications():
    print(f"[{notif.status}] {notif.text}")
```

---

### Other resources

```python
# Platforms, regions
for plat in client.platforms(sort_by="name"):
    print(plat.name, plat.released)

region = client.region("region_id")

# Variables
var = client.variable("var_id")
for value_id, value in var.values.items():
    print(value_id, value.label)

# Guests (unregistered runners)
guest = client.guest("SomeGuest")
for run in guest.runs():
    print(run.times.primary)

# Engines, developers, publishers, gametypes, genres
for engine in client.engines():
    print(engine.name)
```

---

### Pagination — `Collection`

Methods that return multiple resources return a `Collection[T]`, which lazily fetches pages as you iterate.

```python
runs = client.runs(game="nd28z0ed")  # no request yet

for run in runs:           # pages are fetched on demand
    process(run)

first = runs.first()       # fetches only the first page
all_runs = runs.all()      # fetches all pages into a list
```

---

### Embedding

Use `embed=` to include related resources in a single request instead of fetching them separately.

```python
# Without embed: run.game() makes an extra GET /games/{id} request
run = client.run("run_id")
game = run.game()   # network call

# With embed: no extra request
run = client.run("run_id", embed=["game", "category", "players"])
game = run.game()   # returns immediately from embedded data
```

Available embeds vary per endpoint. Common ones:

| Endpoint | Embeds |
|---|---|
| `game()` | `categories`, `levels`, `moderators`, `platforms`, `regions`, `genres`, `developers`, `publishers` |
| `run()` / `runs()` | `game`, `category`, `level`, `platform`, `region`, `players` |
| `leaderboard()` | `game`, `category`, `level`, `platform`, `region`, `variables`, `players` |

---

### Duration

Run times are returned as `Duration` objects.

```python
t = run.times.primary
print(t)            # "1:35:28.000"
print(t.seconds)    # 5728.0  (float)
print(t.to_timedelta())  # datetime.timedelta
```

---

## Resource reference

| Class | Key fields |
|---|---|
| `Game` | `id`, `name`, `abbreviation`, `weblink`, `release_date`, `ruleset`, `platform_ids`, `moderators` |
| `Run` | `id`, `game_id`, `category_id`, `level_id`, `times`, `system`, `status`, `players`, `values` |
| `User` | `id`, `name`, `role`, `signup`, `twitch`, `youtube`, `location` |
| `Category` | `id`, `name`, `type`, `players`, `miscellaneous` |
| `Level` | `id`, `name`, `weblink`, `rules` |
| `Leaderboard` | `game_id`, `category_id`, `timing`, `runs` (list of `LeaderboardEntry`) |
| `LeaderboardEntry` | `place`, `run` |
| `Series` | `id`, `name`, `abbreviation`, `moderators` |
| `Variable` | `id`, `name`, `scope`, `mandatory`, `values` (dict of `VariableValue`) |
| `VariableValue` | `id`, `label`, `rules` |
| `Notification` | `id`, `status`, `text`, `item`, `created` |
| `Platform` | `id`, `name`, `released` |
| `Region` | `id`, `name` |
| `Guest` | `name` |
| `Duration` | `seconds`, `to_timedelta()` |

---

## Error handling

All errors raise `srapi.SrapiError`.

```python
try:
    game = client.game("doesnotexist")
except srapi.SrapiError as e:
    print(e.status_code)  # e.g. 404
    print(e.url)
    print(str(e))
```

---

## Contributors

| | Name | Role |
|---|---|---|
| | **xS2RT** | Author |
| 🤖 | **[Claude](https://claude.ai)** (Anthropic) | Built with Claude Code |

---

## License

MIT — see [LICENSE](LICENSE).
