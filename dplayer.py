#!/usr/bin/env python
# -*- coding: utf-8 -*-
# -----------------------------------------------------------
#  dodPoker:  a poker server to run automated texas hold'em
#  poker rounds with bots
#  Copyright (C) 2017 wobe-systems GmbH
# -----------------------------------------------------------
# -----------------------------------------------------------
# Configuration
# You need to change the setting according to your environment
import random

gregister_url = 'http://192.168.0.5:5001'
glocalip_adr = '192.168.0.5'

# -----------------------------------------------------------

from flask import Flask, request
from flask_restful import Resource, Api
import sys

from requests import put
import json

app = Flask(__name__)
api = Api(app)


# Web API to be called from the poker manager
class PokerPlayerAPI(Resource):
    ## return bid to caller
    #
    #  Depending on the cards passed to this function in the data parameter,
    #  this function has to return the next bid.
    #  The following rules are applied:
    #   -- fold --
    #   bid < min_bid
    #   bid > max_bid -> ** error **
    #   (bid > min_bid) and (bid < (min_bid+big_blind)) -> ** error **
    #
    #   -- check --
    #   (bid == 0) and (min_bid == 0) -> check
    #
    #   -- call --
    #   (bid == min_bid) and (min_bid > 0)
    #
    #   -- raise --
    #   min_bid + big_blind + x
    #   x is any value to increase on top of the Big blind
    #
    #   -- all in --
    #   bid == max_bid -> all in
    #
    #  @param data : a dictionary containing the following values - example: data['pot']
    #                min_bid   : minimum bid to return to stay in the game
    #                max_bid   : maximum possible bid
    #                big_blind : the current value of the big blind
    #                pot       : the total value of the current pot
    #                board     : a list of board cards on the table as string '<rank><suit>'
    #                hand      : a list of individual hand cards as string '<rank><suit>'
    #
    #                            <rank> : 23456789TJQKA
    #                            <suit> : 's' : spades
    #                                     'h' : hearts
    #                                     'd' : diamonds
    #                                     'c' : clubs
    #
    # @return a dictionary containing the following values
    #         bid  : a number between 0 and max_bid
    def __get_bid(self, data):
        #Initializing the Variables
        min_bid = data['min_bid']
        max_bid = data['max_bid']
        big_blind = data['big_blind']
        pot = data['pot']
        board = data['board']
        hand = data['hand']
        rank = data['rank']
        suit = data['suit']

        #Initializing Bid
        bid = {'bid' : random.randrange(0,max_bid)}

        #Conditions for FOLD
        if bid < min_bid:
            return 0
        elif bid > max_bid:
            return -1 #Returning Error
        elif ((bid > min_bid) and (bid < (min_bid + big_blind))):
            return -1 #Returning Error
        #Conditions for CHECK
        elif ((bid == 0) and (min_bid == 0)):
            return bid
        #Conditions for CALL
        elif ((bid == min_bid) and (min_bid > 0)):
            return bid

    # dispatch incoming get commands
    def get(self, command_id):

        data = request.form['data']
        data = json.loads(data)

        if command_id == 'get_bid':
            return {'bid': self.__get_bid(data)}
        else:
            return {}, 201

    # dispatch incoming put commands (if any)
    def put(self, command_id):
        return 201


api.add_resource(PokerPlayerAPI, '/dpoker/player/v1/<string:command_id>')


# main function
def main():
    # run the player bot with parameters
    if len(sys.argv) == 4:
        team_name = sys.argv[1]
        api_port = int(sys.argv[2])
        api_url = 'http://%s:%s' % (glocalip_adr, api_port)
        api_pass = sys.argv[3]
    else:
        print("""
DevOps Poker Bot - usage instruction
------------------------------------
python3 dplayer.py <team name> <port> <password>
example:
    python3 dplayer bazinga 40001 x407
        """)
        return 0

    # register player
    r = put("%s/dpoker/v1/enter_game" % gregister_url, data={'team': team_name, \
                                                             'url': api_url, \
                                                             'pass': api_pass}).json()
    if r != 201:
        raise Exception('registration failed: probably wrong team name')

    else:
        print('registration successful')

    try:
        app.run(host='0.0.0.0', port=api_port, debug=False)
    finally:
        put("%s/dpoker/v1/leave_game" % gregister_url, data={'team': team_name, \
                                                             'url': api_url, \
                                                             'pass': api_pass}).json()


# run the main function
if __name__ == '__main__':
    main()


