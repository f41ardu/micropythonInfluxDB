import time
from machine import Pin
import requests

url = "https://diskstation:6200/api/v2/write?org=private&bucket=GasMeter&precision=ns"

headers = {
        "Authorization": "Token {{your individual token}",
        "Content-Type": "text/plain; charset=utf-8",
        "Accept": "application/json"
}

# variables 
buttonState = 1
lastButtonState = 1
counter = 0 
step = 0.01
timeOut = 150 # if longer idle send number of counts only and 0.00

# set debug True or False
debug = True

# pins's 
#led = Pin(1, Pin.OUT,value = 0) -- not used 
button = Pin(5, Pin.IN, Pin.PULL_UP)

data = f"gasmeter,sensor_id=gasmeter counter={counter},trigger_step={step}"


def wait_pin_change(pin):
    # wait for pin to change value
    # it needs to be stable for a continuous 20ms
    cur_value = pin.value()
    
    active = 0
    #led.value(not led.value())
    if active < 20:
        act_value = pin.value()
        if  act_value != cur_value:
            active += 1
            
        else:
            active = 0
            cur_value = pin.value()
        time.sleep_ms(1)
    
    return act_value

print('... Ready to go ....')
timestamp = time.time()
while True:
    
    #if time.time() - timestamp > 5: ## used for simple tests
    #    print('.....',timestamp)
    #    timestamp = time.time()
        
    buttonState  = wait_pin_change(button)
    if buttonState != lastButtonState:
        if buttonState == 0:
            counter = counter + 1
            step = 0.01
            data = f"gasmeter,sensor_id=gasmeter counter={counter},trigger_step={step}"
            response = requests.post(url, headers=headers, data=data)
            if response.status_code == 204:
                print("Data posted successfully")
            else:
                print("Failed to post data")
                print("Status Code:", response.status_code)
                print("Response:", response.text)
            response.close()

            if debug:
                # print(counter)
                print(data)
            timestamp = time.time()
    # send counter after idle time (rrd) 
    elif time.time() - timestamp > timeOut:
            step = 0.00
            data = f"gasmeter,sensor_id=gasmeter counter={counter},trigger_step={step}"
            response = requests.post(url, headers=headers, data=data)
            if response.status_code == 204:
                print("Data posted successfully")
            else:
                print("Failed to post data")
                print("Status Code:", response.status_code)
                print("Response:", response.text)
            response.close()

            if debug:
                print(data)
                
            timestamp = time.time()
            
    lastButtonState = buttonState
