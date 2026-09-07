# CineWatch TV Web Boundary

This directory is the governed boundary for the CineWatch TV web application.

`CWTV.V1.2.2` establishes the boundary only. The Next.js application skeleton begins in `CWTV.V1.2.4`.

This directory SHALL NOT contain provider secrets or become a second backend authority. CineWatch domain rules, rights enforcement, persistence, and provider-policy enforcement remain behind the FastAPI service boundary.
