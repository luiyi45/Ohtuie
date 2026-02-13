-- ==========================================
-- SCRIPT DE INICIALIZACIÓN COMPLETA - OHTUIE
-- ==========================================

-- 1. Habilitar extensiones necesarias
CREATE EXTENSION IF NOT EXISTS "uuid-ossp";

-- 2. Crear Tabla de Usuarios
CREATE TABLE IF NOT EXISTS public.users (
    id UUID DEFAULT uuid_generate_v4() PRIMARY KEY,
    email VARCHAR(255) NOT NULL UNIQUE,
    hashed_password VARCHAR(255) NOT NULL,
    full_name VARCHAR(100),
    role VARCHAR(20) NOT NULL CHECK (role IN ('admin', 'user')),
    is_active BOOLEAN DEFAULT TRUE,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
);

-- 3. Crear Tabla de Ciclos
CREATE TABLE IF NOT EXISTS public.cycles (
    id UUID DEFAULT uuid_generate_v4() PRIMARY KEY,
    user_id UUID NOT NULL REFERENCES public.users(id) ON DELETE CASCADE,
    start_date DATE NOT NULL,
    end_date DATE,
    notes TEXT,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
);

-- 4. Crear Índices
CREATE INDEX IF NOT EXISTS idx_cycles_user_id ON public.cycles(user_id);

-- 5. Insertar Usuario Administrador por Defecto
-- Email: admin@ohtuie.com
-- Password: admin
INSERT INTO public.users (
    email,
    hashed_password,
    full_name,
    role,
    is_active,
    created_at,
    updated_at
)
VALUES (
    'admin@ohtuie.com',
    '$2b$12$EixZaYVK1fsbw1ZfbX3OXePaWxn96p36WQoeG6Lruj3vjPGga31lW', -- Hash de "admin"
    'System Admin',
    'admin',
    true,
    NOW(),
    NOW()
)
ON CONFLICT (email) DO NOTHING;
