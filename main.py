from fastapi import FastAPI, HTTPException
import json
from pydantic import BaseModel
from datetime import datetime
import geocoder
import time

class users(BaseModel):
	userid: int
	firstname: str
	lastname: str
	email: str
	
class orders(BaseModel):
	orderid: int
	userid: int
	orderstart: datetime
	orderstop: datetime
	duration : int
	
json_filename="main.json"
with open(json_filename,"r") as read_file:
	data = json.load(read_file)
	

app = FastAPI()
@app.get('/users')
async def read_all_users():
	return data['users']

@app.get('/test')
async def loc():
	g=geocoder.ip('me')
	return g.latlng

@app.get('/orders')
async def read_all_orders():
	return data['orders']

@app.post('/users')
async def add_user(userid: int, firstname: str, lastname: str, email: str):
	item_found = False
	for user_item in data['users']:
		if user_item['userid'] == userid:
			item_found = True
			return "User ID "+str(userid)+" is already exists."
	
	if not item_found:
		new_user = {
			"userid": userid,
			"firstname": firstname,
			"lastname": lastname,
			"email": email
		}

		data['users'].append(new_user)

		with open("main.json","w") as write_file:
			json.dump(data, write_file, indent=4)

		return "User ID " + str(userid) + " is added successfully."
	
	raise HTTPException(
		status_code=404, detail=f'item not found'
	)

@app.post('/orders')
async def add_order(orderid: int, userid: int):
	item_found = False
	for order_item in data['orders']:
		if order_item['orderid'] == orderid:
			item_found = True
			return "Order ID "+str(orderid)+" is already exists."
	if not item_found:
		latitude=-7
		longitude=108
		g=geocoder.ip('me')
		orderstart=datetime.now().strftime("%Y-%m-%d %H:%M:%S")
		duration=0
		while ((str(g.lat)==str(latitude)) and (str(g.lng)==str(longitude))):
			g=geocoder.ip('me')
			time.sleep(1)
			duration+=1
		orderstop=datetime.now().strftime("%Y-%m-%d %H:%M:%S")
		new_order = {
			"orderid": orderid,
			"userid": userid,
			"orderstart":orderstart,
			"orderstop":orderstop,
			"duration":duration
		}

		data['orders'].append(new_order)

		with open("main.json","w") as write_file:
			json.dump(data, write_file, indent=4)

		return "User ID " + str(userid) + " is added successfully."
	
	raise HTTPException(
		status_code=404, detail=f'item not found'
	)
    
@app.delete('/orders/{orderid}')
async def delete_order(orderid: int):
	for order_item in data['orders']:
		if order_item['orderid'] == orderid:
			data['orders'].remove(order_item)

			with open("main.json","w") as write_file:
				json.dump(data, write_file, indent=4)
			return "Order with ID " + str(orderid) + " deleted successfully."

	return "Order ID not found."

	raise HTTPException(
	status_code=404, detail=f'item not found'
	)