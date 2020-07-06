import os
import tkinter as tk
import socket
import yaml
import zlib
from datetime import datetime
from time import time_ns
import asyncio

def sendudp(dstPort, srcPort, ip, data):

	sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
	sock.bind(('0.0.0.0', srcPort))
	sock.sendto(data, (ip, dstPort))

def listenudp(port, ip):

	sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
	sock.bind((ip, port))

	while True:
		data, addr = sock.recvfrom(1024) # buffer size is 1024 bytes
		print("received message: %s" %data)

class Packet:

	def __init__(self, packetStructureFileName):
		self.filePath = os.path.dirname(os.path.abspath(__file__))
		os.chdir(self.filePath)
		print(os.getcwd())

		self.packetStructureFileName = packetStructureFileName
		with open(self.packetStructureFileName) as yml:
			self.packetStructure = yaml.load(yml, Loader = yaml.FullLoader)

		for self.packetName in self.packetStructure:
			break
		
		self.sourcePort = 44620
		self.destinationPort = 60804
		self.interval = 200
		self.destinationIpAddr = '192.168.1.24'
		self.counter = -1

	async def main(self):

		while(1):
			
			old = datetime.now()
			self.createPacket()
			print(self.packet)
			new = datetime.now() - old

			await asyncio.sleep((200 - round(new.microseconds / 1000)) / 1000)

			sendudp(self.destinationPort, self.sourcePort, self.destinationIpAddr, self.packet)

	def incrementCounter(self):
		if self.counter == 4294967295:
			self.counter = 0
		else:
			self.counter += 1
		return bytes.fromhex(hex(self.counter)[2:].zfill(8))

	def createPacket(self):

		self.packet = bytes()

		with open(self.packetStructureFileName) as yml:
			self.packetStructure = yaml.load(yml, Loader = yaml.FullLoader)

		for field in self.packetStructure[self.packetName]:
			if self.packetStructure[self.packetName][field]['autoFill']:
				try:
					if self.packetStructure[self.packetName][field]['eval']:
						self.packet += eval(self.packetStructure[self.packetName][field]['val'])
					else:
						self.packet += bytes.fromhex(self.packetStructure[self.packetName][field]['val'])
				except ValueError:
					print('skipped packet due to value error')
def drive():
	sdr = Packet('sdr.yml')
	asyncio.run(sdr.main())
