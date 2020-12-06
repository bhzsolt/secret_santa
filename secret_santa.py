#!/usr/bin/python3

import random
from os import remove
from sendmail import send_mail
from argparse import ArgumentParser

def mkperson(name, mail, data):
    return {'name': name, 'mail': mail, 'data': data}

def get_players(filename):
    with open(filename, 'r') as f:
        contents = f.read().strip()
    lines = contents.split('\n')
    players = []
    sender, pwd = lines[0].split(':\t')
    for line in lines[1:]:
        field = line.split(':\t')
        name = field[0]
        field = field[1].split('\t')
        players.append(mkperson(field[0], field[0], field[1:]))
    return sender, pwd, players

def valid(x):
    i = 0
    while i < len(x):
        if x[i] == i:
            return False
        i += 1
    return True

def create_draw(who):
    found = False
    while not found:
        x = list(range(1, len(who)))
        random.shuffle(x)
        found = valid(x)
    x.append(0)
    x.insert(0,0)
    target = [None]*len(who)
    i = 0
    while i < len(who):
        target[x[i]] = who[x[i + 1]]
        i += 1
    return target

if __name__ == '__main__':
    parser = ArgumentParser('Secret Santa')
    parser.add_argument('-c', '--config', required=True)
    args = parser.parse_args()

    if args.config == None:
        print('[ERROR]: no config file specified')
        exit(1)

    sender, password, players = get_players(args.config)
    print(sender)
    print(password)
    print(players)

    book = dict(map(lambda x: (x['name'], x), players))
    draw = create_draw(list(map(lambda x: x['name'], players)))

    for i in range(0, len(players)):
        name = players[i]['name']
        filename = '/tmp/{}.txt'.format(name)
        address = players[i]['mail']
        with open(filename, 'w') as f:
            f.write('Name: {}\nEmail address: {}\nAdditional data: {}\n'.format(
                book[draw[i]]['name'],
                book[draw[i]]['mail'],
                book[draw[i]]['data']
            ))
        send_mail(['-s', sender, '-p', password, '-f', filename, '-r', address, '-n', name])
        remove(filename)
