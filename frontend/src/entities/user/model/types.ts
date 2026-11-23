export interface User {
  id?: number;
  login?: string;
  username?: string;
  first_name?: string;
  last_name?: string;
  company?: string | null;
  phone_number?: string;
  telegram_username?: string;
  email?: string;
}

export interface UserSchema {
  authData?: User;
  token?: string;
  _inited: boolean;
  isLoading: boolean;
  error?: string;
  isAuthModalOpen: boolean;
}

export interface LoginResponse {
  token: string;
  user?: User;
}

export interface SetPasswordRequest {
  password: string;
  password_confirm: string;
}

export interface SetPasswordResponse {
  message?: string;
}
