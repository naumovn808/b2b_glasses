import type { LoginResponse } from '../types';
import { createAsyncThunk } from '@reduxjs/toolkit';
import { userActions } from '../slice';

interface LoginByUsernameProps {
  login: string;
  password: string;
}

const LOGIN_URL = '/api/v1/auth/login/';

export const loginByUsername = createAsyncThunk<
  LoginResponse,
  LoginByUsernameProps,
  { rejectValue: string }
>('user/loginByUsername', async (authData, thunkApi) => {
  try {
    const response = await fetch(LOGIN_URL, {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json',
      },
      body: JSON.stringify(authData),
    });

    if (response.status === 401) {
      return thunkApi.rejectWithValue('Неверный логин или пароль.');
    }

    if (!response.ok) {
      return thunkApi.rejectWithValue(`Ошибка сети: ${response.status}`);
    }

    const data: LoginResponse = await response.json();

    if (!data.token) {
      return thunkApi.rejectWithValue('Ошибка: токен не получен от сервера.');
    }

    thunkApi.dispatch(userActions.setToken(data.token));
    thunkApi.dispatch(userActions.setAuthData({ login: authData.login }));

    return data;
  } catch (e: any) {
    console.error('Login error:', e);
    return thunkApi.rejectWithValue(e.message || 'Произошла ошибка при входе');
  }
});
