# Create By pekeinfo
# @PekeinfoPkaos


import re
import sys
import os
import requests
import argparse

from pprint import pprint
try:
    from sqlalchemy import Column, ForeignKey, Integer, String, Boolean, update
    from sqlalchemy.ext.declarative import declarative_base
    from sqlalchemy import create_engine
    from sqlalchemy.orm import sessionmaker
    from sqlalchemy.orm import relationship
except Exception as e:
    print "[!]Error: sqlalchemy"

DEBUG = False
UrlUpdate = "https://raw.githubusercontent.com/pan-unit42/iocs/master/keybase/keybase_panels.txt"
###
# BBDD Config
Base = declarative_base()

engine = create_engine('sqlite:///keybase.db', echo=DEBUG)
Session = sessionmaker(bind=engine)
session = Session(autocommit=True)
Base.metadata.create_all(engine)

session = None
###

IGNOREPRE=False

def update_list():
	print "[X]Update List"

	r = requests.get(UrlUpdate, allow_redirects=False, timeout=2.01)
	if len(r.text)>100:
		open("keybase_panels.txt",'w').write(r.text)
	else:
		print "[X]Error Update File"


def printProgress (iteration, total, prefix = '', suffix = '', decimals = 1, barLength = 100):
    """
    Call in a loop to create terminal progress bar
    @params:
        iteration   - Required  : current iteration (Int)
        total       - Required  : total iterations (Int)
        prefix      - Optional  : prefix string (Str)
        suffix      - Optional  : suffix string (Str)
        decimals    - Optional  : positive number of decimals in percent complete (Int)
        barLength   - Optional  : character length of bar (Int)
    """
    formatStr = "{0:." + str(decimals) + "f}"
    percent = formatStr.format(100 * (iteration / float(total)))
    filledLength = int(round(barLength * iteration / float(total)))
    bar = '=' * filledLength + '_' * (barLength - filledLength)
    sys.stdout.write('\r%s 8%sD %s%s %s' % (prefix, bar, percent, '%', suffix)),
    if iteration == total:
        sys.stdout.write('\n')
    sys.stdout.flush()


class Url(Base):
    __tablename__ = 'url'
    id  = Column(Integer,primary_key=True)
    url = Column(String,index=True,nullable=False,unique=True)
    live= Column(Integer)
    expl= Column(Integer)


    #def __repr__(self):
    #    return unicode(self.titulo)

def update_url_live(url):
	print url
	Session = sessionmaker(bind=engine)
	session = Session(autocommit=True)
	Base.metadata.create_all(engine)

	session.query(Url).filter_by(url=url).update({'live':1})

	
	session.begin()
	session.commit()


def get_url_list_live():
	Session = sessionmaker(bind=engine)
	session = Session(autocommit=True)
	Base.metadata.create_all(engine)
	return session.query(Url).filter(Url.live==1).all()

def get_url_list():
	Session = sessionmaker(bind=engine)
	session = Session(autocommit=True)
	Base.metadata.create_all(engine)
	if IGNOREPRE:
		return session.query(Url).all()
	else:
		return session.query(Url).filter(Url.live==-1).all()


def read_file(file="keybase_panels.txt"):
	Session = sessionmaker(bind=engine)
	session = Session(autocommit=True)
	Base.metadata.create_all(engine)
	urllist = open(file,'r').read()
	for i in urllist.split('\n'):
		try:
			urli = i.replace('hxxp','http')
			url = Url(url=urli,live=-1,expl=0)
			session.add(url)
			session.begin()
			session.commit()

		except Exception as e:
			if DEBUG:
				print "[x]Error in url:{0}".format(url.url)
			continue
	
reg = "KeyBase\: Login"


def main(url="keybase_panels.txt"):
	urllist = open(url,'r').read()
	total = len(get_url_list())
	
	e = 0
	for i in get_url_list():
		url = i.url
		e=e+1
		printProgress(e, total, prefix = 'Progress:', suffix = 'Complete', barLength = 50)

		try:
			r = requests.get(url+"/login.php", allow_redirects=False, timeout=2.01)
			if r.status_code == requests.codes.ok:
				m = re.search(reg,r.text)
				if m.group(0):
					print "[ok]: "+ url
					update_url_live(url)
			else:
				exit()
				print "not luck!"
		except:
			continue



if __name__ == '__main__':
	parser = argparse.ArgumentParser('keyBase.py',description="Test keyBase alive!")
	parser.add_argument("-re",action="store_true",help="Analyze url list ignoring preview result,[!]This options analyze all url")
	parser.add_argument("-k","--keybase-list",help="Read file txt with url keybase")
	parser.add_argument("-V",action="store_true",help="Verbose Mode")
	parser.add_argument("-v","--view",action="store_true",help="Only view result")
	parser.add_argument("-U","--update",action="store_true",help="Update list url")

	args = parser.parse_args()


	DEBUG = args.V
	IGNOREPRE = args.re
	if args.update:
		update_list()


	if args.view:
		print "Only view"
		for i in get_url_list_live():
			print(i.url)
		exit()

	if args.keybase_list:
		if os.path.isfile(args.keybase_list):
			read_file(args.keybase_list)
		else:
			print "[X]Error File not exist"
			print "Use Default"
			read_file()

	main()

