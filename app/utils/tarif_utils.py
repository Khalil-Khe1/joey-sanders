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

    list_categories = []
    current = {
        'categorie': '###',
        'temps': time,
        'zone': timezone,
        'date_debut': date,
        'date_fin': date,
        'achat_adulte': 0,
        'recommande_adulte': 0,
        'achat_enfant': 0,
        'recommande_enfant': 0,
        'devise': 'EUR'    
    }

    selected_variants = list(filter(lambda e: group['id'] in e['group_ids'], variants)) # Find variants in group

    #group_name = group_name if not time else f'{group_name} - {time.replace(":", "h")} {timezone}'

    adult_ticket = 0
    adult_purchase = 0
    child_ticket = 0
    child_purchase = 0

    group_name = None
    list_names = []
    for selected_variant in selected_variants:
        if selected_variant['languages'] not in [['en'], ['fr'], ['en', 'fr'], []]:
            continue
        if selected_variant['variant_type'].lower() not in ['adult', 'child']:
            continue

        selected_price = None
        for pricev in price_variants:
            if(selected_variant['id'] == pricev['id']):
                selected_price = pricev
        if not selected_price:
            continue

        group_name = parse_group_and_label(clean_group_name(group['name']), clean_label(selected_variant['label']))
        if group_name != current['categorie']:
            if current['categorie'] != '###':
                list_categories.append(current)
                current = {
                    'categorie': 'awaiting_new_name',
                    'temps': time,
                    'zone': timezone,
                    'date_debut': date,
                    'date_fin': date,
                    'achat_adulte': 0,
                    'recommande_adulte': 0,
                    'achat_enfant': 0,
                    'recommande_enfant': 0,
                    'devise': 'EUR'    
                }
            current['categorie'] = group_name

        if(selected_variant['variant_type'].lower() == 'adult'):
            current['recommande_adulte'] = selected_price['price_mediation']['total_retail_price_incl_vat']
            current['achat_adulte'] = (
                current['recommande_adulte'] - selected_price['price_mediation']['distributor_commission_excl_vat']
            )
        elif(selected_variant['variant_type'].lower() == 'child'):
            current['recommande_enfant'] = selected_price['price_mediation']['total_retail_price_incl_vat']
            current['achat_enfant'] = (
                current['recommande_enfant'] - selected_price['price_mediation']['distributor_commission_excl_vat']
            )

    return list_categories.__add__([current]) if group_name else None

def create_category(
    variants : list, 
    groups : list, 
    time : str, 
    timezone : str, 
    date : str, 
    price_variants : list):
    categories = []
    time = time.replace(':', 'h')

    #groups = clean_groups(groups)
    for group in groups:
        returned_categories = process_category(variants, group, time, timezone, date, price_variants)
        if returned_categories:
            categories.extend(returned_categories)

    return categories

def timegroup_categories(categories, time):
    arr = []
    for day in categories:
        for tarif in day:
            if time == tarif['temps']:
                arr.append(tarif)
    res = {}
    for item in arr:
        if item['categorie'] not in res:
            res[item['categorie']] = []
        res[item['categorie']].append(item)
    
    return res

def process_cleaning(categories, time):
    res = []
    compare_keys = ['categorie', 'achat_adulte', 'recommande_adulte', 'achat_enfant', 'recommande_enfant']

    selected = timegroup_categories(categories, time)
    for value in selected.values():
        local_res = []
        size = len(value)
        if(size > 0):
            local_res.append(value[0])
        i = 1
        while i < size:
            current = value[i]
            if any(local_res[-1][key] != current[key] for key in compare_keys):
                local_res.append(current)
            if all(local_res[-1][key] == current[key] for key in compare_keys):
                local_res[-1]['date_fin'] = current['date_fin']
            i = i + 1
        res = res + local_res
    return res

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

def tarif_workflow(groups : list, variants : list, dates : list):
    categories = []

    for date in dates:
        for timeslot in date['timeslots']:
            tarifs = create_category(
                variants,
                groups,
                timeslot['time'],
                timeslot['timezone'],
                date['date'],
                timeslot['variants']
            )
            if not tarifs:
                continue
            categories.append(tarifs)
    return clean_categories(categories)

def extract_categories(tarifs : list):
    local_categs = []
    for item in tarifs:
        local_categs.append(f'{item["categorie"]}{" - " + item["temps"] if item["temps"] != "whole_day" else ""}')
    return list(set(local_categs))


# Experimental
def clean_groups(groups : list): # For segmenting multuple occurences
    occurences = {}
    new_groups = []

    for group in groups:
        clean_name = clean_group_name(group['name'])
        occurences[clean_name] = sum(1 for grp in groups if clean_group_name(grp['name']) == clean_name)
        occurences[clean_name] = occurences[clean_name] if occurences[clean_name] > 1 else 0

    for group in groups:
        clean_name = clean_group_name(group['name'])
        generated = {
            'id': group['id'],
            'name': clean_name + ('' if occurences[clean_name] == 0 else f' {str(occurences[clean_name])}')
        }
        occurences[clean_name] = occurences[clean_name] - 1
        new_groups.append(generated)
    return new_groups