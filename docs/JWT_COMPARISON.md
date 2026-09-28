# Session 3 JWT vs Keycloak JWT

In Session 3, we manually generated a JWT using a shared secret. The iss (issuer) claim was absent, and the sub (subject) was manually set. The API Gateway verified the token purely by checking if the signature was valid using the shared secret.

With Keycloak, the JWT is signed using RS256 (asymmetric encryption). The iss claim explicitly points to http://localhost:8180/realms/ecommerce-platform, proving its origin. Furthermore, the Keycloak token includes advanced metadata such as ealm_access (containing roles like customer) and ud (audience), allowing for fine-grained, standardized Role-Based Access Control instead of simply checking signature validity.
