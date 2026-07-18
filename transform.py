import pandas as pd

MERCHANT_ALIASES = {
    # Zomato
    "Zomato Ltd": "Zomato",
    "Zomato Media Private Limited": "Zomato",
    "Zomato Online Order": "Zomato",
    "Zomato Wallet": "Zomato",
    "Zomato Limited": "Zomato",
    # Swiggy
    "Swiggy Limited": "Swiggy",
    # Agoda
    "Agoda Company Pte Lt": "Agoda",
    "Agoda Company Pte Ltd": "Agoda",
    # All Season Hyper Mart
    "All Season Hyper Mart C1": "All Season Hyper Mart",
    "All Season Hyper Mart C2": "All Season Hyper Mart",
    "All Season Hyper Mart C3": "All Season Hyper Mart",
    "All Season Hyper Mart D2": "All Season Hyper Mart",
    # Amazon
    "Amazon Pay": "Amazon",
    "Amazon Seller Services Private Limited": "Amazon",
    "Amazon India": "Amazon",
    # Aubree Bel Road
    "Aubree Bel Road 1": "Aubree Bel Road",
    # Bangalore Metro
    "Bangalore Metro Rail Corporati": "Bangalore Metro Rail Corporation Ltd",
    "Bmrcl J P Nagar": "Bangalore Metro Rail Corporation Ltd",
    "Bmrcl Kempegowda": "Bangalore Metro Rail Corporation Ltd",
    "Bmrcl Peyatom0001": "Bangalore Metro Rail Corporation Ltd",
    "Bmrcl Spgdtom0012": "Bangalore Metro Rail Corporation Ltd",
    # McDonalds
    "Mcdonalds": "Mc Donalds",
    "Mcdonalds Hardcastle Restaurants": "Mc Donalds",
    # KFC
    "K214 Kfc Kammanhalli Hs": "Kfc",
    "Bglk221 Kfc Meenak": "Kfc",
    "K547 Kfc Forum Falcon": "Kfc",
    # Dominos
    "Domino'S Pizza": "Dominos Pizza",
    # Blinkit
    "Blinkit Commerce Private Limited": "Blinkit",
    # Taco Bell
    "Taco Bell Forum Falcon Mall": "Taco Bell",
    "Taco Bell Gopalan Innovation Mall": "Taco Bell",
    "Taco Bell Orion Mall": "Taco Bell",
    "Taco Bell Royal Meenakshi Mall": "Taco Bell",
    "Taco Bell Sahakar Nagar": "Taco Bell",
    "Taco  Bell  Mantri Square Mall": "Taco Bell",
    "Tacobell Forum Falcon Mall": "Taco Bell",
    # Chaayos
    "Chaayos Orion Mall First Floor": "Chaayos",
    # Amintiri
    "Amintiri Museum Road": "Amintiri",
    # BigBasket
    "Bigbasket": "Big Basket",
    #Eternal Limited
    "Eternal Ltd": "Eternal Limited",
    # Hiseol
    "Hiseoul Restaurant P": "Hiseoul Restaurant",
    #Houseofcommons
    "House Of Commonshouse Of Commons Jp Nagar": "House Of Commons",
    # Justloaf
    "Justloaf 2": "Justloaf",
    "Justloaf 3": "Justloaf",
    # Kebapci
    "Kebapci Forum": "Kebapci",
    # Koriken
    "Koriken-Bel Road": "Koriken - Bel Road",
    #KFC
    "K214 Kfc Kammanhalli Hs Bgl": "KFC",
    "K221 Kfc Meenak": "KFC",
    "Kfc": "KFC",
    #Sapna
    "Sapna Royal Meenakshi Mall": "Sapna Book House",
    "Sapna The Galleria Mall": "Sapna Book House",
    #Theobroma
    "Theobroma Foods Pvt Ltd" : "Theobroma Foods",
    "Theobroma Jayanagar": "Theobroma Foods",
    #Thoms Bakery
    "Thoms Bakery  Super Market": "Thoms Bakery Super Market",
    #Shoppy Mart
    "Shoppy Mart 1 A190": "Shoppy Mart",
    "Shoppy Mart 2 A910": "Shoppy Mart",
    #Starbucks
    "Starbucks Bangalore Sjr Central S262": "Starbucks Bangalore",
    "Starbucks Vega Mall Bangalore": "Starbucks Bangalore",
    "Tata Starbucks Private Limited": "Starbucks Bangalore",
    #Truffles
    "Truffles  Rmv": "Truffles",
    "Truffles New Bel Road": "Truffles",
    #Smartbaazar
    "Smart Bazaar  Bengaluru Fr40": "Smart Bazaar",
    "Smart Bazaar Fr40": "Smart Bazaar",
    # Magnolia Bakery
    "Magnolia Bakery Falcon": "Magnolia Bakery",
    "Magnolia Bakery Orion": "Magnolia Bakery",
    # IDC Kitchen
    "Idc Kitchen Private Limited": "Idc Kitchen",
    # Burrito Restaurants
    "Burrito Restaurants Private Limited": "Burrito Restaurants",
    # Brevistay
    "Brevistay Hospitalit": "Brevistay",
    # Milano Ice Cream
    "Milano Ice Cream Pvt Ltd": "Milano Ice Cream Private Limited",
    # Pumphouse
    "Pumphouseprivatelimited": "Pumphouseprivatelimi",
    # Thoms Bakery
    "Thoms Bakery Super Market": "Thoms Bakery Super Market",
    # Thriptis Kitchen
    "Thriptis Kitchen Pri": "Thriptis Kitchen Private Limited",
    # Uncle Bros
    "Unclebro'S Grub Hub": "Uncle Bro'S Restaurant",
    #Zepto
    "Zeptonow": "Zepto"
}

def get_time_of_day(hour):
    if 5 <= hour < 12:
        return "Morning"
    elif 12 <= hour < 17:
        return "Afternoon"
    elif 17 <= hour < 21:
        return "Evening"
    else:
        return "Night"

def transform(transactions):
    df = pd.DataFrame(transactions)

    # Clean datetime
    df["datetime"] = df["datetime_raw"].str.replace("\u202f", " ").str.replace(" IST", "").str.strip()
    df["datetime"] = pd.to_datetime(df["datetime"], format="%b %d, %Y, %I:%M:%S %p", errors="coerce")

    # Drop nulls using transaction_id and datetime
    df = df.dropna(subset=["datetime"])

    # Remove duplicates using transaction_id as primary key
    df = df.drop_duplicates(subset=["transaction_id"])

    # Date columns
    df["date"] = df["datetime"].dt.date
    df["month"] = df["datetime"].dt.to_period("M").astype(str)
    df["year"] = df["datetime"].dt.year
    df["day_of_week"] = df["datetime"].dt.day_name()
    df["is_weekend"] = df["datetime"].dt.dayofweek >= 5
    df["is_weekend"] = df["is_weekend"].map({True: "Weekend", False: "Weekday"})
    df["time_of_day"] = df["datetime"].dt.hour.apply(get_time_of_day)

    # Clean merchant names
    df["merchant"] = df["merchant"].str.title().str.strip()
    df["merchant"] = df["merchant"].replace(MERCHANT_ALIASES)

    # Drop raw column
    df = df.drop(columns=["datetime_raw"])

    # Reorder columns
    df = df[[
        "transaction_id", "date", "month", "year", "datetime",
        "merchant", "amount", "status", "day_of_week", "is_weekend", "time_of_day"
    ]]

    return df


if __name__ == "__main__":
    from parse import parse_gpay_html

    raw = parse_gpay_html("data/raw/My Activity.html")
    df = transform(raw)

    print(df.head())
    print(f"\nShape: {df.shape}")
    print(f"\nDate range: {df['date'].min()} to {df['date'].max()}")
    print(f"\nTotal spent: Rs.{df['amount'].sum():,.2f}")

    df.to_csv("data/processed/transactions.csv", index=False)
    print("\nSaved to data/processed/transactions.csv")