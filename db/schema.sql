CREATE EXTENSION IF NOT EXISTS "uuid-ossp";

CREATE TABLE accounts (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    platform VARCHAR(20) NOT NULL,
    handle VARCHAR(100) NOT NULL,
    niche VARCHAR(50),
    first_fetched_at TIMESTAMP,
    last_fetched_at TIMESTAMP,
    UNIQUE(platform, handle)
);

CREATE TABLE posts (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    account_id UUID REFERENCES accounts(id) ON DELETE CASCADE,
    platform_post_id VARCHAR(200) UNIQUE,
    post_url TEXT,
    content_type VARCHAR(20),
    caption TEXT,
    likes INTEGER DEFAULT 0,
    comments INTEGER DEFAULT 0,
    shares INTEGER DEFAULT 0,
    engagement_rate FLOAT,
    posted_at TIMESTAMP,
    fetched_at TIMESTAMP DEFAULT NOW(),
    raw_data JSONB
);

CREATE TABLE account_snapshots (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    account_id UUID REFERENCES accounts(id) ON DELETE CASCADE,
    followers INTEGER,
    following INTEGER,
    post_count INTEGER,
    captured_at TIMESTAMP DEFAULT NOW()
);

CREATE TABLE benchmarks (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    platform VARCHAR(20) NOT NULL,
    niche VARCHAR(50) NOT NULL,
    content_type VARCHAR(20),
    median_engagement_rate FLOAT,
    median_likes FLOAT,
    p75_engagement_rate FLOAT,
    week_of DATE NOT NULL,
    UNIQUE(platform, niche, content_type, week_of)
);

CREATE TABLE analyses (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    post_id UUID REFERENCES posts(id) ON DELETE CASCADE,
    score_timing FLOAT,
    score_format FLOAT,
    score_hook FLOAT,
    score_topic FLOAT,
    score_velocity FLOAT,
    overall_score FLOAT,
    ai_explanation TEXT,
    created_at TIMESTAMP DEFAULT NOW()
);

CREATE INDEX idx_posts_account_id ON posts(account_id);
CREATE INDEX idx_posts_posted_at ON posts(posted_at);
CREATE INDEX idx_analyses_post_id ON analyses(post_id);
CREATE INDEX idx_benchmarks_lookup ON benchmarks(platform, niche, content_type, week_of);