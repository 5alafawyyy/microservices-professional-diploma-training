# Lab 06A — Session 8

## 1. Classification
**OFFICIAL SOURCE LAB**

## 2. Objective
Add Postgres and Redis caching to Product Service.

## 3. Concepts Taught
Relational DB, Cache-Aside

## 4. Why the lab exists
To add persistence and improve read performance.

## 5. Prerequisites
Lab 05A

## 6. Tasks
1. Add Postgres JPA. 2. Add Redis caching.

## 7. Technologies Introduced
Spring Data JPA, Spring Cache

## 8. Files/Components Changed
product-service

## 9. Acceptance Criteria
Products cached in Redis

## 10. How to Verify
Fetch product twice

## 11. Expected Result
Second fetch is faster (cache hit)

## 12. Troubleshooting Notes
Redis serialization

## 13. Related Architecture Changes
Data layer

## 14. Related Commit(s)
session-08

## 15. Relationship to Source/Reference Material
Official document session-08-lab-6a.md
