"""
Este módulo providencia as bibliotecas para os módulos do cliente e servidor
assim como algumas constantes.
"""

import socket
import select
# stdin
import sys

# bibliotecas para transformar dados RAW
import struct
import binascii
import ctypes

# sort list with attribute
import operator

# Print cosmético de estruturas de dados da linguagem, DEBUG purpose.
import pprint

import time

# Protocol const (uint16_t)
CLIREQ = 1
QUERY = 2
RESPONSE = 3

TTL_INITIAL_DEFAULT = 3

# 40 da key + 160 valor associado
BUFFER_SIZE = 202

# TIMEOUT do client quando enviar uma QUERY e esperar por RESPONSE
TIMEOUT_CLIENT = 4

# DEBUG
# Se setado em True, print_bold e print_warning tornam-se operacionais
DEBUG = False

# Colorir letras. Testado apenas no Linux.
CYAN = '\033[95m'
BLUE = '\033[94m'
GREEN = '\033[92m'
WARNING = '\033[93m'
FAIL = '\033[91m'
ENDC = '\033[0m'
BOLD = '\033[1m'
UNDERLINE = '\033[4m'

"""
Abaixo contém funções para imprimir com cor no terminal
Alguns tem como propósito de DEBUG
"""
def print_purple(msg, end=None):
	if end is None:
		print(CYAN + str(msg) + ENDC)
	else:
		print(CYAN + str(msg) + ENDC, end=end)

def print_blue(msg, end=None):
	if end is None:
		print(BLUE + str(msg) + ENDC)
	else:
		print(BLUE + str(msg) + ENDC, end=end)

def print_green(msg, end=None):
	if end is None:
		print(GREEN + str(msg) + ENDC)
	else:
		print(GREEN + str(msg) + ENDC, end=end)

def print_bold(msg, end=None):
	if DEBUG:
		if end is None:
			print(BOLD + str(msg) + ENDC)
		else:
			print(BOLD + str(msg) + ENDC, end=end)

def print_warning(msg, end=None):
	if DEBUG:
		if end is None:
			print(WARNING + str(msg) + ENDC)
		else:
			print(WARNING + str(msg) + ENDC, end=end)

# print errors in RED
def print_error(msg, end=None):
	if end is None:
		print(FAIL + str(msg) + ENDC)
	else:
		print(FAIL + str(msg) + ENDC, end=end)
