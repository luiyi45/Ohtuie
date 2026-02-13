-- Script para crear el usuario administrador por defecto

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
    -- Hash para la contraseña "admin"
    '$2b$12$EixZaYVK1fsbw1ZfbX3OXePaWxn96p36WQoeG6Lruj3vjPGga31lW',
    'System Admin',
    'admin',
    true,
    NOW(),
    NOW()
)
ON CONFLICT (email) DO NOTHING;
