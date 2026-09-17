# mainbranch-extended-feed

Apple-Podcasts-ready RSS proxy for the **MainBranch Extended** show.

The platform-generated feed lacks the iTunes tags Apple Podcasts Connect
requires (`itunes:author`, `itunes:owner`, `itunes:category`) and uses a
non-standard explicit value. `rewrite_feed.py` fetches the source feed,
injects the required tags, and writes `feed.xml`, which is served here via
GitHub Pages. A scheduled job refreshes it hourly so new episodes flow
through automatically.

- Source feed: `https://muse.ai/podcasts/feed/1311603018703153/788213e2-188d-41de-a1c3-17dd14d9129e`
- Public Apple-ready feed: `https://andreagriffiths11.github.io/mainbranch-extended-feed/feed.xml`
