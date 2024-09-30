import os
import json
import copy
import sys
import math
#tabella con risultati
import pandas as pd # type: ignore
import logging

#parte grafica
import matplotlib.pyplot as plt # type: ignore
import matplotlib.patches as patches # type: ignore
import random


cooldown_perc= 0.2

#crea le cartelle da solo
def ensure_directory_exists(path):
    if not os.path.exists(path):
        print(f"Creating directory: {path}")
        os.makedirs(path)

#metodo che data la configurazione del tasks mi restituisce le coordinate di inserimento e mi restituisce la lista slots incrementata
def simple_allocate_task(id, configs, slots):
    config = configs[0]
    task_width = config["width"]
    task_height = config["height"]
    print(f"Dobbiamo inserire task alto: {task_height} e largo: {task_width}")
    
#metodo che mi restituisce le coordinate di inserimento 
    def choose_location(slots, task_width):
        min_val= min(slots)
        print("Il valore minore della lista è: "+str(min_val)+" ed è in posizione: "+str(slots.index(min_val)))

        while True:
            for i in range(len(slots) - task_width + 1):
            # Verifica se ci sono x-1 valori consecutivi minori o uguali al valore minimo
                if all(slots[i + j] <= min_val for j in range(task_width)):
                    print(f"Controllo che ci siano {task_width} valori consecutivi minori o uguali di: {min_val}")
                    return i, min_val

            min_val+=1
    
    position = choose_location(slots, task_width)

#metodo che una volta stabilito dove inserire un task, va a incrementare i corrispettivi valori di slots
    def incrementa_valori(slots, index, task_width, task_height, h_base):
        for i in range(index, index+task_width):
            cooldown_period=round(cooldown_perc*task_height)
            slots[i] = h_base+task_height+cooldown_period
            #print(f"Ora la posizione {i} è: {slots[i]}")
        return slots

    slots=incrementa_valori(slots, position[0], task_width, task_height, position[1])

    return position[0], position[1], slots

#metodo che data la configurazione del tasks mi restituisce le coordinate di inserimento e mi restituisce la lista slots incrementata
'''def simple_allocate_task(id, configs, slots, max_usage_percentage):
    config = configs[0]
    task_width = config["width"]
    task_height = config["height"]
    print(f"Dobbiamo inserire task alto: {task_height} e largo: {task_width}")

    def choose_location(slots, task_width):
        min_val = min(slots)
        print("Il valore minore della lista è: " + str(min_val) + " ed è in posizione: " + str(slots.index(min_val)))

        while True:
            for i in range(len(slots) - task_width + 1):
                if all(slots[i + j] <= min_val for j in range(task_width)):
                    position = check_processor_limit(slots, task_width, max_usage_percentage)
                    if position is not None:
                        return i, min_val

            min_val += 1

    position = choose_location(slots, task_width)

    def incrementa_valori(slots, index, task_width, task_height, h_base):
        for i in range(index, index + task_width):
            slots[i] = h_base + task_height
        return slots

    slots = incrementa_valori(slots, position[0], task_width, task_height, position[1])

    return position[0], position[1], slots'''
    

#devi fixare quel none

#metodo che mi restituisce la lista di task ordinata secondo l'height minore per ogni task    
def lowest_order(tasks):
    tasks_copy = copy.deepcopy(tasks)
    ordered_tasks = []

    for _ in range(len(tasks_copy)):
        i, h_max = min(enumerate(tasks_copy), key=lambda x: x[1]["configs"][0]["height"])
        ordered_tasks.append(tasks_copy[i])
        tasks_copy.pop(i)

    return ordered_tasks

#metodo che mi restituisce la lista di task ordinata secondo l'height maggiore per ogni task    
def highest_order(tasks):
    tasks_copy = copy.deepcopy(tasks)
    ordered_tasks = []

    for _ in range(len(tasks_copy)):
        i, h_max = max(enumerate(tasks_copy), key=lambda x: x[1]["configs"][0]["height"])
        ordered_tasks.append(tasks_copy[i])
        tasks_copy.pop(i)

    return ordered_tasks

#metodo che mi ordina in modo casuale i task
def random_order(tasks):
    rundom_list = tasks.copy()
    random.shuffle(rundom_list)
    return rundom_list

#vogliamo crere un metodo che mi vada a controllare se 
#in corrispenza del min sia possibile inserire un task, altrimenti lo incrementi
def control_remained(slots, tasks, indice_task):
    slots_def = slots.copy()
    tasks_def = tasks.copy()
    min_val = int(min(slots_def))
    contatore = int(slots_def.index(min_val))
    print(f"il prossimo valore minimo è: {min_val}, in POSIZIONE: {contatore}")

    def look_location(slots_def, contatore):
        width_min = 0
        prossimo_scalino_right = 99999999
        for i in range(contatore, int(len(slots_def))):
            if slots_def[i] == min_val:
                width_min = width_min + 1
            else:
                prossimo_scalino_right = slots_def[i]
                break
        
        prossimo_scalino_left = 999999999
        if contatore != 0:
            prossimo_scalino_left = slots[contatore - 1]
        
        scalino_minore = min(prossimo_scalino_right, prossimo_scalino_left)
        print(f"lo scalino MINORE è: {scalino_minore}")

        return width_min, scalino_minore
    
    width_scalino = look_location(slots_def, contatore)
    width_min = width_scalino[0]

    if tasks_def[indice_task]["configs"][0]["width"] <= width_min:
        return slots_def, tasks_def
    else:
        indice_da_modificare = indice_task
        indice_task = indice_task + 1 

        while indice_task < len(tasks_def):
            if tasks_def[indice_task]["configs"][0]["width"] <= width_min:
                task_da_spostare = tasks_def.pop(indice_task)
                tasks_def.insert(indice_da_modificare, task_da_spostare)
                print(f"ho spostato il task: {task_da_spostare['id']} come prossimo elemento della lista in posizione: {indice_da_modificare}")
                return slots_def, tasks_def
            else: 
                indice_task = indice_task + 1
        
        for i in range(contatore, contatore + width_min):
            slots_def[i] = width_scalino[1]
        print(f"Dopo aver incrementato la nuova configurazione è: {slots_def}")

    return control_remained(slots_def, tasks_def, indice_da_modificare)

'''def control_remained(slots, tasks, indice_task):    
    slots_def=slots.copy()
    tasks_def=tasks.copy()
    min_val = int(min(slots_def))
    contatore = int(slots_def.index(min_val))
    print(f"il prossimo valore minimo è: {min_val}, in POSIZIONE: {contatore}")

    def look_location(slots_def, contatore): #questo metodo mi dice quanti blocchi minimi ho attaccati, e l'altezza del prossim scalino
        width_min=0
        prossimo_scalino_right=99999999
        for i in range(contatore, int(len(slots_def))):
            if slots_def[i]==min_val:
                width_min = width_min+1
                #print(f"Incremento la larghezza disp fino a: {width_min}")
            else:
                prossimo_scalino_right=slots_def[i]
                #print(f"il prossimo scalino a DESTRA è: {prossimo_scalino_right}")
                break
        
        prossimo_scalino_left=999999999
        if contatore != 0:
            prossimo_scalino_left = slots[contatore-1]
            #print(f"il prossimo scalino a SINISTRA è: {prossimo_scalino_left}")
        
        scalino_minore=min(prossimo_scalino_right, prossimo_scalino_left)
        print(f"lo scalino MINORE è: {scalino_minore}")

        return width_min, scalino_minore
    
    width_scalino = look_location(slots_def, contatore) #trovo larghezza minima e h prossimo scalino
    #print(f"La larghezza da incrementare è: {width_scalino[0]}, fino a: {width_scalino[1]}")
    width_min = width_scalino[0] #estraggo larghezza del min

    if tasks_def[indice_task]["configs"][0]["width"]<=width_min: #lascia invariato il tutto se il prossimo task ci sta nello spazion min
        return slots_def, tasks_def
    else:
        indice_da_modificare = indice_task
        indice_task = indice_task+1 

        while indice_task < len(tasks_def):       #andiamo a vedere se i prossimi task riescono a riempire lo spazio
            if tasks_def[indice_task]["configs"][0]["width"]<=width_min:
                task_da_spostare=tasks_def.pop(indice_task)
                tasks_def.insert(indice_da_modificare, task_da_spostare)
                print(f"ho spostato il task: {task_da_spostare['id']} come prossimo elemento della lista in posizione: {indice_da_modificare}")
                return slots_def, tasks_def         #nel caso trovassimo un task lo mettiamo al prossimo posto della lista e chiudiamo
            
            else: 
                indice_task=indice_task+1           #continuiamo a iterare 
        
        #print(f"Nessun task riempie lo spazio largo: {width_min}, quindi lo incremento fino a: {width_scalino[1]}")
        for i in range(contatore, contatore+width_min):
            slots_def[i] = width_scalino[1]
        print(f"Dopo aver incrementato la nuova configurazione è: {slots_def}")

    return control_remained(slots_def, tasks_def, indice_da_modificare)'''

def control_perfect(slots, tasks, indice_task):    
    slots_def=slots.copy()
    tasks_def=tasks.copy()
    min_val = int(min(slots_def))
    contatore = int(slots_def.index(min_val))
    print(f"il prossimo valore minimo è: {min_val}, in POSIZIONE: {contatore}")

    def look_location(slots_def, contatore): #questo metodo mi dice quanti blocchi minimi ho attaccati, e l'altezza del prossim scalino
        width_min=0
        prossimo_scalino_right=99999999
        for i in range(contatore, int(len(slots_def))):
            if slots_def[i]==min_val:
                width_min = width_min+1
                #print(f"Incremento la larghezza disp fino a: {width_min}")
            else:
                prossimo_scalino_right=slots_def[i]
                #print(f"il prossimo scalino a DESTRA è: {prossimo_scalino_right}")
                break
        
        prossimo_scalino_left=999999999
        if contatore != 0:
            prossimo_scalino_left = slots[contatore-1]
            #print(f"il prossimo scalino a SINISTRA è: {prossimo_scalino_left}")
        
        scalino_minore=min(prossimo_scalino_right, prossimo_scalino_left)
        print(f"lo scalino MINORE è: {scalino_minore}")

        return width_min, scalino_minore
    
    width_scalino = look_location(slots_def, contatore) #trovo larghezza minima e h prossimo scalino
    #print(f"La larghezza da incrementare è: {width_scalino[0]}, fino a: {width_scalino[1]}")
    width_min = width_scalino[0] #estraggo larghezza del min

    if tasks_def[indice_task]["configs"][0]["width"]<=width_min: #lascia invariato il tutto se il prossimo task ci sta nello spazion min
        return slots_def, tasks_def
    else:
        indice_da_modificare = indice_task
        indice_task = indice_task + 1 

        while indice_task < len(tasks_def):       #andiamo a vedere se i prossimi task riescono a riempire perfettamente lo spazio
            if tasks_def[indice_task]["configs"][0]["width"]==width_min:
                task_da_spostare=tasks_def.pop(indice_task)
                tasks_def.insert(indice_da_modificare, task_da_spostare)
                print(f"ho spostato il task: {task_da_spostare['id']} come prossimo elemento PERFETTO della lista in posizione: {indice_da_modificare}")
                return slots_def, tasks_def         #nel caso trovassimo un task lo mettiamo al prossimo posto della lista e chiudiamo
            
            else: 
                indice_task=indice_task+1           #continuiamo a iterare 
        
        indice_task = indice_da_modificare + 1
        while indice_task < len(tasks_def):       #andiamo a vedere se i prossimi task riescono a riempire lo spazio
            if tasks_def[indice_task]["configs"][0]["width"]<width_min:
                task_da_spostare=tasks_def.pop(indice_task)
                tasks_def.insert(indice_da_modificare, task_da_spostare)
                print(f"ho spostato il task: {task_da_spostare['id']} come prossimo elemento della lista in posizione: {indice_da_modificare}")
                return slots_def, tasks_def         #nel caso trovassimo un task lo mettiamo al prossimo posto della lista e chiudiamo
            
            else: 
                indice_task=indice_task+1           #continuiamo a iterare 

        #print(f"Nessun task riempie lo spazio largo: {width_min}, quindi lo incremento fino a: {width_scalino[1]}")
        for i in range(contatore, contatore+width_min):
            slots_def[i] = width_scalino[1]
        print(f"Dopo aver incrementato la nuova configurazione è: {slots_def}")

    return control_perfect(slots_def, tasks_def, indice_da_modificare)


def control_just_perfect(slots, tasks, indice_task): 
    slots_def=slots.copy()
    tasks_def=tasks.copy()
    min_val = int(min(slots_def))
    contatore = int(slots_def.index(min_val))
    print(f"il prossimo valore minimo è: {min_val}, in POSIZIONE: {contatore}")

    def look_location(slots_def, contatore): #questo metodo mi dice quanti blocchi minimi ho attaccati, e l'altezza del prossim scalino
        width_min=0
        prossimo_scalino_right=99999999
        for i in range(contatore, int(len(slots_def))):
            if slots_def[i]==min_val:
                width_min = width_min+1
                #print(f"Incremento la larghezza disp fino a: {width_min}")
            else:
                prossimo_scalino_right=slots_def[i]
                #print(f"il prossimo scalino a DESTRA è: {prossimo_scalino_right}")
                break
        
        prossimo_scalino_left=999999999
        if contatore != 0:
            prossimo_scalino_left = slots[contatore-1]
            #print(f"il prossimo scalino a SINISTRA è: {prossimo_scalino_left}")
        
        scalino_minore=min(prossimo_scalino_right, prossimo_scalino_left)
        print(f"lo scalino MINORE è: {scalino_minore}")

        return width_min, scalino_minore
    
    width_scalino = look_location(slots_def, contatore) #trovo larghezza minima e h prossimo scalino
    #print(f"La larghezza da incrementare è: {width_scalino[0]}, fino a: {width_scalino[1]}")
    width_min = width_scalino[0] #estraggo larghezza del min

    if tasks_def[indice_task]["configs"][0]["width"]<=width_min: #lascia invariato il tutto se il prossimo task ci sta nello spazion min
        return slots_def, tasks_def
    else:
        indice_da_modificare = indice_task
        indice_task = indice_task + 1 

        while indice_task < len(tasks_def):       #andiamo a vedere se i prossimi task riescono a riempire perfettamente lo spazio
            if tasks_def[indice_task]["configs"][0]["width"]==width_min:
                task_da_spostare=tasks_def.pop(indice_task)
                tasks_def.insert(indice_da_modificare, task_da_spostare)
                print(f"ho spostato il task: {task_da_spostare['id']} come prossimo elemento PERFETTO della lista in posizione: {indice_da_modificare}")
                return slots_def, tasks_def         #nel caso trovassimo un task lo mettiamo al prossimo posto della lista e chiudiamo
            
            else: 
                indice_task=indice_task+1           #continuiamo a iterare 
        
        #print(f"Nessun task riempie perfettamente lo spazio largo: {width_min}, quindi lo incremento fino a: {width_scalino[1]}")
        for i in range(contatore, contatore+width_min):
            slots_def[i] = width_scalino[1]
        print(f"Dopo aver incrementato la nuova configurazione è: {slots_def}")

    return control_just_perfect(slots_def, tasks_def, indice_da_modificare)


#metodo che mi permette di calcolare il coefficiente del cut inbase ai parametri generali dell'istanza
def calculate_global_coeff_ott(W, area_min, num_tasks,tasks):
    # Coefficiente base
    base_coeff = 0.05
    print(f"il numero di task totali è : {num_tasks}")
    #numero processi= numero task*numero ripetizioni
    num_processes=0
    for task in tasks:
        num_processes+=task["repeat"]
    print(f"il numero di processi totali è : {num_processes}")

    # Calcolo di un coefficiente aggiuntivo basato sull'area e il numero di task
    max_height = max(task["configs"][0]["height"] for task in tasks)
    area_factor = area_min / (W * max_height)
    task_factor = math.log(num_tasks + 1) / math.log(25)

    # Calcolo del coefficiente ottimale globale
    coeff_ott = base_coeff + area_factor * 0.2 + task_factor * 0.1
    return coeff_ott



#Metodo che mi restituisce la lista dei task, eliminando se presenti task eccessivamente alti
def cut(tasks, W):
    tasks_cut=tasks.copy()
    area_min=0
    
    #Sommiamo per ogni task la propria area minima contando le ripetizioni
    for task in tasks_cut:
        for y in range (task["repeat"]):
            area_min += task["configs"][0]["height"] * task["configs"][0]["width"]

    print(f"L'area minima è: {area_min}")
    height_ott=area_min/W
    print(f"L'altezza massima accettabile è: {height_ott}")

    #tasks_cut = highest_order(tasks)
    # Calcolo di un coefficiente ottimale unico basato sui parametri globali
    num_tasks = len(tasks_cut)
    coeff_ott = calculate_global_coeff_ott(W, area_min, num_tasks, tasks)
    print(f"Il coefficiente ottimale è: {coeff_ott}")

    for task in tasks_cut:
        configs_cut = task["configs"]
        configs_to_remove = []

        for config in configs_cut:
            if config["height"] > (height_ott + height_ott * coeff_ott):
                configs_to_remove.append(config)

        for config in configs_to_remove:
            configs_cut.remove(config)
            print(f"Altezza eccessiva, rimuovo configs: {config}")

        task["configs"] = configs_cut
    
    return tasks_cut, height_ott


def left_righting (id, configs, slots):
    config = configs[0]
    task_width = config["width"]
    task_height = config["height"]
    print(f"Dobbiamo inserire task alto: {task_height} e largo: {task_width}")

    def choose_location(slots, task_width):
        min_val= min(slots)
        print("Il valore minore della lista è: "+str(min_val)+" ed è in posizione: "+str(slots.index(min_val)))

        while True:
            for i in range(len(slots) - task_width + 1):
            # Verifica se ci sono x-1 valori consecutivi minori o uguali al valore minimo
                if all(slots[i + j] <= min_val for j in range(task_width)) :
                    print(f"Controllo che ci siano {task_width} valori consecutivi minori o uguali di: {min_val}")
                    return i, min_val

            min_val+=1
    
    position = choose_location(slots, task_width) #position 0=i, position 1=min

    def incrementa_valori(slots, index, task_width, task_height, h_base):
        for i in range(index, index+task_width):
            cooldown_period=round(cooldown_perc*task_height)
            slots[i] = h_base+task_height+cooldown_period
        return slots

    safety_index = position[0]
    index_mod = position[0]
    contatore=0
    right_step = 99999999
    left_step = 99999999

    #vado a controllare se lo scalino più alto è right or left rispetto a min_val
    while index_mod < len(slots):
        if slots[index_mod] <= position[1]:
            contatore += 1
            index_mod += 1
        else: 
            right_step = slots[index_mod]
            break
        
    if safety_index != 0:
        left_step = slots[safety_index-1]

    if left_step > right_step:
        slots = incrementa_valori(slots, position[0], task_width, task_height, position[1])

    else:
        safety_index += contatore - task_width
        position = (safety_index, position[1])
        slots = incrementa_valori(slots, safety_index, task_width, task_height, position[1])


    return position[0], position[1], slots




def main(file_path, output_dir):

    frase=[]

    logging.info("Entering main function")
    result = {"status": "failed", "data": {}, "error": ""}  # Inizializza result con un valore di default

    
    
    # Leggi il file di input
    try:
        with open(file_path, 'r') as f:
            data = json.load(f)
            logging.debug(f"Data from {file_path}: {data}")  # Debug: stampa i dati letti
    except FileNotFoundError:
        logging.error(f"File not found: {file_path}")
        result["error"] = f"File not found: {file_path}"
        return result
    except json.JSONDecodeError:
        logging.error(f"Invalid JSON in file: {file_path}")
        result["error"] = f"Invalid JSON in file: {file_path}"
        return result

    # Verifica che 'tasks' sia una lista
    if not isinstance(data.get('instance', {}).get('tasks'), list):
        logging.error("Invalid data format: 'tasks' should be a list")
        return {"error": "Invalid data format: 'tasks' should be a list"}

    with open(file_path, "r") as file:
        instance = json.load(file)

        wmax = int((instance["instance"])['wmax'])
        W = int((instance["instance"])['W'])
        n_tasks = int((instance["instance"])['ntasks'])
        tasks = (instance["instance"])['tasks']

        print(f"W: {W}")
        print(f"n_tasks: {n_tasks}")


        slots = [0] * W
        print(slots)
        painted_area = 0

    

        # applico cut
        cut_result = cut(tasks, W)
        tasks = cut_result[0]
        for task in tasks:
            print("L'altezza cut del task "+str(task["id"])+ " è: " + str(task["configs"][0]["height"]))
        h_ideale = cut_result[1]

        # 1: ordino i task secondo altezza crescente
        tasks = highest_order(tasks)
        for task in tasks:
            print("L'altezza max del task è: " + str(task["configs"][0]["height"]))

        # 2: ordino i task secondo altezza decrescente
        '''tasks = lowest_order(tasks)
        for task in tasks:
            print("L'altezza min del task è: " + str(task["configs"][0]["height"]))'''

        assigned_tasks = {
            "id": [],
            "configs": [],
            "x": [],
            "y": []
        }

        tasks_mod = copy.deepcopy(tasks)
        slots_mod = slots

        for i in range(n_tasks):
            for y in range(tasks_mod[i]["repeat"]):
                if all(elemento != 0 for elemento in slots_mod):
                    id = int(tasks_mod[i]["id"])
                    configs = tasks_mod[i]["configs"]
                    painted_area += tasks_mod[i]["configs"][0]["height"] * tasks_mod[i]["configs"][0]["width"]

                    # Verifica del vincolo di utilizzo dei processori
                    '''position = check_processor_limit(slots_mod, configs[0]["width"], max_usage_percentage)
                    if position is not None:
                        insert = left_righting(id, configs, slots_mod)
                    else:
                        print(f"Non è stato possibile allocare il task {id} rispettando il vincolo. Inserisco spazi bianchi...")
                        for j in range(len(slots_mod)):
                            if slots_mod[j] == 0:
                                slots_mod[j] = -1  # Segna uno spazio bianco
                        continue  # Passa al prossimo task'''

                    insert=left_righting(id, configs, slots_mod)

                    assigned_tasks["id"].append(id)
                    assigned_tasks["configs"].append(configs[0])
                    assigned_tasks["x"].append(insert[0])
                    assigned_tasks["y"].append(insert[1])
                    slots_mod = insert[2]
                    print(f"Abbiamo inserito il task ID: {assigned_tasks['id'][-1]} in posizione: {assigned_tasks['x'][-1]} x e: {assigned_tasks['y'][-1]} y")
                    print(f"La nuova configurazione è: " f"{slots_mod}")
                
                else:
                    #applichiamo il control_remained
                    '''new_slots_tasks = control_remained(slots_mod, tasks_mod, i)
                    slots_mod=new_slots_tasks[0]
                    tasks_mod=new_slots_tasks[1]
                    print("La lista di slots in cui inseriamo il prossimo task sara:")
                    print(slots_mod)'''

                    #applichiamo il control_perfect
                    new_slots_tasks = control_perfect(slots_mod, tasks_mod, i)
                    slots_mod=new_slots_tasks[0]
                    tasks_mod=new_slots_tasks[1]
                    print("La lista di slots in cui inseriamo il prossimo task sara:")
                    print(slots_mod)

                    # Se ci sono ancora task da allocare e non si riesce a trovare uno slot disponibile
                    if all(elemento != 0 for elemento in slots_mod):
                                
                        id = int(tasks_mod[i]["id"])
                        configs = tasks_mod[i]["configs"]
                        #controllare se attivo o meno il metodo cut
                        painted_area+=tasks_mod[i]["configs"][0]["height"] * tasks_mod[i]["configs"][0]["width"]

                        insert=left_righting(id, configs, slots_mod)

                        assigned_tasks["id"].append(id)
                        assigned_tasks["configs"].append(configs[0])
                        assigned_tasks["x"].append(insert[0])
                        assigned_tasks["y"].append(insert[1])
                        slots_mod = insert[2]
                        print("Abbiamo inserito il task ID: "+str(assigned_tasks["id"][-1])+ " in posizione: "+str(assigned_tasks["x"][-1])+ " x e: "+str(assigned_tasks["y"][-1])+ " y")
                        print(f"La nuova configurazione è: " f"{slots_mod}")

                    else:
                        # Inserimento del task senza la verifica del vincolo, ma con l'inserimento degli spazi bianchi
                        id = int(tasks_mod[i]["id"])
                        configs = tasks_mod[i]["configs"]
                        painted_area += tasks_mod[i]["configs"][0]["height"] * tasks_mod[i]["configs"][0]["width"]

                        insert = simple_allocate_task(id, configs, slots_mod)

                        assigned_tasks["id"].append(id)
                        assigned_tasks["configs"].append(configs[0])
                        assigned_tasks["x"].append(insert[0])
                        assigned_tasks["y"].append(insert[1])
                        slots_mod = insert[2]
                        print(f"Abbiamo inserito il task ID: {assigned_tasks['id'][-1]} in posizione: {assigned_tasks['x'][-1]} x e: {assigned_tasks['y'][-1]} y")
                        print(f"La nuova configurazione è: " f"{slots_mod}")


        h_max = max(slots_mod)
        print(f"L'altezza MASSIMA che abbiamo raggiunto è: {h_max}")

        h_ideale = int(painted_area / W) + 1
        print(f"L'altezza IDEALE che abbiamo raggiunto è: {h_ideale}")

        surface_tot=int(h_max*W)
        print(f"L'indice di bilanciamento è: {painted_area/surface_tot*100}")

        aumento_h_percent = int(((h_max / h_ideale) - 1) * 100)
        print(f"L'OP registrato è: {aumento_h_percent}")

        resulto = {'NomeFile': os.path.splitext(os.path.basename(file_path))[0], 'Ideale': h_ideale, 'Raggiunta': h_max, '%': aumento_h_percent}
        frase.append(resulto)

        colori = ['#FFB347', '#A2CD5A', '#EE82EE', '#00BFFF', '#FF6347', '#9370DB', '#7FFFD4', '#D2691E']
        fig, ax = plt.subplots()
        fig.set_figwidth(8)
        fig.set_figheight(8)

        for i in range(len(assigned_tasks["id"])):
            x = assigned_tasks["x"][i]
            y = assigned_tasks["y"][i]
            dim = assigned_tasks["configs"][i]
            color_index = assigned_tasks["id"][i] % 8
            colore = colori[color_index]
            ampx = int(h_max / W)
            rettangolo = patches.Rectangle((ampx * x, y), ampx * dim["width"], dim["height"], edgecolor='black', facecolor=colore)
            ax.add_patch(rettangolo)
            # Aggiungi rettangoli bianchi per gli spazi vuoti
            rettangolo_bianco = patches.Rectangle((ampx * x, y+dim["height"]), ampx * dim["width"], round(cooldown_perc*dim["height"]), edgecolor='black', facecolor='white')
            ax.add_patch(rettangolo_bianco)
            
        ax.set_xlim(0, W)
        ax.set_ylim(0, h_max + 10)
        ax.set_aspect('equal', adjustable='box')
        ax.set_xticks([ampx * tick for tick in ax.get_xticks()])
        ax.set_xticklabels([])
        ax.set_yticks(range(0, int(h_max) + 10, 50))

        # MODIFICA: Assicura che la directory di output esista e salva l'immagine
        output_image_dir = os.path.join(output_dir, "results")
        ensure_directory_exists(output_image_dir)
        output_image_path = os.path.join(output_image_dir, f"{os.path.splitext(os.path.basename(file_path))[0]}.jpeg")
        logging.info(f"Saving image to: {output_image_path}")
        plt.savefig(fname=output_image_path)

        plt.close()
        logging.info("Exiting main function")
        #result = {frase}
        result = {"status": "success", "data": "okokgiorgio"} #data}
        #print(assigned_tasks)
        print (frase)
        return result
    

if __name__ == "__main__":
    if len(sys.argv) != 3:
        print(json.dumps({"error": "Usage: python scheduling_2d.py <file_path> <output_dir>"}))
        sys.exit(1)
    
    file_path = sys.argv[1]
    output_dir = sys.argv[2]
    try:
        result = main(file_path, output_dir)
        print(json.dumps(result))
    except Exception as e:
        logging.error("Exception occurred", exc_info=True)
        print(json.dumps({"error": str(e)}))

#a seconda dell'algoritmo che crei dovresti salvare risultati e immagini in una cartella specifica
