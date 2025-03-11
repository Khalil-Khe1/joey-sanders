import re

def clean_label(label : str):
    original = label

    d = ['Adulte', 'Enfant', 'Jeune', 'Bébé']
    for value in d:
        label = label.replace(value, '')

    i = 0
    while i < len(label):
        tmp = list(label)
        if(i == 0) or (i == len(label) - 1):
            if(tmp[i] == ' '):
                tmp[i] = ''
                i = -1
            if(tmp[i] in ['-', ':', '+']):
                tmp[i] = ''
                i = -1
        label = ''.join(tmp).replace('  ', ' ')
        i += 1

    return label

def clean_group_name(label : str):
    d = {'Default':  'Standard', 'English': 'Anglais', 'French': 'Français'}
    for key, value in d.items():
        label = label.replace(key, value)
    pattern = '[ ]?[\[\(]*[0-2][0-9]:[0-5][0-9][\]\)]*[ ]?|[ ]?[\[\(]*[0-2][0-9]h[0-5][0-9][\]\)]*[ ]?'
    label = re.sub(pattern, '', label)

    return label

def parse_group_and_label(group : str, variant : str):
    return group if (variant.lower() in group.lower()) else f'{group} - {variant}'

def process_category(variants : list, 
    group : dict, 
    time : str, 
    timezone : str, 
    date : str, 
    price_variants : list):
    import math

    selected_variants = list(filter(lambda e: group['id'] in e['group_ids'], variants)) # Find variants in group

    #group_name = group_name if not time else f'{group_name} - {time.replace(":", "h")} {timezone}'

    adult_ticket = 0
    adult_purchase = 0
    child_ticket = 0
    child_purchase = 0
    group_name = ''
    for selected_variant in selected_variants:
        print(clean_group_name(group['name'])) # Clean redundancies

        if selected_variant['languages'] not in [['en'], ['fr'], ['en', 'fr'], []]:
            continue

        filtered = list(filter(lambda e: e['id'] == selected_variant['id'], price_variants)) # Find variants in timeslots
        selected_price = None
        for pricev in price_variants:
            if(selected_variant['id'] == pricev['id']):
                selected_price = pricev
        if not selected_price:
            continue

        group_name = parse_group_and_label(
            clean_group_name(group['name']), 
            clean_label(selected_variant['label'])
        )
        if(selected_variant['variant_type'].lower() == 'adult'):
            adult_ticket = selected_price['price_mediation']['sale_ticket_value_incl_vat']
            adult_purchase = adult_ticket - selected_price['price_mediation']['distributor_commission_excl_vat']
        elif(selected_variant['variant_type'].lower() == 'child'):
            child_ticket = selected_price['price_mediation']['total_retail_price_incl_vat']
            child_purchase = child_ticket - selected_price['price_mediation']['distributor_commission_excl_vat']
    
    return {
        'categorie': group_name,
        'temps': time,
        'zone': timezone,
        'date_debut': date,
        'date_fin': date,
        'achat_adulte': adult_purchase,
        'recommande_adulte': adult_ticket,
        'achat_enfant': child_purchase,
        'recommande_enfant': child_ticket,
        'devise': 'EUR'    
    }

def create_category(
    variants : list, 
    groups : list, 
    time : str, 
    timezone : str, 
    date : str, 
    price_variants : list):
    categories = []
    time = time.replace(':', 'h')

    for group in groups:
        category = process_category(variants, group, time, timezone, date, price_variants)
        categories.append(category)

    return categories

def timegroup_categories(categories, time):
    #time = '14h00'
    res = []
    for day in categories:
        for tarif in day:
            if time == tarif['temps']:
                res.append(tarif)
                break
    for item in res:
        if item['achat_enfant'] > 0:
            pass
    return res

def process_cleaning(categories, time):
    local_res = []
    compare_keys = ['categorie', 'achat_adulte', 'recommande_adulte', 'achat_enfant', 'recommande_enfant']

    selected = timegroup_categories(categories, time)
    size = len(selected)
    if(size > 0):
        local_res.append(selected[0])
    i = 1
    while i < size:
        current = selected[i]
        if any(local_res[-1][key] != current[key] for key in compare_keys):
            local_res.append(current)
        if all(local_res[-1][key] == current[key] for key in compare_keys):
            local_res[-1]['date_fin'] = current['date_fin']
        i = i + 1
    return local_res

def clean_categories(categories):
    res = []

    hour = 0
    minutes = ['00', '15', '30', '45']
    while hour < 24:
        for minute in minutes:
            text_hour = '{:02d}'.format(hour)
            time = f'{text_hour}h{minute}'
            res = res + process_cleaning(categories, time)
        hour = hour + 1
    res = res + process_cleaning(categories, 'whole_day')
    return res


