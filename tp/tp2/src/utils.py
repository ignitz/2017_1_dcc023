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

# ID reservado ao servidor
# 2**16-1
SERVER_ID = 65535

# DEBUG
# Se setado em True, print_bold e print_warning tornam-se operacionais
DEBUG = False

# Constantes destinados ao tipo de cliente
class client_type:
	EMISSOR = 1
	EXIBIDOR = 2

# Constantes para o tipo de mensagem no cabeçalho
class msg_type:
	OK = 1
	ERRO = 2
	OI = 3
	FLW = 4
	MSG = 5
	CREQ = 6
	CLIST = 7

# Colorir letras. Testado apenas no Linux.
class bcolors:
	HEADER = '\033[95m'
	OKBLUE = '\033[94m'
	OKGREEN = '\033[92m'
	WARNING = '\033[93m'
	FAIL = '\033[91m'
	ENDC = '\033[0m'
	BOLD = '\033[1m'
	UNDERLINE = '\033[4m'

# Estrutura do cabeçalho
class Header:
	struct = struct.Struct('! H H H H')

"""
Abaixo contém funções para imprimir com cor no terminal
Alguns tem como propósito de DEBUG
"""
def print_header(msg, end=None):
	if end is None:
		print(bcolors.HEADER + str(msg) + bcolors.ENDC)
	else:
		print(bcolors.HEADER + str(msg) + bcolors.ENDC, end=end)

def print_bold(msg, end=None):
	if DEBUG:
		if end is None:
			print(bcolors.BOLD + str(msg) + bcolors.ENDC)
		else:
			print(bcolors.BOLD + str(msg) + bcolors.ENDC, end=end)

def print_blue(msg, end=None):
	if end is None:
		print(bcolors.OKBLUE + str(msg) + bcolors.ENDC)
	else:
		print(bcolors.OKBLUE + str(msg) + bcolors.ENDC, end=end)

def print_green(msg, end=None):
	if end is None:
		print(bcolors.OKGREEN + str(msg) + bcolors.ENDC)
	else:
		print(bcolors.OKGREEN + str(msg) + bcolors.ENDC, end=end)

def print_warning(msg, end=None):
	if DEBUG:
		if end is None:
			print(bcolors.WARNING + str(msg) + bcolors.ENDC)
		else:
			print(bcolors.WARNING + str(msg) + bcolors.ENDC, end=end)

# print errors in RED
def print_error(msg, end=None):
	if end is None:
		print(bcolors.FAIL + str(msg) + bcolors.ENDC)
	else:
		print(bcolors.FAIL + str(msg) + bcolors.ENDC, end=end)
