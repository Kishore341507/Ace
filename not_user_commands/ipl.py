import discord
from discord.ext import commands , tasks
from database import *
import asyncio
from discord.ext.commands import BucketType, cooldown
import random
import typing
from discord.ui import Button , View , Select
from discord import app_commands
import requests
from bs4 import BeautifulSoup
from datetime import datetime, timedelta
import uuid


class Event:
    def __init__(self, name , total_entry , entry_fee , win_money_distribution):
        self.id = str(uuid.uuid4())
        self.name = name
        self.total_members = total_members
        self.entry_fee = entry_fee
        self.win_money_distribution = win_money_distribution

event = {
            1 : {
            'id' : 1 ,
            'name' : 'One Above All' , 
            'matches' : ['all'] ,
            'max_entry' : 1000 ,
            'entry_fee' : 10 ,
            'price_poll' : 10000 ,
            'info' : ' ' , 
            'price_distribution' : { 1 : 10000 } , 
            'entries' : {} 
            }       
        }

class IPL(commands.Cog):

    def __init__(self , client):
        self.client = client
        self.live_score.start()
        self.fantasy_live = [ "5c496668-8076-4d58-a72a-105e1aeca978" ] 
        self.ipl_matches = ['048d4bdf-88de-4981-b330-03ceb18eb6a1', 'ab52f012-34b7-4a68-a1af-b95668255a40', '034ccab8-50ac-4dc4-affb-38c73cca0a49', '6e853a67-5625-434f-babd-5702dcd846a9', '9759d12a-14a6-42c2-bbe2-833c6f612ceb', 'c8742d20-c3cb-4423-aea1-b436f3ac65c3', '99c2990f-3e53-4cfa-8697-ab3d92b19f35', '4608a16f-c556-4f0d-acc3-63dda814fba8', '7535d936-2907-4b02-b68a-3e7465595e0a', 'e99467c0-dcbb-498e-8aaa-19b88f3a3029', '0bfed52d-36e4-406f-9458-9f3ce533398c', '7aa61b66-0f3c-4a50-8eab-e9e23e7c4fcd', '91ba8452-eb44-464d-8eae-6a53ed46f00a', '63179b6c-0560-45cc-a984-9ad0459c7542', 'a92711fa-55d1-42a1-8cd7-571a0f9fb614', '7f6df32a-e505-495f-9121-c6aca6235306', 'ae24cc6a-8e37-4fd1-bb18-638b56ec4989', '9d22f5ad-e9bc-4a66-82d5-03acfc599434', '0b8981a3-9ae5-442d-ad1a-baab2efbd9e3', 'a1f790e6-59c9-4c63-8b30-6b629531253d', 'cc301267-8a6c-4840-87ff-b7c43ce10bc4', '5c496668-8076-4d58-a72a-105e1aeca978', 'c4774b4c-c2f8-434f-8ee6-0bf8e2c02a99', '31075544-43d6-47a6-afd9-5467a06c6ca2', '10dd76d8-8343-4c72-8447-8bf6e37b609f', 'aeaac025-dd19-4033-a5db-8b93106f75d4', '80efa6af-240d-400c-893b-898152949a4c', 'c5299187-f030-4727-98e1-0667f4626ae5', 'b3216931-c54b-482f-94e6-5d803cc3199e', 'aa0bc972-2377-4407-9bc2-75e0c83c225d', '018878c0-36df-4634-9cc3-5c5ea02378b2', '065089a4-5ba8-4276-9d89-83079af4541c', 'b72aa256-3a2f-4536-bb4f-59cdebf04557', '9513145b-b401-4e72-a898-a4bd7c688be8', '86a12373-e6e4-4315-8da5-73781ef289e2', '043b41db-1968-46c1-997d-4f92833c5a5b', '8325cb10-1f7b-48f8-a41f-2f63799f8177', 'f2b8aa8a-f24c-40b4-99bb-4e6a222a1614', '97f38e12-a13c-4f3d-876f-89abc5da7fdd', '90118c8b-c48a-4eb1-bf1e-8a2ba119e0ea', 'f29a4077-8f04-4cba-90e4-e117b8a10f05', '0c25b28c-6099-486a-ab6f-704b3415728d', '18fd94bb-5218-4845-80c8-bb8400a40c24', 'f0b02afb-7bab-4fad-8724-bf6735b23d32', '7630f8ed-d96f-4ac5-adc9-8c3703c059a0', '6b9daa07-a9f3-46d2-a26a-cd9fde9dcb35', 'fce9c228-f766-4018-b7fc-31484106ebce', '40d33ba3-ac37-4d8b-a45c-d738167a8a39', '494e1d55-324c-42ee-850b-8de25f27f547', '2f9ce8ba-4c85-4e90-8140-d632037d35db', '08629a55-7d6e-4b82-8157-10c1d1eb4d02', '70b387b7-be48-491b-b58f-12b329867124', 'e8d137eb-0133-4b8b-92df-c573f3308e7a', 'bd011ee1-febe-454f-a038-46ef7bc66575', '114b5c32-f7bd-4486-b638-c513bdf80fc5', '3ed57184-bfde-4cd9-9c2e-6214dc12baae', 'd4100a0f-2edb-49d4-a66f-cb5f6695f295', '5db8818a-6291-4b65-a5aa-43cfe66da805', '26bb0e29-afe8-413f-8a43-53af922e4240', '8e3d0b98-0b9b-491b-bbf4-d455303aa020', '35198e8a-10d5-45fd-85f6-25c9ed0943f1', '6b34ffab-0b70-41aa-a56d-70d4eb607e24', 'd96cb055-6050-44b5-88e0-d52eb0314dce', 'b5df4a10-5ec6-4ae1-aa4f-812730191195', 'db9dca42-5673-4129-a726-de77b6394437', '4fcb6fb2-b3d4-4eb6-889c-02a82c46719e', '54425cd2-cf17-4736-9de0-1fec8dd7daf0', 'd0c09198-be2f-4aea-9e9a-9e5a7fb3c532', 'cdf73c94-909e-40a3-917e-54908b3edb9b', 'a266639f-01f4-4ec0-a09c-cee5dca38e74']
        self.event = {
            1 : {
            'id' : 1 ,
            'name' : 'One Above All' , 
            'matches' : self.ipl_matches ,
            'max_entry' : 1000 ,
            'price_distribution' : { },
            'entries' : {} 
            }       
        }
        self.eCricScore = {
                            "apikey": "51af9212-c2f6-418a-96f8-bbac40ad2f11",
                            "data": [
                                {
                                "id": "b4c54667-73f9-48f4-8e07-969b9283b962",
                                "dateTimeGMT": "2023-04-18T04:30:00",
                                "matchType": "test",
                                "status": "Match not started",
                                "ms": "fixture",
                                "t1": "Ireland [IRE]",
                                "t2": "Sri Lanka [SL]",
                                "t1s": "",
                                "t2s": "",
                                "t1img": "https://g.cricapi.com/img/teams/33-637926315578500224.png",
                                "t2img": "https://g.cricapi.com/img/teams/4191-638101639309122979.webp"
                                },
                                {
                                "id": "7630f8ed-d96f-4ac5-adc9-8c3703c059a0",
                                "dateTimeGMT": "2023-04-17T14:00:00",
                                "matchType": "t20",
                                "status": "Match not started",
                                "ms": "fixture",
                                "t1": "Chennai Super Kings [CSK]",
                                "t2": "Royal Challengers Bangalore [RCB]",
                                "t1s": "",
                                "t2s": "",
                                "t1img": "https://g.cricapi.com/img/teams/135-637852956181378533.png",
                                "t2img": "https://g.cricapi.com/img/teams/261-637852957972423711.png"
                                },
                                {
                                "id": "08e5de9b-ff62-475c-adaa-91a0b43b0e90",
                                "dateTimeGMT": "2023-04-16T14:30:00",
                                "matchType": "t20",
                                "status": "Match not started",
                                "ms": "fixture",
                                "t1": "New Zealand [NZ]",
                                "t2": "Pakistan [PAK]",
                                "t1s": "",
                                "t2s": "",
                                "t1img": "https://g.cricapi.com/img/teams/57-637877076980737903.webp",
                                "t2img": "https://g.cricapi.com/img/teams/66-637877075103236690.webp"
                                },
                                {
                                "id": "f0b02afb-7bab-4fad-8724-bf6735b23d32",
                                "dateTimeGMT": "2023-04-16T14:00:00",
                                "matchType": "t20",
                                "status": "Match not started",
                                "ms": "fixture",
                                "t1": "Gujarat Titans [GT]",
                                "t2": "Rajasthan Royals [RR]",
                                "t1s": "",
                                "t2s": "",
                                "t1img": "https://g.cricapi.com/img/teams/172-637852957798476823.png",
                                "t2img": "https://g.cricapi.com/img/teams/251-637852956607161886.png"
                                },
                                {
                                "id": "18fd94bb-5218-4845-80c8-bb8400a40c24",
                                "dateTimeGMT": "2023-04-16T10:00:00",
                                "matchType": "t20",
                                "status": "Match not started",
                                "ms": "fixture",
                                "t1": "Kolkata Knight Riders [KKR]",
                                "t2": "Mumbai Indians [MI]",
                                "t1s": "",
                                "t2s": "",
                                "t1img": "https://g.cricapi.com/img/teams/206-637852958714346149.png",
                                "t2img": "https://g.cricapi.com/img/teams/226-637852956375593901.png"
                                },
                                {
                                "id": "ff3bafe2-cbb7-4e07-9443-703455b435ea",
                                "dateTimeGMT": "2023-04-16T04:30:00",
                                "matchType": "test",
                                "status": "Match not started",
                                "ms": "fixture",
                                "t1": "Ireland [IRE]",
                                "t2": "Sri Lanka [SL]",
                                "t1s": "",
                                "t2s": "",
                                "t1img": "https://g.cricapi.com/img/teams/33-637926315578500224.png",
                                "t2img": "https://g.cricapi.com/img/teams/4191-638101639309122979.webp"
                                },
                                {
                                "id": "cbf01bfa-c286-40f3-8bb2-b34f0d1ba1e2",
                                "dateTimeGMT": "2023-04-15T14:30:00",
                                "matchType": "t20",
                                "status": "Match not started",
                                "ms": "fixture",
                                "t1": "New Zealand [NZ]",
                                "t2": "Pakistan [PAK]",
                                "t1s": "",
                                "t2s": "",
                                "t1img": "https://g.cricapi.com/img/teams/57-637877076980737903.webp",
                                "t2img": "https://g.cricapi.com/img/teams/66-637877075103236690.webp"
                                },
                                {
                                "id": "0c25b28c-6099-486a-ab6f-704b3415728d",
                                "dateTimeGMT": "2023-04-15T14:00:00",
                                "matchType": "t20",
                                "status": "Match not started",
                                "ms": "fixture",
                                "t1": "Lucknow Super Giants [LSG]",
                                "t2": "Punjab Kings [PBKS]",
                                "t1s": "",
                                "t2s": "",
                                "t1img": "https://g.cricapi.com/img/teams/215-637876059669009476.png",
                                "t2img": "https://g.cricapi.com/img/teams/247-637852956959778791.png"
                                },
                                {
                                "id": "f29a4077-8f04-4cba-90e4-e117b8a10f05",
                                "dateTimeGMT": "2023-04-15T10:00:00",
                                "matchType": "t20",
                                "status": "Match not started",
                                "ms": "fixture",
                                "t1": "Delhi Capitals [DC]",
                                "t2": "Royal Challengers Bangalore [RCB]",
                                "t1s": "",
                                "t2s": "",
                                "t1img": "https://g.cricapi.com/img/teams/148-637874596301457910.png",
                                "t2img": "https://g.cricapi.com/img/teams/261-637852957972423711.png"
                                },
                                {
                                "id": "90118c8b-c48a-4eb1-bf1e-8a2ba119e0ea",
                                "dateTimeGMT": "2023-04-14T14:00:00",
                                "matchType": "t20",
                                "status": "Match not started",
                                "ms": "fixture",
                                "t1": "Kolkata Knight Riders [KKR]",
                                "t2": "Sunrisers Hyderabad [SRH]",
                                "t1s": "",
                                "t2s": "",
                                "t1img": "https://g.cricapi.com/img/teams/206-637852958714346149.png",
                                "t2img": "https://g.cricapi.com/img/teams/279-637852957609490368.png"
                                },
                                {
                                "id": "fdf68944-f20e-4ef6-bd94-09885a4c3c09",
                                "dateTimeGMT": "2023-04-13T14:30:00",
                                "matchType": "t20",
                                "status": "Match not started",
                                "ms": "fixture",
                                "t1": "New Zealand [NZ]",
                                "t2": "Pakistan [PAK]",
                                "t1s": "",
                                "t2s": "",
                                "t1img": "https://g.cricapi.com/img/teams/57-637877076980737903.webp",
                                "t2img": "https://g.cricapi.com/img/teams/66-637877075103236690.webp"
                                },
                                {
                                "id": "c4774b4c-c2f8-434f-8ee6-0bf8e2c02a99",
                                "dateTimeGMT": "2023-04-13T14:00:00",
                                "matchType": "t20",
                                "status": "Match not started",
                                "ms": "fixture",
                                "t1": "Gujarat Titans [GT]",
                                "t2": "Punjab Kings [PBKS]",
                                "t1s": "",
                                "t2s": "",
                                "t1img": "https://g.cricapi.com/img/teams/172-637852957798476823.png",
                                "t2img": "https://g.cricapi.com/img/teams/247-637852956959778791.png"
                                },
                                {
                                "id": "2e4d14f7-fd87-4e6a-98d3-9d6c12fe42a9",
                                "dateTimeGMT": "2023-04-13T10:00:00",
                                "matchType": "",
                                "status": "Match not started",
                                "ms": "fixture",
                                "t1": "Middlesex [MDX]",
                                "t2": "Northamptonshire [NOR]",
                                "t1s": "",
                                "t2s": "",
                                "t1img": "https://g.cricapi.com/img/teams/1127-637889091340507643.webp",
                                "t2img": "https://g.cricapi.com/img/teams/1129-637885551856435418.webp"
                                },
                                {
                                "id": "cb8178e1-035b-47d7-8564-ba58140ca4c8",
                                "dateTimeGMT": "2023-04-13T10:00:00",
                                "matchType": "",
                                "status": "Match not started",
                                "ms": "fixture",
                                "t1": "Essex [ESX]",
                                "t2": "Lancashire [LNCS]",
                                "t1s": "",
                                "t2s": "",
                                "t1img": "https://g.cricapi.com/img/teams/1119-637885549753088458.webp",
                                "t2img": "https://g.cricapi.com/img/teams/1125-637885551497331567.webp"
                                },
                                {
                                "id": "cb31882f-0279-430d-a205-27937776dcd0",
                                "dateTimeGMT": "2023-04-13T10:00:00",
                                "matchType": "",
                                "status": "Match not started",
                                "ms": "fixture",
                                "t1": "Nottinghamshire [NOT]",
                                "t2": "Somerset [SOM]",
                                "t1s": "",
                                "t2s": "",
                                "t1img": "https://g.cricapi.com/img/teams/1130-637889092060873937.webp",
                                "t2img": "https://g.cricapi.com/img/teams/1131-637885552070524344.webp"
                                },
                                {
                                "id": "224fdd93-2026-4944-a95f-652d0c3c49b2",
                                "dateTimeGMT": "2023-04-13T10:00:00",
                                "matchType": "",
                                "status": "Match not started",
                                "ms": "fixture",
                                "t1": "Hampshire [HAM]",
                                "t2": "Surrey [SUR]",
                                "t1s": "",
                                "t2s": "",
                                "t1img": "https://g.cricapi.com/img/teams/1122-637885550993657486.webp",
                                "t2img": "https://g.cricapi.com/img/teams/1133-637885552361099530.webp"
                                },
                                {
                                "id": "d2171dfd-d7b2-4c11-bc94-5f519c9b2c85",
                                "dateTimeGMT": "2023-04-13T10:00:00",
                                "matchType": "",
                                "status": "Match not started",
                                "ms": "fixture",
                                "t1": "Kent [KENT]",
                                "t2": "Warwickshire [WRKS]",
                                "t1s": "",
                                "t2s": "",
                                "t1img": "https://g.cricapi.com/img/teams/1124-637885551212175895.webp",
                                "t2img": "https://g.cricapi.com/img/teams/1137-637885552592685258.webp"
                                },
                                {
                                "id": "7bf21b66-a138-454b-a911-1bb4ce12d8dc",
                                "dateTimeGMT": "2023-04-13T10:00:00",
                                "matchType": "",
                                "status": "Match not started",
                                "ms": "fixture",
                                "t1": "Derbyshire [DERB]",
                                "t2": "Leicestershire [LECS]",
                                "t1s": "",
                                "t2s": "",
                                "t1img": "https://g.cricapi.com/img/teams/1117-637889091569915358.webp",
                                "t2img": "https://g.cricapi.com/img/teams/1126-637889090878436462.webp"
                                },
                                {
                                "id": "58a7a401-09f4-4e35-a171-3da3d064f542",
                                "dateTimeGMT": "2023-04-13T10:00:00",
                                "matchType": "",
                                "status": "Match not started",
                                "ms": "fixture",
                                "t1": "Durham [DURH]",
                                "t2": "Worcestershire [WRCS]",
                                "t1s": "",
                                "t2s": "",
                                "t1img": "https://g.cricapi.com/img/teams/1118-637889090599643548.webp",
                                "t2img": "https://g.cricapi.com/img/teams/1138-637889091123850841.webp"
                                },
                                {
                                "id": "c2a1177a-d00f-44cb-9e4f-aae20f84305b",
                                "dateTimeGMT": "2023-04-13T10:00:00",
                                "matchType": "",
                                "status": "Match not started",
                                "ms": "fixture",
                                "t1": "Gloucestershire [GLOU]",
                                "t2": "Yorkshire [YRK]",
                                "t1s": "",
                                "t2s": "",
                                "t1img": "https://g.cricapi.com/img/teams/1121-637885550747990018.webp",
                                "t2img": "https://g.cricapi.com/img/teams/1139-637885552795894277.webp"
                                },
                                {
                                "id": "5c496668-8076-4d58-a72a-105e1aeca978",
                                "dateTimeGMT": "2023-04-12T14:00:00",
                                "matchType": "t20",
                                "status": "Match not started",
                                "ms": "fixture",
                                "t1": "Chennai Super Kings [CSK]",
                                "t2": "Rajasthan Royals [RR]",
                                "t1s": "",
                                "t2s": "",
                                "t1img": "https://g.cricapi.com/img/teams/135-637852956181378533.png",
                                "t2img": "https://g.cricapi.com/img/teams/251-637852956607161886.png"
                                },
                                {
                                "id": "cc301267-8a6c-4840-87ff-b7c43ce10bc4",
                                "dateTimeGMT": "2023-04-11T14:00:00",
                                "matchType": "t20",
                                "status": "Match not started",
                                "ms": "fixture",
                                "t1": "Delhi Capitals [DC]",
                                "t2": "Mumbai Indians [MI]",
                                "t1s": "",
                                "t2s": "",
                                "t1img": "https://g.cricapi.com/img/teams/148-637874596301457910.png",
                                "t2img": "https://g.cricapi.com/img/teams/226-637852956375593901.png"
                                },
                                {
                                "id": "ca6c05b0-86f7-4bf8-9781-fd0f8d1e1aa5",
                                "dateTimeGMT": "2023-04-11T14:00:00",
                                "matchType": "t20",
                                "status": "Match not started",
                                "ms": "fixture",
                                "t1": "Gibraltar [GIB]",
                                "t2": "Portugal [PORT]",
                                "t1s": "",
                                "t2s": "",
                                "t1img": "https://g.cricapi.com/img/teams/608-637874527501988013.webp",
                                "t2img": "https://g.cricapi.com/img/teams/643-637872736165869493.webp"
                                },
                                {
                                "id": "e809890a-3e88-4c2b-86aa-ba7558e06e79",
                                "dateTimeGMT": "2023-04-11T09:00:00",
                                "matchType": "t20",
                                "status": "Match not started",
                                "ms": "fixture",
                                "t1": "Gibraltar [GIB]",
                                "t2": "Portugal [PORT]",
                                "t1s": "",
                                "t2s": "",
                                "t1img": "https://g.cricapi.com/img/teams/608-637874527501988013.webp",
                                "t2img": "https://g.cricapi.com/img/teams/643-637872736165869493.webp"
                                },
                                {
                                "id": "3ff110ac-deba-4564-aade-374757acf5d8",
                                "dateTimeGMT": "2023-04-10T14:00:00",
                                "matchType": "t20",
                                "status": "Match not started",
                                "ms": "live",
                                "t1": "Gibraltar [GIB]",
                                "t2": "Portugal [PORT]",
                                "t1s": "",
                                "t2s": "",
                                "t1img": "https://g.cricapi.com/img/teams/608-637874527501988013.webp",
                                "t2img": "https://g.cricapi.com/img/teams/643-637872736165869493.webp"
                                },
                                {
                                "id": "a1f790e6-59c9-4c63-8b30-6b629531253d",
                                "dateTimeGMT": "2023-04-10T14:00:00",
                                "matchType": "t20",
                                "status": "Lucknow Super Giants won by 1 wkt",
                                "ms": "result",
                                "t1": "Lucknow Super Giants [LSG]",
                                "t2": "Royal Challengers Bangalore [RCB]",
                                "t1s": "213/9 (20)",
                                "t2s": "212/2 (20)",
                                "t1img": "https://g.cricapi.com/img/teams/215-637876059669009476.png",
                                "t2img": "https://g.cricapi.com/img/teams/261-637852957972423711.png"
                                },
                                {
                                "id": "0b8981a3-9ae5-442d-ad1a-baab2efbd9e3",
                                "dateTimeGMT": "2023-04-09T14:00:00",
                                "matchType": "t20",
                                "status": "Sunrisers Hyderabad won by 8 wkts",
                                "ms": "result",
                                "t1": "Punjab Kings [PBKS]",
                                "t2": "Sunrisers Hyderabad [SRH]",
                                "t1s": "143/9 (20)",
                                "t2s": "145/2 (17.1)",
                                "t1img": "https://g.cricapi.com/img/teams/247-637852956959778791.png",
                                "t2img": "https://g.cricapi.com/img/teams/279-637852957609490368.png"
                                },
                                {
                                "id": "9d22f5ad-e9bc-4a66-82d5-03acfc599434",
                                "dateTimeGMT": "2023-04-09T10:00:00",
                                "matchType": "t20",
                                "status": "Kolkata Knight Riders won by 3 wkts",
                                "ms": "result",
                                "t1": "Gujarat Titans [GT]",
                                "t2": "Kolkata Knight Riders [KKR]",
                                "t1s": "204/4 (20)",
                                "t2s": "207/7 (20)",
                                "t1img": "https://g.cricapi.com/img/teams/172-637852957798476823.png",
                                "t2img": "https://g.cricapi.com/img/teams/206-637852958714346149.png"
                                },
                                {
                                "id": "ae24cc6a-8e37-4fd1-bb18-638b56ec4989",
                                "dateTimeGMT": "2023-04-08T14:00:00",
                                "matchType": "t20",
                                "status": "Chennai Super Kings won by 7 wkts",
                                "ms": "result",
                                "t1": "Chennai Super Kings [CSK]",
                                "t2": "Mumbai Indians [MI]",
                                "t1s": "159/3 (18.1)",
                                "t2s": "157/8 (20)",
                                "t1img": "https://g.cricapi.com/img/teams/135-637852956181378533.png",
                                "t2img": "https://g.cricapi.com/img/teams/226-637852956375593901.png"
                                },
                                {
                                "id": "7f6df32a-e505-495f-9121-c6aca6235306",
                                "dateTimeGMT": "2023-04-08T10:00:00",
                                "matchType": "t20",
                                "status": "Rajasthan Royals won by 57 runs",
                                "ms": "result",
                                "t1": "Delhi Capitals [DC]",
                                "t2": "Rajasthan Royals [RR]",
                                "t1s": "142/9 (20)",
                                "t2s": "199/4 (20)",
                                "t1img": "https://g.cricapi.com/img/teams/148-637874596301457910.png",
                                "t2img": "https://g.cricapi.com/img/teams/251-637852956607161886.png"
                                },
                                {
                                "id": "9bf4c41b-514e-464b-8d4d-d9409c61aa7f",
                                "dateTimeGMT": "2023-04-08T00:30:00",
                                "matchType": "t20",
                                "status": "New Zealand won by 4 wkts",
                                "ms": "result",
                                "t1": "New Zealand [NZ]",
                                "t2": "Sri Lanka [SL]",
                                "t1s": "183/6 (19.5)",
                                "t2s": "182/6 (20)",
                                "t1img": "https://g.cricapi.com/img/teams/57-637877076980737903.webp",
                                "t2img": "https://g.cricapi.com/img/teams/4191-638101639309122979.webp"
                                },
                                {
                                "id": "2ef015a9-6017-4979-b0c1-8227ff1a3a3c",
                                "dateTimeGMT": "2023-04-07T21:30:00",
                                "matchType": "test",
                                "status": "Match drawn",
                                "ms": "result",
                                "t1": "Australia A [AUSA]",
                                "t2": "New Zealand A [NZA]",
                                "t1s": "366/8 (106)",
                                "t2s": "174/3 (42)",
                                "t1img": "https://g.cricapi.com/img/teams/1429-637926307133296133.webp",
                                "t2img": "https://g.cricapi.com/img/teams/2180-637982269820638615.webp"
                                },
                                {
                                "id": "a92711fa-55d1-42a1-8cd7-571a0f9fb614",
                                "dateTimeGMT": "2023-04-07T14:00:00",
                                "matchType": "t20",
                                "status": "Lucknow Super Giants won by 5 wkts",
                                "ms": "result",
                                "t1": "Lucknow Super Giants [LSG]",
                                "t2": "Sunrisers Hyderabad [SRH]",
                                "t1s": "127/5 (16)",
                                "t2s": "121/8 (20)",
                                "t1img": "https://g.cricapi.com/img/teams/215-637876059669009476.png",
                                "t2img": "https://g.cricapi.com/img/teams/279-637852957609490368.png"
                                },
                                {
                                "id": "63179b6c-0560-45cc-a984-9ad0459c7542",
                                "dateTimeGMT": "2023-04-06T14:00:00",
                                "matchType": "t20",
                                "status": "Kolkata Knight Riders won by 81 runs",
                                "ms": "result",
                                "t1": "Kolkata Knight Riders [KKR]",
                                "t2": "Royal Challengers Bangalore [RCB]",
                                "t1s": "204/7 (20)",
                                "t2s": "123/10 (17.4)",
                                "t1img": "https://g.cricapi.com/img/teams/206-637852958714346149.png",
                                "t2img": "https://g.cricapi.com/img/teams/261-637852957972423711.png"
                                },
                                {
                                "id": "4d0f818a-afa3-405f-9e16-2d40458e9208",
                                "dateTimeGMT": "2023-04-06T10:00:00",
                                "matchType": "",
                                "status": "Match drawn",
                                "ms": "result",
                                "t1": "Lancashire [LNCS]",
                                "t2": "Surrey [SUR]",
                                "t1s": "247/3 (87.1)",
                                "t2s": "292/6 (65)",
                                "t1img": "https://g.cricapi.com/img/teams/1125-637885551497331567.webp",
                                "t2img": "https://g.cricapi.com/img/teams/1133-637885552361099530.webp"
                                },
                                {
                                "id": "cb48571b-e08d-451a-b40d-0d65a34d3d6c",
                                "dateTimeGMT": "2023-04-06T10:00:00",
                                "matchType": "",
                                "status": "Match drawn",
                                "ms": "result",
                                "t1": "Somerset [SOM]",
                                "t2": "Warwickshire [WRKS]",
                                "t1s": "180/6 (50)",
                                "t2s": "392/10 (109.5)",
                                "t1img": "https://g.cricapi.com/img/teams/1131-637885552070524344.webp",
                                "t2img": "https://g.cricapi.com/img/teams/1137-637885552592685258.webp"
                                },
                                {
                                "id": "42735fd7-0b31-408c-8bf8-536f0d47d196",
                                "dateTimeGMT": "2023-04-06T10:00:00",
                                "matchType": "",
                                "status": "Essex won by 97 runs",
                                "ms": "result",
                                "t1": "Essex [ESX]",
                                "t2": "Middlesex [MDX]",
                                "t1s": "211/10 (63.2)",
                                "t2s": "210/10 (83)",
                                "t1img": "https://g.cricapi.com/img/teams/1119-637885549753088458.webp",
                                "t2img": "https://g.cricapi.com/img/teams/1127-637889091340507643.webp"
                                },
                                {
                                "id": "a6415b14-44ea-4feb-a69a-5451feaf85ea",
                                "dateTimeGMT": "2023-04-06T10:00:00",
                                "matchType": "",
                                "status": "Kent won by 7 wkts",
                                "ms": "result",
                                "t1": "Kent [KENT]",
                                "t2": "Northamptonshire [NOR]",
                                "t1s": "227/3 (64.5)",
                                "t2s": "331/10 (117.3)",
                                "t1img": "https://g.cricapi.com/img/teams/1124-637885551212175895.webp",
                                "t2img": "https://g.cricapi.com/img/teams/1129-637885551856435418.webp"
                                },
                                {
                                "id": "918dd338-4f8b-446a-bfa9-74d08aafacd3",
                                "dateTimeGMT": "2023-04-06T10:00:00",
                                "matchType": "",
                                "status": "Hampshire won by 8 wkts",
                                "ms": "result",
                                "t1": "Hampshire [HAM]",
                                "t2": "Nottinghamshire [NOT]",
                                "t1s": "132/2 (46.2)",
                                "t2s": "177/10 (69.4)",
                                "t1img": "https://g.cricapi.com/img/teams/1122-637885550993657486.webp",
                                "t2img": "https://g.cricapi.com/img/teams/1130-637889092060873937.webp"
                                },
                                {
                                "id": "4e63c4ee-2889-40d7-991e-d6d3bce05750",
                                "dateTimeGMT": "2023-04-06T10:00:00",
                                "matchType": "",
                                "status": "Sussex won by 2 wkts",
                                "ms": "result",
                                "t1": "Durham [DURH]",
                                "t2": "Sussex [SUSS]",
                                "t1s": "189/10 (54)",
                                "t2s": "232/8 (67)",
                                "t1img": "https://g.cricapi.com/img/teams/1118-637889090599643548.webp",
                                "t2img": "https://g.cricapi.com/img/teams/1134-637889091814592518.webp"
                                },
                                {
                                "id": "9090eda5-a8fd-4c98-9dcf-13c129e9e90f",
                                "dateTimeGMT": "2023-04-06T10:00:00",
                                "matchType": "",
                                "status": "Match drawn",
                                "ms": "result",
                                "t1": "Glamorgan [GLAM]",
                                "t2": "Gloucestershire [GLOU]",
                                "t1s": "110/3 (37)",
                                "t2s": "569/7 (138)",
                                "t1img": "https://g.cricapi.com/img/teams/1120-637889090390357869.webp",
                                "t2img": "https://g.cricapi.com/img/teams/1121-637885550747990018.webp"
                                },
                                {
                                "id": "eecc7262-c11d-41de-b124-7c46383efcfd",
                                "dateTimeGMT": "2023-04-06T10:00:00",
                                "matchType": "",
                                "status": "Worcestershire won by 8 wkts",
                                "ms": "result",
                                "t1": "Derbyshire [DERB]",
                                "t2": "Worcestershire [WRCS]",
                                "t1s": "343/10 (95.5)",
                                "t2s": "193/2 (42.1)",
                                "t1img": "https://g.cricapi.com/img/teams/1117-637889091569915358.webp",
                                "t2img": "https://g.cricapi.com/img/teams/1138-637889091123850841.webp"
                                },
                                {
                                "id": "fefd792a-baa7-4f84-954c-ef9e2192082d",
                                "dateTimeGMT": "2023-04-06T10:00:00",
                                "matchType": "",
                                "status": "Leicestershire won by 3 wkts",
                                "ms": "result",
                                "t1": "Leicestershire [LECS]",
                                "t2": "Yorkshire [YRK]",
                                "t1s": "392/7 (85.5)",
                                "t2s": "286/8 (54)",
                                "t1img": "https://g.cricapi.com/img/teams/1126-637889090878436462.webp",
                                "t2img": "https://g.cricapi.com/img/teams/1139-637885552795894277.webp"
                                },
                                {
                                "id": "91ba8452-eb44-464d-8eae-6a53ed46f00a",
                                "dateTimeGMT": "2023-04-05T14:00:00",
                                "matchType": "t20",
                                "status": "Punjab Kings won by 5 runs",
                                "ms": "result",
                                "t1": "Punjab Kings [PBKS]",
                                "t2": "Rajasthan Royals [RR]",
                                "t1s": "197/4 (20)",
                                "t2s": "192/7 (20)",
                                "t1img": "https://g.cricapi.com/img/teams/247-637852956959778791.png",
                                "t2img": "https://g.cricapi.com/img/teams/251-637852956607161886.png"
                                },
                                {
                                "id": "0d200795-9559-4445-882e-e8239da099a4",
                                "dateTimeGMT": "2023-04-05T07:30:00",
                                "matchType": "odi",
                                "status": "United Arab Emirates won by 66 runs",
                                "ms": "result",
                                "t1": "Jersey [JER]",
                                "t2": "United Arab Emirates [UAE]",
                                "t1s": "218/10 (44.5)",
                                "t2s": "284/7 (50)",
                                "t1img": "https://g.cricapi.com/img/teams/619-637877088641021958.webp",
                                "t2img": "https://g.cricapi.com/img/teams/92-637877081068315608.webp"
                                },
                                {
                                "id": "346bd568-a375-4630-848f-050d8eb671d5",
                                "dateTimeGMT": "2023-04-05T07:30:00",
                                "matchType": "odi",
                                "status": "Canada won by 90 runs",
                                "ms": "result",
                                "t1": "Canada [CAN]",
                                "t2": "Papua New Guinea [PNG]",
                                "t1s": "218/8 (50)",
                                "t2s": "128/10 (37)",
                                "t1img": "https://g.cricapi.com/img/teams/14-637877085850526611.webp",
                                "t2img": "https://g.cricapi.com/img/teams/68-637877083835752068.webp"
                                },
                                {
                                "id": "a0d96bcf-1b41-46ec-b9d1-ab67b35e4e97",
                                "dateTimeGMT": "2023-04-05T00:30:00",
                                "matchType": "t20",
                                "status": "New Zealand won by 9 wkts",
                                "ms": "result",
                                "t1": "New Zealand [NZ]",
                                "t2": "Sri Lanka [SL]",
                                "t1s": "146/1 (14.4)",
                                "t2s": "141/10 (19)",
                                "t1img": "https://g.cricapi.com/img/teams/57-637877076980737903.webp",
                                "t2img": "https://g.cricapi.com/img/teams/4191-638101639309122979.webp"
                                },
                                {
                                "id": "7aa61b66-0f3c-4a50-8eab-e9e23e7c4fcd",
                                "dateTimeGMT": "2023-04-04T14:00:00",
                                "matchType": "t20",
                                "status": "Gujarat Titans won by 6 wkts",
                                "ms": "result",
                                "t1": "Delhi Capitals [DC]",
                                "t2": "Gujarat Titans [GT]",
                                "t1s": "162/8 (20)",
                                "t2s": "163/4 (18.1)",
                                "t1img": "https://g.cricapi.com/img/teams/148-637874596301457910.png",
                                "t2img": "https://g.cricapi.com/img/teams/172-637852957798476823.png"
                                },
                                {
                                "id": "a36af2d9-c057-44e4-9623-4ba590f11de7",
                                "dateTimeGMT": "2023-04-04T07:30:00",
                                "matchType": "odi",
                                "status": "Namibia won by 111 runs",
                                "ms": "result",
                                "t1": "Canada [CAN]",
                                "t2": "Namibia [NAM]",
                                "t1s": "156/10 (42.2)",
                                "t2s": "267/9 (50)",
                                "t1img": "https://g.cricapi.com/img/teams/14-637877085850526611.webp",
                                "t2img": "https://g.cricapi.com/img/teams/53-637877082656229722.webp"
                                },
                                {
                                "id": "38a79dd2-59de-4803-a799-5a0e56dede1f",
                                "dateTimeGMT": "2023-04-04T07:30:00",
                                "matchType": "odi",
                                "status": "United States won by 25 runs",
                                "ms": "result",
                                "t1": "Jersey [JER]",
                                "t2": "United States [USA]",
                                "t1s": "206/10 (47.4)",
                                "t2s": "231/10 (50)",
                                "t1img": "https://g.cricapi.com/img/teams/619-637877088641021958.webp",
                                "t2img": "https://g.cricapi.com/img/teams/93-637877085206398451.webp"
                                }
                            ],
                            "status": "success",
                            "info": {
                                "hitsToday": 1,
                                "hitsUsed": 1,
                                "hitsLimit": 100,
                                "credits": 0,
                                "server": 14,
                                "queryTime": 37.8109,
                                "s": 0
                            }
                            }
        self.team_data = { 
                          "5c496668-8076-4d58-a72a-105e1aeca978" : [
                        {
                        "teamName": "Chennai Super Kings",
                        "shortname": "CSK",
                        "img": "https://g.cricapi.com/img/teams/135-637852956181378533.png",
                        "players": [
                        {
                        "id": "4f95ebbb-226b-4bef-bd2c-02daec890ba4",
                        "name": "Shaik Rasheed",
                        "role": "Batsman",
                        "battingStyle": "Right Handed Bat",
                        "bowlingStyle": "Right-arm legbreak",
                        "country": "India",
                        "playerImg": "https://h.cricapi.com/img/icon512.png"
                        },
                        {
                        "id": "81b446e1-bfea-45a7-a15e-062b8157a323",
                        "name": "Ravindra Jadeja",
                        "role": "Bowling Allrounder",
                        "battingStyle": "Left Handed Bat",
                        "bowlingStyle": "Left-arm orthodox",
                        "country": "India",
                        "playerImg": "https://h.cricapi.com/img/players/81b446e1-bfea-45a7-a15e-062b8157a323.jpg"
                        },
                        {
                        "id": "64ab5424-779f-44ad-8135-21097f6eb83c",
                        "name": "Sachin Tendulkar",
                        "role": "Batsman",
                        "battingStyle": "Right Handed Bat",
                        "bowlingStyle": "Right-arm legbreak",
                        "country": "India",
                        "playerImg": "https://h.cricapi.com/img/players/64ab5424-779f-44ad-8135-21097f6eb83c.jpg"
                        },
                        {
                        "id": "1e321877-6f0a-4ebe-aa88-21a40755b396",
                        "name": "Subhranshu Senapati",
                        "role": "Batsman",
                        "battingStyle": "Right Handed Bat",
                        "bowlingStyle": "Right-arm medium",
                        "country": "India",
                        "playerImg": "https://h.cricapi.com/img/icon512.png"
                        },
                        {
                        "id": "4d066db8-b202-45a4-8408-28b335c5a767",
                        "name": "RS Hangargekar",
                        "role": "Bowler",
                        "battingStyle": "Right Handed Bat",
                        "bowlingStyle": "Right-arm fast-medium",
                        "country": "India",
                        "playerImg": "https://h.cricapi.com/img/players/4d066db8-b202-45a4-8408-28b335c5a767.jpg"
                        },
                        {
                        "id": "5e87b30f-0f52-4f12-a341-331674c6fb17",
                        "name": "Mahela Jayawardene",
                        "role": "Batsman",
                        "battingStyle": "Right Handed Bat",
                        "bowlingStyle": "Right-arm medium",
                        "country": "Sri Lanka",
                        "playerImg": "https://h.cricapi.com/img/icon512.png"
                        },
                        {
                        "id": "5673ee27-bf33-44b8-8973-41fd37923fed",
                        "name": "Kyle Jamieson",
                        "role": "Bowler",
                        "battingStyle": "Right Handed Bat",
                        "bowlingStyle": "Right-arm fast-medium",
                        "country": "New Zealand",
                        "playerImg": "https://h.cricapi.com/img/players/5673ee27-bf33-44b8-8973-41fd37923fed.jpg"
                        },
                        {
                        "id": "cdc2646c-1fe7-4bc2-b26e-42453f45a212",
                        "name": "Ajinkya Rahane",
                        "role": "Batsman",
                        "battingStyle": "Right Handed Bat",
                        "bowlingStyle": "Right-arm medium",
                        "country": "India",
                        "playerImg": "https://h.cricapi.com/img/players/cdc2646c-1fe7-4bc2-b26e-42453f45a212.jpg"
                        },
                        {
                        "id": "f3876b65-0643-49df-9255-4a06dd3fa051",
                        "name": "Tushar Deshpande",
                        "role": "Bowler",
                        "battingStyle": "Left Handed Bat",
                        "bowlingStyle": "Right-arm medium",
                        "country": "India",
                        "playerImg": "https://h.cricapi.com/img/players/f3876b65-0643-49df-9255-4a06dd3fa051.jpg"
                        },
                        {
                        "id": "0d267d2d-1a82-4533-8f0c-585aba59a147",
                        "name": "Mark Boucher",
                        "role": "WK-Batsman",
                        "battingStyle": "Right Handed Bat",
                        "bowlingStyle": "Right-arm medium",
                        "country": "South Africa",
                        "playerImg": "https://h.cricapi.com/img/icon512.png"
                        },
                        {
                        "id": "a221f4e5-c0ff-47f9-8458-59a86bfde700",
                        "name": "James Pamment",
                        "role": "--",
                        "battingStyle": "Right Handed Bat",
                        "country": "New Zealand",
                        "playerImg": "https://h.cricapi.com/img/icon512.png"
                        },
                        {
                        "id": "b6e7aa41-b0bb-4b0f-8f59-59f729283be5",
                        "name": "MS Dhoni",
                        "role": "WK-Batsman",
                        "battingStyle": "Right Handed Bat",
                        "bowlingStyle": "Right-arm medium",
                        "country": "India",
                        "playerImg": "https://h.cricapi.com/img/players/b6e7aa41-b0bb-4b0f-8f59-59f729283be5.jpg"
                        },
                        {
                        "id": "7e09eef0-d886-4997-b568-5fd4e0dfbbec",
                        "name": "Maheesh Theekshana",
                        "role": "Bowler",
                        "battingStyle": "Right Handed Bat",
                        "bowlingStyle": "Right-arm offbreak",
                        "country": "Sri Lanka",
                        "playerImg": "https://h.cricapi.com/img/players/7e09eef0-d886-4997-b568-5fd4e0dfbbec.jpg"
                        },
                        {
                        "id": "bda09245-1e64-454b-97d4-61ee7e43cdde",
                        "name": "Akash Singh",
                        "role": "Bowler",
                        "battingStyle": "Right Handed Bat",
                        "bowlingStyle": "Left-arm fast-medium",
                        "country": "India",
                        "playerImg": "https://h.cricapi.com/img/icon512.png"
                        },
                        {
                        "id": "c4de3a4e-77a5-4710-beed-645da803bd77",
                        "name": "Shane Bond",
                        "role": "Bowler",
                        "battingStyle": "Right Handed Bat",
                        "bowlingStyle": "Right-arm fast",
                        "country": "New Zealand",
                        "playerImg": "https://h.cricapi.com/img/icon512.png"
                        },
                        {
                        "id": "fc09ce60-e7e4-44e5-9a53-67a617560161",
                        "name": "Ben Stokes",
                        "role": "Batting Allrounder",
                        "battingStyle": "Left Handed Bat",
                        "bowlingStyle": "Right-arm fast-medium",
                        "country": "England",
                        "playerImg": "https://h.cricapi.com/img/players/fc09ce60-e7e4-44e5-9a53-67a617560161.jpg"
                        },
                        {
                        "id": "014ba4b1-423c-49d3-a6f5-68e6bb90835e",
                        "name": "Ajay Jadav Mandal",
                        "role": "Bowler",
                        "battingStyle": "Left Handed Bat",
                        "bowlingStyle": "Left-arm orthodox",
                        "country": "India",
                        "playerImg": "https://h.cricapi.com/img/icon512.png"
                        },
                        {
                        "id": "9f06f450-c300-4b49-9359-7876f492f686",
                        "name": "Moeen Ali",
                        "role": "Batting Allrounder",
                        "battingStyle": "Left Handed Bat",
                        "bowlingStyle": "Right-arm offbreak",
                        "country": "England",
                        "playerImg": "https://h.cricapi.com/img/players/9f06f450-c300-4b49-9359-7876f492f686.jpg"
                        },
                        {
                        "id": "dc2f7f59-ce15-48aa-b7d9-793314961076",
                        "name": "Mukesh Choudhary",
                        "role": "Bowler",
                        "battingStyle": "Left Handed Bat",
                        "bowlingStyle": "Left-arm medium",
                        "country": "India",
                        "playerImg": "https://h.cricapi.com/img/icon512.png"
                        },
                        {
                        "id": "eba243e1-33b7-42b8-8b8a-8b9e381a96f5",
                        "name": "Dwaine Pretorius",
                        "role": "Bowling Allrounder",
                        "battingStyle": "Right Handed Bat",
                        "bowlingStyle": "Right-arm fast-medium",
                        "country": "South Africa",
                        "playerImg": "https://h.cricapi.com/img/players/eba243e1-33b7-42b8-8b8a-8b9e381a96f5.jpg"
                        },
                        {
                        "id": "d59bfc6b-bf4c-4a23-aa82-954911b0973d",
                        "name": "Matheesha Pathirana",
                        "role": "Bowler",
                        "battingStyle": "Right Handed Bat",
                        "bowlingStyle": "Right-arm medium",
                        "country": "Sri Lanka",
                        "playerImg": "https://h.cricapi.com/img/icon512.png"
                        },
                        {
                        "id": "c66b36de-72b1-4022-b387-99d0ec79fb49",
                        "name": "Sisanda Magala",
                        "role": "Bowler",
                        "battingStyle": "Right Handed Bat",
                        "bowlingStyle": "Right-arm fast-medium",
                        "country": "South Africa",
                        "playerImg": "https://h.cricapi.com/img/players/c66b36de-72b1-4022-b387-99d0ec79fb49.jpg"
                        },
                        {
                        "id": "60d2f2b2-0e1e-4064-9c29-99e6a35fb166",
                        "name": "Jagadeesh Arunkumar",
                        "role": "Batting Allrounder",
                        "battingStyle": "Right Handed Bat",
                        "country": "India",
                        "playerImg": "https://h.cricapi.com/img/icon512.png"
                        },
                        {
                        "id": "5d15a50d-3d28-4576-b237-a0029d0933da",
                        "name": "Prashant Solanki",
                        "role": "Bowler",
                        "battingStyle": "Right Handed Bat",
                        "bowlingStyle": "Right-arm legbreak",
                        "country": "India",
                        "playerImg": "https://h.cricapi.com/img/icon512.png"
                        },
                        {
                        "id": "469321f1-c47f-4a86-83ca-a3110745fb69",
                        "name": "Zaheer Khan",
                        "role": "Bowler",
                        "battingStyle": "Right Handed Bat",
                        "bowlingStyle": "Left-arm fast-medium",
                        "country": "India",
                        "playerImg": "https://h.cricapi.com/img/players/469321f1-c47f-4a86-83ca-a3110745fb69.jpg"
                        },
                        {
                        "id": "95e4705e-d7b3-4c5a-8cf9-b2176abe7019",
                        "name": "Ambati Rayudu",
                        "role": "Batsman",
                        "battingStyle": "Right Handed Bat",
                        "bowlingStyle": "Right-arm offbreak",
                        "country": "India",
                        "playerImg": "https://h.cricapi.com/img/players/95e4705e-d7b3-4c5a-8cf9-b2176abe7019.jpg"
                        },
                        {
                        "id": "0c820e90-aaba-477b-b77c-b9e967725655",
                        "name": "Kieron Pollard",
                        "role": "Batting Allrounder",
                        "battingStyle": "Right Handed Bat",
                        "bowlingStyle": "Right-arm medium",
                        "country": "West Indies",
                        "playerImg": "https://h.cricapi.com/img/players/0c820e90-aaba-477b-b77c-b9e967725655.jpg"
                        },
                        {
                        "id": "50b70c71-1535-41c0-87fd-c12883105ede",
                        "name": "Ruturaj Gaikwad",
                        "role": "Batsman",
                        "battingStyle": "Right Handed Bat",
                        "bowlingStyle": "Right-arm offbreak",
                        "country": "India",
                        "playerImg": "https://h.cricapi.com/img/players/50b70c71-1535-41c0-87fd-c12883105ede.jpg"
                        },
                        {
                        "id": "22ee45d8-0538-4e3e-a758-c515f9b86d11",
                        "name": "Shivam Dube",
                        "role": "Bowling Allrounder",
                        "battingStyle": "Left Handed Bat",
                        "bowlingStyle": "Right-arm medium",
                        "country": "India",
                        "playerImg": "https://h.cricapi.com/img/players/22ee45d8-0538-4e3e-a758-c515f9b86d11.jpg"
                        },
                        {
                        "id": "60610403-b20d-41b5-a1f9-ca5981d192e1",
                        "name": "Simarjeet Singh",
                        "role": "Bowler",
                        "battingStyle": "Right Handed Bat",
                        "bowlingStyle": "Right-arm fast-medium",
                        "country": "India",
                        "playerImg": "https://h.cricapi.com/img/icon512.png"
                        },
                        {
                        "id": "16ec245b-022d-4104-bd8f-ccc780428390",
                        "name": "Mitchell Santner",
                        "role": "Bowling Allrounder",
                        "battingStyle": "Left Handed Bat",
                        "bowlingStyle": "Left-arm orthodox",
                        "country": "New Zealand",
                        "playerImg": "https://h.cricapi.com/img/players/16ec245b-022d-4104-bd8f-ccc780428390.jpg"
                        },
                        {
                        "id": "b25d048e-c5fb-48c3-b9ae-d0c4b8c541f8",
                        "name": "Bhagath Varma",
                        "role": "Bowling Allrounder",
                        "battingStyle": "Right Handed Bat",
                        "bowlingStyle": "Right-arm offbreak",
                        "country": "India",
                        "playerImg": "https://h.cricapi.com/img/icon512.png"
                        },
                        {
                        "id": "237a1ef2-1eae-4877-8b94-d20d84faf635",
                        "name": "Deepak Chahar",
                        "role": "Bowler",
                        "battingStyle": "Right Handed Bat",
                        "bowlingStyle": "Right-arm medium",
                        "country": "India",
                        "playerImg": "https://h.cricapi.com/img/players/237a1ef2-1eae-4877-8b94-d20d84faf635.jpg"
                        },
                        {
                        "id": "3a51a030-8cac-42c7-8a47-e32fd1bcedd4",
                        "name": "Nishant Sindhu",
                        "role": "Batting Allrounder",
                        "battingStyle": "Left Handed Bat",
                        "bowlingStyle": "Left-arm orthodox",
                        "country": "India",
                        "playerImg": "https://h.cricapi.com/img/icon512.png"
                        },
                        {
                        "id": "eac0032b-055a-497b-9d4e-f54008414515",
                        "name": "Devon Conway",
                        "role": "WK-Batsman",
                        "battingStyle": "Left Handed Bat",
                        "bowlingStyle": "Right-arm medium",
                        "country": "New Zealand",
                        "playerImg": "https://h.cricapi.com/img/players/eac0032b-055a-497b-9d4e-f54008414515.jpg"
                        }
                        ]
                        },
                        {
                        "teamName": "Rajasthan Royals",
                        "shortname": "RR",
                        "img": "https://g.cricapi.com/img/teams/251-637852956607161886.png",
                        "players": [
                        {
                        "id": "0d704a13-518a-40a7-bb93-0fc0d92af9e2",
                        "name": "Yuzvendra Chahal",
                        "role": "Bowler",
                        "battingStyle": "Right Handed Bat",
                        "bowlingStyle": "Right-arm legbreak",
                        "country": "India",
                        "playerImg": "https://h.cricapi.com/img/players/0d704a13-518a-40a7-bb93-0fc0d92af9e2.jpg"
                        },
                        {
                        "id": "a2386bdf-81c0-4f3b-b0a0-15aab8604d8f",
                        "name": "KM Asif",
                        "role": "Bowler",
                        "battingStyle": "Right Handed Bat",
                        "bowlingStyle": "Right-arm medium",
                        "country": "India",
                        "playerImg": "https://h.cricapi.com/img/players/a2386bdf-81c0-4f3b-b0a0-15aab8604d8f.jpg"
                        },
                        {
                        "id": "4269d64c-962d-4cd9-b2d2-1a62f51256b8",
                        "name": "Shimron Hetmyer",
                        "role": "Batsman",
                        "battingStyle": "Left Handed Bat",
                        "country": "West Indies",
                        "playerImg": "https://h.cricapi.com/img/players/4269d64c-962d-4cd9-b2d2-1a62f51256b8.jpg"
                        },
                        {
                        "id": "259051b9-d5c9-42f7-9b49-20dc69efdab8",
                        "name": "Kunal Singh Rathore",
                        "role": "Batsman",
                        "battingStyle": "Left Handed Bat",
                        "country": "India",
                        "playerImg": "https://h.cricapi.com/img/icon512.png"
                        },
                        {
                        "id": "1ee41e9e-e219-4df2-9861-2360b28bb307",
                        "name": "Joe Root",
                        "role": "Batsman",
                        "battingStyle": "Right Handed Bat",
                        "bowlingStyle": "Right-arm offbreak",
                        "country": "England",
                        "playerImg": "https://h.cricapi.com/img/players/1ee41e9e-e219-4df2-9861-2360b28bb307.jpg"
                        },
                        {
                        "id": "6004fd3f-2264-470d-b39f-340d530b19b3",
                        "name": "Trent Boult",
                        "role": "Bowler",
                        "battingStyle": "Right Handed Bat",
                        "bowlingStyle": "Left-arm fast-medium",
                        "country": "New Zealand",
                        "playerImg": "https://h.cricapi.com/img/players/6004fd3f-2264-470d-b39f-340d530b19b3.jpg"
                        },
                        {
                        "id": "10237113-888e-4881-a360-4b08577f38cc",
                        "name": "Obed McCoy",
                        "role": "Bowler",
                        "battingStyle": "Left Handed Bat",
                        "bowlingStyle": "Left-arm fast-medium",
                        "country": "West Indies",
                        "playerImg": "https://h.cricapi.com/img/players/10237113-888e-4881-a360-4b08577f38cc.jpg"
                        },
                        {
                        "id": "0068c9d8-be69-46b9-bbef-62c74e480781",
                        "name": "Ravichandran Ashwin",
                        "role": "Bowling Allrounder",
                        "battingStyle": "Right Handed Bat",
                        "bowlingStyle": "Right-arm offbreak",
                        "country": "India",
                        "playerImg": "https://h.cricapi.com/img/players/0068c9d8-be69-46b9-bbef-62c74e480781.jpg"
                        },
                        {
                        "id": "a887af00-ef83-411a-9a42-6758fb6fead6",
                        "name": "Akash Vasisht",
                        "role": "Bowler",
                        "battingStyle": "Left Handed Bat",
                        "bowlingStyle": "Left-arm orthodox",
                        "country": "India",
                        "playerImg": "https://h.cricapi.com/img/icon512.png"
                        },
                        {
                        "id": "cdbccd5a-7f3f-4876-86d8-708578b63ee6",
                        "name": "Abdul Basith",
                        "role": "Bowling Allrounder",
                        "battingStyle": "Right Handed Bat",
                        "bowlingStyle": "Right-arm offbreak",
                        "country": "India",
                        "playerImg": "https://h.cricapi.com/img/icon512.png"
                        },
                        {
                        "id": "b51bb4e5-acdf-423b-abb3-7a1e6694d2c2",
                        "name": "Riyan Parag",
                        "role": "Batsman",
                        "battingStyle": "Right Handed Bat",
                        "bowlingStyle": "Right-arm legbreak",
                        "country": "India",
                        "playerImg": "https://h.cricapi.com/img/players/b51bb4e5-acdf-423b-abb3-7a1e6694d2c2.jpg"
                        },
                        {
                        "id": "a254feed-0d7c-4f04-a2ab-7bf9ceef156b",
                        "name": "Yashasvi Jaiswal",
                        "role": "Batsman",
                        "battingStyle": "Left Handed Bat",
                        "bowlingStyle": "Right-arm legbreak",
                        "country": "India",
                        "playerImg": "https://h.cricapi.com/img/players/a254feed-0d7c-4f04-a2ab-7bf9ceef156b.jpg"
                        },
                        {
                        "id": "e7e08377-a86d-4ce2-8d19-8e748d140417",
                        "name": "Kuldip Yadav",
                        "role": "Bowler",
                        "battingStyle": "Left Handed Bat",
                        "bowlingStyle": "Left-arm fast-medium",
                        "country": "India",
                        "playerImg": "https://h.cricapi.com/img/icon512.png"
                        },
                        {
                        "id": "21d693c2-b4dd-4d24-b747-90dfc8357ef5",
                        "name": "Dhruv Jurel",
                        "role": "WK-Batsman",
                        "battingStyle": "Right Handed Bat",
                        "country": "India",
                        "playerImg": "https://h.cricapi.com/img/players/21d693c2-b4dd-4d24-b747-90dfc8357ef5.jpg"
                        },
                        {
                        "id": "5eee9bae-6aff-4088-bbf4-93837d0250b0",
                        "name": "KC Cariappa",
                        "role": "Bowler",
                        "battingStyle": "Right Handed Bat",
                        "bowlingStyle": "Right-arm legbreak",
                        "country": "India",
                        "playerImg": "https://h.cricapi.com/img/players/5eee9bae-6aff-4088-bbf4-93837d0250b0.jpg"
                        },
                        {
                        "id": "cd141985-bffd-4ffb-8817-9afdafa25e15",
                        "name": "Murugan Ashwin",
                        "role": "Bowler",
                        "battingStyle": "Right Handed Bat",
                        "bowlingStyle": "Right-arm legbreak",
                        "country": "India",
                        "playerImg": "https://h.cricapi.com/img/players/cd141985-bffd-4ffb-8817-9afdafa25e15.jpg"
                        },
                        {
                        "id": "80193c8f-687d-47c3-a7e9-b098a83c7812",
                        "name": "Navdeep Saini",
                        "role": "Bowler",
                        "battingStyle": "Right Handed Bat",
                        "bowlingStyle": "Right-arm fast",
                        "country": "India",
                        "playerImg": "https://h.cricapi.com/img/players/80193c8f-687d-47c3-a7e9-b098a83c7812.jpg"
                        },
                        {
                        "id": "1971093d-b87b-43db-8b1d-b2dcc8e68617",
                        "name": "Adam Zampa",
                        "role": "Bowler",
                        "battingStyle": "Right Handed Bat",
                        "bowlingStyle": "Right-arm legbreak",
                        "country": "Australia",
                        "playerImg": "https://h.cricapi.com/img/players/1971093d-b87b-43db-8b1d-b2dcc8e68617.jpg"
                        },
                        {
                        "id": "b43c2877-2cb4-41f5-951d-bc006eb4f6c0",
                        "name": "Kuldeep Sen",
                        "role": "Bowler",
                        "battingStyle": "Right Handed Bat",
                        "bowlingStyle": "Right-arm fast-medium",
                        "country": "India",
                        "playerImg": "https://h.cricapi.com/img/icon512.png"
                        },
                        {
                        "id": "74c6584a-45a5-4781-a5e7-c0c9340da954",
                        "name": "Devdutt Padikkal",
                        "role": "Batsman",
                        "battingStyle": "Left Handed Bat",
                        "bowlingStyle": "Right-arm offbreak",
                        "country": "India",
                        "playerImg": "https://h.cricapi.com/img/players/74c6584a-45a5-4781-a5e7-c0c9340da954.jpg"
                        },
                        {
                        "id": "3f18b02d-0e1a-49be-aec4-c2fc11503505",
                        "name": "Sandeep Sharma",
                        "role": "Bowler",
                        "battingStyle": "Right Handed Bat",
                        "bowlingStyle": "Right-arm fast-medium",
                        "country": "India",
                        "playerImg": "https://h.cricapi.com/img/players/3f18b02d-0e1a-49be-aec4-c2fc11503505.jpg"
                        },
                        {
                        "id": "f8e6accd-6b73-4869-93a6-d45519a361f0",
                        "name": "Jason Holder",
                        "role": "Bowling Allrounder",
                        "battingStyle": "Right Handed Bat",
                        "bowlingStyle": "Right-arm fast-medium",
                        "country": "West Indies",
                        "playerImg": "https://h.cricapi.com/img/players/f8e6accd-6b73-4869-93a6-d45519a361f0.jpg"
                        },
                        {
                        "id": "3f9ced2d-d71a-4478-93db-d7260c7145ee",
                        "name": "Donavon Ferreira",
                        "role": "WK-Batsman",
                        "battingStyle": "Right Handed Bat",
                        "bowlingStyle": "Right-arm offbreak",
                        "country": "South Africa",
                        "playerImg": "https://h.cricapi.com/img/icon512.png"
                        },
                        {
                        "id": "35ed1b20-38f3-4013-be2e-dc28ffbecfd6",
                        "name": "Sanju Samson",
                        "role": "WK-Batsman",
                        "battingStyle": "Right Handed Bat",
                        "country": "India",
                        "playerImg": "https://h.cricapi.com/img/players/35ed1b20-38f3-4013-be2e-dc28ffbecfd6.jpg"
                        },
                        {
                        "id": "7567e305-1b40-4eee-9290-e2fcb8804496",
                        "name": "Jos Buttler",
                        "role": "WK-Batsman",
                        "battingStyle": "Right Handed Bat",
                        "country": "England",
                        "playerImg": "https://h.cricapi.com/img/players/7567e305-1b40-4eee-9290-e2fcb8804496.jpg"
                        }
                        ]
                        }
                        ]
                          
                          }


    async def cog_unload(self):
        self.live_score.cancel()  
        
    @tasks.loop( minutes= 1)
    async def live_score(self):
        pass
    
    @commands.hybrid_command()
    @commands.guild_only()
    @commands.is_owner()
    # @cooldown(1, 5, BucketType.user)
    async def join(self , ctx ):
        view = View()
        embed = discord.Embed(color=123456 , title= 'Select Match!')
        select = SelectMatch(placeholder= 'Select Match !')
        
        for i , match in enumerate(reversed(self.eCricScore['data'])) :
            if match['ms'] == 'fixture' and match['id'] in self.ipl_matches :
                dt_string = match['dateTimeGMT']
                dt = datetime.strptime(dt_string, "%Y-%m-%dT%H:%M:%S")
                if dt < ( datetime.now() + timedelta(days=3) )  :
                    #embed
                    embed.add_field(name = f"{len(embed.fields)+1}. {match['t1'].split('[')[1][:-1]} vs {match['t2'].split('[')[1][:-1]}" , value= f"\n{match['t1'].split('[')[0][:-1]} vs {match['t2'].split('[')[0][:-1]}\n<t:{int(dt.timestamp())}:R>" , inline= False )
                    #button
                    disabled = True if match['id'] not in self.fantasy_live or dt < datetime.now() else False
                    if disabled == False :
                        style = discord.ButtonStyle.success
                        #adding select option
                        select.add_option(label= f"{len(embed.fields)}. {match['t1'].split('[')[1][:-1]} vs {match['t2'].split('[')[1][:-1]}" , value= match['id']  )
                    elif dt < datetime.now() :
                        style = discord.ButtonStyle.danger
                    else :
                        style = discord.ButtonStyle.secondary         
                    # button = Button(label= len(embed.fields) , style=style , disabled= disabled )
                    # view.add_item(button)
                    #select
        view.add_item(select)                   
        await ctx.send(embed = embed , view = view)
    
    @join.error
    async def join_error(self , ctx ,error) :
        await ctx.send(error)
        
class SelectMatch(Select) :
    
    async def callback( self , interaction : discord.Interaction ) :
        
        view = View()
        embed = discord.Embed(color=123456 , title= 'Join Event!')
        select = SelectEvent(placeholder= 'Select Match !')
        
        for event_id in event :
            if  self.values[0] in event[ event_id]['matches'] or 'all' in event[ event_id ]['matches'] :
                embed.add_field(name = f"{len(embed.fields)+1}. {event[event_id]['name']}" , value= f"Price Poll : {event[event_id]['price_poll']}\nEntry Fee : {event[ event_id]['entry_fee']}\nSlot Left : {event[event_id]['max_entry'] - len(event[event_id]['entries'])}" , inline= False )
                select.add_option(label= f"{len(embed.fields)}. {event[event_id]['name']}" , value= event_id)
        view.add_item(select)
        await interaction.response.edit_message(embed = embed , view = view) 
        
class SelectEvent(Select) :
    
    async def callback( self , interaction : discord.Interaction ) :
        player_list = []
        view = View()
        embed = discord.Embed(color=123456 , title= 'Select Team'  , description= " hello ")
        wk = Select(placeholder= 'Select 1-8 Wicket Keepers' , max_values= 6 )
        bat = Select(placeholder= 'Select 1-8 Batters' , max_values= 6 )
        ar = Select(placeholder= 'Select 1-8 All-Rounder'  , max_values= 6 )
        bowl = Select(placeholder= 'Select 1-8 Bowlers'   , max_values= 6)
        
        for team in players :
            player_list = player_list + team['players']
            
        for player in player_list: 
            if player['role'] == "Batsman" :
                bat.add_option(label= player['name'] , value=player['id'])
                
            if player['role'] == "Bowler" :
                bowl.add_option(label= player['name'] , value=player['id'])
            
            if 'WK' in player['role'] :
                wk.add_option(label= player['name'] , value=player['id'])
            
            if 'Allrounder' in player['role'] :
                ar.add_option(label= player['name'] , value=player['id'])
        
        view.add_item(bat)
        view.add_item(wk)
        view.add_item(ar)
        view.add_item(bowl)
        await interaction.response.edit_message( embed= embed , view = view   )    

        # view = View()
        # embed = discord.Embed(color=123456 , title= 'Join Event!')
        # select = Select(placeholder= 'Select Match !')
        
        # for event_id in event :
        #     if  self.values[0] in event[ event_id]['matches'] or 'all' in event[ event_id ]['matches'] :
        #         embed.add_field(name = f"{len(embed.fields)+1}. {event[event_id]['name']}" , value= f"Price Poll : {event[event_id]['price_poll']}\nEntry Fee : {event[ event_id]['entry_fee']}\nSlot Left : {event[event_id]['max_entry'] - len(event[event_id]['entries'])}" , inline= False )
        #         select.add_option(label= f"{len(embed.fields)}. {event[event_id]['name']}" , value= event_id)
        # view.add_item(select)
        # await interaction.response.edit_message(embed = embed , view = view)               

async def setup(client):
   await client.add_cog(IPL(client))                       