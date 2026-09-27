# SERPGuard AI

> AI-powered job discovery, semantic matching, and job change intelligence using SerpApi.

## Overview

SERPGuard AI is an AI-powered job intelligence platform that helps users discover relevant job opportunities and understand how well each opportunity matches their profile.

Instead of simply returning search results, SERPGuard AI combines:

- SerpApi Google Jobs search
- Job validation and deduplication
- Rule-based skill matching
- Semantic AI matching
- Hybrid match scoring
- Job ranking
- Snapshot-based change detection

The goal is to transform raw job-search results into structured and personalized job intelligence.

---

## Problem

Traditional job searching can produce many results without clearly showing:

- Which jobs are relevant to the candidate
- Which required skills are already available
- Which skills are missing
- How strongly a job matches the candidate
- Which jobs are newly discovered
- Which previously discovered jobs have changed

SERPGuard AI addresses these problems through automated search, validation, AI matching, ranking, and change detection.

---

## How SERPGuard AI Works

```text
User
  │
  ▼
React Frontend
  │
  │ Job query + location
  ▼
FastAPI Backend
  │
  ▼
SerpApi Google Jobs
  │
  ▼
Job Results
  │
  ├── Validation
  │
  ├── Deduplication
  │
  ├── Rule-Based Matching
  │
  ├── Semantic AI Matching
  │
  └── Snapshot Comparison
  │
  ▼
Hybrid Match Score
  │
  ▼
Ranked Job Results
  │
  ▼
React Dashboard
