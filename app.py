from flask import Flask, render_template, request
import feedparser
from flask_caching import Cache
from urllib.parse import urlparse, urljoin
import email.utils
import re

app = Flask(__name__)

# Enable live reloading of templates
app.config['TEMPLATES_AUTO_RELOAD'] = True
app.jinja_env.auto_reload = True

# Cache config
cache = Cache(app, config={'CACHE_TYPE': 'SimpleCache', 'CACHE_DEFAULT_TIMEOUT': 300})

# RSS sources
RSS_FEEDS = {
    'BBC': 'http://feeds.bbci.co.uk/news/rss.xml',
    'CNN': 'http://rss.cnn.com/rss/edition.rss',
    'Reuters': 'http://feeds.reuters.com/reuters/topNews',
    'The Guardian': 'https://www.theguardian.com/world/rss',
    'NYTimes': 'https://rss.nytimes.com/services/xml/rss/nyt/HomePage.xml',
    'Al Jazeera': 'https://www.aljazeera.com/xml/rss/all.xml',
    'Google News': 'https://news.google.com/rss?hl=en-US&gl=US&ceid=US:en',
    'Fox News': 'http://feeds.foxnews.com/foxnews/latest',
    'Hacker News': 'https://hnrss.org/frontpage',
    'NPR': 'https://feeds.npr.org/1001/rss.xml'
}


def is_valid_url(url):
    parsed = urlparse(url)
    return bool(parsed.scheme) and bool(parsed.netloc)


@cache.memoize()
def get_news(feed_url):
    feed = feedparser.parse(feed_url)
    articles = []

    for entry in feed.entries[:30]:
        title = entry.title.lower()

        if any(keyword in title for keyword in ['sport', 'football', 'cricket', 'match']):
            category = 'Sports'
        elif any(keyword in title for keyword in ['tech', 'ai', 'robot', 'startup']):
            category = 'Technology'
        elif any(keyword in title for keyword in ['climate', 'biology', 'space']):
            category = 'Science'
        elif any(keyword in title for keyword in ['politic', 'election']):
            category = 'Politics'
        elif any(keyword in title for keyword in ['war', 'conflict', 'world']):
            category = 'World'
        else:
            category = 'General'

        image_url = None

        if 'media_content' in entry and entry.media_content:
            image_url = entry.media_content[0].get('url')
        elif 'media_thumbnail' in entry and entry.media_thumbnail:
            image_url = entry.media_thumbnail[0].get('url')
        elif 'summary' in entry:
            img_match = re.search(r'<img[^>]+src="([^">]+)"', entry.summary)
            if img_match:
                image_url = img_match.group(1)
        elif 'content' in entry:
            for c in entry.content:
                img_match = re.search(r'<img[^>]+src="([^">]+)"', c.value)
                if img_match:
                    image_url = img_match.group(1)
                    break

        if image_url and not image_url.startswith(('http://', 'https://')):
            base = '{uri.scheme}://{uri.netloc}'.format(uri=urlparse(feed_url))
            image_url = urljoin(base, image_url)

        if not image_url or not is_valid_url(image_url):
            image_url = 'https://via.placeholder.com/400x200?text=No+Image'

        published_raw = entry.get('published', '')
        try:
            published_dt = email.utils.parsedate_to_datetime(published_raw)
            published = published_dt.strftime('%b %d, %Y %I:%M %p')
        except:
            published = published_raw or 'No date'

        articles.append({
            'title': entry.title,
            'link': entry.link,
            'published': published,
            'category': category,
            'image_url': image_url
        })

    return articles


@app.route('/')
def index():
    source = request.args.get('source', 'BBC')
    query = request.args.get('q', '').lower()
    page = int(request.args.get('page', 1))
    category = request.args.get('category', '')
    per_page = 5

    feed_url = RSS_FEEDS.get(source)
    articles = get_news(feed_url) if feed_url else []

    if query:
        articles = [a for a in articles if query in a['title'].lower()]
    if category:
        articles = [a for a in articles if a['category'] == category]

    total = len(articles)
    total_pages = (total + per_page - 1) // per_page
    paginated = articles[(page - 1) * per_page: page * per_page]

    return render_template(
        'index.html',
        articles=paginated,
        sources=RSS_FEEDS.keys(),
        selected_source=source,
        query=query,
        selected_category=category,
        page=page,
        total_pages=total_pages,
        categories=['General', 'World', 'Technology', 'Science', 'Politics', 'Sports']
    )


if __name__ == '__main__':
    app.run(debug=True)
