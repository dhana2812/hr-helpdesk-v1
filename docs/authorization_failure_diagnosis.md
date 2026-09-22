## Authorization Failure Diagnosis

### Failure
The `/chat` endpoint allowed the client to supply `user_id` independently of the authenticated identity.

### Reproduction
Authenticated request:
- Bearer token: valid `CLIENT_TOKEN`
- Request `user_id`: `EMP002`
- Message: `What is my casual leave balance?`

### Observed result
HTTP 200 returned:
`Your casual leave balance is 12.`

### Root cause
`authenticate_client()` returns the fixed identity `authenticated-client`, while `/chat` uses `ChatRequest.user_id` directly. The authenticated identity is therefore not bound to the employee identity used for memory, tool execution, and authorization.

### Security impact
A caller with a valid client token could potentially change `user_id` in the request body and access another employee's deterministic records.

### Planned fix
Bind the authenticated identity to the employee identity before employee-specific tools or employee-scoped memory are accessed.
