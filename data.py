import sys
import time
import datetime
import psutil
import os
import re
from urllib.parse import urlencode
import requests
import glob

cwd = os.getcwd()
cwd = cwd.replace('\monitor',"")
disk = cwd.replace('CAMS',"")
api_key_cpu = 'abd3a1ff-7516-4a28-b004-08160038c34f'
api_key_cams = '798a39e4-f35e-4b2e-9339-b19ae898f870'

def cpu():
	cpu = psutil.cpu_percent(interval=1)
	return cpu

def mem():
	n = psutil.virtual_memory()
	n = str(n)
	m = n.split(',')
	mem = m[2]
	mem = re.sub(r'percent=', '',  mem)
	mem = mem.replace(' ',"")
	return mem

def hdd(disk):
	n = psutil.disk_usage(disk)
	n = str(n)
	m = n.split(',')
	hdd = m[3]
	hdd = re.sub(r'percent=', '',  hdd)
	hdd = hdd.replace(')',"")
	hdd = hdd.replace(' ',"")
	return hdd

def prog(name):
    ls = []
    run = 0
    for p in psutil.process_iter(["name", "exe", "cmdline"]):
        if name == p.info['name'] or p.info['exe'] and os.path.basename(p.info['exe']) == name or p.info['cmdline'] and p.info['cmdline'][0] == name:
            ls.append(p)
            run = 1
    return run

def busca_camgui(palavra):
	file = cwd+"\CamsGUI.ini"
	line_number = 0
	with open(file, 'r') as read_obj:
		for line in read_obj:
			line_number += 1
			if palavra in line:
				n = line.rstrip()
				m = n.split('=')
				dado = m[1]
	return dado

def busca_dongle(palavra):
	file = cwd+"\DonglesConfig.txt"
	line_number = 0
	with open(file, 'r') as read_obj:
		for line in read_obj:
			line_number += 1
			if palavra in line:
				n = line.rstrip()
				m = n.split('=')
				dado = m[1]
	return dado

def busca_camsite(a):
	palavra = '----'
	file = cwd+"\CameraSites.txt"
	with open(file, 'r') as read_obj:
		for line in read_obj:
			if palavra in line:
				j = next(read_obj)
				j = " ".join(j.split())
				m = j.split(' ')
				site = m[0]
				lat = m[1]
				lon = float(m[2])
				alt = m[3]
				lon = lon * -1
				lon = str(lon)
	if a == 0:
		return site, lat, lon, alt
	if a == 1:
		return site
	
def envia_cpu():
	data = "%s" % (time.strftime("%Y-%m-%d %H:%M:00"))
	cpu_data = cpu()
	mem_data = mem()
	hdd_data = hdd(disk)
	gui_info = prog("CamsGUI.exe")
	lan_info = prog("LaunchCapture.exe")
	own_info = prog("owncloud.exe")
	dwagent = prog("dwaglnc.exe")
	site = busca_camsite(1)
	values = {'api_key' : api_key_cpu,
		'data' : data,
		'cpu' : cpu_data,
		'mem' : mem_data,
		'hdd' : hdd_data,
		'lan_cap' : lan_info,
		'gui_cam' : gui_info,
		'own_inf' : own_info,
		'id' : site,
		'dwagent' : dwagent }
	url = 'http://192.168.0.6/insert.php?'
	r = requests.post(url, values)
	pastebin_url = r.text
	#print(data, pastebin_url)

def envia_cams():
	data = "%s" % (time.strftime("%Y-%m-%d %H:%M:00"))
	star = busca_camgui("minimumStarCount")
	days = busca_camgui("diskspacewarning")
	fps = busca_dongle("Desired frame rate in integer fps")
	col = busca_dongle("col")
	row = busca_dongle("row")
	tipo = busca_dongle("Connection type see below")
	forma = busca_dongle("format")
	site,lat,lon,alt = busca_camsite(0)
	res = (col+'x'+row)
	res = res.replace(' ',"")
	pasta = str(cwd)
	datec = calib("Calibration date")
	horac = calib("Calibration time")
	fov = calib("FOV dimension hxw")
	fov = str(fov)
	azim = calib("Cal center Azim")
	elev = calib("Cal center Elev")
	datahorac = datec+" "+horac
	values = {'api_key' : api_key_cams,
		'data' : data,
		'lat' : lat,
		'lon' : lon,
		'alt' : alt,
		'video_form' : forma,
		'con_type' : tipo,
		'fps' : fps,
		'res' : res,
		'det_star' : star,
		'hd_day' : days,
		'id' : site,
		'pasta' : pasta,
		'datahorac' : datahorac,
		'fov' : fov,
		'azim' : azim,
		'elev' : elev,
		'lastfile' : lastfile}
	url = 'http://192.168.0.6/insert.php?'
	r = requests.post(url, values)
	pastebin_url = r.text
	#print(data, pastebin_url)

def calib(palavra):
	global lastfile
	site = busca_camsite(1)
	x = "\cal\BinFiles\CAL_00"+site+"*.txt*"
	caldir = cwd+x
	result = glob.glob(caldir)
	file = result[-1]
	fi = cwd+"\cal\BinFiles\\"
	lastfile = file.replace(str(fi),"")
	line_number = 0
	with open(file, 'r') as read_obj:
		for line in read_obj:
			line_number += 1
			if palavra in line:
				n = line.rstrip()
				m = n.split('=')
				dado = m[1]
	dado = dado.replace(" ","")
	return dado

envia_cams()	
while 1:
	minuto = "%s" % (time.strftime("%M"))
	if minuto == '00':
		for i in range(0,1):
			envia_cams()
	envia_cpu()
	time.sleep(60)