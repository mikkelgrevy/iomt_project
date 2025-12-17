import network
import urequests
import time
import json
import machine
from machine import Pin, UART # NY IMPORT

# --- KONFIGURATION ---
WIFI_SSID = "Pixel"
WIFI_PASSWORD = "internet"
SERVER_IP = "10.24.5.194"  # HUSK: Ret til din laptops/VM's IP
SERVER_PORT = 8000
PATIENT_ID = 2  # HUSK: Ret til et ID der findes i din DB

BASE_URL = "http://{}:{}".format(SERVER_IP, SERVER_PORT)

# --- UART OPSÆTNING ---
uart = UART(2, baudrate=9600, tx=4, rx=5) # Opsætning af UART
is_ready_to_send = True

def send_command(command):
    """Sender kommando over UART og læser svar."""
    global is_ready_to_send
    
    command_str = f"{command}\n"
    uart.read() # Tømmer UART buffer før afsendelse
    print(f"-> Master sender via UART: {command_str.strip()}")
    
    start_time = time.time()
    uart.write(command_str)
    
    response = None
    # Venter på Slaven svarer, maksimalt 2 sekunder
    while (time.time() - start_time) < 2: 
        if uart.any():
            data = uart.readline() 
            if data:
                response = data.decode().strip()
                print(f"<- Master modtog via UART: {response}")
                break
        time.sleep_ms(10)
        
    if response == "OK_MOVED":
        return True
    else:
        return False

def connect_wifi():
    wlan = network.WLAN(network.STA_IF)
    wlan.active(False)
    wlan.active(True)
    if not wlan.isconnected():
        print('Forbinder til WiFi...')
        wlan.connect(WIFI_SSID, WIFI_PASSWORD)
        while not wlan.isconnected():
            time.sleep(1)
            print('.', end='')
    print('\nWiFi forbundet!')
    print('IP-adresse:', wlan.ifconfig()[0])

def sync_time():
    url = "{}/time".format(BASE_URL)
    print("Synkroniserer tid via HTTP fra:", url)
    try:
        response = urequests.get(url)
        if response.status_code == 200:
            t = response.json()
            response.close()
            
            rtc = machine.RTC()
            # Indstil RTC. Format: (year, month, day, weekday, hour, minute, second, subsecond)
            rtc.datetime((
                t['year'], 
                t['month'], 
                t['day'], 
                t['weekday'], 
                t['hour'], 
                t['minute'], 
                t['second'], 
                0
            ))
            print("Tid synkroniseret succesfuldt:", rtc.datetime())
        else:
            print("Fejl ved hentning af tid:", response.status_code)
            response.close()
    except Exception as e:
        print("Kunne ikke forbinde til server for tid:", e)

def get_config():
    url = "{}/dispenser/config/{}".format(BASE_URL, PATIENT_ID)
    print("Henter plan fra:", url)
    try:
        response = urequests.get(url)
        if response.status_code == 200:
            config = response.json()
            print("Plan modtaget:", config)
            response.close()
            return config
        else:
            print("Fejl ved hentning af config:", response.status_code)
            response.close()
            return None
    except Exception as e:
        print("Kunne ikke forbinde til server:", e)
        return None

def send_log(plan_id, status_bool):
    url = "{}/dispenser/log/".format(BASE_URL)
    data = {
        "plan_id": plan_id,
        "dispensed": status_bool,
        "taken": False, # Knappen håndteres senere
        "sensor_error": not status_bool # Hvis ikke dispenseret = fejl
    }
    print("Sender log til:", url, data)
    try:
        headers = {'Content-Type': 'application/json'}
        response = urequests.post(url, json=data, headers=headers)
        print("Log status:", response.status_code)
        response.close()
    except Exception as e:
        print("Fejl ved afsendelse af log:", e)

def dispense_medication(plan):
    global is_ready_to_send
    print("!!! TID TIL MEDICIN !!!")
    print("Dispenserer:", plan['dosage'])
    
    # --- ÆNDRET HER: Nu sender vi til Slaven ---
    success = False
    
    if is_ready_to_send:
        is_ready_to_send = False
        if send_command("NEXT_PILL"):
            print("Slave bekræftede: Motor har drejet!")
            success = True
        else:
            print("FEJL: Slave svarede ikke/fejlede!")
            success = False
        is_ready_to_send = True
    else:
        print("UART optaget - kunne ikke sende kommando.")
        success = False
    
    # Sender log baseret på UART-svaret
    send_log(plan['plan_id'], success)

def main():
    connect_wifi()
    sync_time()
    
    config = get_config()
    
    if not config:
        print("Ingen config. Stopper (eller venter på genstart).")
        return

    print("Starter overvågning...")
    while True:
        # Hent nuværende tid fra RTC
        t = machine.RTC().datetime()
        curr_h = t[4]
        curr_m = t[5]
        curr_s = t[6]
        
        # Print tid hvert 10. sekund for debugging
        if curr_s % 10 == 0:
            print("Klokken er {:02d}:{:02d}".format(curr_h, curr_m))
        
        # Tjek om nogen plan matcher NU
        for plan in config.get('plans', []):
            if plan['hour'] == curr_h and plan['minute'] == curr_m:
                # For at undgå den kører hele minuttet, tjekker vi om sekunder er lave
                if curr_s < 5: 
                    dispense_medication(plan)
                    time.sleep(5) # Vent så vi ikke trigger igen med det samme

        time.sleep(1)

if __name__ == "__main__":
    main()
