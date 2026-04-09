# Dokumentacja — Cyfrowe Archiwum Społecznościowe

---

## Spis treści

1. [Uzasadnienie przyjętych rozwiązań](#1-uzasadnienie-przyjętych-rozwiązań)
2. [Architektura informacji](#2-architektura-informacji)
3. [Architektura systemu](#3-architektura-systemu)
4. [Model danych](#4-model-danych)
5. [Struktura metadanych](#5-struktura-metadanych)
6. [Analiza dostępności informacji](#6-analiza-dostępności-informacji)

---

## 1. Uzasadnienie przyjętych rozwiązań
### 1.1 Wybór technologii — backend

**Python + FastAPI**:

- Krótki czas tworzenia API, przez prostotę użycia, a także automatyczne generowanie dokumentacji OpenAPI (Swagger UI).
- Pydantic zapewnia walidację żądań i odpowiedzi z precyzyjnymi komunikatami błędów i automatyczną konwersją typów.
- Wbudowana integracja z OAuth2 i JWT, obsługa hashowania haseł przez `passlib[bcrypt]`.

**SQLite z aiosqlite**:

- Małe, łatwe i szybkie rozwiązanie dla aplikacji o niewielkiej skali.
- W przypadku zwiększenia zapotrzebowania w przyszłości umożliwia zmianę na PostgreSQL bez zmiany logiki biznesowej.

### 1.2 Wybór technologii — frontend

**Vue + TypeScript**:

- **TypeScript** zapewnia obsługę typów danych, co minimalizuje ryzyko powstawania błędów.
- **Pinia** szybki menedżer stanu aplikacji.
- **Vite** przyspiesza proces developmentu i optymalizuje build produkcyjny.

**Tailwind CSS**:

- Przyspiesza pracę nad stylami.
- Umożliwia łatwe zmiany motywu aplikacji.
- Przyspiesza tworzenie responsywnych layoutów.

### 1.3 Decyzje architektoniczne

| Decyzja | Uzasadnienie |
|---------|-------------|
| JWT z osobnym refresh tokenem | Access token (15 min) ogranicza okno podatności przy wycieku; refresh token (7 dni) eliminuje potrzebę częstego logowania. |
| Daty z precyzją | Pole `date_taken` przechowuje datę jako ciąg (`YYYY`, `YYYY-MM`, `YYYY-MM-DD`), a `date_precision` określa jej dokładność. Rozwiązuje problem fotografii z nieznana dokładną datą. |
| Thumbnail jako WebP | Format WebP zapewnia ~30% mniejszy rozmiar pliku niż JPEG przy porównywalnej jakości, co skraca czas ładowania galerii. |
| Slugi w hierarchii | Slug (`krakow`, `malopolskie`) umożliwia czytelne URLe i wyszukiwanie po nazwie bez rozróżniania znaków specjalnych. |

---

## 2. Architektura informacji

### 2.1 Hierarchia geograficzna

Zdjęcia są organizowane w trójpoziomowej hierarchii odzwierciedlającej strukturę Polski:

```
województwo
└── miasto
    └── dowolny szczegół
```

Zdjęcie przypisane jest dokładnie do jednego węzła, ale wyszukiwarka obsługuje zapytania rekurencyjne, tak że filtrowanie po województwie zwraca zdjęcia przypisane do wszystkich jego miast.

### 2.2 Role użytkowników

System definiuje trzy role, z których dwie są przechowywane w bazie danych:

| Rola | Opis | Możliwości |
|------|------|-----------|
| **Widz** | Niezalogowany użytkownik | Przeglądanie galerii, wyszukiwanie, podgląd szczegółów zdjęcia |
| **Kontrybutor** | Zalogowany, niezablokowany użytkownik | Wszystko co Widz + upload, edycja i usuwanie własnych zdjęć |
| **Administrator** | Użytkownik z rolą admin | Wszystko co Kontrybutor + moderacja treści, zarządzanie użytkownikami i hierarchią |

Administrator jest wyznaczany przez adres e-mail skonfigurowany w zmiennej środowiskowej `ADMIN_EMAIL`. Przy rejestracji konta z tym adresem rola jest automatycznie ustawiana na `admin`.


### 2.3 Struktura nawigacji

```
/ (Strona główna)
├── /browse            Przeglądanie wszystkich zdjęć
├── /search            Wyszukiwarka
├── /photos/:id        Szczegóły zdjęcia
├── /upload            Formularz uploadu
├── /login             Logowanie
├── /register          Rejestracja
├── /profile           Profil użytkownika
└── /admin             Panel administracyjny
    ├── /admin/users       Zarządzanie użytkownikami
    ├── /admin/moderation  Moderacja zdjęć
    └── /admin/hierarchy   Zarządzanie hierarchią
```

---

## 3. Architektura systemu

### 3.1 Przegląd

Aplikacja jest zbudowana w architekturze klient-serwer z podziałem na:

- **Backend**: REST API (FastAPI, Python)
- **Frontend**: Aplikacja SPA (Vue 3, Vite)
- **Baza danych**: SQLite
- **Przechowywanie plików**: System plików serwera (`uploads/`)

### 3.2 Backend — struktura kodu

```
backend/
├── app/
│   ├── main.py           # Tworzenie aplikacji FastAPI
│   ├── config.py         # Pydantic Settings — zmienne środowiskowe z .env
│   ├── database.py       # Tworzenie sesji z bazą danych
│   ├── dependencies.py   # Metody pomocnicze dotyczące dostępności do danych
│   ├── seed.py           # Skrypt wprowadzający do bazy przykładowe dane
│   ├── models/           # Modele używane do ORM
│   │   ├── user.py
│   │   ├── photo.py
│   │   └── hierarchy.py
│   ├── routers/          # Kontrolery do obsługi zapytań HTTP
│   │   ├── auth.py
│   │   ├── photos.py
│   │   ├── hierarchy.py
│   │   ├── search.py
│   │   └── admin.py
│   ├── schemas/          # Modele żądań i odpowiedzi Pydantic
│   └── utils/
│       ├── security.py   # Metody dotyczące autoryzacji
│       └── image.py      # Metody pomocnicze dotyczące operacji na zdjęciach
```

### 3.3 Frontend — struktura kodu

```
frontend/src/
├── main.ts
├── App.vue               # Korzeń aplikacji
├── api/                  # Metody do wywoływania zapytań HTTP
│   ├── client.ts         # Konfiguracja bilioteki Axios
│   ├── auth.ts
│   ├── photos.ts
│   └── admin.ts
├── stores/
│   ├── auth.ts           # Zarządzanie stanem użytkownika i tokenami w localStorage
│   └── theme.ts          # Zarządzanie aktywnym motywem
├── composables/
│   ├── useAuth.ts        # Wrapper na auth store
│   └── useTheme.ts       # Wrapper na theme store
├── router/index.ts       # Vue Router
├── types/                # Typy używane przez TypeScript
├── views/                # Widoki zawarte w aplikacji
├── components/           # Komponenty używane w widokach
│   ├── layout/
│   ├── common/
│   ├── photo/
│   └── admin/
├── utils/
│   └── date.ts           # Metody pomocnicze do formatowania dat
└── style.css             # Zmienne CSS
```

### 3.4 Przepływ autoryzacji (JWT)

```
1. Rejestracja / Logowanie
   POST /api/auth/register lub /login
   → Backend zwraca { access_token, refresh_token }
   → Frontend zapisuje oba tokeny w localStorage

2. Żądanie chronione
   Frontend → Axios interceptor dodaje nagłówek:
   Authorization: Bearer <access_token>
   → Backend: oauth2_scheme wyciąga token
   → get_current_user() dekoduje JWT, sprawdza typ "access" i exp
   → Zwraca obiekt User do handlera

3. Wygaśnięcie access tokenu (odpowiedź 401)
   Axios interceptor response:
   → Jeśli istnieje refresh_token: POST /auth/refresh
   → Nowe tokeny zapisywane w localStorage
   → Oryginalne żądanie ponawiane z nowym tokenem
   → Jeśli refresh nie powiódł się: redirect do /login
```


## 4. Model danych
#### Tabela `users`

| Kolumna | Typ SQL |
|---------|---------|
| `id` | INTEGER |
| `email` | VARCHAR(255) |
| `display_name` | VARCHAR(100) |
| `password_hash` | VARCHAR(255) |
| `role` | ENUM |
| `is_blocked` | BOOLEAN |
| `created_at` | DATETIME |
| `updated_at` | DATETIME |

#### Tabela `photos`

| Kolumna | Typ SQL |
|---------|---------|
| `id` | INTEGER |
| `owner_id` | INTEGER |
| `hierarchy_node_id` | INTEGER |
| `title` | VARCHAR(300) |
| `description` | TEXT |
| `file_path` | VARCHAR(500) |
| `thumbnail_path` | VARCHAR(500) |
| `mime_type` | VARCHAR(50) |
| `file_size` | INTEGER |
| `width` | INTEGER |
| `height` | INTEGER |
| `date_taken` | VARCHAR(10) |
| `date_precision` | ENUM |
| `location_text` | VARCHAR(500) |
| `exif_data` | TEXT |
| `created_at` | DATETIME |
| `updated_at` | DATETIME |

#### Tabela `hierarchy_nodes`

| Kolumna | Typ SQL |
|---------|---------|
| `id` | INTEGER |
| `name` | VARCHAR(200) |
| `slug` | VARCHAR(200) |
| `level` | ENUM |
| `parent_id` | INTEGER |
| `created_at` | DATETIME |

#### Tabela `tags`

| Kolumna | Typ SQL |
|---------|---------|
| `id` | INTEGER |
| `name` | VARCHAR(100) |

#### Tabela `photo_tags` (tabela łącząca)

| Kolumna | Typ SQL |
|---------|---------|
| `photo_id` | INTEGER |
| `tag_id` | INTEGER |

---

## 5. Struktura metadanych

### 5.1 Metadane zdjęcia

Każde zdjęcie w systemie posiada następujące kategorie metadanych:

#### a) Metadane opisowe (wprowadzane przez użytkownika)

| Pole | Opis |
|------|------|
| `title` | Tytuł zdjęcia |
| `description` | Opis zdjęcia |
| `tags` | Słowa kluczowe; wiele tagów per zdjęcie; tagi są współdzielone między zdjęciami |
| `location_text` | Dowolny opis lokalizacji |

#### b) Metadane geograficzne

| Pole | Opis |
|------|------|
| `hierarchy_node_id` | Przypisanie do węzła hierarchii administracyjnej |

Hierarchia pozwala przypisać zdjęcie do województwa i miasta. Pole `location_text` uzupełnia strukturę hierarchiczną o opis adresowy.

#### c) Metadane dotyczące czasu

System obsługuje daty o różnym stopniu dokładności:

| `date_precision` | Przykład | Wyświetlanie |
|-----------------|---------|-|
| `year` | `1965` | 1965 |
| `month` | `1965-07` | lipiec 1965 |
| `day` | `1965-07-23` | 23.07.1965 |
| (brak) | — | Nieznana data |

#### d) Metadane techniczne (automatycznie wyznaczane)

| Pole | Opis |
|------|------|
| `mime_type` | Typ MIME pliku |
| `file_size` | Rozmiar oryginału w bajtach |
| `width`, `height` | Wymiary obrazu w pikselach |
| `exif_data` | Surowe dane EXIF jako JSON |
| `created_at` | Czas dodania do systemu |
| `updated_at` | Czas ostatniej modyfikacji rekordu |

### 5.2 Metadane hierarchii

Każdy węzeł hierarchii przechowuje:

| Pole | Opis |
|------|------|
| `name` | Polska nazwa |
| `slug` | Wersja znormalizowana |
| `level` | Poziom w drzewie: `województwo` / `miasto` |
| `parent_id` | Wskazanie na węzeł nadrzędny |

### 5.3 Metadane użytkownika

| Pole | Opis |
|------|------|
| `email` | Adres e-mail |
| `display_name` | Publiczna nazwa wyświetlana przy zdjęciach |
| `role` | Rola: `admin` lub `contributor` |
| `is_blocked` | Czy użytkownik jest zablokowany przez admina |
| `created_at` | Data rejestracji |

---

## 6. Analiza dostępności informacji

Aplikacja zaprojektowana jest zgodnie z wytycznymi WCAG 2.1 na poziomie AA. Poniżej opisano szczegółowo zaimplementowane mechanizmy.

### 6.1 System motywów i kontrast kolorów

Użytkownik może wybrać jeden z trzech motywów kolorystycznych, trwale zapamiętanych w `localStorage`:

- Motyw jasny (domyślny)

- Motyw ciemny

- Motyw wysokiego kontrastu

### 6.2 Widocznosć fokusu i nawigacja klawiaturą

Globalna reguła CSS zapewnia widoczny fokus we wszystkich motywach:

```css
*:focus-visible {
  outline: 2px solid var(--color-focus-ring);
  outline-offset: 2px;
}
```

#### Pomiń do treści (Skip Link)

W `App.vue` zaimplementowany jest niewidoczny link aktywowany przez fokus klawiatury:

```html
<a href="#main-content" class="skip-link">Przejdź do treści</a>
```

Styl CSS powoduje, że link jest poza ekranem i pojawia się w lewym górnym rogu dopiero gdy otrzyma fokus. Cel (`<main id="main-content">`) jest poprawnie oznaczony.

Mechanizm ten spełnia kryterium **WCAG 2.4.1 — Bypass Blocks (A)**.

#### Kolejność tabulacji

Elementy fokusowalne w całej aplikacji są dostępne w ustalonej kolejności, co pomaga przy poruszaniu się za pomocą tabulatora.

Wyszukiwarki lokalizacji i tagów (w `SearchView`, `UploadView`, `PhotoEditModal`) implementują wzorzec ARIA Combobox zgodnie ze specyfikacją WAI-ARIA 1.2:

#### Atrybuty ARIA

```html
<input
  role="combobox"
  aria-haspopup="listbox"
  :aria-expanded="isOpen"
  :aria-controls="'listbox-' + uid"
  aria-autocomplete="list"
  :aria-activedescendant="activeIndex >= 0 ? 'option-' + uid + '-' + activeIndex : undefined"
/>
<ul
  :id="'listbox-' + uid"
  role="listbox"
>
  <li
    v-for="(item, i) in options"
    :id="'option-' + uid + '-' + i"
    role="option"
    :aria-selected="i === activeIndex"
  >{{ item }}</li>
</ul>
```

#### Obsługiwane klawisze

| Klawisz | Akcja |
|---------|-------|
| `↓` | Przesuń fokus na następną opcję na liście |
| `↑` | Przesuń fokus na poprzednią opcję |
| `Enter` | Wybierz lub zatwierdź |
| `Escape` | Zamknij listę, wróć fokus do pola tekstowego |
| `Tab` | Zamknij listę, przesuń fokus na kolejny element |

### 6.4 Okna dialogowe

Modale implementują mechanizm pułapki fokusa zgodny z wzorcem ARIA Dialog:

**Zachowanie fokusa:**
- Po otwarciu modala fokus jest automatycznie przenoszony na pierwsze pole formularza wewnątrz modala.
- `Tab` przechodzi przez focusowalne elementy wewnątrz modala, przy ostatnim elemencie wraca na pierwszy.
- `Shift+Tab` przesuwa fokus wstecz, przy pierwszym elemencie skacze na ostatni.
- `Escape` zamyka modal i przywraca fokus na element, który go otworzył.

Spełnia to kryteria **WCAG 2.1.1 — Keyboard (A)** i **WCAG 2.1.2 — No Keyboard Trap (A)**.

### 6.5 Grupy przełączników (RadioGroup) — przełącznik motywów

`ThemeSwitcher` używa wzorca ARIA RadioGroup:

```html
<div role="radiogroup" aria-label="Wybierz motyw">
  <button
    v-for="t in themes"
    role="radio"
    :aria-checked="theme === t.value"
    @click="setTheme(t.value)"
  >
    {{ t.label }}
  </button>
</div>
```

Etykiety w języku polskim: „Jasny", „Ciemny", „Wysoki kontrast". Aktywny motyw sygnalizowany przez `aria-checked="true"`.

### 6.6 Obszary semantyczne (Landmarks)

Każda strona posiada zdefiniowane punkty orientacyjne dostępne dla czytników ekranowych:

| Element | Rola ARIA | Przeznaczenie |
|---------|-----------|--------------|
| `<header>` | `banner` | Nagłówek strony z logiem i nawigacją |
| `<nav aria-label="Główna nawigacja">` | `navigation` | Główne menu |
| `<main id="main-content">` | `main` | Główna treść strony |
| `<aside>` | `complementary` | Pasek boczny w widoku przeglądania |
| `<section aria-label="Zdjęcia">` | `region` | Galeria zdjęć |
| `<footer>` | `contentinfo` | Stopka strony |

Użytkownicy czytników ekranowych mogą szybko przeskakiwać między punktami orientacyjnymi.

### 6.7 Etykiety formularzy

Wszystkie pola formularzy mają jawnie powiązane etykiety przez atrybut `for`:

```html
<label for="field-title">Tytuł *</label>
<input id="field-title" type="text" required />
```

### 6.8 Komunikaty dynamiczne (Live Regions)

Zmieniające się treści strony są sygnalizowane czytnikom ekranowym przez regiony live:

| Element | Atrybut | Treść |
|---------|---------|-------|
| Liczba wyników wyszukiwania | `aria-live="polite"` | „Znaleziono X wyników" |
| Stan ładowania | `role="status"` | „Ładowanie…" |
| Komunikaty błędów | `role="alert"` | Treść błędu |


### 6.9 Responsywność

- Bazowy rozmiar czcionki: Rozmiar większy niż standardowe `16px` poprawia czytelność bez konieczności powiększania.
- Układ oparty na jednostkach `rem` i `em` skaluje się wraz z preferencjami systemu operacyjnego.
- Responsywny layout: na małych ekranach siatka przechodzi w układ jednokolumnowy, hamburger menu zastępuje pełny pasek nawigacji.

### 6.10 Redukcja ruchu

Aplikacja respektuje preferencje systemowe co do animacji:

```css
@media (prefers-reduced-motion: reduce) {
  * {
    transition-duration: 0.01ms !important;
    animation-duration: 0.01ms !important;
  }
}
```

Dla użytkowników, u których system sygnalizuje `prefers-reduced-motion: reduce` (wśród nich osoby z zaburzeniami równowagi, epilepsją lub ataksją), wszystkie przejścia CSS i animacje są praktycznie wyłączone.

### 6.12 Atrybuty alt dla obrazów

Zdjęcia wyświetlane w galerii i szczegółach mają atrybut `alt` zawierający tytuł zdjęcia:

```html
<img :src="thumbnailUrl(photo.id)" :alt="photo.title" loading="lazy" />
```

Spełnia kryterium **WCAG 1.1.1 — Non-text Content (A)**.