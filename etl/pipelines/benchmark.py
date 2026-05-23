import os
import numpy as np
from datetime import date
from dotenv import load_dotenv

load_dotenv()

from etl.extractors.instagram import get_account_history, get_profile
from etl.transformers.normalize import normalize_post
from etl.loaders.db import get_connection

NICHES = [
    "lifestyle",
    "fashion",
    "fitness",
    "food",
    "travel",
    "beauty",
    "tech",
    "gaming",
    "finance",
    "sports",
    "entertainment",
    "music",
    "comedy",
    "education",
    "wellness",
    "parenting",
    "pets",
    "sustainability",
    "real_estate",
    "automotive",
    "photography",
    "art",
    "dance",
    "film",
    "books",
    "coffee",
    "streetwear",
    "luxury",
    "wedding",
    "architecture",
    "outdoors",
    "skincare",
    "haircare",
    "mensfashion",
    "plus_size_fashion",
    "vegan",
    "yoga",
    "running",
    "esports",
    "kpop",
]

NICHE_ACCOUNTS = {
    "lifestyle": [
        "humansofny", "natgeo", "theeverygirl", "refinery29",
        "whowhatwear", "mydomaine", "apartmenttherapy", "byrdie",
        "goop", "wellandgood"
    ],
    "fashion": [
        "zara", "hm", "asos", "forever21", "fashionnova",
        "voguemagazine", "harpersbazaarus", "elleusa",
        "nordstrom", "net_a_porter"
    ],
    "fitness": [
        "nike", "gymshark", "lululemon", "underarmour", "adidas",
        "kayla_itsines", "joeheaney_", "natacha.oceane",
        "cbum", "chrisandruth"
    ],
    "food": [
        "tasty", "buzzfeedtasty", "bonappetitmag", "foodnetwork",
        "thefeedfeed", "minimalistbaker", "halfbakedharvest",
        "pinchofyum", "seriouseats", "delish"
    ],
    "travel": [
        "lonelyplanet", "airbnb", "natgeotravel", "travelandleisure",
        "condenasttraveler", "beautifuldestinations", "earthpix",
        "touropia", "expertvagabond", "thebucketlistfamily"
    ],
    "beauty": [
        "fentybeauty", "glossier", "urbandecay", "charlottetilbury",
        "nyxcosmetics", "toofaced", "maccosmetics", "narsissist",
        "makeupbymario", "patmcgrathreal"
    ],
    "tech": [
        "nasa", "spacex", "apple", "google", "microsoft",
        "tesla", "mkbhd", "unboxtherapy", "verge", "techcrunch"
    ],
    "gaming": [
        "playstation", "xbox", "nintendo", "epicgames", "riotgames",
        "twitch", "steam", "ign", "gamespot", "kotaku"
    ],
    "finance": [
        "nerdwallet", "investopedia", "themotleyfool", "grahamstephan",
        "andrei_jikh", "minoritymindset", "financialtimes",
        "bloomberg", "forbes", "wsj"
    ],
    "sports": [
        "nba", "espn", "nfl", "mlb", "nhl",
        "bleacherreport", "cbssports", "sportscenter",
        "laliga", "championsleague"
    ],
    "entertainment": [
        "people", "entertainmentweekly", "variety", "hollywoodreporter",
        "tmz", "e.news", "usweekly", "eonline",
        "complexmag", "pitchfork"
    ],
    "music": [
        "spotify", "applemusic", "billboard", "rollingstone",
        "pitchfork", "recordingacademy", "genius",
        "xxlmag", "hotnewhiphop", "stereogum"
    ],
    "comedy": [
        "9gag", "ladbible", "unilad", "thechive",
        "fuckjerry", "daquan", "shitheadsteve",
        "tank.sinatra", "pubity", "commentawards"
    ],
    "education": [
        "ted", "natgeo", "bbcearth", "discoverychannel",
        "howstuffworks", "kurzgesagt", "vsauce",
        "crashcourse", "smartereveryday", "veritasium"
    ],
    "wellness": [
        "mindbodygreen", "wellandgood", "goop", "headspace",
        "calm", "drmarkhyman", "drwillcole",
        "positivelypositive", "dailyom", "tinybuddha"
    ],
    "parenting": [
        "scarymommy", "whattoexpect", "babycenter", "thebump",
        "modernmom", "fatherly", "dadandburied",
        "mothermag", "parents", "romper"
    ],
    "pets": [
        "the_dodo", "dogsofinsta", "cats_of_instagram", "petco",
        "petsmart", "dogfoodadvisor", "akcdoglovers",
        "barkbox", "iheartdogs", "catsvsbdogs2"
    ],
    "sustainability": [
        "patagonia", "greenpeace", "wwf", "earthday",
        "zerowastehome", "sustainablyvegan", "goingzerowaste",
        "ecowatch", "treehugger", "sustainableish"
    ],
    "real_estate": [
        "zillow", "redfin", "realtor", "mansionglobal",
        "architecturaldigest", "apartmenttherapy", "theagencyre",
        "sothebysrealty", "compassrealestate", "luxuryportfolio"
    ],
    "automotive": [
        "tesla", "bmw", "mercedesbenz", "porsche", "ferrari",
        "lamborghini", "topgear", "motortrend",
        "caranddriver", "roadandtrack"
    ],
    "photography": [
        "natgeo", "500px", "magnum_photos", "lensculture",
        "aphotoeditor", "worldpressphoto", "nikonusa",
        "canonusa", "fujifilmx_us", "hasselblad"
    ],
    "art": [
        "museumofmodernart", "metmuseum", "guggenheim", "tate",
        "artsy", "saatchiart", "artforum",
        "juxtapozmagazine", "hypebeast", "designboom"
    ],
    "dance": [
        "worldofdance", "dancemagazine", "nbcworldofdance",
        "alvin_ailey", "lizzo", "jlo",
        "tiktok_dance", "1milliondance", "mileyofficial", "besperon"
    ],
    "film": [
        "a24", "pitchfork", "variety", "hollywoodreporter",
        "empiremagazine", "screendaily", "deadline",
        "simonandschuster", "criterion", "filmstruck"
    ],
    "books": [
        "penguinrandomhouse", "simonandschuster", "harpercollins",
        "oprahsbookclub", "bookofthemonth", "goodreads",
        "barnesandnoble", "powells", "literaryhub", "electricliterature"
    ],
    "coffee": [
        "starbucks", "bluebottlecoffee", "intelligentsiacoffee",
        "stumptowncoffee", "deathnushcoffee", "lavazzausa",
        "nespresso", "keurig", "coffeeaddict", "dailycortado"
    ],
    "streetwear": [
        "supremenewyork", "offwhite", "palace", "bape_japan",
        "hypebeast", "highsnobiety", "complexmag",
        "kith", "undefeated", "sneakernews"
    ],
    "luxury": [
        "louisvuitton", "gucci", "chanel", "hermes",
        "prada", "dior", "tiffanyandco",
        "cartier", "rolex", "bulgari"
    ],
    "wedding": [
        "brides", "marthastewartweddings", "theknot", "stylemepretty",
        "greenweddingshoes", "junebugweddings", "oncewed",
        "weddingwire", "magnoliarouge", "100layercake"
    ],
    "architecture": [
        "architecturaldigest", "dezeen", "archdaily", "architectural_record",
        "frameweb", "wallpapermag", "domusweb",
        "designmilk", "curbed", "architizer"
    ],
    "outdoors": [
        "redbull", "patagonia", "thenorthface", "rei",
        "natgeo", "outsidemagazine", "backpacker",
        "climbingmagazine", "trailrunnermag", "bikemag"
    ],
    "skincare": [
        "cerave", "theordinary", "paulaschoice", "skinceuticals",
        "tatcha", "drbarbarasturm", "peterthomasroth",
        "olay", "neutrogena", "clinique"
    ],
    "haircare": [
        "olaplex", "moroccanoil", "kerastase_official", "redken",
        "wella", "pantene", "garnier",
        "naturalhairdaily", "curlynikki", "thenaturalhaircommunity"
    ],
    "mensfashion": [
        "mrporter", "gq", "esquire", "hypebeast",
        "highsnobiety", "fashionbeans", "dmarge",
        "complex", "selectism", "theidleman"
    ],
    "plus_size_fashion": [
        "torrid", "eloquii", "addition_elle", "navabi",
        "gwynniebee", "plussize_fashion", "curvyoutfits",
        "thecurvyfashionista", "garnerchic", "stylemeplus"
    ],
    "vegan": [
        "veganfoodshare", "veganfoodlovers", "minimalistbaker",
        "ohsheglows", "thugkitchen", "veganricha",
        "schoolofveganism", "livekindly", "plantbasednews", "peta"
    ],
    "yoga": [
        "yogajournal", "yogainspiration", "kinoyoga",
        "adrienelouise", "mynameisjessamyn", "yoga_girl",
        "beachyogagirl", "patrickbeach", "dylanwerneryoga", "corepower_yoga"
    ],
    "running": [
        "nike", "adidas", "asics", "newbalance",
        "runnersworld", "runnerscommunity", "runningmagazine",
        "irunthisbody", "runtothefinish", "therunexperience"
    ],
    "esports": [
        "esl_csgo", "riotgames", "blizzard_ent", "faceit",
        "eslgaming", "dreamhack", "pgl_esports",
        "fnatic", "teamliquid", "cloud9"
    ],
    "kpop": [
        "bts.bighitofficial", "blackpinkofficial", "smtown",
        "jypentertainment", "pledis_17", "yg_entertainment",
        "twicetagram", "weareone.exo", "nct_dream", "aespa_official"
    ],
}

def run():
    print(f"\n[benchmark] Starting benchmark pipeline — {date.today()}")
    week_of = date.today()

    for niche, accounts in NICHE_ACCOUNTS.items():
        print(f"\n[benchmark] Niche: {niche}")
        all_posts = []

        for handle in accounts:
            print(f"  Fetching @{handle}...")
            try:
                profile = get_profile(handle)
                raw_posts = get_account_history(handle, limit=25)
                normalized = []

                for raw in raw_posts:
                    raw["handle"] = handle
                    raw["platform"] = "instagram"
                    post = normalize_post(raw)
                    post["followers"] = profile.get("followers", 1)
                    normalized.append(post)

                all_posts.extend(normalized)
                print(f"  Got {len(normalized)} posts from @{handle}")
            except Exception as e:
                print(f"  Skipping @{handle}: {e}")
                continue

        if not all_posts:
            print(f"  No posts collected for {niche}, skipping")
            continue

        _compute_and_store(all_posts, "instagram", niche, week_of)

    print(f"\n[benchmark] Done.")

def _compute_and_store(posts: list, platform: str, niche: str, week_of: date):
    by_content_type = {}
    for post in posts:
        ct = post.get("content_type", "image")
        if ct not in by_content_type:
            by_content_type[ct] = []
        by_content_type[ct].append(post.get("engagement_rate", 0))

    conn = get_connection()
    cur = conn.cursor()

    for content_type, rates in by_content_type.items():
        if not rates:
            continue

        median_er = float(np.median(rates))
        p75_er = float(np.percentile(rates, 75))
        median_likes = float(np.median([
            p.get("likes", 0) for p in posts
            if p.get("content_type") == content_type
        ]))

        print(f"  [{content_type}] median={median_er:.2f}% p75={p75_er:.2f}%")

        cur.execute("""
            INSERT INTO benchmarks (
                platform, niche, content_type,
                median_engagement_rate, median_likes,
                p75_engagement_rate, week_of
            )
            VALUES (%s, %s, %s, %s, %s, %s, %s)
            ON CONFLICT (platform, niche, content_type, week_of)
            DO UPDATE SET
                median_engagement_rate = EXCLUDED.median_engagement_rate,
                median_likes = EXCLUDED.median_likes,
                p75_engagement_rate = EXCLUDED.p75_engagement_rate
        """, (
            platform,
            niche,
            content_type,
            median_er,
            median_likes,
            p75_er,
            week_of,
        ))

    conn.commit()
    cur.close()
    conn.close()