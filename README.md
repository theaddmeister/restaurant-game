# 🍽️ Restaurant Manager - 5 Minute Challenge

A fast-paced restaurant management game where you manage a restaurant and try to serve as many customers as possible in 5 minutes!

## 📋 Features

- **Aerial View Floor Plan** - Manage your restaurant from above
- **8 Numbered Tables** - Green when empty, Red when occupied
- **Dynamic Customer AI** - Customers arrive and need seating, ordering, and delivery
- **Order System** - 5 menu items with varying cook times
- **Kitchen Queue** - Real-time cooking with visual feedback
- **Satisfaction System** - Customers get unhappy while waiting
- **Scoring System** - Earn points based on completed orders
- **5-Minute Timer** - Race against the clock!

## 🎮 How to Play

1. **Click to Move** - Click anywhere to move your character
2. **Seat Customers** - Click waiting customers to seat them at available tables
3. **Take Orders** - Click seated customers to take their order
4. **Pick Up Orders** - Orders cook in kitchen, pick up when ready
5. **Deliver Food** - Deliver to the correct table numbers
6. **Maximize Score** - Complete as many orders as possible!

## 🎯 Game Objects

- **Blue Circle** - Your character
- **Yellow Box** - Entrance
- **Green Circles** - Empty tables
- **Red Circles** - Occupied tables
- **Orange Circles** - Customers
- **Brown Box** - Kitchen
- **Light Blue Box** - Toilets

## 📦 Installation

### Requirements
- Python 3.7+
- macOS (Monterey compatible)

### Setup

```bash
# Clone the repository
git clone https://github.com/theaddmeister/restaurant-game.git
cd restaurant-game

# Create virtual environment
python3 -m venv venv
source venv/bin/activate

# Install dependencies
pip install -r requirements.txt

# Run the game
python3 game.py
