#!/usr/bin/env python3

# 0x44 update board

import struct
import serial

class ChessBoard(object):
	def __init__(self):
		self.board = []
		for i in range(8):
			self.board.append(8 * [(None, None)])

	def update(self, x, y, figure):
		self.board[y][x] = figure

	def draw(self):
		for y, row in enumerate(self.board):
			print("\033[0;00m")
			for x, figure in enumerate(row):
				# background colors: 220 130

				color, _ = figure
				match figure:
					case ("white", "pawn"):
						c = "\u2659"
					case ("white", "rook"):
						c = "\u2656"
					case ("white", "knight"):
						c = "\u2658"
					case ("white", "bishop"):
						c = "\u2657"
					case ("white", "king"):
						c = "\u2654"
					case ("white", "queen"):
						c = "\u2655"
					case ("black", "pawn"):
						c = "\u265F"
					case ("black", "rook"):
						c = "\u265C"
					case ("black", "knight"):
						c = "\u265E"
					case ("black", "bishop"):
						c = "\u265D"
					case ("black", "king"):
						c = "\u265A"
					case ("black", "queen"):
						c = "\u265B"
					case (None, None): c = " "
					case default:
						assert False, figure

				background_color = 220 if (x + y) % 2 == 0 else 130
				print("\033[38;5;%sm\033[48;5;%sm" % (15 if color == "white" else 0, background_color,), end="")
				print(c, end="")

		print("\033[0;00m")

board = ChessBoard()

figures = [
	(None, None),  # 0
	("white", "pawn"), # 1
	("white", "rook"), # 2
	("white", "knight"), # 3
	("white", "bishop"), # 4
	("white", "king"), # 5
	("white", "queen"), # 6
	("black", "pawn"), # 7
	("black", "rook"), # 8
	("black", "knight"), # 9
	("black", "bishop"), # 10
	("black", "king"), # 11
	("black", "queen"), # 12
]

assert struct.calcsize(">H") == 2
# b'\x91\x00\x0809713', [145, 0, 8, 48, 57, 55, 49, 51]
ser = serial.Serial("/dev/ttyUSB0", 9600, timeout=0.3)

"""
->  0x42
<-  type 0x86 len: 67: b'\x08\t\n\x0c\x0b\n\t\x08\x07\x07\x07\x07\x07\x07\x07\x07\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x01\x01\x01\x01\x01\x01\x01\x01\x02\x03\x04\x06\x05\x04\x03\x02'
 [8, 9, 10, 12, 11, 10, 9, 8, 7, 7, 7, 7, 7, 7, 7, 7, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 1, 1, 1, 1, 1, 1, 1, 1, 2, 3, 4, 6, 5, 4, 3, 2]
"""

CMD_GET_BOARD = 0x42
CMD_GET_MOVEMENT = 0x44
CMD_GET_SERNR = 0x45
CMD_GET_KQ = 0x46
CMD_GET_VENDOR_INFO = 0x47
CMD_GET_MOVEMENT2 = 0x48
CMD_127 = 0x49 # dangerous
# = 0x4A # no response
CMD_GET_MOVEMENT3 = 0x4B
CMD_GET_MOVEMENT4 = 0x4C

RESPONSE_129 = 0x81
RESPONSE_BOARD = 0x86
RESPONSE_MOVEMENT = 0x8E
RESPONSE_127 = 0x8F # dangerous [127, 127, ...]
RESPONSE_KQ = 0x90
RESPONSE_SERNR = 0x91
RESPONSE_VENDOR_INFO = 0x92

cmd = CMD_GET_MOVEMENT

def queue_command(cmd):
	ser.write([cmd])
	ser.flush()

def send_command(cmd):
	queue_command(cmd)
	t_raw = ser.read(1)
	if t_raw == b"":
		return None, None
	print("-> ", hex(cmd))
	l_raw = ser.read(2)
	l, = struct.unpack(">H", l_raw)
	t, = struct.unpack("B", t_raw)
	print("<- ", "type", hex(t), "len:", l, end=": ")
	payload_raw = ser.read(l - 1 - 2)
	print(payload_raw, [x for x in payload_raw])
	return t, payload_raw

queue_command(CMD_GET_BOARD)

while True:
	#cmd = cmd + 1
	#if cmd > 127:
	#	cmd = 0x4C
	# 0x44 existiert
	#cmd = CMD_GET_MOVEMENT

	t, payload_raw = send_command(cmd)
	if payload_raw is None:
		continue

	#print(payload_raw)
	print(payload_raw, [x for x in payload_raw])
	if t == RESPONSE_MOVEMENT:
		position, figure = struct.unpack("BB", payload_raw)
		y = position // 8
		x = position % 8
		print("FIG", figure, figures[figure])
		board.update(x, y, figures[figure])
		print("")
		board.draw()
		print("")
	elif t == RESPONSE_BOARD:
		board_bytes = struct.unpack("64B", payload_raw)
		for position, figure in enumerate(board_bytes):
			y = position // 8
			x = position % 8
			board.update(x, y, figures[figure])
		print(board_bytes)
		board.draw()

	#s = ser.read(20)
