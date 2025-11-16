import React, { useState, useEffect } from "react";

// --- API Endpoints (Доступные из браузера) ---
const LOGIN_URL = "http://localhost:8000/api/v1/auth/login/";
// (Запросим по 5 шт. для примера)
const FRAMES_URL = "http://localhost:8000/api/v1/catalog/frames/?page_size=5";
const LENSES_URL = "http://localhost:8000/api/v1/catalog/lenses/?page_size=5";

// (Определим типы для TypeScript, чтобы было "чисто")
interface Frame {
  id: number;
  id_1c: string;
  name: string;
  brand: string;
  price: string;
  stock: number;
}
interface Lens {
  id: number;
  id_1c: string;
  series: string; // (StringRelatedField из Django)
  sph: string;
  cyl: string;
  dia: number;
  price: string;
  stock: number;
}

function App() {
  // --- Состояние (State) ---
  const [token, setToken] = useState<string | null>(() =>
    localStorage.getItem("authToken")
  );

  // (Для формы входа)
  const [login, setLogin] = useState<string>("");
  const [password, setPassword] = useState<string>("");

  // (Для данных)
  const [frames, setFrames] = useState<Frame[]>([]);
  const [lenses, setLenses] = useState<Lens[]>([]);

  const [loading, setLoading] = useState<boolean>(false);
  const [error, setError] = useState<string | null>(null);

  // --- Эффекты (Effects) ---

  // Этот useEffect "сработает" 1 раз при загрузке.
  // Он проверит, есть ли токен в localStorage, и если да - загрузит данные.
  useEffect(() => {
    if (token) {
      console.log("Найден токен в localStorage, загружаю данные...");
      fetchData(token);
    }
  }, [token]); // (Зависимость от 'token')

  // --- Функции (Логика) ---

  /**
   * 1. ВХОД: Отправляет логин/пароль в Django
   */
  const handleLogin = async (e: React.FormEvent) => {
    e.preventDefault(); // (Отменяем перезагрузку страницы)
    setLoading(true);
    setError(null);

    try {
      const response = await fetch(LOGIN_URL, {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({ login: login, password: password }),
      });

      if (response.status === 401) {
        throw new Error("Неверный логин или пароль.");
      }
      if (!response.ok) {
        throw new Error(`Ошибка сети: ${response.status}`);
      }

      const data = await response.json();
      const newToken = data.token;

      if (!newToken) {
        throw new Error("Ошибка: токен не получен от сервера.");
      }

      console.log("Успешный вход, получен токен.");
      localStorage.setItem("authToken", newToken); // Сохраняем в браузере
      setToken(newToken); // <-- Это "активирует" useEffect, который загрузит данные
    } catch (err: any) {
      console.error("Ошибка входа:", err);
      setError(err.message);
      setLoading(false);
    }
  };

  /**
   * 2. ЗАГРУЗКА ДАННЫХ: (Используя токен)
   */
  const fetchData = async (authToken: string) => {
    setLoading(true);
    try {
      const headers = { Authorization: `Token ${authToken}` };

      // (Запускаем оба запроса параллельно)
      const [framesResponse, lensesResponse] = await Promise.all([
        fetch(FRAMES_URL, { headers }),
        fetch(LENSES_URL, { headers }),
      ]);

      if (!framesResponse.ok || !lensesResponse.ok) {
        throw new Error("Ошибка при загрузке каталога.");
      }

      const framesData = await framesResponse.json();
      const lensesData = await lensesResponse.json();

      setFrames(framesData.results || []);
      setLenses(lensesData.results || []);
      setError(null);
    } catch (err: any) {
      console.error("Ошибка загрузки данных:", err);
      setError(err.message);
      // (Если ошибка - выходим из системы)
      handleLogout();
    } finally {
      setLoading(false);
    }
  };

  /**
   * 3. ВЫХОД
   */
  const handleLogout = () => {
    setToken(null);
    localStorage.removeItem("authToken");
    setFrames([]);
    setLenses([]);
  };

  // --- 4. РЕНДЕР (Отображение) ---

  // (Если CSS не загружен, эти стили помогут)
  const styles: { [key: string]: React.CSSProperties } = {
    container: {
      padding: "20px",
      fontFamily: "Arial",
      maxWidth: "800px",
      margin: "0 auto",
    },
    form: {
      display: "flex",
      flexDirection: "column",
      gap: "10px",
      maxWidth: "300px",
    },
    input: { padding: "8px", fontSize: "16px" },
    button: {
      padding: "10px",
      fontSize: "16px",
      cursor: "pointer",
      background: "#007bff",
      color: "white",
      border: "none",
    },
    error: { color: "red", fontWeight: "bold" },
    loading: { color: "blue" },
    dataSection: { marginTop: "20px" },
    dataItem: {
      background: "#f4f4f4",
      padding: "10px",
      margin: "5px 0",
      borderRadius: "5px",
    },
  };

  // --- Если нет токена: Показываем форму входа ---
  if (!token) {
    return (
      <div style={styles.container}>
        <h1>B2B Glasses: Вход</h1>
        <form onSubmit={handleLogin} style={styles.form}>
          <input
            type="text"
            placeholder="Логин (телефон или username)"
            value={login}
            onChange={(e) => setLogin(e.target.value)}
            style={styles.input}
          />
          <input
            type="password"
            placeholder="Пароль"
            value={password}
            onChange={(e) => setPassword(e.target.value)}
            style={styles.input}
          />
          <button type="submit" disabled={loading} style={styles.button}>
            {loading ? "Вход..." : "Войти"}
          </button>
          {error && <p style={styles.error}>{error}</p>}
        </form>
      </div>
    );
  }

  // --- Если токен есть: Показываем данные ---
  return (
    <div style={styles.container}>
      <div
        style={{
          display: "flex",
          justifyContent: "space-between",
          alignItems: "center",
        }}
      >
        <h1>B2B Glasses: Каталог</h1>
        <button
          onClick={handleLogout}
          style={{ ...styles.button, background: "#dc3545" }}
        >
          Выйти
        </button>
      </div>

      {loading && <h2 style={styles.loading}>Загрузка данных из Django...</h2>}
      {error && <h2 style={styles.error}>Ошибка: {error}</h2>}

      {!loading && !error && (
        <>
          <div style={styles.dataSection}>
            <h2>Оправы (5 шт.)</h2>
            {frames.length > 0 ? (
              frames.map((frame) => (
                <div key={frame.id_1c} style={styles.dataItem}>
                  <b>{frame.name}</b> (Бренд: {frame.brand})
                  <br />
                  Цена: {frame.price} UZS | Остаток: {frame.stock}
                </div>
              ))
            ) : (
              <p>Оправы не найдены.</p>
            )}
          </div>

          <div style={styles.dataSection}>
            <h2>Линзы (5 шт.)</h2>
            {lenses.length > 0 ? (
              lenses.map((lens) => (
                <div key={lens.id_1c} style={styles.dataItem}>
                  <b>{lens.series}</b>
                  <br />
                  (SPH: {lens.sph} | CYL: {lens.cyl} | DIA: {lens.dia})
                  <br />
                  Цена: {lens.price} UZS | Остаток: {lens.stock}
                </div>
              ))
            ) : (
              <p>Линзы не найдены.</p>
            )}
          </div>
        </>
      )}
    </div>
  );
}

export default App;
