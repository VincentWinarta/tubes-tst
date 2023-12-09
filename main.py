from fastapi import FastAPI, HTTPException, Depends, status, APIRouter
from fastapi.security import OAuth2PasswordBearer, OAuth2PasswordRequestForm
from fastapi.encoders import jsonable_encoder
import jwt
import json
from pydantic import BaseModel
from datetime import datetime, timedelta
import geocoder
import time
from passlib.hash import bcrypt
import requests
from location import get_location
from req import get_reservations
from pymongo import MongoClient
from fastapi.middleware.cors import CORSMiddleware



client = MongoClient("mongodb+srv://vincentw:123@cluster0.juxshun.mongodb.net/?retryWrites=true&w=majority")
db = client['coworking']
collection = db['tst']

data = collection.find_one()

def write_data(data):
    collection.replace_one({}, data, upsert=True)

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
    duration: int

# json_filename = "main.json"
# with open(json_filename, "r") as read_file:
#     data = json.load(read_file)

auth = APIRouter(tags=["Authentication"],)
user = APIRouter(tags=["Users"],)
order = APIRouter(tags=["Orders"],)
loca = APIRouter(tags=["Location"],)
reserve = APIRouter(tags=["Reserve"],)


class signin_user:
    def __init__(self, id, username, pass_hash):
        self.id = id
        self.username = username
        self.pass_hash = pass_hash

    def verify_password(self, password):
        return bcrypt.verify(password, self.pass_hash)

# def write_data(data):
#     with open("main.json", "w") as write_file:
#         json.dump(data, write_file, indent=4)

oauth2_scheme = OAuth2PasswordBearer(tokenUrl='token')

app = FastAPI()

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["GET", "POST", "PUT", "DELETE"],
    allow_headers=["*"],
)

JWT_SECRET = 'coworkingsecret'
ALGORITHM = 'HS256'



def get_user_by_username(username):
    for desain_user in data['signin_user']:
        if desain_user['username'] == username:
            return desain_user
    return None

def authenticate_user(username: str, password: str):
    user_data = get_user_by_username(username)
    if not user_data:
        return None

    user = signin_user(id=user_data['id'], username=user_data['username'], pass_hash=user_data['pass_hash'])

    if not user.verify_password(password):
        return None

    return user


@auth.post('/token')
async def generate_token(form_data: OAuth2PasswordRequestForm = Depends()):
    user = authenticate_user(form_data.username, form_data.password)

    if not user:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED, 
            detail='Invalid username or password'
        )

    token = jwt.encode({'id': user.id, 'username': user.username}, JWT_SECRET, algorithm=ALGORITHM)

    return {'access_token': token, 'token_type': 'bearer'}

async def get_current_user(token: str = Depends(oauth2_scheme)):
    try:
        payload = jwt.decode(token, JWT_SECRET, algorithms=['HS256'])
        user = get_user_by_username(payload.get('username'))
        return signin_user(id=user['id'], username=user['username'], pass_hash=user['pass_hash'])
    except:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED, 
            detail='Invalid username or password'
        )

@auth.post('/signin_user')
async def create_user(username: str, password: str):
    last_user_id = data['signin_user'][-1]['id'] if data['signin_user'] else 0
    user_id = last_user_id + 1
    user = jsonable_encoder(signin_user(id=user_id, username=username, pass_hash=bcrypt.hash(password)))
    data['signin_user'].append(user)
    write_data(data)
    return {'message': 'User created successfully'}

@auth.get('/signin_user/me')
async def get_user(user: signin_user = Depends(get_current_user)):
    return {'id': user.id, 'username': user.username}

@user.get('/users')
async def read_all_users():
	return data['users']

@loca.get('/test')
async def loc():
    alamat = get_location()["ip"]
    dpt = geocoder.ip(alamat)
    return dpt.latlng

@order.get('/orders')
async def read_all_orders(user: signin_user = Depends(get_current_user)):
	return data['orders']

@user.post('/users')
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

		# with open("main.json","w") as write_file:
		# 	json.dump(data, write_file, indent=4)
		write_data(data)

		return "User ID " + str(userid) + " is added successfully."
	
	raise HTTPException(
		status_code=404, detail=f'item not found'
	)

@order.post('/orders')
async def add_order(orderid: int, userid: int, user: signin_user = Depends(get_current_user)):
    item_found = False
    for order_item in data['orders']:
        if order_item['orderid'] == orderid:
            item_found = True
            return "Order ID " + str(orderid) + " is already exists."
    if not item_found:
        latitude = -7
        longitude = 108
        alamat = get_location()["ip"]
        dpt = geocoder.ip(alamat)
        currentlat = dpt.lat
        currentlong = dpt.lng
        orderstart = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        duration = 0
        while ((str(currentlat) == str(latitude)) and (str(currentlong) == str(longitude))):
            time.sleep(1)
            duration += 1
        orderstop = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        new_order = {
            "orderid": orderid,
            "userid": userid,
            "orderstart": orderstart,
            "orderstop": orderstop,
            "duration": duration
        }

        data['orders'].append(new_order)

        # with open("main.json", "w") as write_file:
        #     json.dump(data, write_file, indent=4)
        write_data(data)

        return "User ID " + str(userid) + " is added successfully."

    raise HTTPException(
        status_code=404, detail=f'item not found'
    )


    
@order.delete('/orders/{orderid}')
async def delete_order(orderid: int, user: signin_user = Depends(get_current_user)):
	for order_item in data['orders']:
		if order_item['orderid'] == orderid:
			data['orders'].remove(order_item)

			# with open("main.json","w") as write_file:
			# 	json.dump(data, write_file, indent=4)
			write_data(data)
			return "Order with ID " + str(orderid) + " deleted successfully."

	return "Order ID not found."

	raise HTTPException(
	status_code=404, detail=f'item not found'
	)

@reserve.get('/reserve')
async def get_reservasi():
    list_reservasi = []
    for i in get_reservations():
        list_reservasi.append({k:i[k]for k in ("id_table","hourstart")})

    return list_reservasi



app.include_router(auth)
app.include_router(user)
app.include_router(order)
app.include_router(loca)
app.include_router(reserve)
