export interface User {
  id?: number;
  login?: string;
}

export interface UserSchema {
  authData?: User;
  token?: string;
  _inited: boolean;
  isLoading: boolean;
  error?: string;
}

export interface LoginResponse {
  token: string;
}
