// Deben coincidir con los esquemas de backend/app/schemas/user.py y auth.py

export type Role = 'client' | 'admin'

// UserRead
export type User = {
  id: number
  email: string
  full_name: string
  role: Role
  created_at: string // fecha ISO 8601 en UTC
}

// LoginRequest
export type LoginInput = {
  email: string
  password: string
}

// UserCreate
export type RegisterInput = LoginInput & {
  full_name: string
}
