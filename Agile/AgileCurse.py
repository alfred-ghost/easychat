from ctypes import *
import os
lib = cdll.LoadLibrary(r"Agile\AgileCurse.dll")
lib.set_character.argtypes=[c_int,c_int,c_char,c_bool]
lib.flush_with.argtypes=[c_int,c_int,c_int,c_int,c_char]
lib.set_title.argtypes=[c_char_p]
lib.set_color.argtypes=[c_int,c_int]
lib.set_windowSize.argtypes=[c_int,c_int]
lib.get_window_x0.restype = c_long
lib.get_window_x1.restype = c_long
lib.get_window_y0.restype = c_long
lib.get_window_y1.restype = c_long
lib.move_window.argtypes = [c_int,c_int]
lib.help.argtypes=[c_char_p]
lib.set_cursePos.argtypes = [c_int,c_int]
lib.set_cursor.argtypes = [c_bool]
def set_cursor(option):
	"""
	设置光标模式
	"""
	lib.set_cursor(option)
	
def set_cursePos(row,column):
	"""
	设置光标位置
	"""
	lib.set_cursePos(row,column)

def set_character(row,column,ch,b):
	"""
	在特定位置输出字符
	"""
	lib.set_character(row,column,ch.encode('utf-8'),b)

def set_title(string):
	"""
	设置控制台窗口
	"""
	lib.set_title(string.encode('utf-8'))
	
def set_color(a,b):
	"""
	设置输出的前景和背景颜色，0-15
	"""
	lib.set_color(a,b)
	
def set_windowSize(width,height):
	"""
	设置窗体大小
	"""
	lib.set_windowSize(width,height)
	
def get_windowPos():
	"""
	获得窗体位置
	"""
	return lib.get_window_x0(),lib.get_window_x1(),lib.get_window_y0(),lib.get_window_y1()
	
def move_window(dx,dy):
	"""
	移动窗体
	"""
	return lib.move_window(dx,dy)
	
def help(string):
	"""
	获得帮助
	"""
	print("> |动态库Agile系列由@Alfred制作| >\n\n")
	if string.startswith("lib."):
		lib.help(string[4:].encode('utf-8'))
	else:
		if string == "set_title":
			print("%s 设置窗体的名称"%string)
		elif string == "set_color":
			print("%s 设置输出字体和背景色彩(0-15,可参考cmd的color)"%string)
		elif string == "set_windowSize":
			print("%s 设置窗体大小"%string);
		elif string == "get_eindowPos":
			print("%s 获得窗体的位置坐标"%string);
		elif string  == "move_Window":
			print("%s 移动窗口"%string)
		elif string == "set_cursePos":
			print("%s 设置光标位置"%string)
		
		
		



