from fastapi import FastAPI, HTTPException
from pydantic import BaseModel, Field
from functools import reduce
import uvicorn

app = FastAPI()

menu = {
    "coffee": 120,
    "tea": 80,
    "sandwich": 200,
    "cake": 150,
    "juice": 100
}

orders = {}

class Dish(BaseModel):
    name: str = Field(min_length=2, max_length=20)
    price: int = Field(ge=1, le=10**4)

# 1. Menu sorted by alphabet
@app.get('/menu/alphabet', summary='1️⃣ Menu sorted by alphabet', tags=['for user'])
def get_menu_alphabet():
    return [{'name': k, 'price': p} for k, p in sorted(menu.items(), key=lambda x: x[0])]

# 2. Menu sorted by price
@app.get('/menu/price', summary='2️⃣ Menu sorted by price', tags=['for user'])
def get_menu_price():
    return [{'name': k, 'price': p} for k, p in sorted(menu.items(), key=lambda x: x[1])]

# 3. Average price
@app.get('/menu/avrage', summary='3️⃣ Average price of dishes', tags=['for user'])
def get_avrg_price():
    avrg_price = sum(map(lambda x: x[1], menu.items())) // len(menu)
    return {'msg': f'Average price is {avrg_price}'}

# 4. Add or update dish (admin only)
@app.post('/menu', summary='4️⃣ Add or update dish🍴', tags=['for admin'])
def add_or_update_dish(d: Dish, password: str):
    if password != "admin":
        raise HTTPException(status_code=403, detail="Invalid admin password")
    
    is_update = d.name in menu
    menu.update({d.name: (lambda x: x)(d.price)})
    msg = f"Dish '{d.name}' price updated to {d.price}" if is_update else f"Dish '{d.name}' added with price {d.price}"
    return {'ok': True, 'msg': msg}

# 5. Filter dishes cheaper than N
@app.get('/menu/filter/{N}', summary='5️⃣ Dishes cheaper than N💸', tags=['for user'])
def filter_menu(N: int):
    res = dict(filter(lambda item: item[1] < N, menu.items()))
    return res if res else {'msg': f'No dishes cheaper than {N}'}

# 6. Cheapest and most expensive dishes
@app.get('/menu/cheap_expensive', summary='6️⃣ Cheapest and most expensive💰', tags=['for user'])
def get_the_cheaper_and_expensive():
    if not menu:
        return {'msg': 'Menu is empty'}
    cheapest = min(menu.items(), key=lambda item: item[1])
    expensive = max(menu.items(), key=lambda item: item[1])
    return {
        'cheapest': {'name': cheapest[0], 'price': cheapest[1]},
        'most_expensive': {'name': expensive[0], 'price': expensive[1]}
    }

# 7. Drinks only
drinks = [drink for drink, price in menu.items() if drink in ['coffee', 'tea', 'juice']]
drinks = sorted(drinks, key=lambda x: menu[x])
@app.get('/menu/drinks', summary='7️⃣ Only drinks☕🥤', tags=['for user'])
def return_drinks():
    return drinks

# 8. Make order for user num
@app.post('/menu/order/{num}', summary='8️⃣ Make order🛒', tags=['for user'])
def make_order(num: int, dishes: str):
    """
    dishes: string, comma-separated names, e.g. "coffee, cake, juice"
    """
    dish_list = list(map(lambda x: x.strip(), dishes.split(',')))
    valid_dishes = list(filter(lambda x: x in menu, dish_list))
    if not valid_dishes:
        return {'msg': 'You selected nothing'}
    
    # making order
    order_dict = dict(map(lambda x: (x, menu[x]), valid_dishes))
    orders[num] = order_dict

    # total with discount
    total = reduce(lambda a, b: a + b, map(lambda x: x[1], order_dict.items()))
    if total > 500:
        total_discounted = int(total * 0.9)
        discount_msg = "🎉 Congrats! You have 10% discount!"
    else:
        total_discounted = total
        discount_msg = ""

    # красиво выводим
    result = '\n'.join(map(lambda x: f"{x[0]+1}. {x[1][0]} — {x[1][1]} руб.", enumerate(order_dict.items())))
    
    return {
        'order': result,
        'total': total,
        'total_with_discount': total_discounted,
        'discount': discount_msg
    }

if __name__ == '__main__':
    uvicorn.run(app, host='127.0.0.1', port=8000)