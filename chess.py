#!/usr/bin/python
# -*- coding: utf-8 -*-
"""################################################################################
#
# File Name         : chess.py
# Created By        : Florian MAUFRAIS
# Creation Date     : décembre 8th, 2015
# Version           : 1.0
# Last Change       : August 08th, 2016 at 10:45:00
# Last Changed By   : Florian MAUFRAIS
# Contact           : florian.maufrais@gmail.com
# Purpose           : A complete lib for playing chess, including a cmd for
#                     1 Vs. 1 player, no AI available for this version,
#                     perhaps on 2.0 version.
#                     Lanch main() and play ! ! !
#                     You can also use as a library for Chessboard and Piece 
#                     class, your own version on chess, why not crear another 
#                     interface (graphic or serveur with socket to play 
#                     online),
# 
#                     This program need optimisation and may have bugs, 
#                     If you have any sugestion, please contact !
#
################################################################################"""

import cmd, pyparsing, sys, optparse, re

from optparse import make_option

if sys.version_info[0] == 2:
    pyparsing.ParserElement.enablePackrat()

class OptionParser(optparse.OptionParser):
    def exit(self, status=0, msg=None):
        self.values._exit = True
        if msg:
            print (msg)       
    def print_help(self, *args, **kwargs):
        try:
            print (self._func.__doc__)
        except AttributeError:
            pass
        optparse.OptionParser.print_help(self, *args, **kwargs)
    def error(self, msg):
        """error(msg : string)

        Print a usage message incorporating 'msg' to stderr and exit.
        If you override this in a subclass, it should not return -- it
        should either exit or raise an exception.
        """
        raise optparse.OptParseError(msg)
        
def remaining_args(oldArgs, newArgList):
	pattern = '\s+'.join(re.escape(a) for a in newArgList)
	matchObj = re.search(pattern, oldArgs)
	try:
		return oldArgs[matchObj.start():matchObj.end()]
	except:
		return oldArgs

def _attr_get_(obj, attr):
	try:
		return getattr(obj, attr)
	except AttributeError:
		return None

optparse.Values.get = _attr_get_

options_defined = [] # used to distinguish --options from SQL-style --comments

def options(option_list, arg_desc="arg"):
	if not isinstance(option_list, list):
		option_list = [option_list]
	for opt in option_list:
		options_defined.append(pyparsing.Literal(opt.get_opt_string()))
	def option_setup(func):
		optionParser = OptionParser()
		for opt in option_list:
			optionParser.add_option(opt)
		optionParser.set_usage("%s [options] %s" % (func.__name__[3:], arg_desc))
		optionParser._func = func
		def new_func(instance, arg):
			try:
				opts, newArgList = optionParser.parse_args(arg.split())
				newArgs = remaining_args(arg, newArgList)
				if isinstance(arg, ParsedString):
					arg = arg.with_args_replaced(newArgs)
				else:
					arg = newArgs
			except optparse.OptParseError as e:
				print (e)
				optionParser.print_help()
				return
			if hasattr(opts, '_exit'):
				return None
			result = func(instance, arg, opts)                            
			return result
		new_func.__doc__ = '%s\n%s' % (func.__doc__, optionParser.format_help())
		return new_func
	return option_setup

pyparsing.ParserElement.setDefaultWhitespaceChars(' \t')

def translate_move(move):
	try:
		return chr(int(move[1])+65)+str(int(move[0]+1))
	except:
		raise ValueError, 'Invalid format for a move !'

class ParsedString(str):
	def full_parsed_statement(self):
		new = ParsedString('%s %s' % (self.parsed.command, self.parsed.args))
		new.parsed = self.parsed
		new.parser = self.parser
		return new       
	def with_args_replaced(self, newargs):
		new = ParsedString(newargs)
		new.parsed = self.parsed
		new.parser = self.parser
		new.parsed['args'] = newargs
		new.parsed.statement['args'] = newargs
		return new

class Chessboard:
	"""A class implement all caracteristic of a chessboard
	"""
	def __init__(self, pieces = None):
		"""Initilize the chessboard

		3 different type of initialization :
			- None : get an empty chessboard
			- 'default' : give a classic chessboard, realy to go !
			- dict : complete the chessboard with the given dict of pieces : {Piece:Position,...}
			- list : complete the chessboard with the given list of pieces, Piece or [] are needed, line are completed by 8, idem for column

		After initialization, any pieces get it chessboard update !
		"""
		if isinstance(pieces, dict):
			try:
				if not False in set([isinstance(item, Piece) for item in pieces.keys()]) and not False in set([isinstance(item, Position) for item in pieces.values()]):
					self.__chessboard = [[[],[],[],[],[],[],[],[]],\
							[[],[],[],[],[],[],[],[]],\
							[[],[],[],[],[],[],[],[]],\
							[[],[],[],[],[],[],[],[]],\
							[[],[],[],[],[],[],[],[]],\
							[[],[],[],[],[],[],[],[]],\
							[[],[],[],[],[],[],[],[]],\
							[[],[],[],[],[],[],[],[]]]
					for piece in pieces:
						pos = pieces[piece].__list__()
						self.__chessboard[pos[0]-1][pos[1]-1] = piece
					self.__reset_chessboard()
				else:
					return None
			except:
				return None
		elif pieces == None:
			self.__chessboard = [[[],[],[],[],[],[],[],[]],\
							[[],[],[],[],[],[],[],[]],\
							[[],[],[],[],[],[],[],[]],\
							[[],[],[],[],[],[],[],[]],\
							[[],[],[],[],[],[],[],[]],\
							[[],[],[],[],[],[],[],[]],\
							[[],[],[],[],[],[],[],[]],\
							[[],[],[],[],[],[],[],[]]]
		elif pieces == 'default':
			self.__chessboard = [[Piece('rock','white',1, Chessboard()), 
								Piece('knight', 'white',  1, Chessboard()), 
								Piece('bishop', 'white',  1, Chessboard()), 
								Piece('king', 'white', None, Chessboard()), 
								Piece('queen', 'white', 1, Chessboard()), 
								Piece('bishop', 'white',  2, Chessboard()), 
								Piece('knight', 'white',  2, Chessboard()), 
								Piece('rock', 'white',  2, Chessboard())],\
							[Piece('pawn', 'white',  1, Chessboard()), 
								Piece('pawn', 'white',  2, Chessboard()), 
								Piece('pawn', 'white',  3, Chessboard()), 
								Piece('pawn', 'white',  4, Chessboard()), 
								Piece('pawn', 'white',  5, Chessboard()), 
								Piece('pawn', 'white',  6, Chessboard()), 
								Piece('pawn', 'white',  7, Chessboard()), 
								Piece('pawn', 'white',  8, Chessboard())],\
							[[],[],[],[],[],[],[],[]],\
							[[],[],[],[],[],[],[],[]],\
							[[],[],[],[],[],[],[],[]],\
							[[],[],[],[],[],[],[],[]],\
							[Piece('pawn', 'black',  1, Chessboard()), 
								Piece('pawn', 'black',  2, Chessboard()), 
								Piece('pawn', 'black',  3, Chessboard()), 
								Piece('pawn', 'black',  4, Chessboard()), 
								Piece('pawn', 'black',  5, Chessboard()), 
								Piece('pawn', 'black',  6, Chessboard()), 
								Piece('pawn', 'black',  7, Chessboard()), 
								Piece('pawn', 'black',  8, Chessboard())],\
							[Piece('rock', 'black',  1, Chessboard()), 
								Piece('knight', 'black',  1, Chessboard()), 
								Piece('bishop', 'black',  1, Chessboard()), 
								Piece('queen', 'black', 1, Chessboard()), 
								Piece('king', 'black', None, Chessboard()), 
								Piece('bishop', 'black',  2, Chessboard()), 
								Piece('knight', 'black',  2, Chessboard()), 
								Piece('rock', 'black',  2, Chessboard())]]
			self.__reset_chessboard()
		elif isinstance(pieces, list):
			try:
				self.__chessboard = [[[],[],[],[],[],[],[],[]],\
							[[],[],[],[],[],[],[],[]],\
							[[],[],[],[],[],[],[],[]],\
							[[],[],[],[],[],[],[],[]],\
							[[],[],[],[],[],[],[],[]],\
							[[],[],[],[],[],[],[],[]],\
							[[],[],[],[],[],[],[],[]],\
							[[],[],[],[],[],[],[],[]]]
				for pos in range(len(pieces)):
					if isinstance(pieces[pos],Piece) or pieces[pos] == []:
						self.__chessboard[pos/8][pos%8] = pieces[pos]
					else:
						return None
			except:
				return None
		else:
			return None
	def __reset_chessboard(self):
		for line in self.__chessboard:
			for piece in line:
				if isinstance(piece, Piece):
					piece.set_chessboard(self)
	def get_pieces_in_game(self, color='all'):
		"""Return the list of pieces in the chessboard,
		Default all pieces, but it can be filter by color (black or white)
		"""
		if color.lower() in ['all','white','black']:
			element = []
			for line in self.__chessboard:
				for piece in line:
					if isinstance(piece, Piece) and (color.lower() == piece.color or color.lower() == 'all'):
							element.append(piece)
			return element
		else:
			return None
	__pieces__ = pieces = get_pieces_in_game
	def add_piece(self, piece, position):
		"""Add giving piece to the chessboard,
			
		The chessboard is not update after !
		"""
		if isinstance(piece, Piece):
			if not False in set([position != piece.position() for piece in self.pieces()]+[True]):
				piece.chessboard = self
				pos = piece.position()
				self.__chessboard[pos[0]][pos[1]] = piece
		else:
			pass
	def is_valid_move(self, piece, position):
		"""Check if the position do a valide move 
		
		There is Check ?
			Yes => did the move change this ?
				Yes => move valid
				No => move not valid
			No => move valid
		"""
		if isinstance(piece, Piece) and piece in self.pieces(piece.color) and isinstance(position, Position):
			chessboard = [[p for p in line] for line in self.__chessboard]
			own_pos = piece.position()
			pos = position.__list__()
			self.__chessboard[pos[0]][pos[1]] = piece
			self.__chessboard[own_pos[0]][own_pos[1]] = []
			self.__reset_chessboard()
			own = []
			for line in self.__chessboard:
				for p in line:
					if isinstance(p, Piece) and (p.color == ('black','white')[piece.color == 'white']):
							own.append(p)
			king = [p for p in own if p.type == 'king'][0]		
			other = []
			for line in self.__chessboard:
				for p in line:
					if isinstance(p, Piece) and (p.color == ('black','white')[piece.color == 'black']):
							other.append(p)
			other_moves = []
			for p in other:
				other_moves += p.get_moves(self.__chessboard)
			keep = True
			for p in other:
				moves = p.get_moves(self.__chessboard)
				if king.position() in moves:
					keep = False
			self.__chessboard = chessboard
			self.__reset_chessboard()
			return keep
		else:
			return None
	def move(self, piece, position):
		"""Check if the move is valid, look for Chessboard.is_valid_move(...)
		
		And so change the piece of position, update chessboard for all pieces
		"""
		if self.is_valid_move(piece,position):
			pos = position.__list__()
			own_pos = piece.position()
			self.__chessboard[pos[0]][pos[1]] = piece
			self.__chessboard[own_pos[0]][own_pos[1]] = []
			self.__reset_chessboard()
		return self
	def get_multi_moves(self, turns, pieces):
		"""Return simulation of moves for pieces on the chessboard,
		Given pieces and all other color; Given pieces play 'turns' times and other play 'turns'-1 times
		
		Only one color for all pieces is request
		"""
		if isinstance(turns, int) and isinstance(pieces, list) and len(pieces) > 0 and len(set([piece.__class__.__name__ for piece in pieces])) == 1 and\
			list(set([piece.__class__.__name__ for piece in pieces]))[0] == 'Piece' and len(set([piece.color for piece in pieces])) == 1:
			chess = [[p for p in line] for line in self.__chessboard]
			res_chess = [[chess]]
			for turn in range(2*turns-1):
				print '#'*20+'\n'+'#'*5+' Trun :',turn,'#'*5+'\n'+'#'*20
				res_chess.append([])
				for simulation in range(len(res_chess[turn])):
					print '#'*20+'\n'+'#'*5+' Simu :',simulation,'#'*5+'\n'+'#'*20
					self.__chessboard = [[p for p in line] for line in res_chess[turn][simulation]]
					self.__reset_chessboard()
					for piece in (self.pieces(('black','white')[pieces[0].color == 'black']), pieces)[turn%2 == 0]:
						moves = piece.get_moves(self.__chessboard)
						print piece.__str__(),':',moves
						i = 0
						while i < len(moves):
							self.move(piece,Position(moves[i][1],moves[i][0]))
							res_chess[turn+1].append([[p for p in line] for line in self.__chessboard])
							#for ligne in self.__chessboard:
							#	print '|',
							#	for item in ligne:
							#		print ' '*((18-len(item.__str__()))/2)+item.__str__()+' '*((18-len(item.__str__()))/2+(18-len(item.__str__()))%2)+'|',
							#	print
							self.__chessboard = [[p for p in line] for line in res_chess[turn][simulation]]
							self.__reset_chessboard()
							i += 1
			self.__chessboard = chess
			self.__reset_chessboard()
			return res_chess[0]
		else:
			return None		
	def __list__(self):
		return self.__chessboard

class Piece:
	"""A class implement all caracteristic of a chessboard piece
	"""
	types = ['pawn','rock','knight','bishop','queen','king']
	colors = ['white','black']
	__hash__ = None
	def __init__(self, type, color, number, chessboard):
		"""Initilize the piece
		1. type from Piece.types
		2. color from Piece.colors
		3. number, an int between 1 and 10 or None (only for king)
		
		NB : Only one king for each color in the chessboard
		"""
		if type in ['pawn','rock','knight','bishop','queen','king']:
			if color in ['white','black']:
				if isinstance(chessboard, Chessboard):
					try:
						if type == 'king' and number == None and [piece for piece in chessboard.pieces() if piece.type == 'king' and piece.color == color] == []:
							self.__number = None
							self.__type = type
							self.__color = color
							self.__chessboard = chessboard
							self.__position = None
							for j in range(len(chessboard.__list__())):
								for i in range(len(chessboard.__list__()[j])):
									if chessboard.__list__()[j][i] == self:
										self.__position = [j,i]
										return self
							#if self.__position == None:
							#	print 'Pos not found ! (__init__) (',type,color,number,')'
						elif int(number) > 0 and type != 'king':
							self.__number = number
							self.__type = type
							self.__color = color
							self.__chessboard = chessboard
							self.__position = None
							for j in range(len(chessboard.__list__())):
								for i in range(len(chessboard.__list__()[j])):
									if chessboard.__list__()[j][i] == self:
										self.__position = [j,i]
							#if self.__position == None:
							#	print 'Pos not found ! (__init__) (',type,color,number,')'
						else:
							print 'An error ! 0'
							return None
					except:
						print 'An error ! 1'
						return None
				else:
					print 'An error ! 2'
					return None
			else:
				print 'An error ! 3'
				return None
		else:
			print 'An error ! 4'
			return None
	def get_position(self):
		"""Return the 'Position' of the piece
		"""
		return self.__position
	__position__ = position = get_position
	@property
	def number(self):
		return self.__number
	@number.setter
	def number(self, *ignored):
		pass
	@property
	def type(self):
		return self.__type
	@type.setter
	def type(self, *ignored):
		pass
	@property
	def color(self):
		return self.__color
	@color.setter
	def color(self, *ignored):
		pass
	def get_chessboard(self):
		"""Return the 'Chessboard' of the piece
		"""
		return self.__chessboard
	def set_chessboard(self, chessboard):
		"""Function use to change the chessboard,
		
		Check if the instance of the value is correct
		"""
		if isinstance(chessboard, Chessboard):
			self.__chessboard = chessboard
			for j in range(len(chessboard.__list__())):
				for i in range(len(chessboard.__list__()[j])):
					if chessboard.__list__()[j][i] == self:
						self.__position = [j,i]
						return
			print 'Pos not found ! (set_chessboard) (',self.type,self.color,self.number,')'
			self.__position = None
		else:
			pass
	__chessboard__ = chessboard = get_chessboard
	def get_moves(self, chessboard = None):
		"""Return the list of move valid for the piece
		1. chessboard == None
			return [pos for pos in self.get_moves(self.__chessboard.__list__()) \\
				if self.__chessboard.is_valid_move(self, Position(pos[1],pos[0]))]
		2. chessboard == A valid chessboard
			Return the liste of moves, don't take care of the state of the chessboard,
			except the position of pieces.
		"""
		if chessboard == None:
			return [pos for pos in self.get_moves(self.__chessboard.__list__()) \
				if self.__chessboard.is_valid_move(self, Position(pos[1],pos[0]))]
		else:
			try:
				pos = self.__position
				liste = []
				if self.__type == 'bishop':
					j=1
					while pos[0]-j>=0 and pos[1]-j>=0:
						if chessboard[pos[0]-j][pos[1]-j] == []:
							liste.append([pos[0]-j,pos[1]-j])
						else:
							if self.__color !=  chessboard[pos[0]-j][pos[1]-j].color:
								liste.append([pos[0]-j,pos[1]-j])
							j=8
						j += 1
					j=1
					while pos[0]+j <= 7 and pos[1]+j <= 7:
						if chessboard[pos[0]+j][pos[1]+j] == []:
							liste.append([pos[0]+j,pos[1]+j])
						else:
							if self.__color != chessboard[pos[0]+j][pos[1]+j].color:
								liste.append([pos[0]+j,pos[1]+j])
							j=8
						j += 1
					j=1
					while pos[0]-j >= 0 and pos[1]+j <= 7:
						if chessboard[pos[0]-j][pos[1]+j] == []:
							liste.append([pos[0]-j,pos[1]+j])
						else:
							if self.__color !=  chessboard[pos[0]-j][pos[1]+j].color:
								liste.append([pos[0]-j,pos[1]+j])
							j=8
							j=8
						j += 1
					j=1
					while pos[0]+j <= 7 and pos[1]-j >= 0:
						if chessboard[pos[0]+j][pos[1]-j] == []:
							liste.append([pos[0]+j,pos[1]-j])
						else:
							if self.__color !=  chessboard[pos[0]+j][pos[1]-j].color:
								liste.append([pos[0]+j,pos[1]-j])
							j=8
						j += 1
				elif self.__type == 'king':
					if pos[0]+1 <= 7:
						if chessboard[pos[0]+1][pos[1]] == [] or\
							self.__color != chessboard[pos[0]+1][pos[1]].color:
							liste.append([pos[0]+1,pos[1]])
						if pos[1]+1 <= 7:
							if chessboard[pos[0]+1][pos[1]+1] == [] or\
								self.__color !=  chessboard[pos[0]+1][pos[1]+1].color:
								liste.append([pos[0]+1,pos[1]+1])
						if pos[1]-1 >= 0:
							if chessboard[pos[0]+1][pos[1]-1] == [] or\
								self.__color != chessboard[pos[0]+1][pos[1]-1].color:
								liste.append([pos[0]+1,pos[1]-1])
					if pos[0]-1 >= 0:
						if chessboard[pos[0]-1][pos[1]] == [] or\
							self.__color != chessboard[pos[0]-1][pos[1]].color:
							liste.append([pos[0]-1,pos[1]])
						if pos[1]+1 <= 7:
							if chessboard[pos[0]-1][pos[1]+1] == [] or\
								self.__color != chessboard[pos[0]-1][pos[1]+1].color:
								liste.append([pos[0]-1,pos[1]+1])
						if pos[1]-1 >= 0:
							if chessboard[pos[0]-1][pos[1]-1] == [] or\
								self.__color != chessboard[pos[0]-1][pos[1]-1].color:
								liste.append([pos[0]-1,pos[1]-1])
					if pos[1]+1 <= 7:
						if chessboard[pos[0]][pos[1]+1] == [] or\
							self.__color != chessboard[pos[0]][pos[1]+1].color:
							liste.append([pos[0],pos[1]+1])
					if pos[1]-1 >= 0:
						if chessboard[pos[0]][pos[1]-1] == [] or\
							self.__color != chessboard[pos[0]][pos[1]-1].color:
							liste.append([pos[0],pos[1]-1])
				elif self.__type == 'knight':
					if pos[0]+1 <= 7:
						if pos[1]+2 <= 7:
							if chessboard[pos[0]+1][pos[1]+2] == [] or\
								self.__color != chessboard[pos[0]+1][pos[1]+2].color:
								liste.append([pos[0]+1,pos[1]+2])
						if pos[1]-2 >= 0:
							if chessboard[pos[0]+1][pos[1]-2] == [] or\
								self.__color != chessboard[pos[0]+1][pos[1]-2].color:
								liste.append([pos[0]+1,pos[1]-2])
					if pos[0]-1 >= 0:
						if pos[1]-2 >= 0:
							if chessboard[pos[0]-1][pos[1]-2] == [] or\
								self.__color != chessboard[pos[0]-1][pos[1]-2].color:
								liste.append([pos[0]-1,pos[1]-2])
						if pos[1]+2 <= 7:
							if chessboard[pos[0]-1][pos[1]+2] == [] or\
								self.__color != chessboard[pos[0]-1][pos[1]+2].color:
								liste.append([pos[0]-1,pos[1]+2])
					if pos[0]+2 <= 7:
						if pos[1]+1 <= 7:
							if chessboard[pos[0]+2][pos[1]+1] == [] or\
								self.__color != chessboard[pos[0]+2][pos[1]+1].color:
								liste.append([pos[0]+2,pos[1]+1])
						if pos[1]-1 >= 0:
							if chessboard[pos[0]+2][pos[1]-1] == [] or\
								self.__color != chessboard[pos[0]+2][pos[1]-1].color:
								liste.append([pos[0]+2,pos[1]-1])
					if pos[0]-2 >= 0:
						if pos[1]-1 >= 0:
							if chessboard[pos[0]-2][pos[1]-1] == [] or\
								self.__color != chessboard[pos[0]-2][pos[1]-1].color:
								liste.append([pos[0]-2,pos[1]-1])
						if pos[1]+1 <= 7:
							if chessboard[pos[0]-2][pos[1]+1] == [] or\
								self.__color != chessboard[pos[0]-2][pos[1]+1].color:
								liste.append([pos[0]-2,pos[1]+1])
				elif self.__type == 'pawn':
					if self.__color == 'white':
						if pos[0]+1 <= 7:
							if chessboard[pos[0]+1][pos[1]] == []:
								liste.append([pos[0]+1,pos[1]])
						if pos[0] == 1 and chessboard[pos[0]+2][pos[1]] == [] and chessboard[pos[0]+1][pos[1]] == []:
							liste.append([pos[0]+2,pos[1]])
						if pos[0]+1 <= 7 and pos[1]-1 >= 0:
							if chessboard[pos[0]+1][pos[1]-1] != [] and self.__color != chessboard[pos[0]+1][pos[1]-1].color:
								liste.append([pos[0]+1,pos[1]-1])
						if pos[0]+1 <= 7 and pos[1]+1 <= 7:
							if chessboard[pos[0]+1][pos[1]+1] != [] and self.__color != chessboard[pos[0]+1][pos[1]+1].color:
								liste.append([pos[0]+1,pos[1]+1])
					else:
						if pos[0]-1 >= 0:
							if chessboard[pos[0]-1][pos[1]] == []:
								liste.append([pos[0]-1,pos[1]])
						if pos[0] == 6 and chessboard[pos[0]-2][pos[1]] == [] and chessboard[pos[0]-1][pos[1]] == []:
							liste.append([pos[0]-2,pos[1]])
						if pos[0]-1 >= 0 and pos[1]-1 >= 0:
							if chessboard[pos[0]-1][pos[1]-1] != [] and self.__color != chessboard[pos[0]-1][pos[1]-1].color:
								liste.append([pos[0]-1,pos[1]-1])
						if pos[0]-1 >= 0 and pos[1]+1 <= 7:
							if chessboard[pos[0]-1][pos[1]+1] != [] and self.__color != chessboard[pos[0]-1][pos[1]+1].color:
								liste.append([pos[0]-1,pos[1]+1])
				elif self.__type == 'queen':
					j=1
					while pos[0]-j>=0 and pos[1]-j>=0:
						if chessboard[pos[0]-j][pos[1]-j] == []:
							liste.append([pos[0]-j,pos[1]-j])
						else:
							if self.__color !=  chessboard[pos[0]-j][pos[1]-j].color:
								liste.append([pos[0]-j,pos[1]-j])
							j=8
						j += 1
					j=1
					while pos[0]+j <= 7 and pos[1]+j <= 7:
						if chessboard[pos[0]+j][pos[1]+j] == []:
							liste.append([pos[0]+j,pos[1]+j])
						else:
							if self.__color != chessboard[pos[0]+j][pos[1]+j].color:
								liste.append([pos[0]+j,pos[1]+j])
							j=8
						j += 1
					j=1
					while pos[0]-j >= 0 and pos[1]+j <= 7:
						if chessboard[pos[0]-j][pos[1]+j] == []:
							liste.append([pos[0]-j,pos[1]+j])
						else:
							if self.__color !=  chessboard[pos[0]-j][pos[1]+j].color:
								liste.append([pos[0]-j,pos[1]+j])
							j=8
						j += 1
					j=1
					while pos[0]+j <= 7 and pos[1]-j >= 0:
						if chessboard[pos[0]+j][pos[1]-j] == []:
							liste.append([pos[0]+j,pos[1]-j])
						else:
							if self.__color !=  chessboard[pos[0]+j][pos[1]-j].color:
								liste.append([pos[0]+j,pos[1]-j])
							j=8
						j += 1
					j=1
					while pos[0]-j >= 0 and pos[1] >= 0:
						if chessboard[pos[0]-j][pos[1]] == []:
							liste.append([pos[0]-j,pos[1]])
						else:
							if self.__color != chessboard[pos[0]-j][pos[1]].color:
								liste.append([pos[0]-j,pos[1]])
							j=8
						j += 1
					j=1
					while pos[0]+j <= 7 and pos[1] <= 7:
						if chessboard[pos[0]+j][pos[1]] == []:
							liste.append([pos[0]+j,pos[1]])
						else:
							if self.__color != chessboard[pos[0]+j][pos[1]].color:
								liste.append([pos[0]+j,pos[1]])
							j=8
						j += 1
					j=1
					while pos[0] >= 0 and pos[1]+j <= 7:
						if chessboard[pos[0]][pos[1]+j] == []:
							liste.append([pos[0],pos[1]+j])
						else:
							if self.__color != chessboard[pos[0]][pos[1]+j].color:
								liste.append([pos[0],pos[1]+j])
							j=8
						j += 1
					j=1
					while pos[0] <= 7 and pos[1]-j >= 0:
						if chessboard[pos[0]][pos[1]-j] == []:
							liste.append([pos[0],pos[1]-j])
						else:
							if self.__color != chessboard[pos[0]][pos[1]-j].color:
								liste.append([pos[0],pos[1]-j])
						j=8
					j += 1
				elif self.__type == 'rock':
					j=1
					while pos[0]-j >= 0 and pos[1] >= 0:
						if chessboard[pos[0]-j][pos[1]] == []:
							liste.append([pos[0]-j,pos[1]])
						else:
							if self.__color != chessboard[pos[0]-j][pos[1]].color:
								liste.append([pos[0]-j,pos[1]])
							j=8
						j += 1
					j=1
					while pos[0]+j <= 7 and pos[1] <= 7:
						if chessboard[pos[0]+j][pos[1]] == []:
							liste.append([pos[0]+j,pos[1]])
						else:
							if self.__color != chessboard[pos[0]+j][pos[1]].color:
								liste.append([pos[0]+j,pos[1]])
							j=8
						j += 1
					j=1
					while pos[0] >= 0 and pos[1]+j <= 7:
						if chessboard[pos[0]][pos[1]+j] == []:
							liste.append([pos[0],pos[1]+j])
						else:
							if self.__color != chessboard[pos[0]][pos[1]+j].color:
								liste.append([pos[0],pos[1]+j])
							j=8
						j += 1
					j=1
					while pos[0] <= 7 and pos[1]-j >= 0:
						if chessboard[pos[0]][pos[1]-j] == []:
							liste.append([pos[0],pos[1]-j])
						else:
							if self.__color != chessboard[pos[0]][pos[1]-j].color:
								liste.append([pos[0],pos[1]-j])
							j=8
						j += 1
				else:
					return
				return liste
			except:
				return []
	def __eq__(self, other):
		return isinstance(other, Piece) and self.__number == other.number and \
			self.__type == other.type and self.__color == other.color
	def __str__(self, start = None, stop = None):
		return (str(self.__type)+' '+str(self.__color)+('',' '+str(self.__number))[self.__number != None]+' '+translate_move(self.__position))[start:stop]

class Position:
	def __init__(self, x,y):
		if isinstance(x, int) and isinstance(y, int) and x < 8 and y < 8 and x >= 0 and y >= 0:
			self.__x = x
			self.__y = y
		elif isinstance(x, int) and x < 8 and x >= 0 and\
			isinstance(y, chr) and ord(y) <  73 and ord(y) > 64:
			self.__x = x
			self.__y = ord(y) - 65
		elif isinstance(x, int) and x < 8 and x >= 0 and isinstance(y, chr) and ord(y) < 105 and ord(y) > 96:
			self.__x = x
			self.__y = ord(y) - 97
		else:
			return None
	def __str__(self):
		return '['+str(self.__y)+', '+str(self.__x)+']'
	def __dict__(self, ord = int):
		if ord == int:
			return {'x':self.__x, 'y':self.__y}
		elif ord == chr:
			return {'x':self.__x, 'y':chr(self.__y+65)}
		else:
			raise ValueError, 'Invalid format for "ord" !'
	def __list__(self,ord = int):
		if ord == int:
			return [self.__y, self.__x]
		elif ord == chr:
			return [chr(self.__y+65),self.__x]
		else:
			raise ValueError, 'Invalid format for "ord" !'
	def __eq__(self, other, ord = int):
		return isinstance(other, Position) and self.__list__(ord) == other.__list__(ord)
	def __hash__(self):
		return None

class my_chess(cmd.Cmd):
	def __init__(self):
		"""Initilize the game, creat the 'Chessboard' with 'Piece's for black and white player, white begin !
		The player color is the prompt font color (black or white),
		This terminal is an imporve of cmd lib and custom to play chess"""
		cmd.Cmd.__init__(self)
		self.__players = ['black','white']
		self.__chessboard = Chessboard('default')
		self.__move = 0
		self.__quit = False
		self.__prompt()
	def preloop(self):
		"""Print representation of the 'Chessboard', before the game start"""
		self.__print_chess()
	def postcmd(self, stop, line):
		"""After a request form a player if it's a move, the program check if he win
		and so stop the program,
		Also stop the program if it's needed by the return of a function"""
		if line.split(' ')[0] == 'set' and stop == 1:
			self.__move += 1
			self.__prompt()
			stop = 0
			self.__print_chess()
			return self.__is_win()
		return stop
	def postloop(self):
		"""This function is called at the end of the program and say who win"""
		if not self.__quit:
			print '\033[1;32m'+['black','white'][self.__move%2 == 0]+' player win ! ! !\033[1;m'
		return
	def default(self, arg):
		pass
	def emptyline(self):
		"""Function called if the line is empty,
		Do nothing !"""
		pass
	def do_help(self, arg):
		"""List available commands with "help" or detailed help with "help cmd".
		Same implement than in "cmd" but remove 2 tab in the doc !"""
		if arg:
			# XXX check arg syntax
			try:
				func = getattr(self, 'help_' + arg)
			except AttributeError:
				try:
					doc=getattr(self, 'do_' + arg).__doc__
					if doc:
						self.stdout.write("%s\n"%'\n'.join([line.replace('\t','',2) for line in str(doc).split('\n')]))
						return
				except AttributeError:
					pass
				self.stdout.write("%s\n"%str(self.nohelp % (arg,)))
				return
			func()
		else:
			names = self.get_names()
			cmds_doc = []
			cmds_undoc = []
			help = {}
			for name in names:
				if name[:5] == 'help_':
					help[name[5:]]=1
			names.sort()
			# There can be duplicates if routines overridden
			prevname = ''
			for name in names:
				if name[:3] == 'do_':
					if name == prevname:
						continue
					prevname = name
					cmd=name[3:]
					if cmd in help:
						cmds_doc.append(cmd)
						del help[cmd]
					elif getattr(self, name).__doc__:
						cmds_doc.append(cmd)
					else:
						cmds_undoc.append(cmd)
			self.stdout.write("%s\n"%str(self.doc_leader))
			self.print_topics(self.doc_header,   cmds_doc,   15,80)
			self.print_topics(self.misc_header,  help.keys(),15,80)
			self.print_topics(self.undoc_header, cmds_undoc, 15,80)
	@options([make_option('-v', '--vebose', action="store_true", help="print information normaly hide"),
		make_option('-m', '--moves', action="store_true", help="get moves of pieces; default all; in verbose say explicite no move; Don't duplicate with Arguments"),
		make_option('-c', '--color', action="store", help="get pieces of selected color; default all else black or white; Don't duplicate with Arguments"),
		make_option('-n', '--number', action="store",type = "int", help="get piece with your number"),
		make_option('-t', '--type', action="store", help="get piece with your type"),
		],"[arguments]\n\nArguments:\n"+\
		"  [moves]\t\tget moves of all selected pieces; default all pieces; in verbose\n"+\
		"\t\t\tsay explicite no move; Don't duplicate with Options\n"
		"  [<piece_type>]\tget pieces of selected type; default all, else select a valid type\n"+\
		"  [black|white]\t\tget pieces of selected color; default all, else black or white; \n"+\
		"\t\t\tDon't duplicate with Options\n"+\
		"  [chess]\t\tprint the chess; use it alone\n"+\
		"  [all]\t\t\tget position of all piece; use it alone\n"+\
		"  [multi-moves]\t\tGive [number] of simulation for current player; Default 2 turns")
	def do_get(self, arg, opts):
		"""Give information from the game, imput are protect, request need to be clear and correct,
		"""
		pieces = self.__chessboard.pieces()
		_move = False
		if opts.color in ['black','white']:
			pieces = [piece for piece in pieces if piece.color == opts.color]
		elif opts.color != None:
			pieces = []
		if opts.number:
			pieces = [piece for piece in pieces if piece.number == opts.number]
		if opts.type in Piece.types:
			pieces = [piece for piece in pieces if piece.type == opts.type]
		elif opts.type != None:
			pieces = []
		if arg.split(' ')[0] in ['black','white']:
			if opts.color:
				pieces = []
			else:
				pieces = [piece for piece in pieces if piece.color == arg.split(' ')[0]]
			if len(arg.split(' ')) == 2:
				if arg.split(' ')[1] == 'moves':
					_move = True
				elif arg.split(' ')[1] in Piece.types:
					if opts.type:
						pieces = []
					pieces = [piece for piece in pieces if piece.type == arg.split(' ')[1]]
				else:
					pieces = []
			elif len(arg.split(' ')) == 3:
				if arg.split(' ')[1] == 'moves' and arg.split(' ')[2] in Piece.types:
					if opts.type:
						pieces = []
					pieces = [piece for piece in pieces if piece.type == arg.split(' ')[2]]
					_move = True
				elif arg.split(' ')[2] == 'moves' and arg.split(' ')[1] in Piece.types:
					if opts.type:
						pieces = []
					pieces = [piece for piece in pieces if piece.type == arg.split(' ')[1]]
					_move = True
				else:
					pieces = []
			elif len(arg.split(' ')) != 1:
				pieces =[]
			if opts.moves != _move:
				for piece in pieces:
					moves = piece.get_moves()
					if moves != [] or opts.vebose:
						print piece,':',[translate_move(move) for move in moves]
			elif pieces != []:
				print '\n'.join([piece.__str__() for piece in pieces])
		elif arg.split(' ')[0] == 'moves':
			if len(arg.split(' ')) == 2 :
				if arg.split(' ')[1] in ['black','white']:
					if opts.color:
						pieces = []
					pieces = [piece for piece in pieces if piece.color == arg.split(' ')[1]]
				elif arg.split(' ')[1] in Piece.types:
					if opts.type:
						pieces = []
					pieces = [piece for piece in pieces if piece.type == arg.split(' ')[1]]
				else:
					pieces = []
			elif len(arg.split(' ')) == 3:
				if opts.color:
					pieces = []
				if arg.split(' ')[1] in ['black','white']:
					pieces = [piece for piece in pieces if piece.color == arg.split(' ')[1]]
				elif arg.split(' ')[2] in ['black','white']:
					pieces = [piece for piece in pieces if piece.color == arg.split(' ')[2]]
				else:
					pieces = []
				if arg.split(' ')[1] in Piece.types:
					if opts.type:
						pieces = []
					pieces = [piece for piece in pieces if piece.type == arg.split(' ')[1]]
				elif arg.split(' ')[2] in Piece.types:
					if opts.type:
						pieces = []
					pieces = [piece for piece in pieces if piece.type == arg.split(' ')[2]]
				else:
					pieces = []
			elif len(arg.split(' ')) != 1:
				pieces = []
			if opts.moves:
				pieces = []
			for piece in pieces:
				moves = piece.get_moves()
				if moves != [] or opts.vebose:
					print piece,':',[translate_move(move) for move in moves]
		elif arg.split(' ')[0] in Piece.types:
			if opts.type:
				pieces = []
			if len(arg.split(' ')) == 2 :
				if arg.split(' ')[1] in ['black','white']:
					pieces = [piece for piece in pieces if piece.color == arg.split(' ')[1]]
					if opts.color:
						pieces = []
				elif arg.split(' ')[1] == 'moves':
					_move = True
				else:
					pieces = []
			elif len(arg.split(' ')) == 3 :
				if opts.color:
						pieces = []
				elif arg.split(' ')[1] in ['black','white']:
					pieces = [piece for piece in pieces if piece.color == arg.split(' ')[1]]
				elif arg.split(' ')[2] in ['black','white']:
					pieces = [piece for piece in pieces if piece.color == arg.split(' ')[2]]
				else:
					pieces = []
				if arg.split(' ')[1] == 'moves':
					_move = True
				elif arg.split(' ')[2] == 'moves':
					_move = True
				else:
					pieces = []
			elif len(arg.split(' ')) != 1:
				pieces = []
			pieces = [piece for piece in pieces if piece.type == arg.split(' ')[0]]
			if (opts.moves and not _move) or (not opts.moves and _move):
				for piece in pieces:
					moves = piece.get_moves()
					if moves != [] or opts.vebose:
						print piece.__str__(None,-3),':',[translate_move(move) for move in moves]
			elif pieces != []:
				print '\n'.join([piece.__str__() for piece in pieces])
		elif arg.split(' ')[0] == 'multi-moves' and not opts.color:
			pieces = [piece for piece in pieces if piece.color == ('black','white')[self.__move%2 == 0]]
			turns = 2
			if len(arg.split(' ')) == 2 and arg.split(' ')[1].isdigit():
				turns = int(arg.split(' ')[1])
				if turns > 4:
					print 'No valid entry ! (1)'
					return
			elif len(arg.split(' ')) != 1:
				print 'No valid entry ! (0)'
				return
			print self.__chessboard.get_multi_moves(turns = turns, pieces = pieces)
			return
		elif len(arg) == 0:
			if opts.color in ['black','white']:
				pieces = [piece for piece in pieces if piece.color == opts.color]
			elif opts.color != None:
				pieces = []
			if opts.number:
				pieces = [piece for piece in pieces if piece.number == opts.number]
			if opts.moves:
				for piece in pieces:
					moves = piece.get_moves()
					if moves != [] or opts.vebose:
						print piece,':',[translate_move(move) for move in moves]
			elif opts.color or opts.number and pieces != []:
				print '\n'.join([piece.__str__() for piece in pieces])
		elif arg == 'chess': 
			self.__print_chess()
		elif arg == 'all':
			print '\n'.join([piece.__str__() for piece in pieces])
		else:
			pieces = []
			print 'No valid entry !'
		return
	def complete_get(self, text, arg, start_index, end_index):
		"""Completor for get function, 
		Can complete all valide request"""
		keys = ['moves', 'chess','black', 'white','all','multi-moves']+list(set([item.type for item in self.__chessboard.pieces()]))+[color for color in Piece.colors]
		if text:    
			return [
				address for address in keys
				if address.startswith(text)
				]
		else:
			return keys
	def do_set(self, arg):
		"""Function use to move a piece, juste move 'Piece' of the current player
		Can do a move with few information if there is no ambiguity,
			- Position to set
			- Type of the 'Piece'
			- Number, if it's the only to distinguish to 'Piece'"""
		args = arg.split(' ')
		number = None
		type = None
		position = None
		color = ['black','white'][self.__move%2 == 0]
		for arg in args:
			if arg in Piece.types:
				type = arg
			elif len(arg) == 2 and (ord(arg[0]) > 64 and ord(arg[0]) < 73) and ord(arg[1]) < 57 and ord(arg[1]) > 48:
				position = [ord(arg[1])-49,ord(arg[0])-65]
			elif len(arg) == 2 and (ord(arg[0]) > 96 and ord(arg[0]) < 105) and ord(arg[1]) < 57 and ord(arg[1]) > 48:
				position = [ord(arg[1])-49,ord(arg[0])-97]
			elif arg.isdigit() and len(arg) == 1:
				number = arg
			else:
				return
		if type != None:
			pieces = [piece for piece in self.__chessboard.pieces(color) if piece.type == type]
		else:
			pieces = self.__chessboard.pieces(color)
		if number != None:
			pieces = [piece for piece in pieces if piece.number == int(number)]
		if pieces == []:
			print 'No piece found from description'
			return
		else:
			try:
				pieces = [piece for piece in pieces if position in piece.get_moves()]
				if len(pieces) == 0:
					print 'No piece found from description'
					return
				elif len(pieces) == 1:
					piece = pieces[0]
					pieces = self.__chessboard.pieces(['black','white'][color == 'black'])
					dest = [other for other in pieces if other.position() == position] or None
					mess = 'Your '+piece.type+('',' '+str(piece.number))[piece.number != None]+' go on '+translate_move(position)
					if dest != None:
						mess += ' and take '+('black','white')[color == 'black']+' '+dest[0].type+('',' '+str(dest[0].number))[dest[0].number != None]
					print mess
					self.__chessboard = self.__chessboard.move(piece,Position(position[1],position[0]))
					return 1
				else:
					print 'Desciption invalid, ambiguity of proposition ! ('+' or '.join([piece.__str__() for piece in pieces])+')'
					return
			except:
				return
	def complete_set(self, text, arg, start_index, end_index):
		"""Completor for set function,
		Can complete for valid request, only type of 'Piece'"""
		keys = [type for type  in Piece.types]
		cmd, arg, line = self.parseline(arg)
		if arg in keys:
			return []
		elif text:    
			return [
				address for address in keys
				if address.startswith(text)
				]
		else:
			return keys
	def do_surrender(self, line):
		"""This function make the current player surrender,
		Use with caution !"""
		self.__move += 1
		return 1
	def complete_surrender(self, *ignored):
		pass
	def do_quit(self, arg):
		"""End on the game and stop the program
		"""
		self.__quit = True
		return True 
	def complete_quit(self, *ignoreds):
		pass
	def __is_win(self):
		pieces = self.__chessboard.pieces(['black','white'][self.__move%2 == 0])
		moves = []
		for piece in pieces:
			legit = piece.get_moves()
			no_ligit = piece.get_moves(self.__chessboard.__list__())
			moves += legit
		if moves == []:
			self.__move -= 1
			print '\033[1;34mChessmate ! ! !\033[1;m'
			return True
		else:
			return False
	def __print_chess(self):
		print ' '+'_'*((16+0)*8-0)
		i = 0
		for line in self.__chessboard.__list__():
			print '|'+''.join([('','\033[0;30;47m')[(i+j)%2 == 0]+' '*16+('','\033[1;m')[(i+j)%2 == 0] for j in range(8)])+'|\n'+\
				'|'+''.join([('','\033[0;30;47m')[(i+j)%2 == 0]+' '*16+('','\033[1;m')[(i+j)%2 == 0] for j in range(8)])+'|\n'+\
				'|'+''.join([('','\033[0;30;47m')[(i+j)%2 == 0]+' '*16+('','\033[1;m')[(i+j)%2 == 0] for j in range(8)])+'|'
			j = 0
			for piece in line:
				if piece != []:
					mess = ' '+piece.__str__(None,-3)+' '
					sys.stdout.write(('','|')[j == 0]+('','\033[0;30;47m')[(i+j)%2 == 0]+' '*((16-len(mess))/2)+mess+' '*((16-len(mess))/2+(16-len(mess))%2)+('','\033[1;m')[(i+j)%2 == 0]+'')
				else:
					sys.stdout.write(('','|')[j == 0]+('','\033[0;30;47m')[(i+j)%2 == 0]+' '*16+('','\033[1;m')[(i+j)%2 == 0]+'')
				j += 1
			print '|\n'+'|'+''.join([('','\033[0;30;47m')[(i+j)%2 == 0]+' '*16+('','\033[1;m')[(i+j)%2 == 0] for j in range(8)])+'|\n'+\
				'|'+''.join([('','\033[0;30;47m')[(i+j)%2 == 0]+' '*16+('','\033[1;m')[(i+j)%2 == 0] for j in range(8)])+'|\n'+\
				'|'+''.join([('','\033[0;30;47m')[(i+j)%2 == 0]+((' ',' ')[i == 7],' ')[(i+j)%2 == 0]*16+('','\033[1;m')[(i+j)%2 == 0] for j in range(8)])+'|'
			i += 1
	def __prompt(self):
		self.prompt = '<'+('','\033[0;30;47m')[self.__move%2 == 0]+'Chess\033[1;m> '

def main():
	chess = my_chess()
	chess.cmdloop()

if __name__ == '__main__':
	main()

