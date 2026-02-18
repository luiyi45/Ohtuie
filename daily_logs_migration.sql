-- Migration to add daily_logs table

CREATE TABLE public.daily_logs (
    id UUID DEFAULT uuid_generate_v4() PRIMARY KEY,
    user_id UUID NOT NULL REFERENCES public.users(id) ON DELETE CASCADE,
    date DATE NOT NULL DEFAULT CURRENT_DATE,
    flow VARCHAR(20),
    symptoms JSONB DEFAULT '[]'::jsonb,
    moods JSONB DEFAULT '[]'::jsonb,
    notes TEXT,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    CONSTRAINT unique_user_date UNIQUE (user_id, date)
);

-- Index for faster lookups by user and date
CREATE INDEX idx_daily_logs_user_date ON public.daily_logs(user_id, date);
