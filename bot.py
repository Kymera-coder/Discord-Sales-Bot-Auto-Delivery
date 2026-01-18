import discord
from discord.ext import commands
import json
import os

intents = discord.Intents.default()
intents.message_content = True

bot = commands.Bot(command_prefix="!", intents=intents)

PRODUCTS_FILE = "products.json"
ORDERS_FILE = "orders.json"

def load_json(file):
    if not os.path.exists(file):
        return {}
    with open(file, "r") as f:
        return json.load(f)

def save_json(file, data):
    with open(file, "w") as f:
        json.dump(data, f, indent=4)

@bot.event
async def on_ready():
    print(f"Sales Bot online as {bot.user}")

@bot.command()
async def products(ctx):
    products = load_json(PRODUCTS_FILE)
    if not products:
        await ctx.send("No products available.")
        return

    message = "**🛒 Available Products:**\n"
    for name, data in products.items():
        message += f"- **{name}** | Price: ${data['price']} | Stock: {len(data['keys'])}\n"

    await ctx.send(message)

@bot.command()
async def buy(ctx, product_name: str):
    products = load_json(PRODUCTS_FILE)
    orders = load_json(ORDERS_FILE)

    if product_name not in products:
        await ctx.send("Product not found.")
        return

    if len(products[product_name]["keys"]) == 0:
        await ctx.send("Product out of stock.")
        return

    order_id = str(len(orders) + 1)
    orders[order_id] = {
        "user": str(ctx.author),
        "product": product_name,
        "status": "pending"
    }

    save_json(ORDERS_FILE, orders)

    await ctx.send(
        f"Order **#{order_id}** created for **{product_name}**.\n"
        f"After payment confirmation, an admin can deliver the product."
    )

@bot.command()
@commands.has_permissions(administrator=True)
async def deliver(ctx, order_id: str):
    products = load_json(PRODUCTS_FILE)
    orders = load_json(ORDERS_FILE)

    if order_id not in orders:
        await ctx.send("Order not found.")
        return

    order = orders[order_id]
    product = order["product"]

    if order["status"] != "pending":
        await ctx.send("Order already delivered.")
        return

    key = products[product]["keys"].pop(0)

    order["status"] = "delivered"
    order["key"] = key

    save_json(PRODUCTS_FILE, products)
    save_json(ORDERS_FILE, orders)

    try:
        user = await bot.fetch_user(ctx.author.id)
        await user.send(f"✅ Your product **{product}** key:\n`{key}`")
        await ctx.send("Product delivered successfully.")
    except:
        await ctx.send("Could not send DM to the user.")

TOKEN = os.getenv("DISCORD_TOKEN")
bot.run(TOKEN)