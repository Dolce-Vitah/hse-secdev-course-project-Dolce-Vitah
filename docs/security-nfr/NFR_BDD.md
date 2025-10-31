Сценарии ниже описывают приемочные тесты (Given/When/Then) с конкретными порогами.

**Сценарий 1** — JWT TTL и отзыв:

```
Feature: JWT lifetime and revocation
  Scenario: Access token expires and revoked tokens are rejected
    Given a registered user with valid credentials
    When the user obtains an access token
    And the token is revoked in the revocation store
    Then any API call using this token must be rejected with 401 within 1 second of revocation
    And access tokens older than 15 minutes must be rejected
```

**Сценарий 2** — Password hashing parameters (Argon2id):

```
Feature: Password hashing
  Scenario: Argon2id parameters meet minimum strength
    Given the system uses Argon2id for password hashing
    When creating a user or validating password
    Then Argon2id parameters must be at least: memory ≥ 64 MB, iterations ≥ 2
    And hashing time on CI runner must be between 100 ms and 500 ms
```

**Сценарий 3** — Owner-only access (IDOR):
```
Feature: Owner-only access control
  Scenario: User cannot access another user's wish
    Given user A owns wish W and user B exists
    When user B requests GET /api/v1/wishes/{W.id}
    Then response must be 403 Forbidden and the wish must not be returned
```

**Сценарий 4** — Performance (p95 latency)
```
Feature: API latency
  Scenario: Common endpoints respond quickly under normal load
    Given staging environment with DB of 1k wishes and 100 users
    When running a load test at RPS 50 for 1 minute
    Then p95 latency for GET /api/v1/wishes must be ≤ 200 ms
```

**Негативный сценарий 1** — Brute-force protection:
```
Feature: Brute-force protection
  Scenario: Too many failed logins triggers block
    Given an IP performs 6 failed login attempts for the same username within 15 minutes
    When attempt number 6 occurs
    Then the system must block further attempts from that IP/username for 15 minutes and return 429
```

**Негативный сценарий 2** — DB failure graceful degradation:
```
Feature: Graceful degradation on DB error
  Scenario: DB unavailable leads to controlled error
    Given the database is down
    When user calls GET /api/v1/wishes
    Then the API must return 503 Service Unavailable with standard error body and no sensitive info
```
