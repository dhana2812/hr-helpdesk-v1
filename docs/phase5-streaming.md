\# Phase 5 — Streaming



\## Objective



Modify the HR Helpdesk Assistant backend so that model responses can be

streamed incrementally to the client instead of waiting for the complete

model response.



The implementation uses Server-Sent Events (SSE).



\---



\## Architecture



\### Non-streaming



```text

Client

&#x20; |

&#x20; | POST /chat

&#x20; v

FastAPI Backend

&#x20; |

&#x20; | OpenRouter API request

&#x20; v

LLM

&#x20; |

&#x20; | Complete response

&#x20; v

Backend

&#x20; |

&#x20; | Structured response validation

&#x20; v

Client

