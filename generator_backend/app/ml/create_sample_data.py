import csv
import os
import random
from pathlib import Path

BASE_DIR = Path(__file__).resolve().parent
DATA_DIR = BASE_DIR / "data"
DATA_DIR.mkdir(parents=True, exist_ok=True)

OUTPUT_CSV = DATA_DIR / "training_data.csv"


SIMPLE_IDEAS = [
    "Simple todo app",
    "Personal budget tracker",
    "Notes app",
    "Portfolio website",
    "Landing page generator",
    "Blog platform",
    "URL shortener",
    "Issue tracker",
    "Habit tracker",
    "Contact manager",
]

COMPLEX_IDEAS = [
    "End-to-end CRM with email automation, lead scoring, and reporting dashboards for remote teams",
    "Multi-tenant SaaS platform for freelancers with invoicing, proposals, time tracking, and client portals",
    "E-commerce marketplace with real-time inventory sync, personalized recommendations, and analytics",
    "AI-powered knowledge base with semantic search, analytics, and multi-language support",
    "Project management tool with Gantt charts, kanban boards, time tracking, and reporting",
]

SIMPLE_FEATURE_SETS = [
    "tasks, reminders",
    "contacts, notes",
    "income, expenses, categories",
    "posts, comments, tags",
    "links, clicks, stats",
    "projects, tickets, comments",
]

COMPLEX_FEATURE_SETS = [
    "contacts, deals, proposals, invoices, emails, reports, workflows, integrations",
    "products, inventory, carts, orders, payments, refunds, reviews, recommendations",
    "workspaces, projects, tasks, sprints, timelines, dependencies, reports, alerts",
    "articles, collections, search, permissions, analytics, insights, localization, versions",
]

STACKS_SIMPLE = [
    "react fastapi",
    "vue django",
    "nextjs node",
    "svelte flask",
    "react express",
]

STACKS_COMPLEX = [
    "react fastapi celery postgres redis",
    "vue django channels postgres",
    "nextjs node redis postgres",
    "react nestjs kafka postgres redis",
]


def generate_simple_record() -> dict:
    idea = random.choice(SIMPLE_IDEAS)
    features = random.choice(SIMPLE_FEATURE_SETS)
    stack = random.choice(STACKS_SIMPLE)

    # Simple ideas should succeed most of the time in our synthetic world.
    success = 1 if random.random() < 0.9 else 0
    generation_time = random.uniform(5.0, 15.0)

    return {
        "input_idea": idea,
        "input_features": features,
        "input_stack": stack,
        "success": success,
        "generation_time_seconds": round(generation_time, 2),
    }


def generate_complex_record() -> dict:
    idea = random.choice(COMPLEX_IDEAS)
    features = random.choice(COMPLEX_FEATURE_SETS)
    stack = random.choice(STACKS_COMPLEX)

    # Complex ideas are still harder, but not overwhelmingly doomed.
    success = 1 if random.random() < 0.6 else 0
    generation_time = random.uniform(25.0, 45.0)

    return {
        "input_idea": idea,
        "input_features": features,
        "input_stack": stack,
        "success": success,
        "generation_time_seconds": round(generation_time, 2),
    }


def generate_dataset(n_samples: int = 150):
    records = []

    n_simple = int(n_samples * 0.6)
    n_complex = n_samples - n_simple

    for _ in range(n_simple):
        records.append(generate_simple_record())

    for _ in range(n_complex):
        records.append(generate_complex_record())

    random.shuffle(records)

    fieldnames = [
        "input_idea",
        "input_features",
        "input_stack",
        "success",
        "generation_time_seconds",
    ]

    with OUTPUT_CSV.open("w", newline="", encoding="utf-8") as f:
        writer = csv.DictWriter(f, fieldnames=fieldnames)
        writer.writeheader()
        writer.writerows(records)

    print(f"Wrote {len(records)} records to {OUTPUT_CSV}")


if __name__ == "__main__":
    random.seed(42)
    generate_dataset(150)
