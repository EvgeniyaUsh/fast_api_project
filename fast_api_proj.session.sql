CREATE TABLE user_settings (
    user_id UUID PRIMARY KEY,
    settings JSONB NOT NULL,
    updated_at TIMESTAMP DEFAULT now()
);
