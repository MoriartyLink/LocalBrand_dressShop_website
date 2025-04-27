# Darling & Co Local Brand Dresses 👗✨

[![Django Version](https://img.shields.io/badge/Django-4.2-brightgreen)](https://www.djangoproject.com/)
[![License](https://img.shields.io/badge/License-MIT-blue.svg)](https://opensource.org/licenses/MIT)
[![Build Status](https://img.shields.io/github/actions/workflow/status/MoriartyDresses/moriarty-boutique/django.yml)](https://github.com/MoriartyDresses/moriarty-boutique/actions)

A modern e-commerce platform for Darling & Co's Local Dress Boutique, showcasing handcrafted dresses from local artisans.

![Darling & Co Preview](docs/shop-preview.png)

## Features 🌟
- **Curated Collections**: Beautifully organized dress categories
- **Artisan Profiles**: Meet local dress makers
- **Virtual Fitting Room**: AI-powered size recommendations
- **Sustainable Fashion Hub**: Eco-friendly materials tracker
- **Local Delivery System**: Real-time delivery tracking
- **Customer Stories**: User-generated content gallery

## Quick Start 🚀

### Prerequisites
- Python 3.10+
- PostgreSQL
- Redis (for caching)
- Stripe API key (for payments)

### Installation

```bash
# Clone repository
git clone https://github.com/MoriartyDresses/moriarty-boutique.git
cd moriarty-boutique

# Create virtual environment
python -m venv .venv
source .venv/bin/activate  # Fish: source .venv/bin/activate.fish

# Install dependencies
pip install -r requirements.txt

# Set up environment
cp .env.example .env
