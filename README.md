# 🤖 AI Business Analyst Assistant

An AI-powered Business Intelligence application that allows users to ask
business questions in natural language and receive data-driven insights
from a MySQL database.

The system combines:

- 🤖 Gemini AI
- 🗄️ MySQL
- 🧠 Natural Language → SQL
- 🌐 Flask API
- 📊 Power BI
- 🖥️ Interactive Web Interface

---

## 📌 Project Overview

Traditional business analysis often requires users to know SQL and
understand complex dashboards.

The AI Business Analyst Assistant solves this problem by allowing users
to ask questions in simple natural language.

For example:

> "Which category generated the highest sales?"

The system automatically:

1. Understands the business question.
2. Generates an appropriate SQL query.
3. Validates the SQL query.
4. Executes the query on the MySQL database.
5. Retrieves the business data.
6. Generates an AI-powered business insight.
7. Displays the result through the web interface.

---

# 🏗️ System Architecture

```text
                         USER
                           │
                           ▼
                  ┌─────────────────┐
                  │  Web Frontend   │
                  └────────┬────────┘
                           │
                           ▼
                  ┌─────────────────┐
                  │   Flask API     │
                  └────────┬────────┘
                           │
                           ▼
                  ┌─────────────────┐
                  │    Gemini AI    │
                  │  SQL Generator  │
                  └────────┬────────┘
                           │
                           ▼
                  ┌─────────────────┐
                  │  SQL Validator  │
                  └────────┬────────┘
                           │
                           ▼
                  ┌─────────────────┐
                  │      MySQL      │
                  │ orders Database │
                  └────────┬────────┘
                           │
                           ▼
                  ┌─────────────────┐
                  │ Business Result │
                  └────────┬────────┘
                           │
                           ▼
                  ┌─────────────────┐
                  │   AI Insight    │
                  └─────────────────┘


              ┌──────────────────────┐
              │      Power BI        │
              │ Business Dashboard   │
              └──────────────────────┘
